"""Merge reviewed dynamic proof into canonical static root causes."""

from __future__ import annotations

import ast
import re
from typing import cast

from sentinel.finding import (
    DynamicEvidence,
    Exploitability,
    Finding,
    FindingSource,
    StaticEvidence,
)
from sentinel.llm.tools import ToolCatalog


def merge_findings(
    static_findings: tuple[Finding, ...],
    dynamic_findings: tuple[Finding, ...],
    catalog: ToolCatalog,
) -> tuple[Finding, ...]:
    """Apply the SENT-003/SENT-009/SENT-011 provenance merge contract."""

    merged = list(static_findings)
    for dynamic in dynamic_findings:
        match_index = (
            _sent003_index(merged, dynamic, catalog)
            if dynamic.rule_id in {"SENT-009", "SENT-011"}
            else None
        )
        if match_index is None:
            match_index = next(
                (
                    index
                    for index, current in enumerate(merged)
                    if current.source is FindingSource.DYNAMIC
                    and current.dedup_key == dynamic.dedup_key
                ),
                None,
            )
        if match_index is None:
            merged.append(dynamic)
            continue
        static = merged[match_index]
        data = static.model_dump(
            mode="python", exclude={"severity", "review_disagrees"}
        )
        data.update(
            exploitability=Exploitability.CONFIRMED,
            confidence=dynamic.confidence,
            status=dynamic.status,
            timestamp=dynamic.timestamp,
            provenance=(
                *(
                    entry.model_copy(update={"review": static.review})
                    if entry.review is None
                    else entry
                    for entry in static.provenance
                ),
                *(
                    entry.model_copy(update={"review": dynamic.review})
                    for entry in dynamic.provenance
                ),
            ),
            review=dynamic.review,
        )
        merged[match_index] = Finding.model_validate(data)
    return tuple(sorted(merged, key=_finding_key))


def _sent003_index(
    findings: list[Finding], dynamic: Finding, catalog: ToolCatalog
) -> int | None:
    evidence = dynamic.evidence
    if not isinstance(evidence, DynamicEvidence) or evidence.proof is None:
        return None
    proof = evidence.proof
    # SENT-003 concerns declared-type/required validation. A size breach alone
    # does not establish that same cause, even on the same parameter.
    keywords = {"type", "required"}
    if evidence.response.get("is_error") is not False:
        return None
    path = list(proof.argument_path)
    if not path or not any(
        check.get("keyword") in keywords
        and (
            check.get("instance_path") == path
            or (
                check.get("keyword") == "required"
                and check.get("instance_path") == path[:-1]
                and isinstance(check.get("constraint"), list)
                and path[-1] in cast(list[str], check["constraint"])
            )
        )
        for check in proof.schema_checks
    ):
        return None
    matches = []
    for index, finding in enumerate(findings):
        if finding.rule_id != "SENT-003" or finding.source is not FindingSource.STATIC:
            continue
        if finding.suppression is not None or not isinstance(
            finding.evidence, StaticEvidence
        ):
            continue
        location = finding.location
        if location.kind != "file":
            continue
        tool = catalog.for_location(location.path, location.range.start_line)
        if (
            tool is not None
            and tool.name == proof.tool
            and _parameter_path(finding.evidence.snippet) == proof.argument_path
        ):
            matches.append(index)
    return matches[0] if len(matches) == 1 else None


def _parameter_path(snippet: str) -> tuple[str, ...] | None:
    # Only an exact parameter or literal subscript establishes a mapping.
    # Broader source/data-flow mapping belongs to later coverage work.
    parameter = re.fullmatch(r"\s*([A-Za-z_]\w*)(?:\s*:\s*[\w.\[\], |]+)?\s*", snippet)
    if parameter:
        return (parameter[1],)
    try:
        node = ast.parse(snippet.strip(), mode="eval").body
    except SyntaxError:
        return None
    parts = []
    while (
        isinstance(node, ast.Subscript)
        and isinstance(node.slice, ast.Constant)
        and isinstance(node.slice.value, str)
    ):
        parts.append(node.slice.value)
        node = node.value
    return (node.id, *reversed(parts)) if isinstance(node, ast.Name) else None


def _finding_key(finding: Finding) -> tuple[str, str, str]:
    return finding.rule_id, finding.location.path, finding.dedup_key
