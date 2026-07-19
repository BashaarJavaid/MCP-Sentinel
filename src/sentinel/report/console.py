"""Human-readable scan report with optional terminal styling."""

from __future__ import annotations

import json

import typer

from sentinel.finding import (
    DynamicEvidence,
    FileLocation,
    Finding,
    FindingStatus,
    Severity,
    StaticEvidence,
)
from sentinel.report.model import ScanReport

_SEVERITY_RANK = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.INFORMATIONAL: 4,
}
_SEVERITY_COLORS = {
    Severity.CRITICAL: "bright_red",
    Severity.HIGH: "red",
    Severity.MEDIUM: "yellow",
    Severity.LOW: "blue",
    Severity.INFORMATIONAL: "cyan",
}


def render_console(
    report: ScanReport, *, verbose: bool = False, color: bool = False
) -> str:
    status = "COMPLETE" if report.analysis_complete else "INCOMPLETE"
    lines = [
        _style(f"MCP Sentinel {report.sentinel_version}", color, bold=True),
        f"Target: {report.target.display_name}",
        f"Status: {_status_text(status, report.analysis_complete, color)}",
        _summary_line(report),
    ]
    if report.static_analysis is not None:
        static = report.static_analysis
        lines.extend(
            (
                f"Files: {static.scanned_file_count} scanned, "
                f"{static.ignored_file_count} ignored",
                f"Static duration: {static.duration_ms} ms",
                "",
                _style("Rules", color, bold=True),
            )
        )
        for outcome in static.rule_outcomes:
            detail = f" — {outcome.skip_reason}" if outcome.skip_reason else ""
            lines.append(
                f"  {outcome.rule_id}: {outcome.status.value}, "
                f"{outcome.match_count} match(es){detail}"
            )
            for reason, count in outcome.exemptions_by_reason.items():
                lines.append(f"    exempt {reason}: {count}")
    if report.gpt_review is not None:
        review = report.gpt_review
        label = review.mode.upper()
        lines.extend(
            (
                "",
                _style("GPT review", color, bold=True)
                + f": {label} · {review.reviewed_count}/"
                f"{review.candidate_count} reviewed",
                f"  confirmed {review.confirmed_count}, suppressed "
                f"{review.suppressed_count}, needs review {review.needs_review_count}",
                f"  cache {review.cache_hits} hit(s), {review.cache_misses} miss(es)",
                f"  origin tokens {review.origin_usage.total_tokens or 0}, "
                f"cost {review.origin_cost_micro_usd or 0} micro-USD",
            )
        )
        if review.mode == "replay":
            lines.append(
                _style("  RECORDED REPLAY — no live model call", color, fg="yellow")
            )
        elif review.mode == "degraded":
            lines.append(
                _style("  DEGRADED — semantic review did not run", color, fg="yellow")
            )
    if report.findings:
        lines.extend(("", _style("Findings", color, bold=True)))
        for finding in sorted(report.findings, key=_finding_sort_key):
            lines.extend(_finding_lines(finding, verbose=verbose, color=color))
    if report.warnings:
        lines.extend(("", _style("Warnings", color, fg="yellow", bold=True)))
        lines.extend(
            f"  {warning.code}: {warning.message}" for warning in report.warnings
        )
    lines.extend(("", _style("Pipeline stages", color, bold=True)))
    for stage in report.stages:
        reason = f" — {stage.reason}" if stage.reason else ""
        lines.append(f"  {stage.name.value}: {stage.status.value}{reason}")
    lines.extend(
        (
            "",
            "Analysis complete."
            if report.analysis_complete
            else "Analysis incomplete.",
        )
    )
    return "\n".join(lines) + "\n"


def _summary_line(report: ScanReport) -> str:
    severities = report.summary.by_severity
    statuses = report.summary.by_status
    return (
        f"Findings: {report.summary.total} · "
        f"Critical {severities[Severity.CRITICAL]}, High {severities[Severity.HIGH]}, "
        f"Medium {severities[Severity.MEDIUM]}, Low {severities[Severity.LOW]} · "
        f"confirmed {statuses[FindingStatus.CONFIRMED]}, "
        f"needs review {statuses[FindingStatus.NEEDS_REVIEW]}, "
        f"suppressed {statuses[FindingStatus.SUPPRESSED]}"
    )


def _finding_sort_key(finding: Finding) -> tuple[object, ...]:
    suppressed = finding.status is FindingStatus.SUPPRESSED
    location = finding.location
    line = location.range.start_line if isinstance(location, FileLocation) else 0
    return (
        _SEVERITY_RANK[finding.severity],
        suppressed,
        finding.rule_id,
        location.path,
        line,
    )


def _finding_lines(finding: Finding, *, verbose: bool, color: bool) -> tuple[str, ...]:
    location = finding.location
    if isinstance(location, FileLocation):
        where = (
            f"{location.path}:{location.range.start_line}:{location.range.start_column}"
        )
    else:
        where = location.path
    severity = _style(
        f"[{finding.severity.value}]",
        color,
        fg=_SEVERITY_COLORS[finding.severity],
        bold=finding.severity is Severity.CRITICAL,
    )
    status = _finding_status(finding, color)
    lines = [
        f"  {severity} {finding.rule_id} {finding.title} · {status}",
        f"    {where} · {finding.owasp_category.id} {finding.owasp_category.name}",
        f"    Remediation: {finding.remediation}",
    ]
    if verbose:
        lines.extend(_verbose_finding_lines(finding))
    return tuple(lines)


def _verbose_finding_lines(finding: Finding) -> tuple[str, ...]:
    lines = [f"    Description: {finding.description}"]
    evidence = finding.evidence
    if isinstance(evidence, StaticEvidence):
        snippet = " ".join(evidence.snippet.strip().split())
        lines.append(f"    Evidence: {snippet[:240]}")
    elif isinstance(evidence, DynamicEvidence):
        request = json.dumps(evidence.request, ensure_ascii=False, sort_keys=True)
        response = json.dumps(evidence.response, ensure_ascii=False, sort_keys=True)
        lines.append(f"    Probe: {evidence.probe_id} request {request[:240]}")
        lines.append(f"    Outcome: {response[:240]}")
        if evidence.logs:
            lines.append(f"    Logs: {' | '.join(evidence.logs[-3:])[:240]}")
    if finding.review.reasoning:
        lines.append(f"    GPT reasoning: {finding.review.reasoning[:500]}")
    for reference in finding.review.evidence_refs or ():
        lines.append(
            f"    Claim: {reference.path}:{reference.range.start_line} — "
            f"{reference.claim[:300]}"
        )
    provenance = " → ".join(
        f"{entry.source.value}:{entry.rule_id}" for entry in finding.provenance
    )
    lines.append(f"    Provenance: {provenance}")
    return tuple(lines)


def _finding_status(finding: Finding, color: bool) -> str:
    label = finding.status.value.replace("_", " ")
    if finding.status is FindingStatus.CONFIRMED:
        return _style(label, color, fg="green")
    if finding.status is FindingStatus.SUPPRESSED:
        return _style(label, color, dim=True)
    if finding.status is FindingStatus.NEEDS_REVIEW:
        return _style(label, color, fg="yellow")
    return label


def _status_text(value: str, complete: bool, color: bool) -> str:
    return _style(value, color, fg="green" if complete else "yellow", bold=True)


def _style(
    value: str,
    color: bool,
    *,
    fg: str | None = None,
    bold: bool = False,
    dim: bool = False,
) -> str:
    if not color:
        return value
    return typer.style(value, fg=fg, bold=bold, dim=dim)
