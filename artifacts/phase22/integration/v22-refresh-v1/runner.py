"""Approved historical assessment refresh; scanner bytes stay frozen."""

import ctypes
import hashlib
import importlib.metadata
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
BASE = ASSETS.parent
PROPOSAL = BASE / "v21-historical-assessment-refresh-proposal.json"
APPROVAL = BASE / "v22-refresh-authorization.json"
spec = importlib.util.spec_from_file_location(
    "supervisor", BASE / "v20-linux-diagnostic-v1/runner.py"
)
supervisor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supervisor)
sha, write, clean = supervisor.sha, supervisor.write, supervisor.clean


def approved():
    proposal = json.loads(PROPOSAL.read_text())
    approval = json.loads(APPROVAL.read_text())
    assert approval["approved"] and approval["proposal_sha256"] == sha(PROPOSAL)
    assert approval["bounds"] == proposal["bounds"]
    assert (
        sha(BASE.parents[2] / proposal["configurations"]["path"])
        == proposal["configurations"]["sha256"]
    )
    return proposal


def corpus(kind, proposal):
    assert kind in {"preparatory", "historical_first", "historical_second"}
    from scripts.phase20_corpus import validate
    from scripts.phase20_measurements import frozen as historical_freeze
    from scripts.phase22_corpus import frozen

    key = "development" if kind == "development" else "historical"
    expected = proposal["manifests"][key]
    assert sha(Path.cwd() / expected["path"]) == expected["sha256"]
    if key == "development":
        assert (
            sha(Path("artifacts/phase22/authorization.json"))
            == expected["authorization_sha256"]
        )
        manifest = frozen()
    else:
        assert historical_freeze() == expected["freeze_receipt"]
        manifest = validate()
    selected = [i for i in manifest.inputs if i.id in expected["input_ids"]]
    assert [i.model_dump(mode="json") for i in selected] == expected["inputs"]
    if kind == "preparatory":
        selected = [i for i in selected if i.id in proposal["preparatory_input_order"]]
        assert [i.id for i in selected] == proposal["preparatory_input_order"]
    return manifest, selected


def configuration(config):
    payload = {
        "scanner": config.scanner.model_dump(mode="json"),
        "target": config.target.model_dump(mode="json") if config.target else None,
        "static_only": config.static_only,
        "language": config.language.value,
    }
    return payload, hashlib.sha256(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    ).hexdigest()


def measure_one(kind, input_id, out):
    from scripts import phase20_measurements as harness
    from sentinel.llm.semantic_reviewer import OpenAITransport
    from sentinel.static.engine import STATIC_TIMEOUT_SECONDS

    async def forbidden(*_, **__):
        raise AssertionError("model calls forbidden")

    OpenAITransport.create = forbidden
    proposal = approved()
    assert harness.scanner_identity() == proposal["scanner"]
    assert (
        STATIC_TIMEOUT_SECONDS == 300
        and sha(Path("uv.lock")) == proposal["lock_sha256"]
    )
    manifest, selected = corpus(kind, proposal)
    item = next(i for i in selected if i.id == input_id)
    expected = json.loads((BASE / "v21-full-linux-v1/configurations.json").read_text())[
        input_id
    ]
    original = harness.load_configuration

    def checked_configuration(*args, **kwargs):
        config = original(*args, **kwargs)
        assert configuration(config)[1] == expected["sha256"], (
            "configuration drift before scan"
        )
        assert config.scanner.scanner.rules_only and config.static_only
        return config

    with patch.object(harness, "load_configuration", checked_configuration):
        result = harness.measure(
            manifest.model_copy(update={"inputs": [item]}), "rules", out
        )
    assert result["model_calls"] == 0 and not result["requests"]
    assert harness.scanner_identity() == proposal["scanner"]


def condition_passed(kind, row):
    if row["label"] == "vulnerable":
        return row["candidate_detected"] is True
    erratum = kind == "development" and row["input_id"] in {
        "meta-operator-fallback-fixed",
        "meta-operator-fallback-fixed-mutation",
    }
    return row["false_alarm"] is erratum


def assess(kind, item, directory, timing, proposal):
    from scripts.phase20_scoring import candidate_identity, score
    from sentinel.report.validate_json import validate_report_data
    from sentinel.report.validate_sarif import validate_sarif_data

    result = json.loads((directory / "results.json").read_text())
    assert (
        result["scanner"] == proposal["scanner"]
        and result["model_calls"] == 0
        and not result["requests"]
    )
    manifest_key = "development" if kind == "development" else "historical"
    assert result["manifest_sha256"] == proposal["manifests"][manifest_key]["sha256"]
    assert len(result["outcomes"]) == 1
    outcome = result["outcomes"][0]
    assert outcome["input_id"] == item.id
    report_path = directory / item.id / "report.json"
    report = json.loads(report_path.read_text())
    validate_report_data(report)
    validate_sarif_data(json.loads(report_path.with_suffix(".sarif").read_text()))
    assert sha(report_path) == outcome["report_sha256"]
    configs = json.loads((BASE / "v21-full-linux-v1/configurations.json").read_text())
    assert (
        sha(report_path.parent / "configuration.json")
        == outcome["configuration_sha256"]
        == configs[item.id]["sha256"]
    )
    assert (
        outcome["state"] == "completed"
        and report["analysisComplete"]
        and report["executionSuccessful"]
    )
    native = report["static_analysis"]["duration_ms"] / 1000
    assert native <= 300 and timing["elapsed_seconds"] <= 300, (
        "300-second maximum exceeded"
    )
    name = (
        "development-condition-assessment.json"
        if kind == "development"
        else "condition-assessment.json"
    )
    assessments = (
        []
        if kind == "preparatory"
        else json.loads((ASSETS / name).read_text())["assessments"]
    )
    assessment = next((a for a in assessments if a["input_id"] == item.id), None)
    assert kind == "preparatory" or (
        assessment is not None
        and candidate_identity(report["findings"]) == assessment["candidate_identity"]
    ), "condition assessment identity drift"
    row = {
        "input_id": item.id,
        "label": item.label,
        "outcome": outcome,
        "native_seconds": native,
        "whole_input_seconds": timing["elapsed_seconds"],
        "timing_class": "completed_within_target"
        if max(native, timing["elapsed_seconds"]) <= 120
        else "completed_using_extended_time",
        **score(
            label=item.label,
            state=outcome["state"],
            findings=report["findings"],
            assessment=assessment,
        ),
    }
    if kind != "preparatory":
        assert condition_passed(kind, row), f"condition gate failed: {item.id}"
    else:
        row["source_assessment_pending"] = True
    return row, report


def previous_batch(path, kind, proposal, binding_hash):
    packet = json.loads((path / "packet.json").read_text())
    assert packet["passed"] and packet["budget_closed"]
    assert packet["kind"] == (
        "development" if kind == "historical_first" else "historical_first"
    )
    assert (
        packet["scanner"] == proposal["scanner"]
        and packet["binding_sha256"] == binding_hash
    )
    assert packet["workflow_run"] == os.environ["GITHUB_RUN_ID"]
    assert (
        packet["workflow_revision"] == os.environ["GITHUB_SHA"]
        and packet["workflow_attempt"] == "1"
    )
    for name, digest in packet["files_sha256"].items():
        file = path / name
        assert file.resolve().is_relative_to(path.resolve()) and not file.is_symlink()
        assert sha(file) == digest, name
    expected = proposal["manifests"][
        "development" if packet["kind"] == "development" else "historical"
    ]
    assert [r["input_id"] for r in packet["attempts"]] == expected[
        "input_ids"
    ] and not packet["unstarted"]
    assert packet["metrics"]["inputs"] == len(expected["input_ids"])
    assert packet["metrics"]["candidate"]["completed_detections"] == (
        10 if packet["kind"] == "development" else 20
    )
    assert packet["metrics"]["false_alarm_conditions"] == (
        2 if packet["kind"] == "development" else 0
    )
    assert packet["proposal_sha256"] == sha(PROPOSAL) and packet[
        "approval_sha256"
    ] == sha(APPROVAL)
    for row in packet["attempts"]:
        assert row["state"] == "completed" and condition_passed(packet["kind"], row)
        assert max(row["native_seconds"], row["whole_input_seconds"]) <= 300
        report = path / row["directory"] / row["input_id"] / "report.json"
        assert sha(report) == row["outcome"]["report_sha256"]
    return packet


def run(kind, out, deadline_file, previous):
    proposal = approved()
    binding_path = ASSETS / (
        "preparatory-binding.json" if kind == "preparatory" else "final-binding.json"
    )
    binding_hash = sha(binding_path)
    expected = proposal["manifests"][
        "development" if kind == "development" else "historical"
    ]
    if kind == "preparatory":
        expected = {**expected, "input_ids": proposal["preparatory_input_order"]}
    packet = {
        "kind": kind,
        "scanner": proposal["scanner"],
        "workflow_run": os.environ["GITHUB_RUN_ID"],
        "workflow_revision": os.environ["GITHUB_SHA"],
        "workflow_attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "proposal_sha256": sha(PROPOSAL),
        "approval_sha256": sha(APPROVAL),
        "binding_sha256": binding_hash,
        "python": sys.version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "load_before": os.getloadavg(),
        "memory": Path("/proc/meminfo").read_text(),
        "cpu_topology": subprocess.check_output(["lscpu"], text=True),
        "packages": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
        ),
        "attempts": [],
        "unstarted": expected["input_ids"],
        "passed": False,
        "model_calls": 0,
        "target_execution": False,
    }
    write(out / "packet.json", packet)
    try:
        assert packet["workflow_attempt"] == "1", "reruns are forbidden"
        binding = json.loads(binding_path.read_text())
        for name, digest in binding["files"].items():
            assert sha(ASSETS.parents[3] / name) == digest, name
        supervisor.selfcheck(out)
        selfcheck_conditions()
        first = (
            previous_batch(previous, kind, proposal, binding_hash)
            if kind == "historical_second"
            else None
        )
        if first:
            packet["predecessor_packet_sha256"] = sha(previous / "packet.json")
        _, selected = corpus(kind, proposal)
        stop = float(deadline_file.read_text())
        for index, item in enumerate(selected):
            assert time.monotonic() + 315 < stop, "insufficient full-input allowance"
            label = f"{index + 1:02d}-{item.id}"
            row = {
                "input_id": item.id,
                "directory": label,
                "state": "attempted",
                "started_monotonic": time.monotonic(),
            }
            packet["attempts"].append(row)
            packet["unstarted"] = expected["input_ids"][index + 1 :]
            write(out / "packet.json", packet)
            print("START", kind, label, flush=True)
            timing = supervisor.supervise(
                [
                    sys.executable,
                    "-I",
                    str(Path(__file__).resolve()),
                    "child",
                    kind,
                    item.id,
                    str(out / label),
                ],
                out / (label + ".log"),
                300,
            )
            row.update(timing=timing, state="incomplete")
            write(out / "packet.json", packet)
            assert (
                timing["returncode"] == 0
                and not timing["timed_out"]
                and not timing["remaining_group_killed"]
            ), "child execution or cleanup failure"
            scored, report = assess(kind, item, out / label, timing, proposal)
            row.update(scored)
            if kind == "historical_second":
                earlier = next(r for r in first["attempts"] if r["input_id"] == item.id)
                reference = json.loads(
                    (
                        previous / earlier["directory"] / item.id / "report.json"
                    ).read_text()
                )
                excluded = set(proposal["conditions"]["excluded_volatile_fields"])
                row["ordered_repeat_equal"] = clean(report, excluded) == clean(
                    reference, excluded
                )
                assert row["ordered_repeat_equal"], (
                    "entire ordered historical report mismatch"
                )
            write(out / "packet.json", packet)
            print(json.dumps(row), flush=True)
        from scripts.phase20_scoring import metrics

        packet["metrics"] = metrics(packet["attempts"])
        assert len(packet["attempts"]) == (8 if kind == "preparatory" else 45)
        if kind != "preparatory":
            assert packet["metrics"]["candidate"]["completed_detections"] == 20
            assert packet["metrics"]["false_alarm_conditions"] == 0
        packet["source_assessment_pending"] = kind == "preparatory"
        packet["passed"] = True
    except BaseException as error:
        packet["stop_reason"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        packet["budget_closed"] = True
        packet["load_after"] = os.getloadavg()
        packet["files_sha256"] = {
            str(p.relative_to(out)): sha(p)
            for p in sorted(out.rglob("*"))
            if p.is_file() and p != out / "packet.json"
        }
        write(out / "packet.json", packet)


def selfcheck_conditions():
    positive = {
        "input_id": "example",
        "label": "vulnerable",
        "candidate_detected": True,
    }
    assert condition_passed("development", positive)
    assert not condition_passed(
        "development", {**positive, "candidate_detected": False}
    )
    negative = {"input_id": "example", "label": "fixed", "false_alarm": False}
    assert condition_passed("historical_first", negative)
    assert not condition_passed("historical_first", {**negative, "false_alarm": True})
    erratum = {
        **negative,
        "input_id": "meta-operator-fallback-fixed",
        "false_alarm": True,
    }
    assert condition_passed("development", erratum)
    assert not condition_passed("development", {**erratum, "false_alarm": False})
    assert not condition_passed("historical_first", erratum)


if __name__ == "__main__":
    for key in list(os.environ):
        if key.startswith(("OPENAI_", "SENTINEL_")):
            os.environ.pop(key)
    sys.path[:0] = [str(Path.cwd() / "src"), str(Path.cwd())]
    signal.signal(signal.SIGTERM, supervisor.stopped)
    if sys.argv[1] == "child":
        measure_one(sys.argv[2], sys.argv[3], Path(sys.argv[4]))
    else:
        assert sys.platform == "linux"
        assert ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) == 0
        out = Path(sys.argv[3]).resolve()
        out.mkdir(exist_ok=False)
        if sys.argv[1] == "selfcheck":
            supervisor.selfcheck(out)
            selfcheck_conditions()
            write(out / "condition-selfcheck.json", {"passed": True, "corpus_runs": 0})
        else:
            assert sys.argv[1] == "run"
            run(sys.argv[2], out, Path(sys.argv[4]), Path(sys.argv[5]))
