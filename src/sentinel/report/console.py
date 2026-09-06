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
from sentinel.report.presentation import concise_finding

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
        _style(f"PortunusMCP Sentinel {report.sentinel_version}", color, bold=True),
        f"Target: {report.target.display_name}",
        f"Status: {_status_text(status, report.analysis_complete, color)}",
        _summary_line(report),
    ]
    if any(stage.reason == "rules-only scan requested" for stage in report.stages):
        lines.append("Tier: RULES-ONLY · GPT review and dynamic probes skipped")
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
    lines.extend(_coverage_lines(report))
    if report.dynamic_analysis is not None:
        lines.extend(("", _style("Dynamic probes", color, bold=True)))
        for probe in report.dynamic_analysis.probe_outcomes:
            binding = ".".join(
                part for part in (probe.tool, *probe.argument_path) if part
            )
            verdict = f" · {probe.verdict}" if probe.verdict else ""
            lines.append(
                f"  {probe.probe_id}: {probe.status}{verdict} · "
                f"{binding or 'unbound'} — {probe.reason} · "
                f"baseline sent={probe.baseline_attempted}, "
                f"attack sent={probe.attack_attempted}"
            )
            response = probe.baseline.get("response")
            process = (
                response.get("process_state") if isinstance(response, dict) else None
            )
            lines.append(
                "    baseline control succeeded="
                + str(
                    isinstance(response, dict)
                    and response.get("is_error") is False
                    and isinstance(process, dict)
                    and process.get("Running") is True
                    if isinstance(response, dict) and isinstance(process, dict)
                    else "unknown"
                )
            )
    if report.baseline is not None:
        baseline = report.baseline
        lines.extend(
            (
                "",
                _style("Baseline", color, bold=True),
                f"  matched {baseline.matched_finding_count}, new "
                f"{baseline.new_finding_count}, resolved "
                f"{baseline.resolved_finding_count} (not observed in this scan), prior "
                f"{baseline.baseline_finding_count}",
                f"  {baseline.matcher_version}, schema "
                f"{baseline.source_schema_version}, source "
                f"{baseline.source_sha256[:12]}",
            )
        )
    if report.gpt_review is not None:
        review = report.gpt_review
        label = review.mode.upper()
        lines.extend(
            (
                "",
                _style("GPT review", color, bold=True)
                + f": {label} · {review.reviewed_count}/"
                f"{review.candidate_count} reviewed",
                f"  model {review.requested_model}, reasoning "
                f"{review.reasoning_effort.value}, endpoint "
                f"{review.endpoint_mode.value}",
                f"  model judgments: confirmed {review.confirmed_count}, suppressed "
                f"{review.suppressed_count}, needs review {review.needs_review_count}",
                f"  cache {review.cache_hits} hit(s), {review.cache_misses} miss(es)",
                f"  origin tokens {review.origin_usage.total_tokens or 0}, "
                + (
                    f"cost {review.origin_cost_micro_usd or 0} micro-USD"
                    if review.origin_cost_micro_usd is not None
                    else "cost unavailable"
                ),
            )
        )
        if review.disagreement_count:
            lines.append(f"  runtime proof disagreements: {review.disagreement_count}")
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
            "Selected analysis complete. Coverage limits remain; "
            "this is not proof of safety."
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
    baseline = (
        " · baseline"
        if finding.baseline_matched is True
        else " · new"
        if finding.baseline_matched is False
        else ""
    )
    lines = [
        f"  {severity} {finding.rule_id} {finding.title} · {status}{baseline}",
        f"    {where} · {finding.owasp_category.id} {finding.owasp_category.name}",
    ]
    lines.extend(
        "    " + line.replace("\n", "\n    ") for line in concise_finding(finding)
    )
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
    if finding.review and finding.review.reasoning:
        lines.append(f"    GPT reasoning: {finding.review.reasoning[:500]}")
    for reference in (finding.review.evidence_refs or ()) if finding.review else ():
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


def _coverage_lines(report: ScanReport) -> list[str]:
    lines: list[str] = []
    static = report.static_analysis.coverage if report.static_analysis else None
    if static is not None:
        lines.extend(
            (
                "",
                f"Static surface inventory: {len(static.surfaces)} observed; "
                "total possible unknown",
            )
        )
        for surface in static.surfaces:
            loc = surface.location
            handler = surface.handler
            lines.append(
                f"  {surface.kind} {surface.name!r} at {loc.path}:"
                f"{loc.range.start_line}:{loc.range.start_column}: {surface.status}; "
                "examined by "
                f"{', '.join(surface.examined_rule_ids) or 'no handler rule'}"
            )
            if handler:
                lines.append(
                    f"    handler {handler.path}:{handler.range.start_line}:"
                    f"{handler.range.start_column}"
                )
            lines.extend(
                f"    {reason.code}: {reason.message}" for reason in surface.reasons
            )
        lines.extend(
            f"  {gap.code} at {gap.location.path}:"
            f"{gap.location.range.start_line}: {gap.message}"
            for gap in static.unresolved_flows
        )
        lines.append(
            "  Configuration-excluded rules: "
            f"{', '.join(static.excluded_rule_ids) or 'none'}"
        )
        lines.append(
            "  File/configuration-wide rules: "
            f"{', '.join(static.file_wide_rule_ids) or 'none'}"
        )
        lines.append(
            "  Rule evaluated does not mean every implementation was recognized."
        )
    elif report.static_analysis:
        lines.append("Static surface coverage: unavailable")
    dynamic = report.dynamic_analysis
    if dynamic and dynamic.coverage:
        lines.extend(
            (
                "",
                "Runtime discovery: separate baseline/attack sessions; "
                "four fixed attempts",
            )
        )
        for binding in dynamic.coverage.planned_bindings:
            lines.append(
                f"  Planned {binding.probe_id}: tool={binding.tool!r}, "
                f"field={binding.field!r} (null uses runtime fallback)"
            )
        outcomes = {str(item.probe_id): item for item in dynamic.probe_outcomes}
        for snapshot in dynamic.coverage.discovery:
            total = (
                str(snapshot.tool_total)
                if snapshot.tool_total is not None
                else "unknown"
            )
            lines.append(
                f"  {snapshot.probe_id} {snapshot.role}: "
                f"{len(snapshot.tools)} observed, session total {total}, "
                f"more pages={snapshot.more_pages}"
            )
            if snapshot.reason:
                lines.append(f"    {snapshot.reason}")
            outcome = outcomes[snapshot.probe_id]
            for tool in snapshot.tools:
                attacked = (
                    snapshot.role == "attack"
                    and outcome.attack_attempted is True
                    and outcome.tool == tool.name
                )
                paths = tuple(
                    path
                    for path in tool.field_paths
                    if attacked and path == outcome.argument_path
                )
                unprobed = tuple(path for path in tool.field_paths if path not in paths)
                lines.append(
                    f"    {tool.name!r}: attack "
                    f"{'sent' if attacked else 'not sent in this session'}; "
                    f"schema {tool.schema_sha256 or 'unknown'}"
                )
                lines.append(
                    f"      fields attacked: {json.dumps(paths)}; "
                    f"fields not attacked: {json.dumps(unprobed)}"
                )
                if attacked and outcome.argument_path not in paths:
                    lines.append(
                        "      exact attempted path: "
                        f"{json.dumps(outcome.argument_path)} "
                        "(outside enumeration or tool-level call)"
                    )
                lines.extend(
                    f"      unresolved {json.dumps(gap.path)}: {gap.reason}"
                    for gap in tool.unresolved
                )
    elif dynamic:
        lines.append("Runtime discovery coverage: unavailable")
    lines.extend(("", "Review activity by stage"))
    for name in ("static", "dynamic"):
        activity = getattr(report.review_activity, name)
        if activity is None:
            lines.append(f"  {name}: unavailable historical activity")
            continue
        lines.append(
            f"  {name}: {activity.state}; candidates {activity.candidate_count}, "
            f"excluded {activity.excluded_count}, selected {activity.selected_count}, "
            f"reviewed {activity.reviewed_count}, "
            f"unreviewed {activity.unreviewed_count}; "
            f"modes {', '.join(activity.modes) or 'none'}"
        )
        lines.append(f"    {activity.reason}")
    return lines
