"""Budget-gated GPT-5.6 review cassette capture utility."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import tempfile
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid4

import tiktoken

from sentinel.config import LlmConfig, ReasoningEffort, load_configuration
from sentinel.dynamic.prober import run_dynamic_scan
from sentinel.dynamic.sandbox import DockerSandbox, reap_orphans
from sentinel.finding import Finding, FindingSource, TokenUsage
from sentinel.llm.cache import ReviewCache
from sentinel.llm.context import build_finding_context, sanitize_text
from sentinel.llm.semantic_reviewer import (
    MODEL,
    SemanticReviewer,
    _Batch,
    _build_batches,
    _Candidate,
    _candidate_sort_key,
    _cost,
    _tool_for_finding,
)
from sentinel.llm.tools import ToolCatalog, extract_tool_catalog
from sentinel.report.model import GptReviewSummary
from sentinel.static.engine import run_static_scan

ROOT = Path(__file__).resolve().parents[1]
CASSETTES = ROOT / "src" / "sentinel" / "_cassettes"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "checkpoint",
        choices=(
            "smoke",
            "eval-medium",
            "eval-low",
            "demo",
            "phase3-integrated",
        ),
    )
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--max-usd", type=float)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    if args.checkpoint == "phase3-integrated":
        return _capture_phase3_integrated(args, parser)

    effort = (
        ReasoningEffort.LOW if args.checkpoint == "eval-low" else ReasoningEffort.MEDIUM
    )
    batches, config = _planned_batches(args.checkpoint, effort)
    reservations = {batch.fingerprint: _reserved_micro_usd(batch) for batch in batches}
    reserved = sum(reservations.values())
    print(f"checkpoint: {args.checkpoint}")
    print(f"reasoning effort: {effort.value}")
    print(f"request count: {len(batches)}")
    print(f"finding count: {sum(len(batch.candidates) for batch in batches)}")
    print(f"aggregate worst-case cost: ${reserved / 1_000_000:.6f}")
    if not args.live:
        print("dry run: no API key read and no network call made")
        return 0
    if args.max_usd is None or args.max_usd <= 0:
        parser.error("--live requires a positive --max-usd ceiling")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        parser.error("--live requires OPENAI_API_KEY in the environment")

    checkpoint_dir = CASSETTES / args.checkpoint
    new_batches = [
        batch
        for batch in batches
        if args.replace or not (checkpoint_dir / f"{batch.fingerprint}.json").is_file()
    ]
    budget_micro_usd = round(args.max_usd * 1_000_000)
    largest_reservation = max(
        (reservations[batch.fingerprint] for batch in new_batches), default=0
    )
    if largest_reservation > budget_micro_usd:
        parser.error("an uncaptured request's worst-case reservation exceeds --max-usd")
    return asyncio.run(
        _capture(
            batches,
            new_batches,
            config,
            api_key,
            args.checkpoint,
            checkpoint_dir,
            budget_micro_usd=budget_micro_usd,
            replace=args.replace,
        )
    )


def _capture_phase3_integrated(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> int:
    fixture = ROOT / "tests" / "fixtures" / "vulnerable_server"
    loaded = load_configuration(
        fixture,
        environ={},
        cli_overrides={"rules": ("SENT-002",)},
    )
    llm = loaded.scanner.llm.model_copy(
        update={"max_concurrency": 1, "retries": 0, "cache_enabled": False}
    )
    loaded = loaded.model_copy(
        update={"scanner": loaded.scanner.model_copy(update={"llm": llm})}
    )
    scan_id = uuid4()
    timestamp = datetime.now(timezone.utc)
    static_findings = run_static_scan(loaded, scan_id, timestamp=timestamp).findings
    if len(static_findings) != 1 or static_findings[0].rule_id != "SENT-002":
        raise RuntimeError("Phase 3 checkpoint requires exactly one SENT-002 candidate")
    static_batches = _batches_for_findings(fixture, static_findings, llm)
    static_reservation = sum(_reserved_micro_usd(batch) for batch in static_batches)
    print("checkpoint: phase3-integrated")
    print(f"reasoning effort: {llm.reasoning_effort.value}")
    print(f"static request count: {len(static_batches)}")
    print(f"static worst-case cost: ${static_reservation / 1_000_000:.6f}")
    if not args.live:
        print("dry run: dynamic reservation is computed after Docker probing")
        print("dry run: no API key read, Docker launch, or network call made")
        return 0
    if args.replace:
        parser.error("phase3-integrated captures cannot be replaced")
    if args.max_usd is None or args.max_usd <= 0:
        parser.error("--live requires a positive --max-usd ceiling")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        parser.error("--live requires OPENAI_API_KEY in the environment")
    checkpoint_dir = CASSETTES / args.checkpoint
    if checkpoint_dir.exists():
        parser.error("phase3-integrated checkpoint already exists")
    budget_micro_usd = round(args.max_usd * 1_000_000)
    if static_reservation > budget_micro_usd:
        parser.error("static request worst-case reservation exceeds --max-usd")

    static_raw: dict[str, dict[str, Any]] = {}
    static_review = SemanticReviewer(
        root=fixture,
        config=llm,
        max_findings=1,
        mode="live",
        api_key=api_key,
        cache=ReviewCache(enabled=False),
        capture_sink=_capture_into(static_raw),
    ).review(static_findings, allow_degraded=False)
    if static_review.fatal:
        raise RuntimeError("live static review failed during Phase 3 checkpoint")
    plan = static_review.findings[0].review.probe_plan
    if plan is None or plan.target_tool != "unsafe_calculator":
        raise RuntimeError("live static review did not produce the intended probe plan")

    reap_orphans()
    dynamic = run_dynamic_scan(
        DockerSandbox(loaded, scan_id),
        static_review.findings,
        scan_id=scan_id,
        timestamp=timestamp,
    )
    dynamic_rule_ids = {finding.rule_id for finding in dynamic.findings}
    if dynamic_rule_ids != {"SENT-008", "SENT-009", "SENT-010", "SENT-011"}:
        raise RuntimeError(
            f"Phase 3 fixture produced unexpected dynamic rules: {dynamic_rule_ids}"
        )
    dynamic_batches = _batches_for_findings(fixture, dynamic.findings, llm)
    dynamic_reservation = sum(_reserved_micro_usd(batch) for batch in dynamic_batches)
    spent = static_review.summary.current_cost_micro_usd or 0
    print(f"dynamic request count: {len(dynamic_batches)}")
    print(f"dynamic worst-case cost: ${dynamic_reservation / 1_000_000:.6f}")
    if spent + dynamic_reservation > budget_micro_usd:
        raise RuntimeError(
            "remaining live-capture budget cannot reserve dynamic review"
        )

    dynamic_raw: dict[str, dict[str, Any]] = {}
    dynamic_review = SemanticReviewer(
        root=fixture,
        config=llm,
        max_findings=len(dynamic.findings),
        mode="live",
        api_key=api_key,
        cache=ReviewCache(enabled=False),
        capture_sink=_capture_into(dynamic_raw),
    ).review(dynamic.findings, allow_degraded=False)
    if dynamic_review.fatal:
        raise RuntimeError("live dynamic review failed during Phase 3 checkpoint")
    if any(
        finding.source is not FindingSource.DYNAMIC
        or finding.review.probe_plan is not None
        for finding in dynamic_review.findings
    ):
        raise RuntimeError("dynamic review violated source or post-probe plan contract")

    staging = Path(tempfile.mkdtemp(prefix=".phase3-integrated-", dir=CASSETTES))
    try:
        manifest_batches = [
            *_write_captures(staging, "static", static_raw, static_review.summary),
            *_write_captures(staging, "dynamic", dynamic_raw, dynamic_review.summary),
        ]
        _atomic_json(
            staging / "manifest.json",
            {
                "checkpoint": args.checkpoint,
                "model": MODEL,
                "reasoning_effort": llm.reasoning_effort.value,
                "fixture": "vulnerable_server",
                "dynamic_rule_ids": sorted(dynamic_rule_ids),
                "pricing": (
                    dynamic_review.summary.pricing.model_dump(mode="json")
                    if dynamic_review.summary.pricing is not None
                    else None
                ),
                "batches": manifest_batches,
            },
        )
        _replay_phase3(
            fixture,
            llm,
            staging,
            static_findings,
            dynamic.findings,
        )
        os.replace(staging, checkpoint_dir)
    finally:
        if staging.exists():
            shutil.rmtree(staging)

    total = spent + (dynamic_review.summary.current_cost_micro_usd or 0)
    print(f"captured live spend: ${total / 1_000_000:.6f}")
    print("replay validation: passed")
    return 0


def _batches_for_findings(
    root: Path, findings: tuple[Finding, ...], config: LlmConfig
) -> tuple[_Batch, ...]:
    catalog = extract_tool_catalog(root)
    candidates = tuple(
        _Candidate(
            finding=finding,
            context=build_finding_context(root, finding),
            tool=_tool_for_finding(catalog, finding),
        )
        for finding in sorted(findings, key=_candidate_sort_key)
    )
    return _build_batches(candidates, config.reasoning_effort)


def _capture_into(
    destination: dict[str, dict[str, Any]],
) -> Callable[[str, dict[str, Any], dict[str, Any]], None]:
    def sink(
        fingerprint: str, request: dict[str, Any], response: dict[str, Any]
    ) -> None:
        del request
        destination[fingerprint] = response

    return sink


def _write_captures(
    directory: Path,
    stage: str,
    raw_by_fingerprint: dict[str, dict[str, Any]],
    summary: GptReviewSummary,
) -> list[dict[str, Any]]:
    records = {item.request_fingerprint: item for item in summary.batches}
    if set(records) != set(raw_by_fingerprint):
        raise RuntimeError(f"{stage} capture records do not match accepted responses")
    entries: list[dict[str, Any]] = []
    captured_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    for fingerprint, raw in raw_by_fingerprint.items():
        record = records[fingerprint]
        payload = {
            "cassette_version": 1,
            "checkpoint": "phase3-integrated",
            "stage": stage,
            "fingerprint": fingerprint,
            "captured_at": captured_at,
            "requested_model": record.requested_model,
            "returned_model": record.returned_model,
            "reasoning_effort": record.reasoning_effort.value,
            "usage": record.origin_usage.model_dump(mode="json"),
            "latency_ms": record.origin_latency_ms,
            "retry_count": record.retry_count,
            "batch_id": record.batch_id,
            "cost_micro_usd": record.origin_cost_micro_usd,
            "response": _sanitize_raw_response(raw, fingerprint),
        }
        _atomic_json(directory / f"{fingerprint}.json", payload)
        entries.append(_manifest_entry(payload))
    return entries


def _replay_phase3(
    root: Path,
    config: LlmConfig,
    cassette_root: Path,
    static_findings: tuple[Finding, ...],
    dynamic_findings: tuple[Finding, ...],
) -> None:
    static = SemanticReviewer(
        root=root,
        config=config,
        max_findings=len(static_findings),
        mode="replay",
        cache=ReviewCache(enabled=False),
        cassette_root=cassette_root,
    ).review(static_findings, allow_degraded=False)
    rebound = tuple(
        finding.model_copy(update={"finding_id": uuid4()})
        for finding in dynamic_findings
    )
    dynamic = SemanticReviewer(
        root=root,
        config=config,
        max_findings=len(rebound),
        mode="replay",
        cache=ReviewCache(enabled=False),
        cassette_root=cassette_root,
    ).review(rebound, allow_degraded=False)
    if static.fatal or dynamic.fatal:
        raise RuntimeError("captured Phase 3 responses failed production replay")


def _planned_batches(
    checkpoint: str, effort: ReasoningEffort
) -> tuple[tuple[_Batch, ...], LlmConfig]:
    fixture = (
        ROOT / "tests" / "fixtures" / "vulnerable_server"
        if checkpoint == "demo"
        else ROOT / "tests" / "fixtures" / "gpt_review_eval"
    )
    loaded = load_configuration(fixture, environ={}, static_only=True)
    llm = loaded.scanner.llm.model_copy(
        update={"reasoning_effort": effort, "max_concurrency": 1, "retries": 0}
    )
    loaded = loaded.model_copy(
        update={"scanner": loaded.scanner.model_copy(update={"llm": llm})}
    )
    findings = run_static_scan(
        loaded, uuid4(), timestamp=datetime.now(timezone.utc)
    ).findings
    catalog = extract_tool_catalog(fixture, loaded.scanner.scanner.ignore_paths)
    if checkpoint == "smoke":
        findings = tuple(
            item
            for item in findings
            if item.rule_id == "SENT-003"
            and _tool_name(catalog, item) == "unchecked_lookup"
        )
    findings = tuple(sorted(findings, key=_candidate_sort_key))
    candidates = tuple(
        _Candidate(
            finding=item,
            context=build_finding_context(fixture, item),
            tool=_tool_for_finding(catalog, item),
        )
        for item in findings
    )
    return _build_batches(candidates, effort), llm


def _tool_name(catalog: ToolCatalog, finding: Finding) -> str | None:
    tool = _tool_for_finding(catalog, finding)
    return tool.name if tool is not None else None


def _reserved_micro_usd(batch: _Batch) -> int:
    request_text = json.dumps(batch.request, sort_keys=True, separators=(",", ":"))
    try:
        encoding = tiktoken.encoding_for_model(MODEL)
        input_tokens = len(encoding.encode(request_text))
    except KeyError:
        # The pinned tokenizer does not yet map this new model. UTF-8 bytes are
        # a conservative, offline upper bound and therefore preserve the hard
        # spending ceiling without fetching tokenizer assets at runtime.
        input_tokens = len(request_text.encode("utf-8"))
    output_tokens = int(batch.request["max_output_tokens"])
    return _cost(TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens))


async def _capture(
    batches: tuple[_Batch, ...],
    new_batches: list[_Batch],
    config: LlmConfig,
    api_key: str,
    checkpoint: str,
    checkpoint_dir: Path,
    *,
    budget_micro_usd: int,
    replace: bool,
) -> int:
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    reviewer = SemanticReviewer(
        root=ROOT,
        config=config,
        max_findings=500,
        mode="live",
        api_key=api_key,
        cache=ReviewCache(enabled=False),
    )
    new_fingerprints = {batch.fingerprint for batch in new_batches}
    manifest_batches: list[dict[str, Any]] = []
    spent_micro_usd = 0
    for batch in batches:
        path = checkpoint_dir / f"{batch.fingerprint}.json"
        if batch.fingerprint not in new_fingerprints:
            print(f"reused: {batch.fingerprint}")
            existing = json.loads(path.read_text(encoding="utf-8"))
            manifest_batches.append(_manifest_entry(existing))
            continue
        reservation = _reserved_micro_usd(batch)
        if spent_micro_usd + reservation > budget_micro_usd:
            raise RuntimeError(
                "remaining live-capture budget cannot reserve the next request"
            )
        result = await reviewer._run_batch(batch)
        if result.accepted is None:
            raise RuntimeError(result.failure or "GPT capture failed")
        accepted = result.accepted
        sanitized = _sanitize_raw_response(accepted.raw, batch.fingerprint)
        cost_micro_usd = _cost(accepted.usage)
        payload = {
            "cassette_version": 1,
            "checkpoint": checkpoint,
            "fingerprint": batch.fingerprint,
            "captured_at": accepted.reviewed_at.isoformat().replace("+00:00", "Z"),
            "requested_model": MODEL,
            "returned_model": accepted.returned_model,
            "reasoning_effort": config.reasoning_effort.value,
            "usage": accepted.usage.model_dump(mode="json"),
            "latency_ms": accepted.latency_ms,
            "retry_count": accepted.retries,
            "batch_id": batch.batch_id,
            "cost_micro_usd": cost_micro_usd,
            "response": sanitized,
        }
        spent_micro_usd += cost_micro_usd
        if path.exists() and not replace:
            raise RuntimeError(f"refusing to replace existing cassette {path.name}")
        _atomic_json(path, payload)
        manifest_batches.append(_manifest_entry(payload))
        print(f"captured: {batch.fingerprint}")
        print(
            "current live spend: "
            f"${spent_micro_usd / 1_000_000:.6f}; "
            "remaining ceiling: "
            f"${(budget_micro_usd - spent_micro_usd) / 1_000_000:.6f}"
        )
    _atomic_json(
        checkpoint_dir / "manifest.json",
        {
            "checkpoint": checkpoint,
            "model": MODEL,
            "reasoning_effort": config.reasoning_effort.value,
            "batches": manifest_batches,
        },
    )
    return 0


def _sanitize_raw_response(raw: dict[str, Any], fingerprint: str) -> dict[str, Any]:
    response = cast(dict[str, Any], json.loads(json.dumps(raw)))
    response["id"] = f"resp_{fingerprint[:24]}"
    runtime_ids = _stable_uuid4s(fingerprint, len(_response_reviews(response)))
    for index, item in enumerate(response.get("output", [])):
        if isinstance(item, dict) and "id" in item:
            item["id"] = f"item_{fingerprint[:16]}_{index}"
    reviews = _response_reviews(response)
    for review, stable_id in zip(reviews, runtime_ids, strict=True):
        review["finding_id"] = str(stable_id)
        review["reasoning"] = sanitize_text(str(review["reasoning"]))
        for evidence in review["evidence_refs"]:
            evidence["claim"] = sanitize_text(str(evidence["claim"]))
    message = next(item for item in response["output"] if item["type"] == "message")
    message["content"][0]["text"] = json.dumps(
        {"reviews": reviews}, sort_keys=True, separators=(",", ":")
    )
    return response


def _response_reviews(response: dict[str, Any]) -> list[dict[str, Any]]:
    message = next(item for item in response["output"] if item["type"] == "message")
    payload = json.loads(message["content"][0]["text"])
    return cast(list[dict[str, Any]], payload["reviews"])


def _stable_uuid4s(fingerprint: str, count: int) -> tuple[UUID, ...]:
    values: list[UUID] = []
    for index in range(count):
        raw = bytearray(hashlib.sha256(f"{fingerprint}:{index}".encode()).digest()[:16])
        raw[6] = (raw[6] & 0x0F) | 0x40
        raw[8] = (raw[8] & 0x3F) | 0x80
        values.append(UUID(bytes=bytes(raw)))
    return tuple(values)


def _manifest_entry(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: payload[key]
        for key in (
            "stage",
            "fingerprint",
            "captured_at",
            "returned_model",
            "usage",
            "latency_ms",
            "cost_micro_usd",
        )
        if key in payload
    }


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
