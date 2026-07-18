"""Phase ordering and report construction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sentinel import __version__
from sentinel.config import LoadedConfiguration
from sentinel.report.model import (
    ReportWarning,
    ScanContext,
    ScanReport,
    StageName,
    StageRecord,
    StageStatus,
    summarize,
)
from sentinel.static.engine import run_static_scan


@dataclass(frozen=True)
class ScanOutcome:
    report: ScanReport
    exit_code: int


def run_phase1_scan(
    configuration: LoadedConfiguration,
    context: ScanContext,
    *,
    completed_at: datetime,
) -> ScanOutcome:
    """Run Phase 1 static analysis and mark later required stages incomplete."""

    static_result = run_static_scan(
        configuration,
        context.scan_id,
        timestamp=completed_at,
    )
    skipped_reason = "not implemented after Phase 1 static analysis"
    stages = (
        StageRecord(
            name=StageName.STATIC,
            status=StageStatus.SUCCEEDED,
            reason=None,
        ),
        *(
            StageRecord(name=name, status=StageStatus.SKIPPED, reason=skipped_reason)
            for name in (
                StageName.GPT_STATIC,
                StageName.DYNAMIC,
                StageName.GPT_DYNAMIC,
                StageName.MERGE,
            )
        ),
        StageRecord(
            name=StageName.REPORTING,
            status=StageStatus.SUCCEEDED,
            reason=None,
        ),
    )
    findings = static_result.findings
    report = ScanReport(
        scan_id=context.scan_id,
        sentinel_version=__version__,
        started_at=context.started_at,
        completed_at=completed_at,
        target=context.target,
        analysis_complete=False,
        execution_successful=False,
        stages=stages,
        summary=summarize(findings),
        warnings=(
            *static_result.warnings,
            ReportWarning(
                code="analysis_incomplete",
                message=(
                    "Static analysis completed; required GPT and dynamic stages "
                    "are not implemented yet."
                ),
            ),
        ),
        findings=findings,
        static_analysis=static_result.summary,
    )
    return ScanOutcome(report=report, exit_code=3)


# Kept as a source-compatible alias for Phase 0 callers while Phase 1 lands.
run_phase0_scan = run_phase1_scan
