"""Human-readable Phase 1 console report."""

from __future__ import annotations

from sentinel.finding import FileLocation, Finding
from sentinel.report.model import ScanReport


def render_console(report: ScanReport) -> str:
    lines = [
        f"MCP Sentinel {report.sentinel_version}",
        f"Target: {report.target.display_name}",
        "Status: INCOMPLETE",
        f"Static findings: {report.summary.total}",
    ]
    if report.static_analysis is not None:
        static = report.static_analysis
        lines.extend(
            (
                f"Files: {static.scanned_file_count} scanned, "
                f"{static.ignored_file_count} ignored",
                f"Static duration: {static.duration_ms} ms",
                "",
                "Rules:",
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
    if report.findings:
        lines.extend(("", "Findings:"))
        for finding in report.findings:
            lines.extend(_finding_lines(finding))
    if report.warnings:
        lines.extend(("", "Warnings:"))
        lines.extend(
            f"  {warning.code}: {warning.message}" for warning in report.warnings
        )
    lines.extend(("", "Pipeline stages:"))
    for stage in report.stages:
        reason = f" — {stage.reason}" if stage.reason else ""
        lines.append(f"  {stage.name.value}: {stage.status.value}{reason}")
    lines.extend(
        (
            "",
            "Analysis is incomplete; GPT review and dynamic probing are not "
            "implemented.",
        )
    )
    return "\n".join(lines) + "\n"


def _finding_lines(finding: Finding) -> tuple[str, ...]:
    location = finding.location
    if isinstance(location, FileLocation):
        where = (
            f"{location.path}:{location.range.start_line}:{location.range.start_column}"
        )
    else:
        where = location.path
    return (
        f"  [{finding.severity.value}] {finding.rule_id} {finding.title}",
        f"    {where} · {finding.owasp_category.id} {finding.owasp_category.name}",
        f"    {finding.description}",
        f"    Remediation: {finding.remediation}",
    )
