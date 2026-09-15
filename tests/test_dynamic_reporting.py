"""Phase 17 report, proof, migration, and replay regression controls."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from sentinel.baseline import annotate_report, finding_identity, load_baseline
from sentinel.config import FailThreshold, LlmConfig, LoadedConfiguration
from sentinel.dynamic.merge import merge_findings
from sentinel.dynamic.prober import (
    DEFAULT_ORDER,
    DynamicScanResult,
    ProbeBinding,
    ProbeCampaign,
    _finding_from_observation,
    _Observation,
)
from sentinel.dynamic.sandbox import DependencyImage
from sentinel.finding import DynamicEvidence, Finding, FindingStatus, StaticEvidence
from sentinel.llm.context import build_finding_context
from sentinel.llm.semantic_reviewer import SemanticReviewer
from sentinel.orchestrator import _finalize_outcome
from sentinel.report.console import render_console
from sentinel.report.json_report import render_json
from sentinel.report.model import (
    DynamicAnalysisSummary,
    DynamicProbeOutcome,
    ScanReport,
)
from sentinel.report.sarif import render_sarif
from sentinel.report.validate_json import validate_report_data
from sentinel.report.validate_sarif import validate_sarif_data
from tests.conftest import NOW, SCAN_ID
from tests.test_baseline import _report
from tests.test_dynamic_prober import _catalog
from tests.test_gpt_review import ROOT, FakeTransport


def _proof(**changes: Any) -> Finding:
    data: dict[str, Any] = dict(
        probe_id="SENT-011",
        target_tool="unsafe_calculator",
        field="expression",
        argument_path=("expression",),
        request={"expression": 0},
        response={"is_error": False, "content": [{"text": "incidental output"}]},
        logs=("incidental log",),
        vulnerable=True,
        baseline={
            "tool": "unsafe_calculator",
            "request": {"expression": "1"},
            "schema_valid": True,
            "response": {"is_error": False},
            "logs": [],
        },
        schema_checks=[
            {"keyword": "type", "constraint": "string", "instance_path": ["expression"]}
        ],
        effects={"schema_sha256": "a" * 64, "request_sha256": "b" * 64},
        timings={"baseline_ms": 1.0, "attack_ms": 2.0},
    )
    data.update(changes)
    return _finding_from_observation(_Observation(**data), SCAN_ID, NOW)


def _result(observations: tuple[_Observation, ...]) -> DynamicScanResult:
    bindings = tuple(
        ProbeBinding(
            item.probe_id,
            item.target_tool,
            item.field,
            {
                "SENT-009": "__SENTINEL_OVERSIZED__",
                "SENT-010": "__SENTINEL_INJECTION__",
                "SENT-011": "__SENTINEL_WRONG_TYPE__",
            }.get(item.probe_id),
            path=item.argument_path,
        )
        for item in observations
    )
    for item, binding in zip(observations, bindings, strict=True):
        item.attempt_id = binding.attempt_id
        item.mutation = binding.mutation
        item.argument_path = binding.argument_path
        item.started = item.status != "untested"
    return DynamicScanResult(
        tuple(
            _finding_from_observation(item, SCAN_ID, NOW)
            for item in observations
            if item.vulnerable
        ),
        (),
        DependencyImage("test", "test", True),
        ProbeCampaign(
            DEFAULT_ORDER, bindings, None, True, enumeration_complete=bool(observations)
        ),
        observations,
    )


@pytest.mark.parametrize(
    "status", ["tested", "unsupported", "untested", "inconclusive"]
)
def test_probe_outcomes_agree_across_formats_and_exit_precedence(
    status: str,
    loaded_config: LoadedConfiguration,
) -> None:
    observations = tuple(
        _Observation(
            rule_id,
            "process",
            "value",
            {},
            {},
            (),
            index == 0,
            status="tested" if index == 0 else status,  # type: ignore[arg-type]
            reason="control observation",
            argument_path=("value",),
        )
        for index, rule_id in enumerate(DEFAULT_ORDER)
    )
    dynamic = _result(observations)
    report = _report(dynamic.findings).model_copy(
        update={
            "analysis_complete": dynamic.complete,
            "dynamic_analysis": dynamic.summary,
        }
    )
    native = json.loads(render_json(report))
    validate_report_data(native)
    sarif = json.loads(render_sarif(report))
    validate_sarif_data(sarif)
    assert (
        native["dynamic_analysis"]
        == sarif["runs"][0]["invocations"][0]["properties"]["dynamicAnalysis"]
    )
    console = render_console(report)
    for outcome in dynamic.summary.probe_outcomes:
        assert f"{outcome.probe_id}: {outcome.status}" in console
        assert (outcome.verdict is not None) == (outcome.status == "tested")
    configuration = loaded_config.model_copy(update={"fail_on": FailThreshold.CRITICAL})
    assert _finalize_outcome(report, configuration, None).exit_code == (
        1 if dynamic.complete else 3
    )
    assert len(report.findings) == 1


def test_missing_results_are_untested_and_invalid_contracts_rejected() -> None:
    dynamic = _result(())
    assert not dynamic.complete
    assert all(item.status == "untested" for item in dynamic.summary.probe_outcomes)
    assert DynamicAnalysisSummary(probe_outcomes=()).probe_outcomes == ()
    with pytest.raises(ValidationError, match="only tested"):
        DynamicProbeOutcome(
            attempt_id="test:SENT-008",
            probe_id="SENT-008",
            status="inconclusive",
            verdict="no_violation_observed",
            tool=None,
            field=None,
            reason="timeout",
        )
    payload = _report(()).model_dump(exclude={"findings"})
    payload.update(dynamic_analysis=dynamic.summary)
    with pytest.raises(ValidationError, match="incomplete campaign"):
        ScanReport.model_validate({**payload, "findings": ()})


def _static(sample: Finding, snippet: str = "expression") -> Finding:
    assert sample.location.kind == "file"
    assert isinstance(sample.evidence, StaticEvidence)
    return sample.model_copy(
        update={
            "rule_id": "SENT-003",
            "location": sample.location.model_copy(
                update={
                    "range": sample.location.range.model_copy(
                        update={"start_line": 12, "end_line": 12}
                    )
                }
            ),
            "evidence": sample.evidence.model_copy(update={"snippet": snippet}),
            "provenance": (
                sample.provenance[0].model_copy(update={"rule_id": "SENT-003"}),
            ),
        }
    )


@pytest.mark.parametrize(
    "case",
    [
        "same",
        "other_field",
        "other_tool",
        "resource_only",
        "nested_unmapped",
        "historical",
        "ambiguous",
        "wrong_constraint",
    ],
)
def test_merge_requires_a_unique_tool_parameter_and_validation_cause(
    sample_finding: Finding, case: str
) -> None:
    static = _static(sample_finding)
    dynamic = _proof()
    if case == "other_field":
        static = _static(sample_finding, "other")
    if case == "other_tool":
        dynamic = _proof(target_tool="other")
    if case == "resource_only":
        dynamic = _proof(
            probe_id="SENT-009", schema_checks=[], effects={"resource_failure": True}
        )
    if case == "nested_unmapped":
        dynamic = _proof(argument_path=("arguments", "expression"))
    if case == "wrong_constraint":
        dynamic = _proof(
            schema_checks=[{"keyword": "enum", "instance_path": ["expression"]}]
        )
    if case == "historical":
        assert isinstance(dynamic.evidence, DynamicEvidence)
        old = dynamic.evidence.model_copy(update={"proof": None})
        dynamic = dynamic.model_copy(
            update={
                "evidence": old,
                "provenance": (
                    dynamic.provenance[0].model_copy(update={"evidence": old}),
                ),
            }
        )
    candidates = (static, static) if case == "ambiguous" else (static,)
    merged = merge_findings(candidates, (dynamic,), _catalog())
    assert len(merged) == (1 if case == "same" else len(candidates) + 1)
    if case == "same":
        assert merged[0].finding_id == static.finding_id
        assert merged[0].source == static.source
        assert merged[0].evidence == static.evidence
        assert merged[0].status is FindingStatus.CONFIRMED
        assert merged[0].provenance[-1].evidence == dynamic.evidence


@pytest.mark.parametrize("version", ["1.3.0", "1.4.0", "1.5.0"])
def test_historical_reports_cannot_match_new_or_merged_runtime_proof(
    tmp_path: Path,
    sample_finding: Finding,
    version: str,
) -> None:
    static = _static(sample_finding)
    dynamic = _proof()
    assert isinstance(dynamic.evidence, DynamicEvidence)
    old_evidence = dynamic.evidence.model_copy(update={"proof": None})
    old = dynamic.model_copy(
        update={
            "evidence": old_evidence,
            "provenance": (
                dynamic.provenance[0].model_copy(update={"evidence": old_evidence}),
            ),
        }
    )
    payload = json.loads(render_json(_report((static, old))))
    payload["schema_version"] = version
    if version != "1.5.0":
        payload.pop("dynamic_analysis")
        for finding in payload["findings"]:
            finding.pop("review_disagrees")
            if finding["evidence"]["kind"] == "dynamic":
                finding["evidence"].pop("proof")
            for entry in finding["provenance"]:
                entry.pop("review")
                if entry["evidence"]["kind"] == "dynamic":
                    entry["evidence"].pop("proof")
    if version == "1.3.0":
        payload.pop("baseline")
        for finding in payload["findings"]:
            finding.pop("baseline_matched")
            finding.pop("suppression")
    path = tmp_path / "historical.json"
    raw = json.dumps(payload)
    path.write_text(raw)
    baseline = load_baseline(path)
    assert path.read_text() == raw
    assert baseline.report.dynamic_analysis is None
    unchanged = annotate_report(_report((static,)), baseline)
    assert unchanged.findings[0].baseline_matched
    current = annotate_report(_report((dynamic,)), baseline)
    assert current.findings[0].baseline_matched is False
    merged = merge_findings((static,), (dynamic,), _catalog())
    assert (
        annotate_report(_report(merged), baseline).findings[0].baseline_matched is False
    )
    assert (
        current.baseline and current.baseline.matcher_version == "sentinel-baseline-v2"
    )


def test_diagnostics_do_not_change_proof_baseline_or_replay_input(
    tmp_path: Path,
) -> None:
    original = _proof()
    changed = _proof(
        timings={"baseline_ms": 999.0, "attack_ms": 333.0},
        logs=("container different",),
        response={
            "is_error": False,
            "content": [{"text": "different incidental output"}],
            "container_id": "diagnostic",
        },
    )
    assert finding_identity(original) == finding_identity(changed)
    assert (
        build_finding_context(ROOT, original).context_hash
        == build_finding_context(ROOT, changed).context_hash
    )
    transport = FakeTransport()
    captured: dict[str, Any] = {}

    def sink(
        fingerprint: str, request: dict[str, Any], response: dict[str, Any]
    ) -> None:
        captured.update(fingerprint=fingerprint, response=response)

    records = []
    for finding in (original, changed):
        outcome = SemanticReviewer(
            root=ROOT,
            config=LlmConfig(retries=0, cache_enabled=False),
            max_findings=10,
            mode="live",
            transport=transport,
            capture_sink=sink,
            cassette_root=tmp_path,
            now=lambda: NOW,
        ).review((finding,), allow_degraded=False)
        assert not outcome.fatal
        records.append(outcome.summary.batches[0].request_fingerprint)
    assert records[0] == records[1]
    fingerprint = captured["fingerprint"]
    (tmp_path / f"{fingerprint}.json").write_text(
        json.dumps(
            {
                "captured_at": NOW.isoformat(),
                "latency_ms": 1,
                "retry_count": 0,
                "batch_id": f"batch_{fingerprint[:24]}",
                "response": captured["response"],
            }
        )
    )
    replay = SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0, cache_enabled=False),
        max_findings=10,
        mode="replay",
        cassette_root=tmp_path,
    ).review((original,), allow_degraded=False)
    assert not replay.fatal
    assert replay.findings[0].review is not None
    assert replay.findings[0].review.mode == "replay"
    assert replay.summary.current_usage.total_tokens == 0


@pytest.mark.parametrize("change", ["tool", "field", "schema", "request", "result"])
def test_decisive_proof_changes_invalidate_matching_and_review(change: str) -> None:
    finding = _proof()
    cases: dict[str, dict[str, Any]] = {
        "tool": {"target_tool": "other"},
        "field": {"field": "other", "argument_path": ("other",)},
        "schema": {"effects": {"schema_sha256": "c" * 64}},
        "request": {"request": {"expression": False}},
        "result": {"response": {"is_error": True}},
    }
    changed = _proof(**cases[change])
    assert finding_identity(finding) != finding_identity(changed)
    assert (
        build_finding_context(ROOT, finding).context_hash
        != build_finding_context(ROOT, changed).context_hash
    )


@pytest.mark.parametrize("healthy", [True, False])
def test_pipeline_retains_partial_proof_and_reports_infrastructure_health(
    loaded_config: LoadedConfiguration,
    monkeypatch: pytest.MonkeyPatch,
    healthy: bool,
) -> None:
    from sentinel.orchestrator import run_scan
    from sentinel.report.model import ScanContext, ScanTarget

    observations = tuple(
        _Observation(
            rule_id,
            "process",
            "value",
            {},
            {"is_error": False},
            (),
            index == 0,
            status="tested" if index == 0 else "unsupported" if healthy else "untested",
            reason="synthetic complete proof"
            if index == 0
            else "synthetic unsupported or infrastructure failure",
            execution_successful=healthy or index == 0,
        )
        for index, rule_id in enumerate(DEFAULT_ORDER)
    )
    dynamic = _result(observations)
    from sentinel.static.model import StaticScanResult

    summary = _report(()).static_analysis
    assert summary is not None
    monkeypatch.setattr("sentinel.orchestrator.reap_orphans", lambda: None)
    monkeypatch.setattr(
        "sentinel.orchestrator.run_static_scan",
        lambda *args, **kwargs: StaticScanResult((), (), summary),
    )
    monkeypatch.setattr(
        "sentinel.orchestrator.run_dynamic_scan", lambda *args, **kwargs: dynamic
    )
    outcome = run_scan(
        loaded_config,
        ScanContext(
            scan_id=SCAN_ID, started_at=NOW, target=ScanTarget(display_name="synthetic")
        ),
        completed_at=NOW,
        allow_degraded=False,
        transport=FakeTransport(),
    )
    assert outcome.exit_code == 3
    assert outcome.report.execution_successful is healthy
    assert outcome.report.dynamic_analysis == dynamic.summary
    assert len(outcome.report.findings) == 1
    assert outcome.report.findings[0].status is FindingStatus.CONFIRMED


@pytest.mark.parametrize("merged", [False, True])
def test_model_disagreement_survives_review_and_all_output_formats(
    sample_finding: Finding,
    merged: bool,
) -> None:
    class Disagree(FakeTransport):
        async def create(self, request: dict[str, Any]) -> dict[str, Any]:
            response = await super().create(request)
            content = response["output"][1]["content"][0]
            payload = json.loads(content["text"])
            for judgment in payload["reviews"]:
                judgment.update(status="suppressed", confidence=0.1, probe_plan=None)
            content["text"] = json.dumps(payload)
            return response

    proof = _proof()
    candidate = (
        merge_findings((_static(sample_finding),), (proof,), _catalog())[0]
        if merged
        else proof
    )
    outcome = SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0, cache_enabled=False),
        max_findings=10,
        mode="live",
        transport=Disagree(),
    ).review((candidate,), allow_degraded=False)
    assert not outcome.fatal
    report = _report(outcome.findings).model_copy(
        update={"gpt_review": outcome.summary}
    )
    native = json.loads(render_json(report))
    sarif = json.loads(render_sarif(report))
    validate_report_data(native)
    validate_sarif_data(sarif)
    assert native["findings"][0]["status"] == "confirmed"
    assert native["findings"][0]["review"]["status"] == "suppressed"
    assert native["findings"][0]["review_disagrees"] is True
    assert sarif["runs"][0]["results"][0]["properties"]["reviewDisagrees"] is True
    assert "suppressions" not in sarif["runs"][0]["results"][0]
    assert "GPT disagrees with runtime proof" in render_console(report)
    assert outcome.summary.confirmed_count == 0
    assert outcome.summary.suppressed_count == 1
    assert outcome.summary.disagreement_count == 1


def test_size_only_is_separate_and_a_shared_type_violation_can_merge(
    sample_finding: Finding,
) -> None:
    static = _static(sample_finding)
    size = {"keyword": "maxLength", "constraint": 4096, "instance_path": ["expression"]}
    size_only = _proof(probe_id="SENT-009", schema_checks=[size])
    assert len(merge_findings((static,), (size_only,), _catalog())) == 2
    shared = _proof(
        probe_id="SENT-009",
        schema_checks=[
            size,
            {
                "keyword": "type",
                "constraint": "string",
                "instance_path": ["expression"],
            },
        ],
    )
    assert len(merge_findings((static,), (shared,), _catalog())) == 1


def test_required_omission_and_literal_nested_parameter_mapping(
    sample_finding: Finding,
) -> None:
    static = _static(sample_finding, 'arguments["record_id"]')
    dynamic = _proof(
        field="record_id",
        argument_path=("arguments", "record_id"),
        schema_checks=[
            {
                "keyword": "required",
                "constraint": ["record_id"],
                "instance_path": ["arguments"],
            }
        ],
    )
    assert len(merge_findings((static,), (dynamic,), _catalog())) == 1


@pytest.mark.parametrize("probe", ["SENT-009", "SENT-010"])
def test_protocol_timing_does_not_change_decisive_process_or_canary_proof(
    probe: str,
) -> None:
    state = {"Running": False, "OOMKilled": True, "ExitCode": 137, "Error": ""}
    effects = (
        {"resource_failure": True}
        if probe == "SENT-009"
        else {"canary_before": False, "canary_after": True}
    )
    timed_out = _proof(
        probe_id=probe,
        effects=effects,
        response={"is_error": True, "timed_out": True, "process_state": state},
    )
    disconnected = _proof(
        probe_id=probe,
        effects=effects,
        response={"is_error": True, "protocol_failure": True, "process_state": state},
    )
    assert finding_identity(timed_out) == finding_identity(disconnected)
    assert (
        build_finding_context(ROOT, timed_out).context_hash
        == build_finding_context(ROOT, disconnected).context_hash
    )


@pytest.mark.parametrize("merged", [False, True])
def test_current_proof_baselines_match_after_roundtrip(
    tmp_path: Path,
    sample_finding: Finding,
    merged: bool,
) -> None:
    static = _static(sample_finding)
    original = _proof()
    later = _proof(timings={"baseline_ms": 123.0, "attack_ms": 456.0})
    old_findings = (
        merge_findings((static,), (original,), _catalog()) if merged else (original,)
    )
    new_findings = (
        merge_findings((static,), (later,), _catalog()) if merged else (later,)
    )
    path = tmp_path / "baseline.json"
    path.write_text(render_json(_report(old_findings)))
    annotated = annotate_report(_report(new_findings), load_baseline(path))
    assert all(finding.baseline_matched is True for finding in annotated.findings)
