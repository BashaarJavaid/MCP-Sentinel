"""Phase ordering and report construction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sentinel import __version__
from sentinel.config import FailThreshold, LoadedConfiguration
from sentinel.errors import InfrastructureError
from sentinel.llm.semantic_reviewer import (
    RawTransport,
    SemanticReviewer,
    empty_review_outcome,
    unavailable_review_outcome,
)
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


def run_scan(
    configuration: LoadedConfiguration,
    context: ScanContext,
    *,
    completed_at: datetime,
    allow_degraded: bool,
    review_mode: str = "live",
    api_key: str | None = None,
    transport: RawTransport | None = None,
    cassette_root: Path | None = None,
) -> ScanOutcome:
    """Run static analysis and required semantic review; Phase 3 remains explicit."""

    static_result = run_static_scan(
        configuration,
        context.scan_id,
        timestamp=completed_at,
    )
    if not static_result.findings:
        review = empty_review_outcome(configuration.scanner.llm, mode=review_mode)
    else:
        try:
            reviewer = SemanticReviewer(
                root=configuration.scan_root,
                config=configuration.scanner.llm,
                max_findings=configuration.scanner.scanner.max_findings_per_scan,
                mode=review_mode,
                api_key=api_key,
                transport=transport,
                cassette_root=cassette_root,
            )
            review = reviewer.review(
                static_result.findings, allow_degraded=allow_degraded
            )
        except InfrastructureError as error:
            review = unavailable_review_outcome(
                static_result.findings,
                config=configuration.scanner.llm,
                reason=str(error),
                allow_degraded=allow_degraded,
                applied_at=completed_at,
            )

    static_only_complete = configuration.static_only and not review.fatal
    later_reason = (
        "static-only scan requested"
        if configuration.static_only
        else "not implemented until Phase 3 dynamic probing"
    )
    gpt_status = StageStatus.FAILED if review.fatal else StageStatus.SUCCEEDED
    stages = (
        StageRecord(name=StageName.STATIC, status=StageStatus.SUCCEEDED),
        StageRecord(
            name=StageName.GPT_STATIC,
            status=gpt_status,
            reason="GPT semantic review failed" if review.fatal else None,
        ),
        StageRecord(
            name=StageName.DYNAMIC, status=StageStatus.SKIPPED, reason=later_reason
        ),
        StageRecord(
            name=StageName.GPT_DYNAMIC, status=StageStatus.SKIPPED, reason=later_reason
        ),
        StageRecord(
            name=StageName.MERGE,
            status=StageStatus.SUCCEEDED
            if static_only_complete
            else StageStatus.SKIPPED,
            reason=None if static_only_complete else later_reason,
        ),
        StageRecord(name=StageName.REPORTING, status=StageStatus.SUCCEEDED),
    )
    warnings = [*static_result.warnings, *review.warnings]
    if not configuration.static_only:
        warnings.append(
            ReportWarning(
                code="analysis_incomplete",
                message="Static and GPT review completed; dynamic probing is Phase 3.",
            )
        )
    report = ScanReport(
        scan_id=context.scan_id,
        sentinel_version=__version__,
        started_at=context.started_at,
        completed_at=completed_at,
        target=context.target,
        analysis_complete=static_only_complete,
        execution_successful=static_only_complete,
        stages=stages,
        summary=summarize(review.findings),
        warnings=tuple(warnings),
        findings=review.findings,
        static_analysis=static_result.summary,
        gpt_review=review.summary,
    )
    if review.fatal or not configuration.static_only:
        exit_code = 3
    else:
        exit_code = (
            1
            if _threshold_failed(review.findings, configuration.scanner.scanner.fail_on)
            else 0
        )
    return ScanOutcome(report=report, exit_code=exit_code)


def _threshold_failed(findings: tuple[object, ...], threshold: FailThreshold) -> bool:
    from sentinel.finding import Finding, FindingStatus

    ranks = {
        "informational": 0,
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }
    minimum = ranks[threshold.value]
    return any(
        isinstance(item, Finding)
        and item.status is not FindingStatus.SUPPRESSED
        and ranks[item.severity.value.lower()] >= minimum
        for item in findings
    )


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
        gpt_review=None,
    )
    return ScanOutcome(report=report, exit_code=3)


# Kept as a source-compatible alias for Phase 0 callers while Phase 1 lands.
run_phase0_scan = run_phase1_scan
