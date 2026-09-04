"""Phase ordering and report construction."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sentinel import __version__
from sentinel.baseline import LoadedBaseline, annotate_report
from sentinel.config import FailThreshold, LoadedConfiguration, TargetLanguage
from sentinel.dynamic.merge import merge_findings
from sentinel.dynamic.prober import run_dynamic_scan
from sentinel.dynamic.sandbox import DockerSandbox, reap_orphans
from sentinel.errors import InfrastructureError
from sentinel.finding import DegradedReview, Finding, TokenUsage
from sentinel.llm.semantic_reviewer import (
    RawTransport,
    ReviewOutcome,
    SemanticReviewer,
    empty_review_outcome,
    unavailable_review_outcome,
)
from sentinel.llm.tools import extract_tool_catalog
from sentinel.report.model import (
    GptReviewSummary,
    ReportWarning,
    ScanContext,
    ScanReport,
    StageName,
    StageRecord,
    StageStatus,
    summarize,
)
from sentinel.static.engine import STATIC_TIMEOUT_SECONDS, run_static_scan
from sentinel.static.model import StaticScanResult
from sentinel.static.semgrep_adapter import TYPESCRIPT_CATALOG_RULE_ID, run_semgrep
from sentinel.static.traversal import collect_static_files


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
    baseline: LoadedBaseline | None = None,
) -> ScanOutcome:
    """Run the complete static, GPT, Docker probe, merge, and report pipeline."""

    configuration, forced_ignored_paths = _exclude_baseline(configuration, baseline)
    if not configuration.static_only:
        reap_orphans()

    deadline = time.monotonic() + STATIC_TIMEOUT_SECONDS
    catalog = None
    if configuration.language is TargetLanguage.TYPESCRIPT:
        files = collect_static_files(
            configuration.scan_root,
            configuration.scanner.scanner.ignore_paths,
            configuration.language,
        )
        candidates = run_semgrep(
            files,
            (TYPESCRIPT_CATALOG_RULE_ID,),
            configuration.scan_root,
            deadline=deadline,
        )[TYPESCRIPT_CATALOG_RULE_ID]
        catalog = extract_tool_catalog(
            configuration.scan_root,
            configuration.scanner.scanner.ignore_paths,
            configuration.language,
            typescript_candidates=tuple(candidates),
        )
    if configuration.language is TargetLanguage.TYPESCRIPT:
        if forced_ignored_paths:
            static_result = run_static_scan(
                configuration,
                context.scan_id,
                timestamp=completed_at,
                deadline=deadline,
                forced_ignored_paths=forced_ignored_paths,
            )
        else:
            static_result = run_static_scan(
                configuration,
                context.scan_id,
                timestamp=completed_at,
                deadline=deadline,
            )
    elif forced_ignored_paths:
        static_result = run_static_scan(
            configuration,
            context.scan_id,
            timestamp=completed_at,
            forced_ignored_paths=forced_ignored_paths,
        )
    else:
        static_result = run_static_scan(
            configuration,
            context.scan_id,
            timestamp=completed_at,
        )
    if catalog is None:
        catalog = extract_tool_catalog(
            configuration.scan_root,
            configuration.scanner.scanner.ignore_paths,
            configuration.language,
        )
    static_result = StaticScanResult(
        findings=static_result.findings,
        warnings=_unique_warnings((*static_result.warnings, *catalog.warnings)),
        summary=static_result.summary,
    )
    reviewable = tuple(
        finding for finding in static_result.findings if finding.suppression is None
    )
    if not reviewable:
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
                catalog=catalog,
            )
            review = reviewer.review(reviewable, allow_degraded=allow_degraded)
        except InfrastructureError as error:
            review = unavailable_review_outcome(
                reviewable,
                config=configuration.scanner.llm,
                reason=str(error),
                allow_degraded=allow_degraded,
                applied_at=completed_at,
            )
    review = _restore_inline_suppressions(static_result.findings, review)

    if configuration.static_only:
        return _static_only_outcome(
            configuration,
            context,
            completed_at,
            static_result,
            review,
            baseline,
        )

    if review.fatal:
        return _failed_dynamic_outcome(
            configuration,
            context,
            completed_at,
            static_result,
            review,
            reason="static GPT review failed before dynamic probing",
            dynamic_started=False,
            baseline=baseline,
        )

    try:
        dynamic = run_dynamic_scan(
            DockerSandbox(configuration, context.scan_id),
            review.findings,
            scan_id=context.scan_id,
            timestamp=completed_at,
        )
    except InfrastructureError as error:
        return _failed_dynamic_outcome(
            configuration,
            context,
            completed_at,
            static_result,
            review,
            reason=str(error),
            dynamic_started=True,
            baseline=baseline,
        )

    remaining = max(
        0,
        configuration.scanner.scanner.max_findings_per_scan
        - review.summary.selected_count,
    )
    if not dynamic.findings:
        dynamic_review = empty_review_outcome(
            configuration.scanner.llm, mode=review_mode
        )
    elif remaining == 0:
        dynamic_review = _cap_overflow_review(
            dynamic.findings, configuration, applied_at=completed_at
        )
    else:
        try:
            reviewer = SemanticReviewer(
                root=configuration.scan_root,
                config=configuration.scanner.llm,
                max_findings=remaining,
                mode=review_mode,
                api_key=api_key,
                transport=transport,
                cassette_root=cassette_root,
                catalog=catalog,
            )
            dynamic_review = reviewer.review(
                dynamic.findings, allow_degraded=allow_degraded
            )
        except InfrastructureError as error:
            dynamic_review = unavailable_review_outcome(
                dynamic.findings,
                config=configuration.scanner.llm,
                reason=str(error),
                allow_degraded=allow_degraded,
                applied_at=completed_at,
            )

    findings = merge_findings(review.findings, dynamic_review.findings, catalog)
    combined_gpt = _combine_gpt_summaries(review.summary, dynamic_review.summary)
    stages = (
        StageRecord(name=StageName.STATIC, status=StageStatus.SUCCEEDED),
        StageRecord(name=StageName.GPT_STATIC, status=StageStatus.SUCCEEDED),
        StageRecord(name=StageName.DYNAMIC, status=StageStatus.SUCCEEDED),
        StageRecord(
            name=StageName.GPT_DYNAMIC,
            status=(
                StageStatus.FAILED if dynamic_review.fatal else StageStatus.SUCCEEDED
            ),
            reason=("GPT dynamic review failed" if dynamic_review.fatal else None),
        ),
        StageRecord(name=StageName.MERGE, status=StageStatus.SUCCEEDED),
        StageRecord(name=StageName.REPORTING, status=StageStatus.SUCCEEDED),
    )
    complete = not dynamic_review.fatal
    report = ScanReport(
        scan_id=context.scan_id,
        sentinel_version=__version__,
        started_at=context.started_at,
        completed_at=completed_at,
        target=context.target,
        analysis_complete=complete,
        execution_successful=complete,
        stages=stages,
        summary=summarize(findings),
        warnings=_unique_warnings(
            (
                *static_result.warnings,
                *review.warnings,
                *dynamic.warnings,
                *dynamic_review.warnings,
            )
        ),
        findings=findings,
        static_analysis=static_result.summary,
        gpt_review=combined_gpt,
    )
    return _finalize_outcome(report, configuration, baseline)


def _static_only_outcome(
    configuration: LoadedConfiguration,
    context: ScanContext,
    completed_at: datetime,
    static_result: StaticScanResult,
    review: ReviewOutcome,
    baseline: LoadedBaseline | None,
) -> ScanOutcome:
    static_only_complete = not review.fatal
    later_reason = "static-only scan requested"
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
        warnings=_unique_warnings(tuple(warnings)),
        findings=review.findings,
        static_analysis=static_result.summary,
        gpt_review=review.summary,
    )
    return _finalize_outcome(report, configuration, baseline)


def _failed_dynamic_outcome(
    configuration: LoadedConfiguration,
    context: ScanContext,
    completed_at: datetime,
    static_result: StaticScanResult,
    review: ReviewOutcome,
    *,
    reason: str,
    dynamic_started: bool,
    baseline: LoadedBaseline | None,
) -> ScanOutcome:
    stages = (
        StageRecord(name=StageName.STATIC, status=StageStatus.SUCCEEDED),
        StageRecord(
            name=StageName.GPT_STATIC,
            status=StageStatus.FAILED if review.fatal else StageStatus.SUCCEEDED,
            reason="GPT semantic review failed" if review.fatal else None,
        ),
        StageRecord(
            name=StageName.DYNAMIC,
            status=StageStatus.FAILED if dynamic_started else StageStatus.SKIPPED,
            reason=reason,
        ),
        StageRecord(
            name=StageName.GPT_DYNAMIC,
            status=StageStatus.SKIPPED,
            reason=reason,
        ),
        StageRecord(name=StageName.MERGE, status=StageStatus.SKIPPED, reason=reason),
        StageRecord(name=StageName.REPORTING, status=StageStatus.SUCCEEDED),
    )
    report = ScanReport(
        scan_id=context.scan_id,
        sentinel_version=__version__,
        started_at=context.started_at,
        completed_at=completed_at,
        target=context.target,
        analysis_complete=False,
        execution_successful=False,
        stages=stages,
        summary=summarize(review.findings),
        warnings=(
            *static_result.warnings,
            *review.warnings,
            ReportWarning(code="dynamic_analysis_failed", message=reason),
        ),
        findings=review.findings,
        static_analysis=static_result.summary,
        gpt_review=review.summary,
    )
    return _finalize_outcome(report, configuration, baseline)


def _cap_overflow_review(
    findings: tuple[Finding, ...],
    configuration: LoadedConfiguration,
    *,
    applied_at: datetime,
) -> ReviewOutcome:

    reason = "scan-wide GPT review cap was exhausted before dynamic review"
    updated: list[Finding] = []
    for finding in findings:
        data = finding.model_dump(mode="python", exclude={"severity"})
        data["review"] = DegradedReview(reason=reason, applied_at=applied_at)
        updated.append(Finding.model_validate(data))
    empty = empty_review_outcome(configuration.scanner.llm, mode="degraded")
    summary = empty.summary.model_copy(
        update={
            "mode": "degraded",
            "candidate_count": len(updated),
            "overflow_count": len(updated),
            "needs_review_count": len(updated),
        }
    )
    warning = ReportWarning(code="gpt_review_truncated", message=reason)
    return ReviewOutcome(tuple(updated), (warning,), summary, fatal=False)


def _restore_inline_suppressions(
    original: tuple[Finding, ...], review: ReviewOutcome
) -> ReviewOutcome:
    reviewed = {finding.finding_id: finding for finding in review.findings}
    findings = tuple(
        finding if finding.suppression is not None else reviewed[finding.finding_id]
        for finding in original
    )
    return ReviewOutcome(findings, review.warnings, review.summary, review.fatal)


def _exclude_baseline(
    configuration: LoadedConfiguration, baseline: LoadedBaseline | None
) -> tuple[LoadedConfiguration, frozenset[str]]:
    if baseline is None:
        return configuration, frozenset()
    try:
        relative = baseline.path.relative_to(configuration.scan_root).as_posix()
    except ValueError:
        return configuration, frozenset()
    scanner = configuration.scanner.scanner
    if relative not in scanner.ignore_paths:
        scanner = scanner.model_copy(
            update={"ignore_paths": (*scanner.ignore_paths, relative)}
        )
        configuration = configuration.model_copy(
            update={
                "scanner": configuration.scanner.model_copy(update={"scanner": scanner})
            }
        )
    return configuration, frozenset({relative})


def _finalize_outcome(
    report: ScanReport,
    configuration: LoadedConfiguration,
    baseline: LoadedBaseline | None,
) -> ScanOutcome:
    if baseline is not None:
        report = annotate_report(report, baseline)
    if not report.analysis_complete or not report.execution_successful:
        return ScanOutcome(report=report, exit_code=3)
    return ScanOutcome(
        report=report,
        exit_code=(
            1
            if _threshold_failed(report.findings, configuration.scanner.scanner.fail_on)
            else 0
        ),
    )


def _combine_gpt_summaries(
    first: GptReviewSummary, second: GptReviewSummary
) -> GptReviewSummary:
    mode = first.mode if first.mode == second.mode else "mixed"
    return GptReviewSummary(
        requested_model=first.requested_model,
        reasoning_effort=first.reasoning_effort,
        endpoint_mode=first.endpoint_mode,
        endpoint_url_hash=first.endpoint_url_hash,
        mode=mode,
        candidate_count=first.candidate_count + second.candidate_count,
        selected_count=first.selected_count + second.selected_count,
        overflow_count=first.overflow_count + second.overflow_count,
        reviewed_count=first.reviewed_count + second.reviewed_count,
        confirmed_count=first.confirmed_count + second.confirmed_count,
        suppressed_count=first.suppressed_count + second.suppressed_count,
        needs_review_count=first.needs_review_count + second.needs_review_count,
        failure_count=first.failure_count + second.failure_count,
        cache_hits=first.cache_hits + second.cache_hits,
        cache_misses=first.cache_misses + second.cache_misses,
        cache_writes=first.cache_writes + second.cache_writes,
        cache_errors=first.cache_errors + second.cache_errors,
        current_usage=_sum_usage(first.current_usage, second.current_usage),
        origin_usage=_sum_usage(first.origin_usage, second.origin_usage),
        current_latency_ms=(first.current_latency_ms + second.current_latency_ms),
        origin_latency_ms=first.origin_latency_ms + second.origin_latency_ms,
        current_cost_micro_usd=_sum_optional(
            first.current_cost_micro_usd, second.current_cost_micro_usd
        ),
        origin_cost_micro_usd=_sum_optional(
            first.origin_cost_micro_usd, second.origin_cost_micro_usd
        ),
        pricing=first.pricing if first.pricing == second.pricing else None,
        batches=(*first.batches, *second.batches),
    )


def _sum_usage(first: TokenUsage, second: TokenUsage) -> TokenUsage:
    values: dict[str, int | None] = {}
    for name in TokenUsage.model_fields:
        values[name] = _sum_optional(getattr(first, name), getattr(second, name))
    return TokenUsage.model_validate(values)


def _sum_optional(first: int | None, second: int | None) -> int | None:
    if first is None and second is None:
        return None
    return (first or 0) + (second or 0)


def _unique_warnings(warnings: tuple[ReportWarning, ...]) -> tuple[ReportWarning, ...]:
    result: list[ReportWarning] = []
    key_guidance_seen: set[str] = set()
    for warning in warnings:
        if warning.code == "gpt_review_unavailable" and warning.message.startswith(
            "OPENAI_API_KEY is not set;"
        ):
            if warning.message in key_guidance_seen:
                continue
            key_guidance_seen.add(warning.message)
        result.append(warning)
    return tuple(result)


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
        and item.baseline_matched is not True
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
