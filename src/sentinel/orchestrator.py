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


@dataclass(frozen=True)
class ScanOutcome:
    report: ScanReport
    exit_code: int


def run_phase0_scan(
    configuration: LoadedConfiguration,
    context: ScanContext,
    *,
    completed_at: datetime,
) -> ScanOutcome:
    """Produce a truthful incomplete report without invoking later-phase engines."""

    del configuration
    skipped_reason = "not implemented in Phase 0"
    stages = (
        *(
            StageRecord(name=name, status=StageStatus.SKIPPED, reason=skipped_reason)
            for name in StageName
            if name is not StageName.REPORTING
        ),
        StageRecord(
            name=StageName.REPORTING,
            status=StageStatus.SUCCEEDED,
            reason=None,
        ),
    )
    findings = ()
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
            ReportWarning(
                code="analysis_incomplete",
                message="Detector stages are not implemented in Phase 0.",
            ),
        ),
        findings=findings,
    )
    return ScanOutcome(report=report, exit_code=3)
