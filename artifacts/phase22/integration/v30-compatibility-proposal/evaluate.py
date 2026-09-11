"""Exact54-observation local compatibility sequence; no execution without a new approval."""

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
PROPOSAL = ASSETS / "evaluation-proposal.json"
APPROVAL = ASSETS / "evaluation-authorization.json"
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
    assert receipt["order"] == proposal["order"]
    return proposal


def identity(group):
    from scripts.phase20_measurements import scanner_identity
    from scripts.phase20_corpus import validate
    from scripts.phase22_corpus import frozen
    from sentinel.static.engine import STATIC_TIMEOUT_SECONDS

    proposal = approved()
    assert scanner_identity() == proposal["scanner"]
    assert sha(Path.cwd() / "uv.lock") == proposal["lock_sha256"]
    assert STATIC_TIMEOUT_SECONDS == 300
    g = proposal["groups"][group]
    assert sha(Path.cwd() / g["manifest"]) == g["manifest_sha256"]
    manifest = validate() if group == "historical" else frozen(approval_path=Path.cwd() / g["source_freeze_approval"])
    selected = [i for i in manifest.inputs if i.id in g["input_ids"]]
    assert [i.id for i in selected] == g["input_ids"]
    assert all(i.model_dump(mode="json") == g["inputs"][i.id]["input"] for i in selected)
    return proposal, manifest, selected


def condition(report, reference, assessment, label, excluded):
    from scripts.phase20_scoring import score

    same = supervisor.clean(report["findings"], excluded) == supervisor.clean(reference["findings"], excluded)
    if not same:
        return {"condition_passed": False, "ordered_findings_equal": False, "source_assessment_pending": True}
    row = score(label=label, state="completed", findings=report["findings"], assessment=assessment)
    return {**row, "condition_passed": row["candidate_detected"] if label == "vulnerable" else row["false_alarm"] is False, "ordered_findings_equal": True, "source_assessment_pending": True}


def child(group, input_id, out):
    from scripts import phase20_measurements as harness
    from sentinel.llm.semantic_reviewer import OpenAITransport
    from sentinel.report.validate_json import validate_report_data
    from sentinel.report.validate_sarif import validate_sarif_data

    async def forbidden(*_, **__):
        raise AssertionError("Live model transport forbidden")

    OpenAITransport.create = forbidden
    proposal, manifest, selected = identity(group)
    item = next(i for i in selected if i.id == input_id)
    g = proposal["groups"][group]
    expected = g["inputs"][input_id]
    original = harness.load_configuration

    def checked(*args, **kwargs):
        config = original(*args, **kwargs)
        assert config.static_only and config.scanner.scanner.rules_only
        assert prior.configuration(config) == expected["configuration_sha256"]
        return config

    with patch.object(harness, "load_configuration", checked):
        result = harness.measure(
            manifest.model_copy(update={"inputs": [item]}),
            "rules",
            out,
            phase22_approval=Path.cwd() / g["source_freeze_approval"] if g["source_freeze_approval"] else None,
        )
    assert result["scanner"] == proposal["scanner"]
    assert result["manifest_sha256"] == g["manifest_sha256"]
    if g["source_freeze_approval"]:
        assert result["authorization_sha256"] == sha(Path.cwd() / g["source_freeze_approval"])
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
    assert sha(report_path.parent / "configuration.json") == expected["configuration_sha256"]
    judgement = condition(report, json.loads((ROOT / expected["reference_report"]).read_text()), expected["assessment"], item.label, set(proposal["volatile_exclusions"]))
    write(out / "condition.json", judgement)
    assert harness.scanner_identity() == proposal["scanner"]


def run(out):
    proposal = approved()
    order = proposal["order"]
    stop = time.monotonic() + proposal["bounds"]["sequence_maximum_minutes"] * 60
    packet = {
        "scanner": proposal["scanner"],
        "proposal_sha256": sha(PROPOSAL),
        "approval_sha256": sha(APPROVAL),
        "execution": "single local serial sequence",
        "runner_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": sys.version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "cpu_topology": subprocess.check_output(["sysctl", "hw.ncpu", "hw.memsize"], text=True),
        "attempts": [],
        "unstarted": order,
        "passed": False,
        "model_calls": 0,
        "target_execution": False,
        "source_assessment_pending": True,
    }
    write(out / "packet.json", packet)
    try:
        assert sys.platform == "darwin"
        assert not (ASSETS / "execution-consumed.json").exists(), "Sequence budget already consumed"
        with (ASSETS / "execution-consumed.json").open("x") as receipt:
            json.dump({"proposal_sha256": sha(PROPOSAL), "approval_sha256": sha(APPROVAL), "output": str(out), "budget_consumed": True}, receipt)
        supervisor.selfcheck(out)
        selfcheck()
        previous = {}
        for n, observation in enumerate(order):
            assert time.monotonic() + 315 < stop, "Insufficient whole-input allowance"
            identity(observation["group"])
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
                observation["group"],
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
            if observation["batch"] == "repeat":
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
        assert len(packet["attempts"]) == 54 and not packet["unstarted"]
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
    from scripts.phase20_scoring import candidate_identity
    prior.selfcheck()
    f = {"dedup_key": "key", "status": "needs_review", "review": None}
    r = {"findings": [f]}
    a = {"candidate_identity": candidate_identity([f]), "matches": ["key"], "rationale": "Synthetic control"}
    assert condition(r, r, a, "vulnerable", set())["condition_passed"]
    assert not condition(r, r, a, "fixed", set())["condition_passed"]
    assert condition(r, r, {**a, "matches": []}, "fixed", set())["condition_passed"]
    assert not condition({"findings": []}, r, a, "vulnerable", set())["condition_passed"]
    assert not condition({"findings": [{**f, "description": "changed"}]}, r, a, "vulnerable", set())["condition_passed"]


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
        assert mode in {"run", "selfcheck"} and sys.platform == "darwin"
        out = Path(sys.argv[2]).resolve()
        out.mkdir(exist_ok=False)
        if mode == "selfcheck":
            supervisor.selfcheck(out)
            selfcheck()
        else:
            run(out)
