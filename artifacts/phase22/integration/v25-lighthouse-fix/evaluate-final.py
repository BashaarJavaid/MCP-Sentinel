"""Exact exposed Lighthouse regression; no execution without a new approval."""

import ctypes
import importlib.util
import json
import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

ASSETS = Path(__file__).resolve().parent
ROOT = ASSETS.parents[3]
PROPOSAL = ASSETS / "evaluation-proposal-final.json"
APPROVAL = ASSETS / "evaluation-authorization-final.json"
spec = importlib.util.spec_from_file_location(
    "prior", ASSETS.parent / "v23-fresh-v5/runner.py"
)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
supervisor = prior.supervisor
sha, write = supervisor.sha, supervisor.write


def verify():
    proposal = json.loads(PROPOSAL.read_text())
    for name, digest in proposal["files_sha256"].items():
        assert sha(ROOT / name) == digest, name
    return proposal


def approved():
    proposal = verify()
    receipt = json.loads(APPROVAL.read_text())
    assert receipt["approved"] is True and receipt["user_decision"].strip()
    assert receipt["proposal_sha256"] == sha(PROPOSAL)
    assert receipt["scanner"] == proposal["scanner"]
    assert receipt["bounds"] == proposal["bounds"]
    assert receipt["corpus"] == {**proposal["corpus"], "freeze_approved": True}
    return proposal


def identity():
    from scripts.phase20_measurements import scanner_identity
    from scripts.phase22_corpus import frozen
    from sentinel.static.engine import STATIC_TIMEOUT_SECONDS

    proposal = approved()
    assert scanner_identity() == proposal["scanner"]
    assert sha(Path.cwd() / "uv.lock") == proposal["lock_sha256"]
    assert STATIC_TIMEOUT_SECONDS == 300
    manifest = frozen(approval_path=APPROVAL)
    selected = [i for i in manifest.inputs if i.id in proposal["corpus"]["input_ids"]]
    assert [i.id for i in selected] == proposal["corpus"]["input_ids"]
    return proposal, manifest, selected


def condition(report, witness):
    matches = [
        f
        for f in report["findings"]
        if f["rule_id"] == "SENT-015"
        and f["location"]["path"] == witness["path"]
        and f["location"]["range"]["start_line"] == witness["sink_line"]
    ]
    qualified = [
        f
        for f in matches
        if f["description"].startswith(
            "The source rejects literal link-local IPv4 destinations for this "
            "caller URL before the request."
        )
    ]
    return {
        "sink_candidates": len(matches),
        "qualified_candidates": len(qualified),
        "condition_passed": bool(matches)
        and (
            not qualified
            if witness["label"] == "vulnerable"
            else len(qualified) == len(matches)
        ),
        "source_assessment_pending": True,
    }


def child(batch, input_id, out):
    from scripts import phase20_measurements as harness
    from sentinel.llm.semantic_reviewer import OpenAITransport
    from sentinel.report.validate_json import validate_report_data
    from sentinel.report.validate_sarif import validate_sarif_data

    async def forbidden(*_, **__):
        raise AssertionError("Live model transport forbidden")

    OpenAITransport.create = forbidden
    proposal, manifest, selected = identity()
    assert batch in proposal["batch_order"]
    item = next(i for i in selected if i.id == input_id)
    configs = json.loads((ROOT / proposal["configuration_path"]).read_text())
    original = harness.load_configuration

    def checked(*args, **kwargs):
        config = original(*args, **kwargs)
        assert config.static_only and config.scanner.scanner.rules_only
        assert prior.configuration(config) == configs[input_id]["sha256"]
        return config

    with patch.object(harness, "load_configuration", checked):
        result = harness.measure(
            manifest.model_copy(update={"inputs": [item]}),
            "rules",
            out,
            phase22_approval=APPROVAL,
        )
    assert result["scanner"] == proposal["scanner"]
    assert result["manifest_sha256"] == proposal["corpus"]["sha256"]
    assert result["authorization_sha256"] == sha(APPROVAL)
    assert result["model_calls"] == 0 and not result["requests"]
    assert (
        len(result["outcomes"]) == 1 and result["outcomes"][0]["state"] == "completed"
    )
    report_path = out / input_id / "report.json"
    report = json.loads(report_path.read_text())
    validate_report_data(report)
    validate_sarif_data(json.loads(report_path.with_suffix(".sarif").read_text()))
    assert report["analysisComplete"] and report["executionSuccessful"]
    assert report["static_analysis"]["duration_ms"] <= 300000
    assert sha(report_path) == result["outcomes"][0]["report_sha256"]
    assert sha(report_path.parent / "configuration.json") == configs[input_id]["sha256"]
    judgement = condition(report, proposal["witnesses"][input_id])
    write(out / "condition.json", judgement)
    assert harness.scanner_identity() == proposal["scanner"]


def run(out, deadline_file):
    proposal = approved()
    order = [
        {"batch": b, "input_id": i}
        for b in proposal["batch_order"]
        for i in proposal["corpus"]["input_ids"]
    ]
    packet = {
        "scanner": proposal["scanner"],
        "proposal_sha256": sha(PROPOSAL),
        "approval_sha256": sha(APPROVAL),
        "workflow_run": os.environ["GITHUB_RUN_ID"],
        "workflow_revision": os.environ["GITHUB_SHA"],
        "workflow_attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "python": sys.version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "memory": Path("/proc/meminfo").read_text(),
        "cpu_topology": subprocess.check_output(["lscpu"], text=True),
        "attempts": [],
        "unstarted": order,
        "passed": False,
        "model_calls": 0,
        "target_execution": False,
        "source_assessment_pending": True,
    }
    write(out / "packet.json", packet)
    try:
        assert packet["workflow_attempt"] == "1", "Reruns forbidden"
        supervisor.selfcheck(out)
        selfcheck()
        stop = float(deadline_file.read_text())
        previous = {}
        for n, observation in enumerate(order):
            assert time.monotonic() + 315 < stop, "Insufficient whole-input allowance"
            identity()
            assert time.monotonic() + 315 < stop, "Insufficient whole-input allowance"
            label = f"{n + 1:02d}-{observation['batch']}-{observation['input_id']}"
            row = {**observation, "directory": label, "state": "attempted"}
            packet["attempts"].append(row)
            packet["unstarted"] = order[n + 1 :]
            command = [
                sys.executable,
                "-I",
                str(Path(__file__).resolve()),
                "child",
                observation["batch"],
                observation["input_id"],
                str(out / label),
            ]
            row["command"] = command
            write(out / "packet.json", packet)
            print("START", label, flush=True)
            row["timing"] = supervisor.supervise(command, out / (label + ".log"), 300)
            row["state"] = "incomplete"
            write(out / "packet.json", packet)
            prior.completed(row["timing"])
            report = json.loads(
                (out / label / observation["input_id"] / "report.json").read_text()
            )
            row["native_seconds"] = report["static_analysis"]["duration_ms"] / 1000
            row["state"] = "completed"
            row["timing_class"] = (
                "completed_within_target"
                if max(row["native_seconds"], row["timing"]["elapsed_seconds"]) <= 120
                else "completed_using_extended_time"
            )
            canonical = supervisor.clean(report, prior.EXCLUDED)
            if observation["batch"] == "rules-repeat":
                row["ordered_repeat_equal"] = (
                    previous[observation["input_id"]] == canonical
                )
                assert row["ordered_repeat_equal"], "Entire ordered report mismatch"
            else:
                previous[observation["input_id"]] = canonical
            row["condition"] = json.loads((out / label / "condition.json").read_text())
            assert row["condition"]["condition_passed"], (
                "Named-condition discrimination gate failed"
            )
            write(out / "packet.json", packet)
            print(json.dumps(row), flush=True)
        assert len(packet["attempts"]) == 10 and not packet["unstarted"]
        packet["passed"] = True
    except BaseException as error:
        packet["stop_reason"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        packet["budget_closed"] = True
        packet["files_sha256"] = {
            p.relative_to(out).as_posix(): sha(p)
            for p in sorted(out.rglob("*"))
            if p.is_file() and p != out / "packet.json"
        }
        write(out / "packet.json", packet)


def selfcheck():
    prior.selfcheck()
    candidate = {
        "rule_id": "SENT-015",
        "location": {"path": "unit.ts", "range": {"start_line": 7}},
        "description": "Candidate",
    }
    witness = {"path": "unit.ts", "sink_line": 7, "label": "vulnerable"}
    assert condition({"findings": [candidate]}, witness)["condition_passed"]
    assert not condition({"findings": []}, witness)["condition_passed"]
    assert not condition({"findings": [candidate]}, {**witness, "sink_line": 8})[
        "condition_passed"
    ]
    fixed = {**witness, "label": "fixed"}
    assert not condition({"findings": [candidate]}, fixed)["condition_passed"]
    guarded = {
        **candidate,
        "description": "The source rejects literal link-local IPv4 destinations "
        "for this caller URL before the request. Broader protection unestablished.",
    }
    assert condition({"findings": [guarded]}, fixed)["condition_passed"]
    assert not condition({"findings": [guarded]}, witness)["condition_passed"]
    assert not condition({"findings": [guarded, candidate]}, fixed)["condition_passed"]


if __name__ == "__main__":
    for name in list(os.environ):
        if name.startswith(("OPENAI_", "SENTINEL_")):
            os.environ.pop(name)
    sys.path[:0] = [str(Path.cwd() / "src"), str(Path.cwd())]
    signal.signal(signal.SIGTERM, supervisor.stopped)
    mode = sys.argv[1]
    if mode == "check":
        verify()
        selfcheck()
        print("Source-only proposal and boundary checks pass; zero observations.")
    elif mode == "child":
        child(sys.argv[2], sys.argv[3], Path(sys.argv[4]))
    else:
        assert mode in {"run", "selfcheck"} and sys.platform == "linux"
        assert ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) == 0
        out = Path(sys.argv[2]).resolve()
        out.mkdir(exist_ok=False)
        if mode == "selfcheck":
            supervisor.selfcheck(out)
            selfcheck()
        else:
            run(out, Path(sys.argv[3]))
