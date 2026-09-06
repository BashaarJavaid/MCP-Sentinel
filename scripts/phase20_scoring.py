"""Condition-level scoring; unmatched warnings never become false positives."""

from __future__ import annotations

import json
from collections import Counter
from typing import Any

from scripts.capture_gpt_reviews import _atomic_json
from scripts.phase20_corpus import Manifest, digest
from scripts.phase20_measurements import ARTIFACTS, frozen
from sentinel.finding import Finding, runtime_evidence

TREATMENTS = ("rules", "replay", "dynamic", "semgrep")


def candidate_identity(findings: list[dict[str, Any]]) -> str:
    return digest(json.dumps(sorted({f["dedup_key"] for f in findings})).encode())


def score(
    *,
    label: str,
    state: str,
    findings: list[dict[str, Any]],
    assessment: dict[str, Any] | None,
) -> dict[str, Any]:
    unique = {f["dedup_key"]: f for f in findings}
    matched: set[str] = set()
    adjudicated = not unique and state == "completed"
    if assessment is not None:
        if assessment["candidate_identity"] != candidate_identity(findings):
            raise ValueError("adjudication candidate identity drift")
        matched = set(assessment["matches"])
        if not matched <= unique.keys() or not assessment["rationale"]:
            raise ValueError("invalid condition adjudication")
        adjudicated = True
    related = [unique[k] for k in matched]
    retained = [
        f
        for f in related
        if f["status"] in {"confirmed", "needs_review"} and not f.get("suppression")
    ]
    confirmed = [f for f in retained if f["status"] == "confirmed"]
    completed = state == "completed"
    return {
        "state": state,
        "candidate_count": len(unique)
        if state not in {"not_evaluated", "unsupported"}
        else None,
        "duplicate_count": len(findings) - len(unique),
        "condition_adjudicated": adjudicated,
        "matched_keys": sorted(matched),
        "unadjudicated_keys": sorted(unique.keys() - matched),
        "candidate_detected": bool(related) if adjudicated else None,
        "retained_detected": bool(retained) if adjudicated else None,
        "confirmed_detected": bool(confirmed) if adjudicated else None,
        "completed_miss": completed
        and adjudicated
        and label == "vulnerable"
        and not related,
        "false_alarm": bool(retained)
        if label != "vulnerable" and adjudicated
        else None,
        "abstentions": sum(
            (f.get("review") or {}).get("status") == "needs_review"
            and (f.get("review") or {}).get("reviewed") is True
            for f in related
        ),
        "incorrect_suppressions": sum(
            (f.get("review") or {}).get("status") == "suppressed"
            and (f.get("review") or {}).get("reviewed") is True
            for f in related
        )
        if label == "vulnerable"
        else 0,
        "runtime_confirmations": sum(
            bool(
                runtime_evidence(
                    Finding.model_validate_json(
                        json.dumps(
                            {
                                k: v
                                for k, v in f.items()
                                if k not in Finding.model_computed_fields
                            }
                        )
                    )
                )
            )
            if "provenance" in f
            else False
            for f in related
        ),
    }


def metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    positive = [r for r in rows if r["label"] == "vulnerable"]
    applicable = [r for r in positive if r["state"] != "unsupported"]
    completed = [
        r
        for r in applicable
        if r["state"] == "completed" and r["condition_adjudicated"]
    ]
    safe = [
        r
        for r in rows
        if r["label"] != "vulnerable"
        and r["state"] == "completed"
        and r["condition_adjudicated"]
    ]
    result: dict[str, Any] = {
        "inputs": len(rows),
        "states": dict(Counter(r["state"] for r in rows)),
        "vulnerable_total": len(positive),
        "vulnerable_applicable": len(applicable),
        "vulnerable_completed_adjudicated": len(completed),
        "safe_completed_adjudicated": len(safe),
        "false_alarm_conditions": sum(bool(r["false_alarm"]) for r in safe),
        "unadjudicated_findings": sum(len(r["unadjudicated_keys"]) for r in rows),
        "abstentions": sum(r["abstentions"] for r in rows),
        "incorrect_suppressions": sum(r["incorrect_suppressions"] for r in rows),
        "runtime_confirmations": sum(r["runtime_confirmations"] for r in rows),
    }
    for name in ("candidate", "retained", "confirmed"):
        observed = sum(bool(r[f"{name}_detected"]) for r in positive)
        detections = sum(bool(r[f"{name}_detected"]) for r in completed)
        result[name] = {
            "observed_detections": observed,
            "total_corpus_observed_fraction": observed / len(positive)
            if positive
            and any(
                r["state"] not in {"not_evaluated", "unsupported"} for r in positive
            )
            else None,
            "completed_recall": detections / len(completed) if completed else None,
            "completed_detections": detections,
        }
    return result


def comparator_findings(raw: dict[str, Any], scan_root: str) -> list[dict[str, Any]]:
    findings = []
    for value in raw.get("results", []):
        path = value["path"]
        if path.startswith(scan_root.rstrip("/") + "/"):
            path = path[len(scan_root.rstrip("/")) + 1 :]
        identity = {
            "rule": value["check_id"],
            "path": path,
            "start": value["start"],
            "end": value["end"],
            "message": value["extra"]["message"],
        }
        findings.append(
            {
                "dedup_key": digest(json.dumps(identity, sort_keys=True).encode()),
                "status": "needs_review",
                "review": None,
                "source": "static",
                "location": identity,
                "description": value["extra"]["message"],
            }
        )
    return findings


def build_results(manifest: Manifest) -> dict[str, Any]:
    approval = frozen()
    assessments_path = ARTIFACTS / "adjudications.json"
    if (
        assessments_path.exists()
        and json.loads(assessments_path.read_text())["manifest_sha256"]
        != approval["manifest_sha256"]
    ):
        raise ValueError("adjudication manifest drift")
    assessments = (
        json.loads(assessments_path.read_text())["assessments"]
        if assessments_path.exists()
        else []
    )
    indexed = {(a["treatment"], a["input_id"]): a for a in assessments}
    if len(indexed) != len(assessments):
        raise ValueError("duplicate adjudication")
    result: dict[str, Any] = {
        "version": 1,
        "phase_status": "in_progress",
        "manifest_sha256": approval["manifest_sha256"],
        "treatments": {},
    }
    result["adjudications_sha256"] = (
        digest(assessments_path.read_bytes()) if assessments_path.exists() else None
    )
    result["environment"] = json.loads(
        (ARTIFACTS / "measurement-environment.json").read_text()
    )
    ledger_path = ARTIFACTS / "captures/ledger.json"
    ledger = (
        json.loads(ledger_path.read_text())
        if ledger_path.exists()
        else {"attempts": [], "decisions": {}}
    )
    result["capture_accounting"] = {
        "attempted_requests": len(ledger["attempts"]),
        "states": dict(Counter(a["state"] for a in ledger["attempts"])),
        "charged_micro_usd": sum(a["charged_micro_usd"] for a in ledger["attempts"]),
        "accepted_usage_cost_micro_usd": sum(
            a["charged_micro_usd"]
            for a in ledger["attempts"]
            if a["state"] == "accepted"
        ),
        "decisions": ledger["decisions"],
    }
    for treatment in TREATMENTS:
        directory = ARTIFACTS / treatment
        if (
            treatment == "dynamic"
            and (ARTIFACTS / "runtime-replay/results.json").exists()
        ):
            directory = ARTIFACTS / "runtime-replay"
        measurement = (
            json.loads((directory / "results.json").read_text())
            if (directory / "results.json").exists()
            else None
        )
        outcomes = (
            {o["input_id"]: o for o in measurement["outcomes"]} if measurement else {}
        )
        if measurement and (
            len(outcomes) != len(measurement["outcomes"])
            or not outcomes.keys() <= {i.id for i in manifest.inputs}
        ):
            raise ValueError("duplicate or unknown measurement input")
        if (
            measurement
            and measurement["manifest_sha256"] != approval["manifest_sha256"]
        ):
            raise ValueError("measurement manifest drift")
        rows = []
        for item in manifest.inputs:
            outcome = outcomes.get(
                item.id, {"state": "not_evaluated", "reason": "measurement pending"}
            )
            findings: list[dict[str, Any]] = []
            report: dict[str, Any] = {}
            if treatment == "dynamic" and item.runtime_applicability != "eligible":
                outcome = {"state": "unsupported", "reason": item.runtime_reason}
            if treatment == "semgrep" and (directory / item.id / "raw.json").exists():
                if outcome.get("raw_sha256") and outcome["raw_sha256"] != digest(
                    (directory / item.id / "raw.json").read_bytes()
                ):
                    raise ValueError("comparator evidence drift")
                try:
                    raw = json.loads((directory / item.id / "raw.json").read_text())
                    command = json.loads(
                        (directory / item.id / "command.json").read_text()
                    )
                    findings = comparator_findings(raw, command["cwd"])
                except json.JSONDecodeError:
                    pass  # Failed execution stays visible; no fabricated empty success.
            elif (directory / item.id / "report.json").exists():
                report_path = directory / item.id / "report.json"
                if outcome.get("report_sha256") != digest(report_path.read_bytes()):
                    raise ValueError("native measurement report drift")
                report = json.loads(report_path.read_text())
                findings = report["findings"]
            row = {
                "input_id": item.id,
                "label": item.label,
                "language": item.language,
                "repository": item.repository,
                "split": item.split,
                "variant": item.variant,
                **score(
                    label=item.label,
                    state=outcome["state"],
                    findings=findings,
                    assessment=indexed.get((treatment, item.id)),
                ),
                "reason": outcome.get("reason"),
                "wall_duration_ms": outcome.get("wall_duration_ms"),
                "coverage": report.get("static_analysis"),
                "dynamic": report.get("dynamic_analysis"),
                "review_activity": report.get("review_activity"),
                "review_usage": report.get("gpt_review"),
            }
            rows.append(row)
        breakdowns = {}
        for dimension in ("split", "variant", "language", "repository"):
            breakdowns[dimension] = {
                value: metrics([r for r in rows if r[dimension] == value])
                for value in sorted({r[dimension] for r in rows})
            }
        result["treatments"][treatment] = {
            "measurement": measurement
            and {
                k: v
                for k, v in measurement.items()
                if k not in {"requests", "outcomes"}
            },
            "outcomes": rows,
            "metrics": metrics(rows),
            "breakdowns": breakdowns,
        }
    _atomic_json(ARTIFACTS / "results.json", result)
    return result


def render_results(result: dict[str, Any]) -> str:
    lines = [
        "# Phase 20 — Independent detection benchmark",
        "",
        "**Partial baseline. Checkpoint 1 is approved; paid review and "
        "runtime gates remain open.**",
        "",
        f"Frozen manifest: `{result['manifest_sha256']}`.",
        "",
        "The 45 condition-labeled inputs comprise ten original "
        "vulnerable/fixed pairs, ten paired structural mutations, and five "
        "safe controls across five repositories. Development and held-out "
        "repositories were separated before evaluation. Correlated variants "
        "are reported separately; public historical cases cannot establish "
        "absence of model exposure.",
        "",
        "| Treatment | Completed / 45 | Incomplete | Unsupported | "
        "Inconclusive | Unmeasured | Vulnerable "
        "completed / 20 | Candidate recall on completed, adjudicated cases | "
        "Unadjudicated findings |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, treatment in result["treatments"].items():
        m = treatment["metrics"]
        recall = m["candidate"]["completed_recall"]
        lines.append(
            f"| {name} | {m['states'].get('completed', 0)} | "
            f"{m['states'].get('incomplete', 0)} | "
            f"{m['states'].get('unsupported', 0)} | "
            f"{m['states'].get('inconclusive', 0)} | "
            f"{m['states'].get('not_evaluated', 0)} | "
            f"{m['vulnerable_completed_adjudicated']} | "
            f"{f'{recall:.1%}' if recall is not None else 'unmeasured'} | "
            f"{m['unadjudicated_findings']} |"
        )
    lines.extend(
        [
            "",
            "## Observed limitations",
            "",
            "Sentinel cannot parse Atlassian's JSON-with-comments devcontainer "
            "configuration under the frozen input configuration: all 13 inputs "
            "remain incomplete. Git's low-level tool dispatch is reported as an "
            "unsupported registration by source coverage; completed rules do "
            "not imply the vulnerable handler flow was covered. The 70 Sentinel "
            "warnings concern generic validation, credentials or authentication "
            "and do not identify the labeled conditions.",
            "",
            "The comparator returned 271 raw alerts. Kubernetes command-injection "
            "warnings concern other handlers, not the labeled kubectl_get flow. "
            "Filesystem audit warnings do not identify failure of the colliding "
            "directory-prefix check. These stay unadjudicated under the frozen "
            "input/enforcement-failure/sink criterion. This is not evidence that "
            "those warnings are useless or false positives. Twelve comparator "
            "runs include a rule timeout and remain incomplete. The initial "
            "certificate-setup failure is retained separately and is not an "
            "accuracy observation. Actual engine rule and file counts are in "
            "the raw evidence; the selected 533 rule identities are not a claim "
            "that every rule ran on every input.",
            "",
            "All 13 eligible Docker runs failed because the native image lacks "
            "the Git executable. No legitimate baseline or attack completed. "
            "The remaining probes are untested; no defense or exploit confirmation "
            "is inferred. The retained runtime review packet has zero requests.",
            "",
            "Paid attempts recorded: "
            f"{result['capture_accounting']['attempted_requests']}. "
            "Review cost is counted once per capture in the ledger, not once per "
            "replayed input. With no captures, completed static replay entries "
            "are zero-candidate stages, not evidence of model accuracy.",
            "",
            "`replay` is the GPT-reviewed static treatment; `dynamic` is the "
            "normal reviewed pipeline. Original live latency is retained in "
            "native review telemetry; replay wall duration is separate. "
            "Runtime has 13 eligible Python Git inputs and 32 unsupported "
            "inputs. Eligibility does not imply successful probing.",
            "",
            "Candidate, retained (including `needs_review`), and "
            "confirmed-only recall, false alarms on labeled safe conditions, "
            "abstentions, incorrect suppressions, coverage, and all "
            "split/language/repository/variant breakdowns are in the "
            "generated JSON. Total-corpus observed fractions include "
            "unfinished inputs in their denominator and are not "
            "completed-treatment recall. Zero denominators are null. "
            "Unmatched findings remain unadjudicated; whole-repository "
            "precision is not claimed.",
            "",
            "## Reproduction",
            "",
            "```sh",
            "python -m scripts.run_phase20_benchmark validate",
            "python -m scripts.run_phase20_benchmark rules --output "
            "/tmp/phase20-rules-repeat",
            "python -m scripts.run_phase20_benchmark prepare-live --output "
            "/tmp/phase20-requests-repeat",
            "python -m scripts.run_phase20_benchmark replay --output "
            "/tmp/phase20-replay-repeat",
            "python -m scripts.run_phase20_benchmark semgrep --rules-dir "
            "/tmp/phase20-community-rules --output "
            "/tmp/phase20-comparator-repeat",
            "python -m scripts.run_phase20_benchmark report",
            "```",
            "",
            "Install the locked development environment first (`uv sync "
            "--frozen --extra dev`). Obtain the exact private community-rule "
            "snapshot using the Checkpoint 1 packet; do not commit rule "
            "bytes. Measurement commands refuse to overwrite evidence. "
            "Repeated static execution is reproducibility verification, not "
            "an additional accuracy observation. Full native JSON 1.6.0 and "
            "SARIF 2.1.0 reports are retained per input; failures without "
            "native reports remain in `results.json`.",
            "",
            "`prepare-live` runs the production request builder offline, "
            "serially, with GPT-5.6 Sol medium, retries disabled, cache "
            "disabled, and the 500-finding default. It never reads an API "
            "key. `capture-live --stage static --approval <file>` requires a "
            "separately approved packet hash and cumulative request/dollar "
            "ceilings. Runtime capture uses `--stage runtime` and a separate "
            "Checkpoint 3 decision. `dynamic` requires completed eligible "
            "static replay and uses native Docker isolation. It preserves "
            "runtime proof and prepares new runtime review requests offline.",
            "",
            "Phase 20 remains open until all evidence gates pass. Detectors, "
            "prompts and probes have not been tuned. Historical "
            "ablation/walkthrough artifacts and native scanner contracts are "
            "unchanged. Draft PR merge, public deployment and final "
            "acceptance still require explicit approval.",
            "",
        ]
    )
    return "\n".join(lines)
