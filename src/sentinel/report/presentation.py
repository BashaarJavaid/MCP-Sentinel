"""Compact evidence shared by console and SARIF result messages."""

from __future__ import annotations

import json

from sentinel.finding import (
    DynamicEvidence,
    FileLocation,
    Finding,
    ReviewStatus,
    StaticEvidence,
)
from sentinel.llm.context import sanitize_text


def concise_finding(finding: Finding) -> tuple[str, ...]:
    location = finding.location
    where = location.path
    if isinstance(location, FileLocation):
        where += f":{location.range.start_line}:{location.range.start_column}"
    evidence = [finding.evidence, *(entry.evidence for entry in finding.provenance)]
    observations: list[DynamicEvidence] = []
    for item in evidence:
        if isinstance(item, DynamicEvidence) and item not in observations:
            observations.append(item)
    labels = []
    if any(isinstance(item, StaticEvidence) for item in evidence):
        labels.append("static suspicion")
    if any(
        review and review.reviewed and review.status is ReviewStatus.CONFIRMED
        for review in (finding.review, *(entry.review for entry in finding.provenance))
    ):
        labels.append("model corroboration")
    if observations:
        labels.append("runtime observation")
    if any(item.proof is not None for item in observations):
        labels.append("verified security effect")
    lines = [f"{where} · {', '.join(labels)}", finding.description]
    if isinstance(finding.evidence, StaticEvidence):
        snippet = sanitize_text(finding.evidence.snippet)
        source_lines = snippet.splitlines()
        excerpt = "\n".join(source_lines[:3])[:480]
        lines.append("Source evidence:\n" + excerpt)
        if len(source_lines) > 3 or len("\n".join(source_lines[:3])) > 480:
            lines.append("[source evidence omitted after 3 lines / 480 characters]")
        if "through a same-file helper" in finding.description:
            lines.append(
                "[helper sink locations referenced above; bodies not displayed]"
            )
    facts = []
    for item in observations:
        proof = item.proof
        if proof is None:
            facts.append(
                f"{item.probe_id}: observed response "
                f"{json.dumps(item.response, sort_keys=True)}; "
                "verified proof unavailable"
            )
            continue
        baseline = proof.baseline.get("response")
        succeeded = isinstance(baseline, dict) and baseline.get("is_error") is False
        facts.append(
            f"{item.probe_id}: {proof.tool} path {json.dumps(proof.argument_path)}; "
            f"baseline success={succeeded}"
        )
        decisive = {
            key: proof.effects[key]
            for key in (
                "canary_before",
                "canary_after",
                "resource_failure",
            )
            if key in proof.effects
        }
        if proof.schema_checks:
            decisive["schema_checks"] = [dict(check) for check in proof.schema_checks]
        facts.append(
            f"{item.probe_id}: {json.dumps(decisive, sort_keys=True)}; "
            f"attack is_error={item.response.get('is_error')}"
        )
    for fact in facts[:3]:
        text = sanitize_text(fact)
        lines.append(
            "Runtime evidence: "
            + text[:480]
            + (" [omitted]" if len(text) > 480 else "")
        )
    if len(facts) > 3:
        lines.append(
            "[additional runtime proof facts omitted; retained in machine evidence]"
        )
    lines.append(f"Remediation: {finding.remediation}")
    if finding.review_disagrees:
        lines.append(
            "GPT disagrees with runtime proof — confirmed host evidence retained"
        )
    if (
        finding.review
        and finding.review.reviewed
        and finding.review.status is ReviewStatus.NEEDS_REVIEW
    ):
        lines.append("Model abstained: needs_review judgment retained")
    if finding.suppression:
        lines.append(
            f"Inline suppression: {finding.suppression.reason} "
            f"({finding.suppression.path}:{finding.suppression.line})"
        )
    elif finding.review and finding.review.status is ReviewStatus.SUPPRESSED:
        lines.append(
            "Model suppression judgment: "
            f"{finding.review.reason or finding.review.reasoning}"
        )
    return tuple(lines)
