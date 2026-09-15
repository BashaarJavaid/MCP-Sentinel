"""Proposed12-observation first-frozen two-repository sequence; no execution without a new approval."""

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
    "prior", ASSETS.parent / "v43-four-fresh-preparation/runner.py"
)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
supervisor = prior.supervisor
sha, write = supervisor.sha, supervisor.write


def verify():
    proposal = json.loads(PROPOSAL.read_text())
    for name, digest in proposal["files_sha256"].items():
        assert sha(ROOT / name) == digest, name
    assert proposal["bounds"]["native_observations"] == len(proposal["order"]) == 12
    assert len({(x["group"], x["input_id"]) for x in proposal["order"]}) == 6
    assert len(proposal["volatile_exclusions"]) == 11
    assert set(proposal["volatile_exclusions"]) == prior.EXCLUDED
    return proposal


def approved():
    proposal = verify()
    receipt = json.loads(APPROVAL.read_text())
    assert receipt["approved"] is True and receipt["user_decision"].strip()
    assert receipt["proposal_sha256"] == sha(PROPOSAL)
    assert receipt["scanner"] == proposal["scanner"]
    assert receipt["bounds"] == proposal["bounds"]
    assert receipt["order"] == proposal["order"]
    assert receipt["rubric_sha256"] == sha(ASSETS / "scoring-rubric.json")
    assert receipt["precuration_freeze_sha256"] == sha(ASSETS / "scope-and-precuration-freeze.json")
    source_receipt = json.loads((ASSETS / "source-freeze-authorization.json").read_text())
    assert source_receipt["parent_authorization_sha256"] == sha(APPROVAL)
    assert source_receipt["corpus"] == {"manifest": proposal["manifest"]["path"], "sha256": proposal["manifest"]["sha256"], "freeze_approved": True, "input_ids": proposal["input_order"], "treatments": ["rules"]}

    assert not subprocess.check_output(["git", "diff", "HEAD", "--", "src", "scripts", "uv.lock", "pyproject.toml"])
    assert Path.cwd().resolve() == Path(proposal["frozen_checkout"]).resolve()
    return proposal


def identity(group):
    from scripts.phase20_measurements import scanner_identity
    from unseen_corpus import frozen
    from sentinel.static.engine import STATIC_TIMEOUT_SECONDS
    from sentinel.static.semgrep_adapter import SEMGREP_TIMEOUT_SECONDS

    proposal = approved()
    assert scanner_identity() == proposal["scanner"]
    assert sha(Path.cwd() / "uv.lock") == proposal["lock_sha256"]
    assert STATIC_TIMEOUT_SECONDS == 1800 and SEMGREP_TIMEOUT_SECONDS == 10
    g = proposal["groups"][group]
    assert sha(Path.cwd() / g["manifest"]) == g["manifest_sha256"]
    manifest = frozen(approval_path=ASSETS / "source-freeze-authorization.json")
    selected = [i for i in manifest.inputs if i.id in g["input_ids"]]
    assert [i.id for i in selected] == g["input_ids"]
    assert all(i.model_dump(mode="json") == g["inputs"][i.id]["input"] for i in selected)
    return proposal, manifest, selected


def condition(report, witness):
    matches = [f for f in report["findings"] if f["rule_id"] == witness["rule_id"] and f.get("location", {}).get("path") == witness["path"] and f.get("location", {}).get("range", {}).get("start_line") == witness["sink_line"]]
    return {"source_assessment_pending": True, "condition_passed": None,
            "provisional_sink_candidates": len(matches),
            "qualification": "Rule/path/line candidates only. Full source assessment must establish named caller, boundary, sink and supported negatives."}


def child(group, input_id, out):
    from scripts import phase20_measurements as harness
    from sentinel.llm.semantic_reviewer import OpenAITransport
    from sentinel.report.validate_json import validate_report_data
    from sentinel.report.validate_sarif import validate_sarif_data

    async def forbidden(*_, **__):
        raise AssertionError("Live model transport forbidden")

    OpenAITransport.create = forbidden
    proposal, manifest, selected = identity(group)
    consumed = json.loads((ASSETS / "execution-consumed.json").read_text())
    assert consumed["proposal_sha256"] == sha(PROPOSAL)
    parent = json.loads((Path(consumed["output"]) / "packet.json").read_text())
    assert not parent.get("budget_closed", False)
    active = parent["attempts"][-1]
    assert active["group"] == group and active["input_id"] == input_id and active["state"] == "attempted"
    assert out.resolve() == (Path(consumed["output"]) / active["directory"]).resolve()
    item = next(i for i in selected if i.id == input_id)
    g = proposal["groups"][group]
    expected = g["inputs"][input_id]
    original = harness.load_configuration

    def checked(*args, **kwargs):
        config = original(*args, **kwargs)
        assert config.static_only and config.scanner.scanner.rules_only
        assert prior.configuration(config) == expected["configuration_sha256"]
        return config

    from sentinel.static import engine, workers, path_flow, typescript_path_flow, semgrep_adapter
    modules = (engine, workers, path_flow, typescript_path_flow, semgrep_adapter)
    imports = {module.__name__: str(module.__file__) for module in modules}
    assert all(Path(path).is_relative_to(Path(proposal["frozen_checkout"]) / "src") for path in imports.values())
    assert engine.STATIC_TIMEOUT_SECONDS == 1800 and semgrep_adapter.SEMGREP_TIMEOUT_SECONDS == 10
    write(out.with_name(out.name + "-runtime-binding.json"), {
        "scanner": proposal["scanner"], "imports": imports,
        "configuration_sha256": expected["configuration_sha256"],
        "normal_static_deadline_seconds": 1800, "semgrep_rule_timeout_seconds": 10,
        "maximum_existing_flow_workers_per_input": 4, "runtime_policy_override": False,
        "verified_before_target_access": True,
    })

    from unseen_corpus import frozen
    with patch.object(harness, "load_configuration", checked), patch.object(harness, "frozen_phase22", frozen):
        result = harness.measure(
            manifest.model_copy(update={"inputs": [item]}),
            "rules",
            out,
            phase22_approval=ASSETS / "source-freeze-authorization.json",
        )
    assert result["scanner"] == proposal["scanner"]
    assert result["manifest_sha256"] == g["manifest_sha256"]
    if g["source_freeze_approval"]:
        assert result["authorization_sha256"] == sha(ASSETS / "source-freeze-authorization.json")
    assert result["model_calls"] == 0 and not result["requests"]
    assert (
        len(result["outcomes"]) == 1 and result["outcomes"][0]["state"] == "completed"
    )
    report_path = out / input_id / "report.json"
    report = json.loads(report_path.read_text())
    validate_report_data(report)
    validate_sarif_data(json.loads(report_path.with_suffix(".sarif").read_text()))
    assert report["analysisComplete"] and report["executionSuccessful"]
    assert report["static_analysis"]["duration_ms"] <= 1800000
    assert sha(report_path) == result["outcomes"][0]["report_sha256"]
    assert sha(report_path.parent / "configuration.json") == expected["configuration_sha256"]
    judgement = condition(report, proposal["witnesses"][input_id])
    write(out / "condition.json", judgement)
    assert harness.scanner_identity() == proposal["scanner"]


def completed(timing):
    assert timing["returncode"] == 0 and not timing["timed_out"]
    assert timing["cleanup_verified"] and not timing["remaining_group_killed"]
    assert timing["elapsed_seconds"] <= 1800
    assert timing["elapsed_including_cleanup_seconds"] - timing["elapsed_seconds"] <= 15


def run(out):
    proposal = approved()
    order = proposal["order"]
    sequence_start = time.monotonic()
    stop = sequence_start + proposal["bounds"]["internal_stop_minutes"] * 60
    signal.signal(signal.SIGALRM, supervisor.stopped)
    signal.setitimer(signal.ITIMER_REAL, max(0.001, stop - time.monotonic()))
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
            assert time.monotonic() + 1815 < stop, "Insufficient whole-input allowance"
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
            row["timing"] = supervisor.supervise(command, out / (label + ".log"), 1800)
            row["state"] = "incomplete"
            write(out / "packet.json", packet)
            completed(row["timing"])
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
            # All condition and coverage gates require separate source assessment.
            # Collection stops only on execution/identity/schema/timing/cleanup/repeat failure.
            write(out / "packet.json", packet)
            print(json.dumps(row), flush=True)
        assert len(packet["attempts"]) == proposal["bounds"]["native_observations"] == 12 and not packet["unstarted"]
        packet["passed"] = True
        packet["detection_and_coverage_gate_passed"] = None
    except BaseException as error:
        packet["stop_reason"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        packet["elapsed_sequence_seconds"] = time.monotonic() - sequence_start
        packet["remaining_observation_budget"] = 0
        packet["budget_closed"] = True
        packet["darwin_process_group_checks"] = prior.DARWIN_GROUP_CHECKS
        packet["files_sha256"] = {
            p.relative_to(out).as_posix(): sha(p)
            for p in sorted(out.rglob("*"))
            if p.is_file() and p != out / "packet.json"
        }
        write(out / "packet.json", packet)


def selfcheck():
    prior.selfcheck()
    witness = {"rule_id": "SENT-002", "path": "synthetic.ts", "sink_line": 2}
    hit = {"rule_id": "SENT-002", "location": {"path": "synthetic.ts", "range": {"start_line": 2}}}
    assert condition({"findings": [hit]}, witness)["provisional_sink_candidates"] == 1
    assert condition({"findings": []}, witness)["condition_passed"] is None
    assert condition({"findings": [{**hit, "rule_id": "SENT-012"}]}, witness)["provisional_sink_candidates"] == 0


if __name__ == "__main__":
    for name in list(os.environ):
        if name.startswith(("OPENAI_", "SENTINEL_")):
            os.environ.pop(name)
    sys.path[:0] = [str(Path.cwd() / "src"), str(Path.cwd())]
    schema_spec = importlib.util.spec_from_file_location("unseen_corpus", ASSETS / "corpus.py")
    schema = importlib.util.module_from_spec(schema_spec)
    sys.modules["unseen_corpus"] = schema
    schema_spec.loader.exec_module(schema)
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
