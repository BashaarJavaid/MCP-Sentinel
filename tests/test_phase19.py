"""Phase 19 reporting controls; synthetic inputs, no model or target execution."""

from __future__ import annotations

import asyncio
import copy
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import pytest
from mcp.types import ListToolsResult, Tool

from sentinel.baseline import migrate_report_data
from sentinel.config import LlmConfig, load_configuration
from sentinel.finding import Finding
from sentinel.llm.semantic_reviewer import empty_review_outcome
from sentinel.orchestrator import _combine_gpt_summaries
from sentinel.static.engine import run_static_scan
from tests.conftest import NOW, make_target
from tests.test_dynamic_correctness import SyntheticSandbox, _attempt, _tool
from tests.test_typescript_static import _typescript_target


def test_empty_review_does_not_claim_a_model_call() -> None:
    empty = empty_review_outcome(LlmConfig(), mode="live").summary
    assert empty.mode == "not_run"
    replay = empty.model_copy(update={"mode": "replay", "candidate_count": 1})
    assert _combine_gpt_summaries(empty, replay).mode == "replay"


def test_inventory_keeps_duplicates_gaps_and_actual_visits(tmp_path: Path) -> None:
    root = make_target(tmp_path / "target")
    (root / "server.py").write_text("""from mcp.server.fastmcp import FastMCP
from elsewhere import imported
mcp = FastMCP("sample")
@mcp.tool(name="duplicate")
def first(value: str):
    return value
@mcp.tool(name="duplicate")
def second(value: str):
    return value
mcp.add_tool(imported)
""")
    config = load_configuration(
        root, environ={}, cli_overrides={"rules_only": True, "rules": ("SENT-003",)}
    )
    result = run_static_scan(config, uuid4(), timestamp=NOW)
    coverage = result.summary.coverage
    assert coverage is not None
    assert coverage.total_possible_surfaces is None
    tools = [item for item in coverage.surfaces if item.name == "duplicate"]
    assert len(tools) == 2
    assert tools[0].location != tools[1].location
    assert all(item.examined_rule_ids == ("SENT-003",) for item in tools)
    assert any(item.status == "unresolved" for item in coverage.surfaces)
    assert "SENT-002" in coverage.excluded_rule_ids
    assert not result.findings


def test_runtime_catalog_preserves_fields_and_unknown_space() -> None:
    from sentinel.dynamic.coverage import discovery_snapshot

    schema = {
        "type": "object",
        "properties": {
            "nested": {"$ref": "#/$defs/nested"},
            "items": {"type": "array", "items": {"type": "string"}},
        },
        "$defs": {
            "nested": {
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "additionalProperties": False,
            }
        },
        "additionalProperties": False,
    }
    snapshot = discovery_snapshot(
        "SENT-009",
        "baseline",
        (
            Tool(name="one", inputSchema=schema),
            Tool(name="two", inputSchema={"type": "object"}),
        ),
        more_pages=True,
    )
    assert snapshot.tool_total is None
    assert ("nested", "value") in snapshot.tools[0].field_paths
    assert any(item.path == ("items",) for item in snapshot.tools[0].unresolved)
    assert snapshot.tools[1].unresolved
    assert "inputSchema" not in snapshot.model_dump_json()


def test_historical_coverage_is_unavailable_without_mutation() -> None:
    old = {
        "schema_version": "1.5.0",
        "static_analysis": {},
        "dynamic_analysis": {"probe_outcomes": [{"probe_id": "SENT-008"}]},
    }
    original = copy.deepcopy(old)
    migrated = migrate_report_data(old)
    assert old == original
    assert migrated["schema_version"] == "1.6.0"
    assert migrated["static_analysis"]["coverage"] is None
    assert migrated["review_activity"] == {"static": None, "dynamic": None}
    assert migrated["dynamic_analysis"]["probe_outcomes"][0]["attack_attempted"] is None


@pytest.mark.parametrize("language", ["python", "typescript"])
def test_partial_recognition_and_exclusions(tmp_path: Path, language: str) -> None:
    source = """from mcp.server.fastmcp import FastMCP
from external import Schema
mcp = FastMCP("partial")
@mcp.tool(name=compute_name())
def computed(value: Schema):
    return value
class Handlers:
    @mcp.tool()
    def unsupported(self, value):
        return value
"""
    if language == "python":
        root = make_target(tmp_path / "target")
        (root / "server.py").write_text(source)
        suffix = ".py"
    else:
        source = """import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { handler, schema } from "./external";
const server = new McpServer({ name: "partial", version: "1" });
server.registerTool(computeName(), { inputSchema: schema }, handler);
server.registerPrompt("prompt", {}, handler);
"""
        root = _typescript_target(tmp_path / "target", source)
        suffix = ".ts"
    (root / ("ignored" + suffix)).write_text(source)
    (root / ("baseline" + suffix)).write_text(source)
    config = load_configuration(
        root,
        environ={},
        cli_overrides={
            "rules_only": True,
            "rules": ("SENT-005",),
            "ignore_paths": ("ignored*",),
        },
    )
    result = run_static_scan(
        config,
        uuid4(),
        timestamp=NOW,
        forced_ignored_paths=frozenset({"baseline" + suffix}),
    )
    coverage = result.summary.coverage
    assert coverage is not None
    assert not result.findings
    assert len(coverage.surfaces) == 2
    assert all(not surface.examined_rule_ids for surface in coverage.surfaces)
    assert {surface.status for surface in coverage.surfaces} == {
        "unresolved",
        "unsupported",
    }
    assert all(
        surface.location.path == "server" + suffix for surface in coverage.surfaces
    )
    assert len(coverage.surfaces[0].reasons) >= 2


@pytest.mark.parametrize(
    "fixture",
    [
        "clean_server",
        "vulnerable_server",
        "typescript_clean_server",
        "typescript_vulnerable_server",
    ],
)
def test_paired_inventory_and_machine_outputs(fixture: str) -> None:
    from sentinel.orchestrator import run_scan
    from sentinel.report.console import render_console
    from sentinel.report.model import ScanContext, ScanTarget
    from sentinel.report.sarif import render_sarif
    from sentinel.report.validate_json import validate_report_data
    from sentinel.report.validate_sarif import validate_sarif_data

    root = Path(__file__).parent / "fixtures" / fixture
    config = load_configuration(root, environ={}, cli_overrides={"rules_only": True})
    report = run_scan(
        config,
        ScanContext(
            scan_id=uuid4(), started_at=NOW, target=ScanTarget(display_name=fixture)
        ),
        completed_at=NOW,
        allow_degraded=False,
    ).report
    assert report.static_analysis and report.static_analysis.coverage
    assert any(
        item.kind == "tool" and "SENT-003" in item.examined_rule_ids
        for item in report.static_analysis.coverage.surfaces
    )
    assert (
        report.review_activity.static
        and report.review_activity.static.state == "not_requested"
    )
    assert (
        report.review_activity.dynamic
        and report.review_activity.dynamic.state == "not_requested"
    )
    assert report.gpt_review is None
    native = report.model_dump(mode="json", by_alias=True)
    validate_report_data(native)
    sarif = json.loads(render_sarif(report))
    validate_sarif_data(sarif)
    props = sarif["runs"][0]["invocations"][0]["properties"]
    assert props["staticAnalysis"]["coverage"] == native["static_analysis"]["coverage"]
    assert props["reviewActivity"] == native["review_activity"]
    assert "total possible unknown" in render_console(report)


def test_selected_execution_skip_gets_no_visit_credit(tmp_path: Path) -> None:
    root = make_target(tmp_path / "target")
    (root / "server.py").write_text(
        "@mcp.tool()\ndef tool(value: str):\n return value\n"
    )
    (root / "sentinel.permissions.yaml").unlink()
    config = load_configuration(root, environ={}, cli_overrides={"rules_only": True})
    result = run_static_scan(config, uuid4(), timestamp=NOW)
    assert result.summary.coverage
    assert not result.summary.coverage.excluded_rule_ids
    assert "SENT-001" not in result.summary.coverage.surfaces[0].examined_rule_ids
    assert result.summary.rule_outcomes[0].skip_reason


@pytest.mark.parametrize(
    "case",
    [
        "sent",
        "baseline_failure",
        "changed",
        "paginated",
        "discovery_failure",
        "unhealthy",
        "timeout",
    ],
)
def test_actual_calls_and_partial_discovery(case: str) -> None:
    from sentinel.dynamic.prober import WRONG_TYPE_MARKER

    class CatalogSandbox(SyntheticSandbox):
        @asynccontextmanager
        async def probe_session(
            self, image: str, probe_id: str, *, timeout: float = 10
        ) -> AsyncIterator[Any]:
            async with super().probe_session(
                image, probe_id, timeout=timeout
            ) as session:

                async def list_tools() -> ListToolsResult:
                    if case == "discovery_failure" and self.sessions == 2:
                        raise RuntimeError("synthetic discovery failure")
                    tool = self.tool.model_copy(deep=True)
                    if case == "changed" and self.sessions == 2:
                        tool.inputSchema["title"] = "different session"
                    return ListToolsResult(
                        tools=[
                            tool,
                            Tool(
                                name="unprobed",
                                inputSchema={
                                    "type": "object",
                                    "properties": {
                                        "nested": {
                                            "type": "object",
                                            "properties": {"field": {"type": "string"}},
                                        }
                                    },
                                },
                            ),
                        ],
                        nextCursor="private-cursor" if case == "paginated" else None,
                    )

                session.list_tools = list_tools
                if case == "unhealthy":
                    session.process_state = lambda: {
                        "Running": False,
                        "Error": "",
                        "OOMKilled": False,
                    }
                if case == "timeout":

                    async def call_tool(name: str, arguments: dict[str, Any]) -> None:
                        self.calls.append((self.sessions, name, arguments))
                        raise TimeoutError("synthetic timeout")

                    session.call_tool = call_tool
                yield session

    sandbox = CatalogSandbox(
        _tool({"type": "string"}), baseline_error=case == "baseline_failure"
    )
    result = _attempt(sandbox, "SENT-011", WRONG_TYPE_MARKER)
    assert result.baseline_attempted == (case != "unhealthy")
    assert result.attack_attempted == (case in {"sent", "paginated"})
    assert result.baseline_attempted == any(
        session == 1 for session, _, _ in sandbox.calls
    )
    assert result.attack_attempted == any(
        session == 2 for session, _, _ in sandbox.calls
    )
    assert all(
        "private-cursor" not in snap.model_dump_json() for snap in result.discovery
    )
    first = result.discovery[0]
    assert first.tools[1].field_paths == (("nested",), ("nested", "field"))
    assert first.tool_total == (None if case == "paginated" else 2)
    if case == "changed":
        assert (
            result.discovery[0].tools[0].schema_sha256
            != result.discovery[1].tools[0].schema_sha256
        )
    if case == "discovery_failure":
        assert result.discovery[1].tool_total is None
        assert result.discovery[1].reason == "runtime tool discovery failed"


@pytest.mark.parametrize(
    "schema,reason",
    [
        (
            {
                "$schema": "https://example.invalid/custom-dialect",
                "type": "object",
                "properties": {"field": {"type": "string"}},
                "additionalProperties": False,
            },
            "dialect",
        ),
        ({"$ref": "https://example.invalid/schema"}, "reference"),
        ({"$ref": "#"}, "recursive"),
        ({"oneOf": [{"type": "string"}, {"type": "object"}]}, "alternatives"),
        ({"properties": {"bad": False}}, "cannot generate"),
        ({"properties": []}, "invalid properties"),
    ],
)
def test_unsupported_field_spaces_remain_explicit(
    schema: dict[str, Any], reason: str
) -> None:
    from sentinel.dynamic.coverage import discovery_snapshot

    snapshot = discovery_snapshot(
        "SENT-011", "attack", (Tool(name="tool", inputSchema=schema),), more_pages=False
    )
    assert snapshot.tool_total == 1
    assert any(reason in gap.reason for gap in snapshot.tools[0].unresolved)


def test_empty_baseline_deadline_does_not_claim_a_sent_call() -> None:
    from types import SimpleNamespace

    from sentinel.dynamic.prober import _call, _Observation
    from sentinel.dynamic.sandbox import ProbeSession

    observation = _Observation("SENT-011", "tool", None, {}, {}, (), False)

    async def run() -> None:
        async def call_tool(name: str, arguments: dict[str, Any]) -> None:
            raise AssertionError("expired deadline must not send a call")

        probe = SimpleNamespace(
            client=SimpleNamespace(call_tool=call_tool),
            deadline=0,
            process_state=lambda: {"Running": True, "Error": "", "OOMKilled": False},
        )
        await _call(cast(ProbeSession, probe), "tool", {}, observation, "attack")

    asyncio.run(run())
    assert observation.attack_attempted is False


@pytest.mark.parametrize(
    "state",
    [
        "not_requested",
        "not_reached",
        "no_candidates",
        "all_suppressed",
        "completed",
        "incomplete",
    ],
)
def test_every_review_activity_state(state: str, sample_finding: Finding) -> None:
    from sentinel.finding import InlineSuppression
    from sentinel.llm.semantic_reviewer import ReviewOutcome
    from sentinel.orchestrator import _review_activity
    from tests.test_dynamic_prober import _reviewed_finding

    findings = () if state == "no_candidates" else (sample_finding,)
    if state == "all_suppressed":
        findings = (
            sample_finding.model_copy(
                update={
                    "suppression": InlineSuppression(
                        path="server.py",
                        line=4,
                        reason="synthetic exclusion",
                    )
                }
            ),
        )
    reviewed = state == "completed"
    if reviewed:
        findings = (_reviewed_finding(sample_finding),)
    summary = empty_review_outcome(LlmConfig(), mode="live").summary.model_copy(
        update={
            "candidate_count": len(findings),
            "selected_count": int(reviewed),
            "reviewed_count": int(reviewed),
        }
    )
    review = ReviewOutcome(findings, (), summary, False)
    activity = _review_activity(
        None if state == "not_reached" else findings,
        None if state in {"not_requested", "not_reached"} else review,
        requested=state != "not_requested",
    )
    assert activity.state == state
    assert activity.reviewed_count == int(reviewed)
    assert activity.unreviewed_count == (
        None
        if state == "not_reached"
        else int(state in {"not_requested", "incomplete"})
    )
    assert activity.excluded_count == (
        None if state == "not_reached" else int(state == "all_suppressed")
    )


def test_abstention_and_suppression_evidence_remain_visible(
    sample_finding: Finding,
) -> None:
    from sentinel.finding import FindingStatus, ReviewStatus, StaticEvidence
    from sentinel.report.presentation import concise_finding
    from tests.test_dynamic_prober import _reviewed_finding

    finding = _reviewed_finding(sample_finding)
    assert finding.review is not None
    assert isinstance(sample_finding.provenance[0].evidence, StaticEvidence)
    finding = finding.model_copy(
        update={
            "review": finding.review.model_copy(
                update={"status": ReviewStatus.NEEDS_REVIEW}
            ),
            "status": FindingStatus.NEEDS_REVIEW,
            "description": "Input reaches eval at server.py:20 "
            "through a same-file helper.",
            "evidence": StaticEvidence(
                range=sample_finding.provenance[0].evidence.range,
                snippet="eval(value)\n" + "x" * 500 + "\nthird\nfourth",
            ),
        }
    )
    text = "\n".join(concise_finding(finding))
    assert "server.py:4:2" in text
    assert "static suspicion" in text and "model corroboration" not in text
    assert "Model abstained" in text
    assert "[source evidence omitted" in text
    assert "bodies not displayed" in text
    assert "fourth" not in text
    assert finding.remediation in text


def test_merged_runtime_proof_is_visible_with_model_disagreement(
    sample_finding: Finding,
) -> None:
    from sentinel.dynamic.prober import _finding_from_observation, _Observation
    from sentinel.finding import ReviewStatus
    from sentinel.report.presentation import concise_finding
    from tests.test_dynamic_prober import _reviewed_finding

    runtime = _finding_from_observation(
        _Observation(
            "SENT-010",
            "tool",
            "value",
            {},
            {"is_error": True},
            (),
            True,
            baseline={"response": {"is_error": False}},
            effects={"canary_before": False, "canary_after": True},
        ),
        sample_finding.scan_id,
        NOW,
    )
    finding = _reviewed_finding(sample_finding)
    assert finding.review is not None
    finding = finding.model_copy(
        update={
            "provenance": (*finding.provenance, *runtime.provenance),
            "review": finding.review.model_copy(
                update={"status": ReviewStatus.SUPPRESSED}
            ),
        }
    )
    text = "\n".join(concise_finding(finding))
    assert "static suspicion" in text and "runtime observation" in text
    assert "verified security effect" in text
    assert "canary_after" in text and "baseline success=True" in text
    assert "GPT disagrees" in text and "Model suppression judgment" in text


def test_schema_enumeration_depth_deadline_and_duplicate_names() -> None:
    from sentinel.dynamic.coverage import discovery_snapshot

    nested: dict[str, Any] = {"type": "string"}
    for _ in range(10):
        nested = {
            "type": "object",
            "properties": {"child": nested},
            "additionalProperties": False,
        }
    tool = Tool(name="tool", inputSchema=nested)
    snapshot = discovery_snapshot("SENT-011", "attack", (tool, tool), more_pages=False)
    assert snapshot.tool_total is None
    assert max(map(len, snapshot.tools[0].field_paths)) == 8
    assert "depth 8" in snapshot.tools[0].unresolved[0].reason
    expired = discovery_snapshot(
        "SENT-011", "attack", (tool,), more_pages=False, deadline=0
    )
    assert not expired.tools[0].field_paths
    assert "deadline" in expired.tools[0].unresolved[0].reason


def test_missing_historical_baseline_control_stays_unknown() -> None:
    from sentinel.report.console import render_console
    from sentinel.report.model import (
        PROBE_IDS,
        DynamicAnalysisSummary,
        DynamicProbeOutcome,
    )
    from tests.test_baseline import _report

    report = _report(()).model_copy(
        update={
            "analysis_complete": False,
            "dynamic_analysis": DynamicAnalysisSummary(
                probe_outcomes=tuple(
                    DynamicProbeOutcome(
                        probe_id=probe,
                        status="untested",
                        verdict=None,
                        tool=None,
                        field=None,
                        reason="historical outcome",
                    )
                    for probe in PROBE_IDS
                )
            ),
        }
    )
    text = render_console(report)
    assert text.count("baseline control succeeded=unknown") == 4


def test_inventory_cannot_finish_after_the_static_deadline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from sentinel.errors import InfrastructureError
    from sentinel.static.coverage import inventory
    from sentinel.static.model import StaticContext
    from sentinel.static.traversal import collect_static_files

    root = _typescript_target(tmp_path / "target", "export const value = 1;")
    config = load_configuration(root, environ={}, static_only=True)
    files = collect_static_files(root, (), config.language)
    expired = False

    def recognize(file: Any) -> tuple[()]:
        nonlocal expired
        expired = True
        return ()

    monkeypatch.setattr("sentinel.static.coverage.ts.tools_in_file", recognize)
    monkeypatch.setattr(
        "sentinel.static.execution.time.monotonic", lambda: 2 if expired else 0
    )
    with pytest.raises(InfrastructureError, match="timeout"):
        inventory(StaticContext(config, files, deadline=1), {})
