"""Minimal truthful Phase 0 console renderer."""

from __future__ import annotations

from sentinel.report.model import ScanReport


def render_console(report: ScanReport) -> str:
    lines = [
        f"MCP Sentinel {report.sentinel_version}",
        f"Target: {report.target.display_name}",
        "Status: INCOMPLETE",
        f"Findings: {report.summary.total}",
        "",
        "Pipeline stages:",
    ]
    for stage in report.stages:
        reason = f" — {stage.reason}" if stage.reason else ""
        lines.append(f"  {stage.name.value}: {stage.status.value}{reason}")
    lines.extend(("", "Analysis is incomplete; detector stages are not implemented."))
    return "\n".join(lines) + "\n"
