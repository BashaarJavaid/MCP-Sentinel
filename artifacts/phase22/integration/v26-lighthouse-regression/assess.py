"""Assess the retained stopped regression; never rescan a corpus input."""
import hashlib
import importlib.util
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from scripts.phase22_corpus import frozen, input_files
from sentinel.report.validate_json import validate_report_data
from sentinel.report.validate_sarif import validate_sarif_data

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
ASSETS = OUT.parent / "v25-lighthouse-fix"
HOSTED = OUT / "hosted"
RAW = HOSTED / "artifacts/phase22-lighthouse-regression"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load_module("regression", ASSETS / "evaluate-final.py")
old = load_module("fresh_assessment", OUT.parent / "v24-fresh-v5/assess.py")
proposal = runner.approved()
retained = json.loads((HOSTED / "packet.json").read_text())
assert retained["retention_complete"]
for name, digest in retained["files_sha256"].items():
    assert sha(HOSTED / name) == digest, name
packet = json.loads((RAW / "packet.json").read_text())
assert packet["scanner"] == proposal["scanner"]
assert packet["workflow_revision"] == retained["run"]["headSha"] == "fc3a49a351bf2951751edcf7e9be4fe61659110a"
assert packet["workflow_run"] == "34621524649" and packet["workflow_attempt"] == "1"
assert packet["proposal_sha256"] == sha(ASSETS / "evaluation-proposal-final.json")
assert packet["approval_sha256"] == sha(ASSETS / "evaluation-authorization-final.json")
assert packet["budget_closed"] and not packet["passed"]
assert packet["model_calls"] == 0 and not packet["target_execution"]
for name, digest in packet["files_sha256"].items():
    assert sha(RAW / name) == digest, name
order = [{"batch": b, "input_id": i} for b in proposal["batch_order"] for i in proposal["corpus"]["input_ids"]]
assert len(packet["attempts"]) == 1 and packet["unstarted"] == order[1:]
attempt = packet["attempts"][0]
assert {k: attempt[k] for k in ("batch", "input_id")} == order[0]
assert attempt["state"] == "completed"
runner.prior.completed(attempt["timing"])
assert attempt["timing"]["elapsed_including_cleanup_seconds"] - attempt["timing"]["elapsed_seconds"] <= 15
folder = RAW / attempt["directory"]
result = json.loads((folder / "results.json").read_text())
assert result["scanner"] == proposal["scanner"] and result["model_calls"] == 0 and not result["requests"]
assert result["manifest_sha256"] == proposal["corpus"]["sha256"]
assert result["authorization_sha256"] == packet["approval_sha256"]
assert len(result["outcomes"]) == 1 and result["outcomes"][0]["state"] == "completed"
report_path = folder / attempt["input_id"] / "report.json"
report = json.loads(report_path.read_text())
validate_report_data(report)
validate_sarif_data(json.loads(report_path.with_suffix(".sarif").read_text()))
assert sha(report_path) == result["outcomes"][0]["report_sha256"]
assert report["analysisComplete"] and report["executionSuccessful"] and report["findings"] == []
assert runner.condition(report, proposal["witnesses"][attempt["input_id"]]) == attempt["condition"]
assert attempt["condition"] == {"condition_passed": False, "qualified_candidates": 0, "sink_candidates": 0, "source_assessment_pending": True}
manifest = frozen(approval_path=ASSETS / "evaluation-authorization-final.json")
item = next(i for i in manifest.inputs if i.id == attempt["input_id"])
snapshot = next(s for s in manifest.snapshots if s.revision == item.snapshot)
sources = input_files(item, snapshot, ROOT)
source = sources["src/index.ts"]
assert hashlib.sha256(source).hexdigest() == proposal["witnesses"][item.id]["source_sha256"]
lines = source.decode().splitlines()
reviews = dict(old.REVIEWS)
reviews["console"] = ("console.error", "The source uses the ordinary console object for error/startup logging and passes console.error as a catch callback. An unresolved builtin binding is not an SSRF finding or evidence of failed runtime startup.")
scope = "Constructor eligibility scans descendant Return nodes without excluding nested function/class scopes. The concise onerror callback at line103 is not a constructor return. A synthetic equivalent reproduces the false class rejection at6db3858. This is a source-supported diagnosis, not a counterfactual corpus run or proof that this correction alone restores detection."
diagnostics = []
for index, warning in enumerate(report["warnings"]):
    if warning["code"] == "static_flow_unresolved":
        assert "unsupported class inheritance, decorators or members" in warning["message"]
        locations, assessment = [84, 103], scope
    else:
        assert warning["code"] == "static_binding_unresolved"
        binding = warning["message"].split("binding '", 1)[1].removesuffix("'")
        pattern, assessment = reviews[binding]
        locations = [n for n, line in enumerate(lines, 1) if pattern in line]
        assert locations, binding
    diagnostics.append({"kind": "warning", "index": index, "diagnostic": warning, "source_path": "src/index.ts", "source_sha256": hashlib.sha256(source).hexdigest(), "source_lines": locations, "assessment": assessment, "disposition": "Retained source-assessed diagnostic; not runtime proof or a finding."})
coverage = report["static_analysis"]["coverage"]
assert coverage["surfaces"] == [] and coverage["total_possible_surfaces"] is None
for index, flow in enumerate(coverage["unresolved_flows"]):
    assert flow["location"]["path"] == "src/index.ts" and flow["location"]["range"]["start_line"] == 84
    assert "unsupported class inheritance, decorators or members" in flow["message"]
    diagnostics.append({"kind": "unresolved_flow", "index": index, "diagnostic": flow, "source_path": "src/index.ts", "source_sha256": hashlib.sha256(source).hexdigest(), "source_lines": [84, 103], "assessment": scope, "disposition": "Retained duplicate shared-flow diagnostic; no inferred complete handler coverage."})
assert len(report["warnings"]) == 21 and len(coverage["unresolved_flows"]) == 6 and len(diagnostics) == 27
with zipfile.ZipFile(HOSTED / "logs.zip") as archive:
    checkout_logs = [archive.read(n).decode() for n in archive.namelist() if "Check out" in n and "Post" not in n]
    assert any(packet["workflow_revision"] in text for text in checkout_logs)
    assert any(proposal["scanner"]["revision"] in text for text in checkout_logs)
assert retained["run"]["conclusion"] == "failure"
assert [j["name"] for j in retained["run"]["jobs"] if j["conclusion"] == "failure"] == ["Approved Phase 22 exposed Lighthouse regression"]
assert all(j["conclusion"] in {"failure", "skipped"} for j in retained["run"]["jobs"])
path = OUT / "diagnostic-source-assessment.json"
assert not path.exists()
path.write_text(json.dumps({"rows": diagnostics, "warnings": 21, "unresolved_flow_occurrences": 6, "unassessed": 0, "findings": 0}, indent=2) + "\n")
assessment = {
    "recorded_at": datetime.now(timezone.utc).isoformat(),
    "run": 34621524649,
    "workflow": packet["workflow_revision"],
    "scanner": packet["scanner"],
    "execution_checks_passed_for_attempted_input": True,
    "condition_gate_passed": False,
    "source_assessment_complete": True,
    "budget": {"dispatches_consumed": 1, "native_attempted": 1, "native_completed": 1, "native_unstarted_closed": 9, "remaining": 0, "closed": True, "retries": 0, "comparators": 0, "profiles": 0, "paid_calls": 0, "target_execution": False},
    "observed_vulnerable_condition_hits": 0,
    "observed_vulnerable_inputs": 1,
    "fixed_or_control_inputs_observed": 0,
    "ordered_repeats_observed": 0,
    "whole_input_seconds": attempt["timing"]["elapsed_seconds"],
    "native_seconds": attempt["native_seconds"],
    "timing_class": attempt["timing_class"],
    "cleanup_verified": True,
    "source_gap_assessment": scope,
    "warnings": 21,
    "unresolved_flow_occurrences": 6,
    "tool_coverage": "Zero discovered surfaces; total possible surfaces unknown. 11 rules evaluated and SENT-001 skipped without permissions; completion is not coverage or protection.",
    "product_implication": "The requested correction is not yet demonstrated on the actual Lighthouse case. The first completed exposed observation still misses; fixed/control discrimination and repeat stability were not measured because the exact stop closed all nine unstarted observations.",
    "first_frozen_result": "Original1f3f72f fresh result remains15 completed and0/2 vulnerable hits per native batch and comparator. This later failed exposed regression does not replace it.",
    "references_sha256": {str(p.relative_to(OUT.parent)): sha(p) for p in [ASSETS / "evaluation-proposal-final.json", ASSETS / "evaluation-authorization-final.json", OUT / "binding.json", OUT / "dispatch-consumed.json", HOSTED / "packet.json", RAW / "packet.json", path, OUT / "constructor-scope-complete-before.log"]},
    "measured_scanner_source_sha256": {name: hashlib.sha256(subprocess.check_output(["git", "show", proposal["scanner"]["revision"] + ":" + name], cwd=ROOT)).hexdigest() for name in ["src/sentinel/static/typescript_discovery.py", "src/sentinel/static/typescript_path_flow.py"]},
    "technical_acceptance_received": False,
    "phase22_complete": False,
}
path = OUT / "assessment.json"
assert not path.exists()
path.write_text(json.dumps(assessment, indent=2) + "\n")
print("Validated1 completed miss;9 unstarted closed;27 diagnostics source-assessed;0 paid calls.")
