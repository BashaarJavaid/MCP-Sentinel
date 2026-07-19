"""Phase 3 orchestration and infrastructure-failure contracts."""

from __future__ import annotations

import json
from datetime import datetime
from uuid import UUID

import pytest

from sentinel.config import LlmConfig, LoadedConfiguration
from sentinel.dynamic.merge import merge_findings as merge_findings_impl
from sentinel.dynamic.prober import (
    DEFAULT_ORDER,
    DynamicScanResult,
    ProbeBinding,
    ProbeCampaign,
    _finding_from_observation,
    _Observation,
)
from sentinel.dynamic.sandbox import DependencyImage, DockerSandbox
from sentinel.errors import InfrastructureError
from sentinel.finding import Finding, FindingSource
from sentinel.llm.semantic_reviewer import (
    ReviewOutcome,
    empty_review_outcome,
)
from sentinel.llm.tools import ToolCatalog
from sentinel.report.model import (
    ScanContext,
    ScanTarget,
    StageName,
    StageStatus,
    StaticAnalysisSummary,
    StaticRuleOutcome,
    StaticRuleStatus,
)
from sentinel.report.sarif import render_sarif
from sentinel.report.validate_sarif import validate_sarif_data
from sentinel.static.model import StaticScanResult
from tests.conftest import NOW, SCAN_ID


def _context() -> ScanContext:
    return ScanContext(
        scan_id=SCAN_ID,
        started_at=NOW,
        target=ScanTarget(display_name="fixture"),
    )


def _static_result(finding: Finding) -> StaticScanResult:
    return StaticScanResult(
        findings=(finding,),
        warnings=(),
        summary=StaticAnalysisSummary(
            selected_rule_ids=(finding.rule_id,),
            scanned_file_count=1,
            ignored_file_count=0,
            total_matches=1,
            duration_ms=1,
            rule_outcomes=(
                StaticRuleOutcome(
                    rule_id=finding.rule_id,
                    status=StaticRuleStatus.EVALUATED,
                    match_count=1,
                    exemptions_by_reason={},
                ),
            ),
        ),
    )


def _empty_static_result() -> StaticScanResult:
    return StaticScanResult(
        findings=(),
        warnings=(),
        summary=StaticAnalysisSummary(
            selected_rule_ids=(),
            scanned_file_count=0,
            ignored_file_count=0,
            total_matches=0,
            duration_ms=0,
            rule_outcomes=(),
        ),
    )


def test_full_orchestration_orders_both_reviews_and_merge(
    loaded_config: LoadedConfiguration,
    sample_finding: Finding,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    reviewer_limits: list[int] = []
    static = sample_finding.model_copy(update={"scan_id": SCAN_ID, "timestamp": NOW})
    dynamic = _finding_from_observation(
        _Observation(
            probe_id="SENT-008",
            target_tool="ungranted_echo",
            field=None,
            request={},
            response={"isError": False},
            logs=(),
            vulnerable=True,
        ),
        SCAN_ID,
        NOW,
    )

    def fake_reap() -> None:
        calls.append("reap")

    def fake_static(
        configuration: LoadedConfiguration,
        scan_id: UUID,
        *,
        timestamp: datetime,
    ) -> StaticScanResult:
        del configuration
        assert scan_id == SCAN_ID
        assert timestamp == NOW
        calls.append("static")
        return _static_result(static)

    class FakeReviewer:
        def __init__(
            self,
            *,
            config: LlmConfig,
            max_findings: int,
            **kwargs: object,
        ) -> None:
            del kwargs
            self.config = config
            reviewer_limits.append(max_findings)

        def review(
            self, findings: tuple[Finding, ...], *, allow_degraded: bool
        ) -> ReviewOutcome:
            assert allow_degraded is False
            source = findings[0].source
            calls.append(f"review:{source.value}")
            summary = empty_review_outcome(self.config, mode="replay").summary
            summary = summary.model_copy(
                update={
                    "candidate_count": len(findings),
                    "selected_count": len(findings),
                    "reviewed_count": len(findings),
                    "needs_review_count": len(findings),
                }
            )
            return ReviewOutcome(findings, (), summary, fatal=False)

    def fake_dynamic(
        sandbox: DockerSandbox,
        static_findings: tuple[Finding, ...],
        *,
        scan_id: UUID,
        timestamp: datetime,
    ) -> DynamicScanResult:
        assert sandbox.configuration == loaded_config
        assert static_findings == (static,)
        assert scan_id == SCAN_ID
        assert timestamp == NOW
        calls.append("dynamic")
        bindings = {
            rule_id: ProbeBinding(rule_id, None, None, None)
            for rule_id in DEFAULT_ORDER
        }
        return DynamicScanResult(
            findings=(dynamic,),
            warnings=(),
            image=DependencyImage("deps:test", "cache-key", True),
            campaign=ProbeCampaign(DEFAULT_ORDER, bindings, None, True),
        )

    def fake_merge(
        static_findings: tuple[Finding, ...],
        dynamic_findings: tuple[Finding, ...],
        catalog: ToolCatalog,
    ) -> tuple[Finding, ...]:
        calls.append("merge")
        return merge_findings_impl(static_findings, dynamic_findings, catalog)

    monkeypatch.setattr("sentinel.orchestrator.reap_orphans", fake_reap)
    monkeypatch.setattr("sentinel.orchestrator.run_static_scan", fake_static)
    monkeypatch.setattr("sentinel.orchestrator.SemanticReviewer", FakeReviewer)
    monkeypatch.setattr("sentinel.orchestrator.run_dynamic_scan", fake_dynamic)
    monkeypatch.setattr("sentinel.orchestrator.merge_findings", fake_merge)

    from sentinel.orchestrator import run_scan

    outcome = run_scan(
        loaded_config,
        _context(),
        completed_at=NOW,
        allow_degraded=False,
        review_mode="replay",
    )

    assert calls == [
        "reap",
        "static",
        "review:static",
        "dynamic",
        "review:dynamic",
        "merge",
    ]
    assert reviewer_limits == [500, 499]
    assert outcome.exit_code == 1
    assert outcome.report.analysis_complete is True
    assert outcome.report.execution_successful is True
    assert {item.source for item in outcome.report.findings} == {
        FindingSource.STATIC,
        FindingSource.DYNAMIC,
    }
    assert all(stage.status is StageStatus.SUCCEEDED for stage in outcome.report.stages)
    sarif = json.loads(render_sarif(outcome.report))
    validate_sarif_data(sarif)
    assert [rule["id"] for rule in sarif["runs"][0]["tool"]["driver"]["rules"]] == [
        "SENT-002",
        "SENT-008",
    ]
    dynamic_result = sarif["runs"][0]["results"][1]
    dynamic_location = dynamic_result["locations"][0]
    physical = dynamic_location["physicalLocation"]
    assert physical["artifactLocation"]["uri"] == "sentinel.target.yaml"
    assert physical["artifactLocation"]["uriBaseId"] == "SRCROOT"
    assert physical["region"]["startLine"] == 1
    assert dynamic_location["message"]["text"].startswith("Runtime location:")


@pytest.mark.parametrize(
    "reason",
    (
        "Docker daemon is unavailable",
        "dependency image build failed",
        "probe container failed to start",
        "failed to clean probe container",
    ),
)
def test_dynamic_infrastructure_failures_return_incomplete_exit_three(
    reason: str,
    loaded_config: LoadedConfiguration,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sentinel.orchestrator.reap_orphans", lambda: None)
    monkeypatch.setattr(
        "sentinel.orchestrator.run_static_scan",
        lambda *args, **kwargs: _empty_static_result(),
    )

    def fail_dynamic(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise InfrastructureError(reason)

    monkeypatch.setattr("sentinel.orchestrator.run_dynamic_scan", fail_dynamic)

    from sentinel.orchestrator import run_scan

    outcome = run_scan(
        loaded_config,
        _context(),
        completed_at=NOW,
        allow_degraded=False,
    )

    stages = {stage.name: stage for stage in outcome.report.stages}
    assert outcome.exit_code == 3
    assert outcome.report.analysis_complete is False
    assert outcome.report.execution_successful is False
    assert stages[StageName.DYNAMIC].status is StageStatus.FAILED
    assert stages[StageName.DYNAMIC].reason == reason
    assert stages[StageName.GPT_DYNAMIC].status is StageStatus.SKIPPED
    assert stages[StageName.MERGE].status is StageStatus.SKIPPED
    assert outcome.report.warnings[-1].code == "dynamic_analysis_failed"
