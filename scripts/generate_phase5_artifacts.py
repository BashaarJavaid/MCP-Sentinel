"""Generate the replay ablation and the explicitly budgeted live SARIF proof."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import tiktoken

from scripts.generate_gpt_static_ablation import (
    _atomic_json,
    _cases,
    _evaluate,
    _ratio,
    _rules_only,
)
from sentinel.config import ReasoningEffort, load_configuration
from sentinel.dynamic.catalog import RULE_IDS as DYNAMIC_RULE_IDS
from sentinel.dynamic.prober import (
    INJECTION_MARKER,
    OVERSIZED_MARKER,
    WRONG_TYPE_MARKER,
    run_dynamic_scan,
)
from sentinel.dynamic.sandbox import DockerSandbox, reap_orphans
from sentinel.finding import Finding, FindingStatus, ProbePlan, TokenUsage
from sentinel.llm.cache import ReviewCache
from sentinel.llm.semantic_reviewer import (
    MODEL,
    PRICING,
    OpenAITransport,
    RawTransport,
    SemanticReviewer,
    _cost,
    _usage,
)
from sentinel.llm.tools import extract_tool_catalog
from sentinel.orchestrator import run_scan
from sentinel.report.model import ScanContext, ScanTarget
from sentinel.report.sarif import render_sarif
from sentinel.report.validate_sarif import validate_sarif_data
from sentinel.static.engine import run_static_scan

ROOT = Path(__file__).resolve().parents[1]
EVAL_FIXTURE = ROOT / "tests" / "fixtures" / "gpt_review_eval"
VULNERABLE_FIXTURE = ROOT / "tests" / "fixtures" / "vulnerable_server"
CASSETTES = ROOT / "src" / "sentinel" / "_cassettes"
DEFAULT_ABLATION = ROOT / "artifacts" / "gpt-ablation.json"
DEFAULT_SARIF = ROOT / "artifacts" / "example.sarif"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--max-usd", type=float)
    parser.add_argument("--ablation-output", type=Path, default=DEFAULT_ABLATION)
    parser.add_argument("--sarif-output", type=Path, default=DEFAULT_SARIF)
    args = parser.parse_args()
    if args.check and args.live:
        parser.error("--check and --live are mutually exclusive")
    if args.live and (args.max_usd is None or args.max_usd <= 0):
        parser.error("--live requires a positive --max-usd hard ceiling")
    if not args.live and args.max_usd is not None:
        parser.error("--max-usd is valid only with --live")

    if args.check:
        validate_checked_ablation(args.ablation_output)
        validate_checked_sarif(args.sarif_output)
        return 0

    if args.live:
        generate_live_sarif(args.sarif_output, max_usd=cast(float, args.max_usd))
    else:
        generate_ablation(args.ablation_output)
    return 0


def generate_ablation(output: Path) -> None:
    cases = _cases()
    treatments = {
        effort.value: _evaluate(effort, cases)
        for effort in (ReasoningEffort.MEDIUM, ReasoningEffort.LOW)
    }
    payload = {
        "artifact_version": 1,
        "generated_from": "checked-in GPT replay plus isolated Docker campaigns",
        "model": MODEL,
        "pricing": PRICING.model_dump(mode="json"),
        "truth_policy": {
            "ambiguous_excluded_from_binary_metrics": True,
            "ambiguous_reported_as_abstention": True,
            "dynamic_scores_case_specific_root_cause_probe": True,
            "all_four_probes_execute_for_each_eligible_case": True,
        },
        "rules_only": _rules_only(cases),
        "gpt_reviewed": treatments,
        "gpt_plus_dynamic": _dynamic_treatment(cases),
    }
    _atomic_json(output, payload)


def validate_checked_ablation(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError(f"missing GPT ablation artifact: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {"rules_only", "gpt_reviewed", "gpt_plus_dynamic", "pricing"}
    if not isinstance(payload, dict) or not required.issubset(payload):
        raise RuntimeError("GPT ablation artifact is incomplete")
    dynamic = payload["gpt_plus_dynamic"]
    if not isinstance(dynamic, dict) or dynamic.get("quality_gate_passed") is not True:
        raise RuntimeError("GPT dynamic ablation quality gate did not pass")


def _dynamic_treatment(cases: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [case for case in cases if isinstance(case.get("dynamic"), dict)]
    records: list[dict[str, Any]] = []
    reap_orphans()
    for case in eligible:
        records.append(_run_dynamic_case(case))
    true_positives = sum(
        item["expected_vulnerable"] and item["observed_vulnerable"] for item in records
    )
    false_positives = sum(
        not item["expected_vulnerable"] and item["observed_vulnerable"]
        for item in records
    )
    vulnerable = sum(item["expected_vulnerable"] for item in records)
    matches = sum(
        item["expected_vulnerable"] == item["observed_vulnerable"] for item in records
    )
    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "precision": _ratio(true_positives, true_positives + false_positives),
        "recall": _ratio(true_positives, vulnerable),
        "accuracy": _ratio(matches, len(records)),
        "abstentions": sum(case.get("dynamic") is None for case in cases),
        "quality_gate_passed": matches == len(records),
        "cases": records,
    }


def _run_dynamic_case(case: dict[str, Any]) -> dict[str, Any]:
    rule_id = str(case["rule_id"])
    tool_name = str(case["tool"])
    expectation = cast(dict[str, Any], case["dynamic"])
    configuration = load_configuration(
        EVAL_FIXTURE,
        environ={},
        cli_overrides={"rules": (rule_id,)},
    )
    llm = configuration.scanner.llm.model_copy(
        update={"cache_enabled": False, "max_concurrency": 1, "retries": 0}
    )
    configuration = configuration.model_copy(
        update={"scanner": configuration.scanner.model_copy(update={"llm": llm})}
    )
    scan_id = uuid4()
    timestamp = datetime.now(timezone.utc)
    findings = run_static_scan(configuration, scan_id, timestamp=timestamp).findings
    catalog = extract_tool_catalog(EVAL_FIXTURE)
    selected = tuple(
        finding for finding in findings if _tool_name(catalog, finding) == tool_name
    )
    if len(selected) != 1:
        raise RuntimeError(
            f"dynamic truth case {case['id']} resolved {len(selected)} candidates"
        )
    review = SemanticReviewer(
        root=EVAL_FIXTURE,
        config=llm,
        max_findings=1,
        mode="replay",
        cache=ReviewCache(enabled=False),
        cassette_root=CASSETTES / "eval-medium",
    ).review(selected, allow_degraded=False)
    if review.fatal:
        raise RuntimeError(f"dynamic truth case {case['id']} GPT review failed")
    planned = review.findings[0]
    plan = planned.review.probe_plan
    plan_source = "gpt"
    if plan is None:
        plan = _evaluation_probe_plan(catalog, tool_name, str(expectation["probe_id"]))
        plan_source = "fixed_root_cause_evaluation"
        planned = planned.model_copy(
            update={"review": planned.review.model_copy(update={"probe_plan": plan})}
        )
    evaluation_finding = (
        planned.model_copy(update={"status": FindingStatus.CONFIRMED})
        if planned.status is FindingStatus.SUPPRESSED
        else planned
    )
    dynamic = run_dynamic_scan(
        DockerSandbox(configuration, scan_id),
        (evaluation_finding,),
        scan_id=scan_id,
        timestamp=timestamp,
    )
    if set(dynamic.campaign.ordered_probe_ids) != set(DYNAMIC_RULE_IDS):
        raise RuntimeError(f"dynamic truth case {case['id']} skipped a required probe")
    probe_id = str(expectation["probe_id"])
    observed = any(
        finding.rule_id == probe_id and tool_name in finding.location.path
        for finding in dynamic.findings
    )
    return {
        "case": case["id"],
        "probe_id": probe_id,
        "target_tool": tool_name,
        "expected_vulnerable": bool(expectation["expected_vulnerable"]),
        "observed_vulnerable": observed,
        "ordered_probe_ids": list(dynamic.campaign.ordered_probe_ids),
        "gpt_status": planned.status.value,
        "probe_plan_source": plan_source,
        "suppressed_plan_executed_for_evaluation": (
            planned.status is FindingStatus.SUPPRESSED
        ),
    }


def _evaluation_probe_plan(
    catalog: Any, tool_name: str, root_probe_id: str
) -> ProbePlan:
    tool = next((item for item in catalog.tools if item.name == tool_name), None)
    if tool is None:
        raise RuntimeError(f"evaluation tool is absent from catalog: {tool_name}")
    properties = tool.input_schema.get("properties", {})
    if not isinstance(properties, dict) or len(properties) != 1:
        raise RuntimeError(
            f"evaluation tool {tool_name} must declare exactly one logical field"
        )
    field = str(next(iter(properties)))
    order = (
        root_probe_id,
        *(item for item in DYNAMIC_RULE_IDS if item != root_probe_id),
    )
    return ProbePlan(
        ordered_probe_ids=order,
        target_tool=tool_name,
        argument_bindings={
            "SENT-009": {field: OVERSIZED_MARKER},
            "SENT-010": {field: INJECTION_MARKER},
            "SENT-011": {field: WRONG_TYPE_MARKER},
        },
    )


def _tool_name(catalog: Any, finding: Finding) -> str | None:
    location = finding.location
    if location.kind != "file":
        return None
    tool = catalog.for_location(location.path, location.range.start_line)
    return tool.name if tool is not None else None


def generate_live_sarif(output: Path, *, max_usd: float) -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("live Phase 5 artifacts require OPENAI_API_KEY")
    configuration = load_configuration(VULNERABLE_FIXTURE, environ={})
    llm = configuration.scanner.llm.model_copy(
        update={"cache_enabled": False, "max_concurrency": 1, "retries": 0}
    )
    configuration = configuration.model_copy(
        update={"scanner": configuration.scanner.model_copy(update={"llm": llm})}
    )
    transport: RawTransport = _BudgetedLiveTransport(
        api_key=api_key,
        timeout_seconds=llm.timeout_seconds,
        budget_micro_usd=round(max_usd * 1_000_000),
    )
    now = datetime.now(timezone.utc)
    outcome = run_scan(
        configuration,
        ScanContext(
            scan_id=uuid4(),
            started_at=now,
            target=ScanTarget(display_name="vulnerable_server"),
        ),
        completed_at=datetime.now(timezone.utc),
        allow_degraded=False,
        review_mode="live",
        api_key=api_key,
        transport=transport,
    )
    if outcome.exit_code == 3 or not outcome.report.analysis_complete:
        raise RuntimeError("final live demo analysis was incomplete")
    if outcome.report.gpt_review is None or outcome.report.gpt_review.mode != "live":
        raise RuntimeError("final evidence is not a live GPT review")
    rendered = render_sarif(outcome.report)
    validate_sarif_data(json.loads(rendered))
    _atomic_text(output, rendered)
    validate_checked_sarif(output)


def validate_checked_sarif(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError(
            f"missing live SARIF artifact: {path}; run with --live --max-usd 0.50"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_sarif_data(payload)
    run = payload["runs"][0]
    results = run.get("results", [])
    rule_ids = {item.get("ruleId") for item in results}
    if len(results) != 11 or rule_ids != {f"SENT-{item:03d}" for item in range(1, 12)}:
        raise RuntimeError("example SARIF must contain SENT-001 through SENT-011")
    review = run["invocations"][0]["properties"].get("gptReview")
    if not isinstance(review, dict) or review.get("mode") != "live":
        raise RuntimeError("example SARIF must preserve live GPT review telemetry")


class _BudgetedLiveTransport:
    def __init__(
        self, *, api_key: str, timeout_seconds: int, budget_micro_usd: int
    ) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.budget = budget_micro_usd
        self.spent = 0
        self.reserved = 0
        self.lock = threading.Lock()

    async def create(self, request: dict[str, Any]) -> dict[str, Any]:
        reservation = _request_reservation(request)
        with self.lock:
            if self.spent + self.reserved + reservation > self.budget:
                raise RuntimeError("live GPT request exceeds the Phase 5 hard ceiling")
            self.reserved += reservation
        try:
            response = await OpenAITransport(self.api_key, self.timeout_seconds).create(
                request
            )
            actual = _cost(_usage(response))
        finally:
            with self.lock:
                self.reserved -= reservation
        with self.lock:
            self.spent += actual
            if self.spent > self.budget:
                raise RuntimeError("live GPT spend exceeded the Phase 5 hard ceiling")
        return response


def _request_reservation(request: dict[str, Any]) -> int:
    request_text = json.dumps(request, sort_keys=True, separators=(",", ":"))
    try:
        encoding = tiktoken.encoding_for_model(MODEL)
        input_tokens = len(encoding.encode(request_text))
    except KeyError:
        input_tokens = len(request_text.encode("utf-8"))
    output_tokens = int(request["max_output_tokens"])
    return int(
        _cost(TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens))
    )


def _atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
