"""Generate the Phase 2 rules-only versus GPT-reviewed ablation artifact."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import yaml

from sentinel.config import ReasoningEffort, load_configuration
from sentinel.finding import FindingStatus
from sentinel.llm.cache import ReviewCache
from sentinel.llm.semantic_reviewer import MODEL, PRICING, SemanticReviewer
from sentinel.llm.tools import extract_tool_catalog
from sentinel.static.engine import run_static_scan

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts" / "gpt-static-ablation.json",
    )
    args = parser.parse_args()
    cases = _cases()
    treatments = {
        effort.value: _evaluate(effort, cases)
        for effort in (ReasoningEffort.MEDIUM, ReasoningEffort.LOW)
    }
    rules = _rules_only(cases)
    payload = {
        "artifact_version": 1,
        "generated_from": "checked-in cassette replay",
        "model": MODEL,
        "pricing": PRICING.model_dump(mode="json"),
        "truth_policy": {
            "ambiguous_excluded_from_binary_metrics": True,
            "ambiguous_reported_as_abstention": True,
            "cost_per_success_counts_every_fully_valid_decision": True,
        },
        "rules_only": rules,
        "gpt_reviewed": treatments,
        "phase3_artifact": "artifacts/gpt-ablation.json",
    }
    _atomic_json(args.output, payload)
    return 0


def _cases() -> list[dict[str, Any]]:
    path = ROOT / "tests" / "evals" / "gpt_review_cases.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return cast(list[dict[str, Any]], payload["cases"])


def _rules_only(cases: list[dict[str, Any]]) -> dict[str, Any]:
    binary = [item for item in cases if item["truth"] != "ambiguous"]
    true_positives = sum(item["truth"] == "vulnerable" for item in binary)
    false_positives = sum(item["truth"] == "safe" for item in binary)
    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "precision": _ratio(true_positives, true_positives + false_positives),
        "recall": 1.0,
        "abstentions": sum(item["truth"] == "ambiguous" for item in cases),
    }


def _evaluate(effort: ReasoningEffort, cases: list[dict[str, Any]]) -> dict[str, Any]:
    fixture = ROOT / "tests" / "fixtures" / "gpt_review_eval"
    loaded = load_configuration(fixture, environ={}, static_only=True)
    llm = loaded.scanner.llm.model_copy(
        update={"reasoning_effort": effort, "cache_enabled": False}
    )
    loaded = loaded.model_copy(
        update={"scanner": loaded.scanner.model_copy(update={"llm": llm})}
    )
    findings = run_static_scan(
        loaded, uuid4(), timestamp=datetime.now(timezone.utc)
    ).findings
    outcome = SemanticReviewer(
        root=fixture,
        config=llm,
        max_findings=500,
        mode="replay",
        cache=ReviewCache(enabled=False),
        cassette_root=ROOT / "src" / "sentinel" / "_cassettes" / f"eval-{effort.value}",
    ).review(findings, allow_degraded=False)
    if outcome.fatal:
        raise RuntimeError(f"{effort.value} cassette replay failed")
    catalog = extract_tool_catalog(fixture)
    case_by_key = {(item["rule_id"], item["tool"]): item for item in cases}
    decisions: list[tuple[dict[str, Any], FindingStatus]] = []
    first_probes: dict[str, str | None] = {}
    for finding in outcome.findings:
        location = finding.location
        line = location.range.start_line if hasattr(location, "range") else 0
        tool = catalog.for_location(location.path, line)
        case = case_by_key[(finding.rule_id, tool.name if tool else "")]
        decisions.append((case, finding.status))
        plan = finding.review.probe_plan
        first_probes[case["id"]] = plan.ordered_probe_ids[0] if plan else None
    binary = [item for item in decisions if item[0]["truth"] != "ambiguous"]
    true_positives = sum(
        case["truth"] == "vulnerable" and status is FindingStatus.CONFIRMED
        for case, status in binary
    )
    false_positives = sum(
        case["truth"] == "safe" and status is not FindingStatus.SUPPRESSED
        for case, status in binary
    )
    vulnerable = sum(case["truth"] == "vulnerable" for case, _ in binary)
    valid = outcome.summary.reviewed_count
    status_matches = sum(
        status.value == case["expected_status"] for case, status in decisions
    )
    priority_cases = [
        case for case, _ in decisions if "expected_first_probe" in case
    ]
    priority_matches = sum(
        first_probes[case["id"]] == case["expected_first_probe"]
        for case in priority_cases
    )
    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "precision": _ratio(true_positives, true_positives + false_positives),
        "recall": _ratio(true_positives, vulnerable),
        "abstentions": sum(
            status is FindingStatus.NEEDS_REVIEW for _, status in decisions
        ),
        "structured_output_validity": _ratio(valid, len(decisions)),
        "evidence_grounding_validity": _ratio(valid, len(decisions)),
        "probe_plan_validity": _ratio(valid, len(decisions)),
        "expected_status_accuracy": _ratio(status_matches, len(decisions)),
        "expected_probe_priority_accuracy": _ratio(
            priority_matches, len(priority_cases)
        ),
        "quality_gate_passed": (
            status_matches == len(decisions)
            and priority_matches == len(priority_cases)
        ),
        "origin_latency_ms": outcome.summary.origin_latency_ms,
        "origin_usage": outcome.summary.origin_usage.model_dump(mode="json"),
        "cache_hits": outcome.summary.cache_hits,
        "origin_cost_micro_usd": outcome.summary.origin_cost_micro_usd,
        "cost_per_valid_review_micro_usd": (
            (outcome.summary.origin_cost_micro_usd or 0) // valid if valid else None
        ),
        "status_transitions": [
            {
                "case": case["id"],
                "from": "needs_review",
                "to": status.value,
            }
            for case, status in decisions
        ],
    }


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
