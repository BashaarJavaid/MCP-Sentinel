"""Bounded replacement-v6 evaluation; requires a separate exact approval."""

import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

ASSETS = Path(__file__).resolve().parent
BASE = ASSETS.parent
DELIVERY = BASE.parents[2]
CORPUS = DELIVERY / "artifacts/phase22/corpus-replacement-v6"
PROPOSAL = ASSETS / "evaluation-proposal.json"
APPROVAL = ASSETS / "evaluation-authorization.json"
spec = importlib.util.spec_from_file_location(
    "supervisor", BASE / "v20-linux-diagnostic-v1/runner.py"
)
supervisor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supervisor)
sha, write = supervisor.sha, supervisor.write

# macOS can deny killpg(..., 0) after an orphan is adopted by launchd.
# Verify exact group states instead; live members and unreadable ps fail closed.
DARWIN_GROUP_CHECKS = []
original_group_exists = supervisor.group_exists


def group_exists(pgid):
    try:
        return original_group_exists(pgid)
    except PermissionError:
        if sys.platform != "darwin":
            raise
        rows = subprocess.check_output(["ps", "-axo", "pid=,pgid=,stat="], text=True, timeout=2)
        members = []
        for line in rows.splitlines():
            fields = line.split()
            if not fields:
                continue
            assert len(fields) == 3, "Unexpected process-state record"
            pid, group, state = fields
            if int(group) == pgid:
                members.append({"pid": int(pid), "state": state})
        DARWIN_GROUP_CHECKS.append({"pgid": pgid, "members": members})
        return any(not item["state"].startswith("Z") for item in members)


supervisor.group_exists = group_exists
EXCLUDED = frozenset(
    {
        "scan_id",
        "finding_id",
        "timestamp",
        "started_at",
        "completed_at",
        "duration_ms",
        "reviewed_at",
        "applied_at",
        "latency_ms",
        "execution_latency_ms",
        "origin_latency_ms",
    }
)


def verify_packet():
    proposal = json.loads(PROPOSAL.read_text())
    for name, digest in proposal["files_sha256"].items():
        assert sha(DELIVERY / name) == digest, name
    for key in (
        "checkpoint",
        "manifest",
        "configuration",
        "pre_curation_freeze",
        "comparator_preparation",
        "source_only_authorization",
        "condition_review",
        "novelty",
    ):
        record = proposal[key]
        assert sha(DELIVERY / record["path"]) == record["sha256"], key
    return proposal


def approved():
    proposal = verify_packet()
    approval = json.loads(APPROVAL.read_text())
    assert approval["approved"] is True and approval["user_decision"].strip()
    assert approval["proposal_sha256"] == sha(PROPOSAL)
    assert approval["checkpoint_sha256"] == proposal["checkpoint"]["sha256"]
    assert approval["scanner"] == proposal["scanner"]
    assert approval["bounds"] == proposal["bounds"]
    assert approval["corpus"] == {
        "manifest": proposal["manifest"]["path"],
        "sha256": proposal["manifest"]["sha256"],
        "freeze_approved": True,
        "input_ids": proposal["input_order"],
        "treatments": ["rules", "semgrep"],
    }
    binding = json.loads((ASSETS / "binding.json").read_text())
    for name, digest in binding["files"].items():
        assert sha(DELIVERY / name) == digest, name
    return proposal


def configuration(config):
    payload = {
        "scanner": config.scanner.model_dump(mode="json"),
        "target": config.target.model_dump(mode="json") if config.target else None,
        "static_only": config.static_only,
        "language": config.language.value,
    }
    return hashlib.sha256(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    ).hexdigest()


def stage():
    """Copy only new, hash-checked corpus assets to a separate frozen checkout."""
    from scripts.phase20_measurements import scanner_identity
    from scripts.phase22_corpus import validate

    proposal = verify_packet()
    assert scanner_identity() == proposal["scanner"]
    assert Path.cwd() != DELIVERY
    expected = json.loads((ASSETS / "staging-files.json").read_text())
    for name, digest in expected.items():
        source, dest = DELIVERY / name, Path.cwd() / name
        assert sha(source) == digest, name
        assert name.startswith("artifacts/phase22/")
        if dest.exists():
            assert not dest.is_symlink() and sha(dest) == digest, name
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
    validate(Path.cwd() / proposal["manifest"]["path"])
    assert scanner_identity() == proposal["scanner"]
    print("Staged and validated corpus assets; zero observations.")


def check_identity(rules):
    from scripts import phase20_measurements as harness
    from scripts.phase22_corpus import frozen
    from sentinel.static.engine import STATIC_TIMEOUT_SECONDS

    proposal = approved()
    assert harness.scanner_identity() == proposal["scanner"]
    checkpoint = json.loads((CORPUS / "checkpoint-f85a90f.json").read_text())
    for name, digest in checkpoint["harness_and_lock_sha256"].items():
        assert sha(Path.cwd() / name) == digest, name
    assert STATIC_TIMEOUT_SECONDS == 300
    harness.verify_rules(rules)
    manifest = frozen(approval_path=APPROVAL)
    selected = [i for i in manifest.inputs if i.id in proposal["input_order"]]
    assert [i.id for i in selected] == proposal["input_order"]
    return proposal, manifest, selected


def child(batch, input_id, out, rules):
    from scripts import phase20_measurements as harness
    from sentinel.llm.semantic_reviewer import OpenAITransport
    from sentinel.report.validate_json import validate_report_data
    from sentinel.report.validate_sarif import validate_sarif_data

    async def forbidden(*_, **__):
        raise AssertionError("model transport forbidden")

    OpenAITransport.create = forbidden
    proposal, manifest, selected = check_identity(rules)
    assert batch in proposal["batch_order"]
    consumed = json.loads((ASSETS / "execution-consumed.json").read_text())
    assert consumed["proposal_sha256"] == sha(PROPOSAL)
    parent_packet = json.loads((Path(consumed["output"]) / "packet.json").read_text())
    assert not parent_packet.get("budget_closed", False)
    active = parent_packet["attempts"][-1]
    assert active["batch"] == batch and active["input_id"] == input_id and active["state"] == "attempted"
    assert out.resolve() == (Path(consumed["output"]) / active["directory"]).resolve()
    item = next(i for i in selected if i.id == input_id)
    configs = json.loads((CORPUS / "configurations.json").read_text())
    original = harness.load_configuration

    def checked_configuration(*args, **kwargs):
        config = original(*args, **kwargs)
        assert config.scanner.scanner.rules_only and config.static_only
        assert configuration(config) == configs[input_id]["sha256"]
        return config

    treatment = "semgrep" if batch == "semgrep-first" else "rules"
    with patch.object(harness, "load_configuration", checked_configuration):
        result = harness.measure(
            manifest.model_copy(update={"inputs": [item]}),
            treatment,
            out,
            rules_dir=rules,
            phase22_approval=APPROVAL,
        )
    assert result["scanner"] == proposal["scanner"]
    assert result["manifest_sha256"] == proposal["manifest"]["sha256"]
    assert result["authorization_sha256"] == sha(APPROVAL)
    assert result["model_calls"] == 0 and not result["requests"]
    assert len(result["outcomes"]) == 1
    outcome = result["outcomes"][0]
    assert outcome["input_id"] == input_id and outcome["state"] == "completed", outcome
    if treatment == "rules":
        report_path = out / input_id / "report.json"
        report = json.loads(report_path.read_text())
        validate_report_data(report)
        validate_sarif_data(json.loads(report_path.with_suffix(".sarif").read_text()))
        assert sha(report_path) == outcome["report_sha256"]
        assert (
            sha(report_path.parent / "configuration.json")
            == outcome["configuration_sha256"]
            == configs[input_id]["sha256"]
        )
        assert report["analysisComplete"] and report["executionSuccessful"]
        assert report["static_analysis"]["duration_ms"] <= 300000
    else:
        assert sha(out / input_id / "raw.json") == outcome["raw_sha256"]
    assert harness.scanner_identity() == proposal["scanner"]
    write(
        out / "validation.json",
        {
            "passed": True,
            "label": item.label,
            "tree_sha256": item.tree_sha256,
            "source_assessment_pending": True,
        },
    )


def completed(timing):
    assert timing["returncode"] == 0 and not timing["timed_out"]
    assert timing["cleanup_verified"] and not timing["remaining_group_killed"]
    assert timing["elapsed_seconds"] <= 300
    assert timing["elapsed_including_cleanup_seconds"] - timing["elapsed_seconds"] <= 15


def run(out, rules):
    proposal = approved()
    order = [
        {"batch": b, "input_id": i}
        for b in proposal["batch_order"]
        for i in proposal["input_order"]
    ]
    packet = {
        "execution": "one local serial macOS sequence",
        "runner_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=DELIVERY, text=True).strip(),
        "scanner": proposal["scanner"],
        "proposal_sha256": sha(PROPOSAL),
        "approval_sha256": sha(APPROVAL),
        "binding_sha256": sha(ASSETS / "binding.json"),
        "python": sys.version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "load_before": os.getloadavg(),
        "cpu_topology": subprocess.check_output(["sysctl", "hw.ncpu", "hw.memsize"], text=True),
        "packages": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
        ),
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
        with (ASSETS / "execution-consumed.json").open("x") as receipt:
            json.dump({"proposal_sha256": sha(PROPOSAL), "approval_sha256": sha(APPROVAL), "output": str(out), "budget_consumed": True}, receipt)
        stop = time.monotonic() + proposal["bounds"]["internal_stop_minutes"] * 60
        supervisor.selfcheck(out)
        selfcheck()
        previous = {}
        for index, observation in enumerate(order):
            assert time.monotonic() + 315 < stop, "insufficient whole-input allowance"
            check_identity(rules)
            assert time.monotonic() + 315 < stop, "insufficient whole-input allowance"
            label = f"{index + 1:02d}-{observation['batch']}-{observation['input_id']}"
            row = {**observation, "directory": label, "state": "attempted"}
            packet["attempts"].append(row)
            packet["unstarted"] = order[index + 1 :]
            write(out / "packet.json", packet)
            print("START", label, flush=True)
            command = [
                sys.executable,
                "-I",
                str(Path(__file__).resolve()),
                "child",
                observation["batch"],
                observation["input_id"],
                str(out / label),
                str(rules),
            ]
            row["command"] = command
            write(out / "packet.json", packet)
            row["timing"] = supervisor.supervise(command, out / (label + ".log"), 300)
            row["state"] = "incomplete"
            write(out / "packet.json", packet)
            completed(row["timing"])
            result = json.loads((out / label / "results.json").read_text())
            row["outcome"] = result["outcomes"][0]
            row["validation"] = json.loads(
                (out / label / "validation.json").read_text()
            )
            if observation["batch"] != "semgrep-first":
                report = json.loads(
                    (out / label / observation["input_id"] / "report.json").read_text()
                )
                row["native_seconds"] = report["static_analysis"]["duration_ms"] / 1000
                row["timing_class"] = (
                    "completed_within_target"
                    if max(row["native_seconds"], row["timing"]["elapsed_seconds"])
                    <= 120
                    else "completed_using_extended_time"
                )
                canonical = supervisor.clean(report, EXCLUDED)
                if observation["batch"] == "rules-repeat":
                    row["ordered_repeat_equal"] = (
                        previous[observation["input_id"]] == canonical
                    )
                    assert row["ordered_repeat_equal"], "entire ordered report mismatch"
                else:
                    previous[observation["input_id"]] = canonical
            else:
                row["timing_class"] = "comparator_completed_within_maximum"
            row["state"] = "completed"
            write(out / "packet.json", packet)
            print(json.dumps(row), flush=True)
        assert len(packet["attempts"]) == 15 and not packet["unstarted"]
        packet["passed"] = True
        packet["execution_gate_passed"] = True
        packet["fresh_detection_gate_passed"] = None  # Set only by separate source-bound assessment.
    except BaseException as error:
        packet["stop_reason"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        packet["budget_closed"] = True
        packet["darwin_group_checks"] = DARWIN_GROUP_CHECKS
        packet["load_after"] = os.getloadavg()
        packet["files_sha256"] = {
            p.relative_to(out).as_posix(): sha(p)
            for p in sorted(out.rglob("*"))
            if p.is_file() and p != out / "packet.json"
        }
        write(out / "packet.json", packet)


def selfcheck():
    timing = {
        "returncode": 0,
        "timed_out": False,
        "cleanup_verified": True,
        "remaining_group_killed": False,
        "elapsed_seconds": 300,
        "elapsed_including_cleanup_seconds": 315,
    }
    completed(timing)
    for change in (
        {"returncode": 1},
        {"timed_out": True},
        {"cleanup_verified": False},
        {"remaining_group_killed": True},
        {"elapsed_seconds": 300.001},
        {"elapsed_including_cleanup_seconds": 315.001},
    ):
        try:
            completed({**timing, **change})
        except AssertionError:
            pass
        else:
            raise AssertionError(f"invalid result accepted: {change}")
    assert len(EXCLUDED) == 11
    original = {
        "findings": [1, 2],
        "warnings": ["a", "b"],
        "coverage": {"known": 1},
        "timestamp": "old",
    }
    for key, value in (
        ("findings", [2, 1]),
        ("warnings", ["b", "a"]),
        ("coverage", {"known": 0}),
    ):
        assert supervisor.clean(original, EXCLUDED) != supervisor.clean(
            {**original, key: value}, EXCLUDED
        )
    assert supervisor.clean(original, EXCLUDED) == supervisor.clean(
        {**original, "timestamp": "new"}, EXCLUDED
    )


if __name__ == "__main__":
    for key in list(os.environ):
        if key.startswith(("OPENAI_", "SENTINEL_")):
            os.environ.pop(key)
    sys.path[:0] = [str(Path.cwd() / "src"), str(Path.cwd())]
    signal.signal(signal.SIGTERM, supervisor.stopped)
    mode = sys.argv[1]
    if mode == "stage":
        stage()
    elif mode == "check":
        verify_packet()
        selfcheck()
        print("Runner boundary checks passed; zero observations.")
    elif mode == "child":
        child(sys.argv[2], sys.argv[3], Path(sys.argv[4]), Path(sys.argv[5]))
    else:
        assert mode in {"run", "selfcheck"} and sys.platform == "darwin"
        out = Path(sys.argv[2]).resolve()
        out.mkdir(exist_ok=False)
        if mode == "selfcheck":
            supervisor.selfcheck(out)
            selfcheck()
            write(out / "darwin-group-checks.json", DARWIN_GROUP_CHECKS)
        else:
            run(out, Path(sys.argv[3]).resolve())
