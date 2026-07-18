"""Merge reviewed dynamic proof into canonical static root causes."""

from __future__ import annotations

from sentinel.finding import Exploitability, Finding, FindingSource, LogicalLocation
from sentinel.llm.tools import ToolCatalog


def merge_findings(
    static_findings: tuple[Finding, ...],
    dynamic_findings: tuple[Finding, ...],
    catalog: ToolCatalog,
) -> tuple[Finding, ...]:
    """Apply the SENT-003/SENT-009/SENT-011 provenance merge contract."""

    merged = list(static_findings)
    for dynamic in dynamic_findings:
        target = _dynamic_tool_name(dynamic)
        match_index = (
            _sent003_index(merged, target, catalog)
            if dynamic.rule_id in {"SENT-009", "SENT-011"}
            else None
        )
        if match_index is None:
            merged.append(dynamic)
            continue
        static = merged[match_index]
        data = static.model_dump(mode="python", exclude={"severity"})
        data.update(
            exploitability=Exploitability.CONFIRMED,
            confidence=dynamic.confidence,
            status=dynamic.status,
            timestamp=dynamic.timestamp,
            provenance=(*static.provenance, *dynamic.provenance),
            review=dynamic.review,
        )
        merged[match_index] = Finding.model_validate(data)
    return tuple(sorted(merged, key=_finding_key))


def _sent003_index(
    findings: list[Finding], target: str | None, catalog: ToolCatalog
) -> int | None:
    if target is None:
        return None
    for index, finding in enumerate(findings):
        if finding.rule_id != "SENT-003" or finding.source is not FindingSource.STATIC:
            continue
        location = finding.location
        if location.kind != "file":
            continue
        tool = catalog.for_location(location.path, location.range.start_line)
        if tool is not None and tool.name == target:
            return index
    return None


def _dynamic_tool_name(finding: Finding) -> str | None:
    location = finding.location
    if not isinstance(location, LogicalLocation):
        return None
    parts = location.path.split("/")
    if len(parts) < 3 or parts[1] != "tools":
        return None
    return parts[2].replace("~1", "/").replace("~0", "~")


def _finding_key(finding: Finding) -> tuple[str, str, str]:
    return finding.rule_id, finding.location.path, finding.dedup_key
