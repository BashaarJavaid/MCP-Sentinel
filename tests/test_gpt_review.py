"""Offline Phase 2 semantic-review contract tests."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from functools import cache
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import openai

from scripts.capture_gpt_reviews import _planned_batches, _reserved_micro_usd
from sentinel.config import LlmConfig, ReasoningEffort, load_configuration
from sentinel.finding import (
    DynamicEvidence,
    Finding,
    FindingSource,
    FindingStatus,
    LogicalLocation,
    ProvenanceEntry,
    make_dedup_key,
)
from sentinel.llm.cache import ReviewCache
from sentinel.llm.context import (
    PATH_PLACEHOLDER,
    SECRET_PLACEHOLDER,
    build_finding_context,
    sanitize_text,
)
from sentinel.llm.semantic_reviewer import SemanticReviewer, _classify
from sentinel.llm.tools import extract_tool_catalog
from sentinel.static.engine import run_static_scan

ROOT = Path(__file__).parent / "fixtures" / "gpt_review_eval"
NOW = datetime(2026, 7, 18, tzinfo=timezone.utc)


class FakeTransport:
    def __init__(self, *, invalid_id: bool = False) -> None:
        self.calls = 0
        self.invalid_id = invalid_id
        self.requests: list[dict[str, Any]] = []

    async def create(self, request: dict[str, Any]) -> dict[str, Any]:
        self.calls += 1
        self.requests.append(request)
        untrusted = json.loads(request["input"])["untrusted_repository_data"]
        reviews = []
        for item in untrusted["candidates"]:
            context = untrusted["contexts"][item["context_id"]][0]
            tool = (
                untrusted["tools"][item["tool_id"]]
                if item["tool_id"] is not None
                else None
            )
            plan = None
            if tool is not None and any(
                value.get("type") == "string"
                for value in tool["input_schema"].get("properties", {}).values()
            ):
                field = next(
                    name
                    for name, value in tool["input_schema"]["properties"].items()
                    if value.get("type") == "string"
                )
                plan = {
                    "ordered_probe_ids": [
                        "SENT-011",
                        "SENT-009",
                        "SENT-010",
                        "SENT-008",
                    ],
                    "target_tool": tool["name"],
                    "argument_bindings": [
                        {
                            "probe_id": "SENT-009",
                            "field": field,
                            "value": "__SENTINEL_OVERSIZED__",
                        },
                        {
                            "probe_id": "SENT-010",
                            "field": field,
                            "value": "__SENTINEL_INJECTION__",
                        },
                        {
                            "probe_id": "SENT-011",
                            "field": field,
                            "value": "__SENTINEL_WRONG_TYPE__",
                        },
                    ],
                }
            reviews.append(
                {
                    "finding_id": str(uuid4())
                    if self.invalid_id
                    else item["finding_id"],
                    "status": "confirmed",
                    "confidence": 0.91,
                    "reasoning": "Direct unsafe data flow is visible.",
                    "evidence_refs": [
                        {
                            "path": context["path"],
                            "start_line": context["start_line"],
                            "end_line": context["end_line"],
                            "claim": "The supplied unit contains the unsafe operation.",
                        }
                    ],
                    "probe_plan": plan,
                    "suggested_severity_override": None,
                }
            )
        return {
            "id": "resp_test",
            "status": "completed",
            "error": None,
            "incomplete_details": None,
            "model": "gpt-5.6-sol-2026-07-18",
            "output": [
                {"type": "reasoning", "id": "rs_test"},
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps({"reviews": reviews}),
                            "annotations": [],
                        }
                    ],
                },
            ],
            "usage": {
                "input_tokens": 100,
                "input_tokens_details": {"cached_tokens": 20},
                "output_tokens": 50,
                "output_tokens_details": {"reasoning_tokens": 10},
                "total_tokens": 150,
            },
        }


@cache
def _all_eval_findings() -> tuple[Finding, ...]:
    configuration = load_configuration(ROOT, environ={}, static_only=True)
    return run_static_scan(configuration, uuid4(), timestamp=NOW).findings


def _sent002_findings() -> tuple[Finding, ...]:
    return tuple(item for item in _all_eval_findings() if item.rule_id == "SENT-002")


def test_live_capture_plans_one_attempt_with_per_request_reservations() -> None:
    batches, config = _planned_batches("eval-medium", ReasoningEffort.MEDIUM)

    assert config.retries == 0
    assert len(batches) == 4
    assert all(_reserved_micro_usd(batch) < 250_000 for batch in batches)


def test_demo_capture_uses_production_candidate_order() -> None:
    batches, _ = _planned_batches("demo", ReasoningEffort.MEDIUM)
    file_batch = next(batch for batch in batches if len(batch.candidates) > 1)

    assert [item.finding.rule_id for item in file_batch.candidates] == [
        "SENT-005",
        "SENT-004",
        "SENT-006",
        "SENT-007",
    ]


def test_tool_metadata_comes_from_ast_and_matching_manifest() -> None:
    catalog = extract_tool_catalog(ROOT)
    assert [item.name for item in catalog.tools] == [
        "custom_validated",
        "indirect_reader",
        "unchecked_lookup",
        "unsafe_evaluator",
    ]
    unsafe = next(item for item in catalog.tools if item.name == "unsafe_evaluator")
    assert unsafe.input_schema["properties"] == {"expression": {"type": "string"}}
    assert unsafe.description == "Evaluate a user expression."
    assert catalog.warnings == ()


def test_unversioned_manifest_is_accepted_and_bad_version_falls_back(
    tmp_path: Path,
) -> None:
    (tmp_path / "server.py").write_text(
        '''\
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("test")
@mcp.tool()
def search(query: str | None, limit: int = 10) -> list[str]:
    """AST description."""
    return []
''',
        encoding="utf-8",
    )
    manifest = tmp_path / "tools.yaml"
    manifest.write_text(
        "tools:\n  - name: search\n    description: Manifest description.\n",
        encoding="utf-8",
    )
    accepted = extract_tool_catalog(tmp_path)
    assert accepted.tools[0].description == "Manifest description."
    assert accepted.warnings == ()
    manifest.write_text("version: 2\ntools: []\n", encoding="utf-8")
    fallback = extract_tool_catalog(tmp_path)
    assert fallback.tools[0].description == "AST description."
    assert fallback.warnings[0].code == "tool_manifest_fallback"


def test_context_is_bounded_grounded_and_line_preserving() -> None:
    finding = _sent002_findings()[0]
    context = build_finding_context(ROOT, finding)
    assert sum(block.end_line - block.start_line + 1 for block in context.blocks) <= 160
    assert context.contains("server.py", 16, 17)
    text = 'api_key = "sk-abcdefghijklmnopqrstuvwxyz"\n/Users/alice/private/file'
    sanitized = sanitize_text(text)
    assert SECRET_PLACEHOLDER in sanitized
    assert PATH_PLACEHOLDER in sanitized
    assert sanitized.count("\n") == text.count("\n")


def test_ambiguous_eval_context_does_not_expose_imported_helper() -> None:
    finding = next(item for item in _all_eval_findings() if item.rule_id == "SENT-001")
    context = build_finding_context(ROOT, finding)

    assert len(context.blocks) == 1
    assert "read_one_file(path)" in context.blocks[0].text
    assert "open(" not in context.blocks[0].text


def test_live_review_merges_status_plan_usage_and_authority(tmp_path: Path) -> None:
    finding = _sent002_findings()[0]
    transport = FakeTransport()
    reviewer = SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0),
        max_findings=500,
        mode="live",
        transport=transport,
        cache=ReviewCache(enabled=True, root=tmp_path / "cache"),
        now=lambda: NOW,
    )
    outcome = reviewer.review((finding,), allow_degraded=False)
    reviewed = outcome.findings[0]
    assert outcome.fatal is False
    assert reviewed.status is FindingStatus.CONFIRMED
    assert reviewed.exploitability.value == "likely"
    assert reviewed.review.mode == "live"
    assert reviewed.review.probe_plan is not None
    assert reviewed.review.probe_plan.ordered_probe_ids[0] == "SENT-011"
    assert reviewed.review.probe_plan.argument_bindings["SENT-010"] == {
        "expression": "__SENTINEL_INJECTION__"
    }
    assert reviewed.rule_id == finding.rule_id
    assert reviewed.source == finding.source
    assert reviewed.impact == finding.impact
    assert outcome.summary.origin_usage.total_tokens == 150
    assert outcome.summary.origin_cost_micro_usd is not None
    assert transport.calls == 1
    request = transport.requests[0]
    assert request["model"] == "gpt-5.6-sol"
    assert request["store"] is False
    assert request["service_tier"] == "default"
    assert request["tools"] == []
    assert request["background"] is False
    assert request["text"]["verbosity"] == "low"
    assert request["max_output_tokens"] == 2048
    assert "SENT-011 omits a required" in request["instructions"]
    assert "SENT-003 is absence of" in request["instructions"]
    assert request["prompt_cache_key"].startswith("mcp_sentinel_prompt_v3:")


def test_cache_rebinds_new_runtime_finding_ids(tmp_path: Path) -> None:
    cache = ReviewCache(enabled=True, root=tmp_path / "cache")
    first = _sent002_findings()[0]
    live = FakeTransport()
    SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0),
        max_findings=500,
        mode="live",
        transport=live,
        cache=cache,
        now=lambda: NOW,
    ).review((first,), allow_degraded=False)

    second = first.model_copy(update={"finding_id": uuid4()})
    unused = FakeTransport(invalid_id=True)
    outcome = SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0),
        max_findings=500,
        mode="live",
        transport=unused,
        cache=cache,
        now=lambda: NOW,
    ).review((second,), allow_degraded=False)
    assert outcome.findings[0].finding_id == second.finding_id
    assert outcome.findings[0].review.mode == "cached"
    assert outcome.summary.current_usage.total_tokens == 0
    assert outcome.summary.origin_usage.total_tokens == 150
    assert unused.calls == 0


def test_replay_rebinds_ids_and_preserves_capture_provenance(tmp_path: Path) -> None:
    captured: dict[str, Any] = {}

    def sink(
        fingerprint: str, request: dict[str, Any], response: dict[str, Any]
    ) -> None:
        del request
        captured.update(fingerprint=fingerprint, response=response)

    first = _sent002_findings()[0]
    SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0, cache_enabled=False),
        max_findings=500,
        mode="live",
        transport=FakeTransport(),
        cache=ReviewCache(enabled=False),
        now=lambda: NOW,
        capture_sink=sink,
    ).review((first,), allow_degraded=False)
    fingerprint = captured["fingerprint"]
    cassette = {
        "captured_at": NOW.isoformat().replace("+00:00", "Z"),
        "latency_ms": 123,
        "retry_count": 0,
        "batch_id": f"batch_{fingerprint[:24]}",
        "response": captured["response"],
    }
    (tmp_path / f"{fingerprint}.json").write_text(
        json.dumps(cassette), encoding="utf-8"
    )
    second = first.model_copy(update={"finding_id": uuid4()})
    outcome = SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0, cache_enabled=False),
        max_findings=500,
        mode="replay",
        cache=ReviewCache(enabled=False),
        cassette_root=tmp_path,
        now=lambda: datetime(2030, 1, 1, tzinfo=timezone.utc),
    ).review((second,), allow_degraded=False)
    review = outcome.findings[0].review
    assert review.mode == "replay"
    assert review.reviewed_at == NOW
    assert review.applied_at == datetime(2030, 1, 1, tzinfo=timezone.utc)
    assert review.latency_ms == 123
    assert outcome.summary.current_usage.total_tokens == 0
    assert outcome.summary.origin_usage.total_tokens == 150


def test_invalid_batch_is_atomic_and_fails_closed(tmp_path: Path) -> None:
    finding = _sent002_findings()[0]
    outcome = SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0),
        max_findings=500,
        mode="live",
        transport=FakeTransport(invalid_id=True),
        cache=ReviewCache(enabled=False, root=tmp_path),
        now=lambda: NOW,
    ).review((finding,), allow_degraded=False)
    assert outcome.fatal is True
    assert outcome.findings[0].status is FindingStatus.NEEDS_REVIEW
    assert outcome.findings[0].review.mode == "not_reviewed"


def test_suppressed_static_finding_can_use_fixed_probe_fallback(
    tmp_path: Path,
) -> None:
    class SuppressionTransport(FakeTransport):
        async def create(self, request: dict[str, Any]) -> dict[str, Any]:
            raw = await super().create(request)
            message = next(item for item in raw["output"] if item["type"] == "message")
            payload = json.loads(message["content"][0]["text"])
            payload["reviews"][0].update(status="suppressed", probe_plan=None)
            message["content"][0]["text"] = json.dumps(payload)
            return raw

    finding = next(item for item in _all_eval_findings() if item.rule_id == "SENT-003")
    outcome = SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0),
        max_findings=500,
        mode="live",
        transport=SuppressionTransport(),
        cache=ReviewCache(enabled=False, root=tmp_path),
        now=lambda: NOW,
    ).review((finding,), allow_degraded=False)

    assert outcome.fatal is False
    assert outcome.findings[0].status is FindingStatus.SUPPRESSED
    assert outcome.findings[0].review.probe_plan is None


def test_retry_then_success_uses_sentinel_owned_backoff(tmp_path: Path) -> None:
    class FlakyTransport(FakeTransport):
        async def create(self, request: dict[str, Any]) -> dict[str, Any]:
            if self.calls == 0:
                self.calls += 1
                raise TimeoutError("first attempt timed out")
            return await super().create(request)

    delays: list[float] = []

    async def no_sleep(delay: float) -> None:
        delays.append(delay)

    finding = _sent002_findings()[0]
    transport = FlakyTransport()
    outcome = SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=1),
        max_findings=500,
        mode="live",
        transport=transport,
        cache=ReviewCache(enabled=False, root=tmp_path),
        sleep=no_sleep,
        now=lambda: NOW,
    ).review((finding,), allow_degraded=False)
    assert outcome.fatal is False
    assert transport.calls == 2
    assert len(delays) == 1
    assert 1.0 <= delays[0] <= 2.0
    assert outcome.summary.batches[0].retry_count == 1


def test_api_contract_errors_preserve_safe_diagnostic_detail() -> None:
    response = httpx.Response(
        400,
        request=httpx.Request("POST", "https://api.openai.com/v1/responses"),
    )
    error = openai.BadRequestError(
        "bad request",
        response=response,
        body={
            "error": {
                "message": "Invalid schema for response_format.",
                "param": "text.format.schema",
            }
        },
    )

    failure = _classify(error)

    assert str(failure) == (
        "GPT HTTP 400: Invalid schema for response_format. (param: text.format.schema)"
    )
    assert failure.retryable is False


def test_refusal_can_only_become_explicit_degraded_review(tmp_path: Path) -> None:
    class RefusalTransport:
        async def create(self, request: dict[str, Any]) -> dict[str, Any]:
            del request
            return {
                "status": "completed",
                "error": None,
                "incomplete_details": None,
                "model": "gpt-5.6-sol",
                "output": [
                    {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "refusal", "refusal": "cannot comply"}],
                    }
                ],
            }

    finding = _sent002_findings()[0]
    outcome = SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0),
        max_findings=500,
        mode="live",
        transport=RefusalTransport(),
        cache=ReviewCache(enabled=False, root=tmp_path),
        now=lambda: NOW,
    ).review((finding,), allow_degraded=True)
    assert outcome.fatal is False
    assert outcome.findings[0].review.mode == "degraded"
    assert outcome.findings[0].review.reviewed_at is None
    assert outcome.findings[0].review.applied_at == NOW
    assert any(warning.code == "gpt_review_failed" for warning in outcome.warnings)


def test_finding_cap_keeps_overflow_visible_without_failure(tmp_path: Path) -> None:
    transport = FakeTransport()
    findings = _all_eval_findings()
    outcome = SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0),
        max_findings=1,
        mode="live",
        transport=transport,
        cache=ReviewCache(enabled=False, root=tmp_path),
        now=lambda: NOW,
    ).review(findings, allow_degraded=False)
    assert outcome.fatal is False
    assert outcome.summary.selected_count == 1
    assert outcome.summary.overflow_count == 3
    assert sum(item.review.mode == "degraded" for item in outcome.findings) == 3
    assert any(warning.code == "gpt_review_truncated" for warning in outcome.warnings)


def test_dynamic_candidate_uses_supplied_evidence_and_never_gets_probe_plan(
    sample_finding: Finding, tmp_path: Path
) -> None:
    class ExtraPlanTransport(FakeTransport):
        async def create(self, request: dict[str, Any]) -> dict[str, Any]:
            raw = await super().create(request)
            message = next(item for item in raw["output"] if item["type"] == "message")
            payload = json.loads(message["content"][0]["text"])
            payload["reviews"][0]["probe_plan"] = {
                "ordered_probe_ids": [
                    "SENT-008",
                    "SENT-009",
                    "SENT-010",
                    "SENT-011",
                ],
                "target_tool": "invented_tool",
                "argument_bindings": [
                    {
                        "probe_id": "SENT-009",
                        "field": "value",
                        "value": "__SENTINEL_OVERSIZED__",
                    },
                    {
                        "probe_id": "SENT-010",
                        "field": "value",
                        "value": "__SENTINEL_INJECTION__",
                    },
                    {
                        "probe_id": "SENT-011",
                        "field": "value",
                        "value": "__SENTINEL_WRONG_TYPE__",
                    },
                ],
            }
            message["content"][0]["text"] = json.dumps(payload)
            return raw

    evidence = DynamicEvidence(
        probe_id="SENT-010",
        request={"value": "__SENTINEL_INJECTION__"},
        response={"accepted": True},
    )
    data = sample_finding.model_dump(mode="python", exclude={"severity"})
    data.update(
        finding_id=uuid4(),
        dedup_key=make_dedup_key(("SENT-010", "tool", "probe")),
        rule_id="SENT-010",
        source=FindingSource.DYNAMIC,
        location=LogicalLocation(path="/tools/search"),
        evidence=evidence,
        provenance=(
            ProvenanceEntry(
                source=FindingSource.DYNAMIC,
                rule_id="SENT-010",
                evidence=evidence,
                timestamp=NOW,
            ),
        ),
    )
    dynamic = Finding.model_validate(data)
    outcome = SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0),
        max_findings=500,
        mode="live",
        transport=ExtraPlanTransport(),
        cache=ReviewCache(enabled=False, root=tmp_path),
        now=lambda: NOW,
    ).review((dynamic,), allow_degraded=False)
    reviewed = outcome.findings[0]
    assert reviewed.status is FindingStatus.CONFIRMED
    assert reviewed.exploitability.value == "confirmed"
    assert reviewed.review.probe_plan is None
