"""Single approved Linux diagnostic; no scanner edits or target execution."""

import ctypes
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import signal
import subprocess
import sys
import time
from contextlib import suppress
from pathlib import Path
from unittest.mock import patch

ASSETS = Path(__file__).resolve().parent
BASE = ASSETS.parent
PROPOSAL = BASE / "v19-linux-timeout-diagnostic-proposal.json"
APPROVAL = BASE / "v20-diagnostic-authorization.json"
GRACE = 5


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def approved():
    proposal = json.loads(PROPOSAL.read_text())
    approval = json.loads(APPROVAL.read_text())
    assert approval["approved"] and approval["proposal_sha256"] == sha(PROPOSAL)
    assert approval["bounds"] == proposal["bounds"]
    for item in proposal["inputs"]:
        assert (
            sha(ASSETS / (item["input_id"] + ".json"))
            == item["reference_report_sha256"]
        )
    return proposal


def clean(value, excluded):
    if isinstance(value, dict):
        return {k: clean(v, excluded) for k, v in value.items() if k not in excluded}
    if isinstance(value, list):
        return [clean(v, excluded) for v in value]
    return value


def stopped(*_):
    raise SystemExit("supervisor termination")


def group_exists(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def reap(pgid):
    # Linux subreaper owns orphaned grandchildren, including stubborn dummy children.
    while True:
        try:
            pid, _ = os.waitpid(-pgid, os.WNOHANG)
        except ChildProcessError:
            return
        if pid == 0:
            return


def supervise(command, log, limit):
    start = time.monotonic()  # Includes Popen and interpreter startup.
    before = tuple(resource.getrusage(resource.RUSAGE_CHILDREN))
    with log.open("wb") as stream:
        child = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        elapsed = None
        timed_out = False
        leftovers = False
        try:
            try:
                child.wait(timeout=max(0, start + limit - time.monotonic()))
                elapsed = time.monotonic() - start
            except subprocess.TimeoutExpired:
                elapsed = time.monotonic() - start
                timed_out = True
        finally:
            # Signal the parent first so scanner worker finally blocks can reap.
            if child.poll() is None:
                child.terminate()
                with suppress(subprocess.TimeoutExpired):
                    child.wait(timeout=GRACE)
            reap(child.pid)
            leftovers = group_exists(child.pid)
            if leftovers:
                with suppress(ProcessLookupError):
                    os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=GRACE)
            until = time.monotonic() + GRACE
            while group_exists(child.pid) and time.monotonic() < until:
                reap(child.pid)
                time.sleep(0.01)
            assert not group_exists(child.pid), "owned process group survived cleanup"
    return {
        "elapsed_seconds": elapsed,
        "returncode": child.returncode,
        "timed_out": timed_out,
        "remaining_group_killed": leftovers,
        "cleanup_verified": True,
        "elapsed_including_cleanup_seconds": time.monotonic() - start,
        "child_resource_before": before,
        "child_resource_after": tuple(resource.getrusage(resource.RUSAGE_CHILDREN)),
    }


def selfcheck(out):
    rows = []
    commands = [
        ("success", "pass", False, False),
        ("cooperative", "import time; time.sleep(30)", True, False),
        (
            "stubborn",
            "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); "
            "time.sleep(30)",
            True,
            True,
        ),
        (
            "orphan",
            "import subprocess,sys; subprocess.Popen([sys.executable,'-c',"
            "'import time; time.sleep(30)'])",
            False,
            True,
        ),
    ]
    for name, code, timeout, remaining in commands:
        row = supervise([sys.executable, "-I", "-c", code], out / (name + ".log"), 0.5)
        rows.append({"control": name, **row})
        assert (
            row["timed_out"] == timeout and row["remaining_group_killed"] == remaining
        ), row
    sample = {
        "findings": [{"x": 1, "timestamp": "old"}, {"x": 2}],
        "warnings": ["a", "b"],
    }
    assert clean(sample, {"timestamp"}) != clean(
        {**sample, "findings": list(reversed(sample["findings"]))}, {"timestamp"}
    )
    assert clean(sample, {"timestamp"}) != clean(
        {**sample, "warnings": ["b", "a"]}, {"timestamp"}
    )
    assert clean({"x": 1, "timestamp": "old"}, {"timestamp"}) == {"x": 1}
    write(
        out / "selfcheck.json",
        {
            "passed": True,
            "dummy_controls": rows,
            "ordered_comparison": True,
            "corpus_runs": 0,
        },
    )


def measure_one(input_id, out):
    root = Path.cwd()
    sys.path[:0] = [str(root / "src"), str(root)]
    from scripts import phase20_measurements as harness
    from scripts.phase22_corpus import frozen
    from sentinel.llm.semantic_reviewer import OpenAITransport
    from sentinel.static.engine import STATIC_TIMEOUT_SECONDS

    async def forbidden(*_, **__):
        raise AssertionError("model calls forbidden")

    OpenAITransport.create = forbidden
    proposal = approved()
    expected = next(i for i in proposal["inputs"] if i["input_id"] == input_id)
    assert harness.scanner_identity() == proposal["scanner"]
    assert (
        STATIC_TIMEOUT_SECONDS == 300
        and sha(root / "uv.lock") == proposal["lock_sha256"]
    )
    manifest = frozen()
    decision = json.loads((root / "artifacts/phase22/authorization.json").read_text())[
        "corpus"
    ]
    assert sha(root / decision["manifest"]) == expected["manifest_sha256"]
    item = next(i for i in manifest.inputs if i.id == input_id)
    assert item.model_dump(mode="json") == expected["manifest_input"]
    original = harness.load_configuration

    def checked_configuration(*args, **kwargs):
        config = original(*args, **kwargs)
        payload = {
            "scanner": config.scanner.model_dump(mode="json"),
            "target": config.target.model_dump(mode="json") if config.target else None,
            "static_only": config.static_only,
            "language": config.language.value,
        }
        digest = hashlib.sha256(
            (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
        ).hexdigest()
        assert digest == expected["configuration_sha256"], (
            "configuration mismatch before scan"
        )
        assert config.scanner.scanner.rules_only and config.static_only
        return config

    # Validate the existing harness's actual configuration before it calls run_scan.
    with patch.object(harness, "load_configuration", checked_configuration):
        result = harness.measure(
            manifest.model_copy(update={"inputs": [item]}), "rules", out
        )
    assert result["model_calls"] == 0 and not result["requests"]
    assert harness.scanner_identity() == proposal["scanner"]


def run(out, deadline_file):
    proposal = approved()
    packet = {
        "workflow_run": os.environ["GITHUB_RUN_ID"],
        "workflow_revision": os.environ["GITHUB_SHA"],
        "workflow_attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "scanner": proposal["scanner"],
        "proposal_sha256": sha(PROPOSAL),
        "approval_sha256": sha(APPROVAL),
        "runner_sha256": sha(Path(__file__)),
        "python": sys.version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "load_before": os.getloadavg(),
        "cpu_topology": subprocess.check_output(["lscpu"], text=True),
        "memory": Path("/proc/meminfo").read_text(),
        "model_calls": 0,
        "target_execution": False,
        "attempts": [],
        "passed": False,
        "unstarted": proposal["order"],
    }
    write(out / "packet.json", packet)
    try:
        assert packet["workflow_attempt"] == "1", "job rerun is forbidden"
        binding = json.loads((ASSETS / "binding.json").read_text())
        for name, digest in binding["files"].items():
            assert sha(ASSETS.parents[3] / name) == digest, name
        selfcheck(out)
        stop = float(deadline_file.read_text())
        previous = {}
        root = Path.cwd()
        sys.path[:0] = [str(root / "src"), str(root)]
        from sentinel.report.validate_json import validate_report_data
        from sentinel.report.validate_sarif import validate_sarif_data

        packet["semgrep_version"] = importlib.metadata.version("semgrep")
        for index, observation in enumerate(proposal["order"]):
            assert time.monotonic() + 300 + 3 * GRACE < stop, (
                "insufficient full observation allowance"
            )
            label = f"{index + 1}-{observation['input_id']}"
            row = {
                **observation,
                "label": label,
                "started_monotonic": time.monotonic(),
                "state": "attempted",
            }
            packet["attempts"].append(row)
            packet["unstarted"] = proposal["order"][index + 1 :]
            write(out / "packet.json", packet)  # Count before launch, even on failure.
            print("START", label, flush=True)
            measured = out / label
            row.update(
                supervise(
                    [
                        sys.executable,
                        "-I",
                        str(Path(__file__).resolve()),
                        "child",
                        observation["input_id"],
                        str(measured),
                    ],
                    out / (label + ".log"),
                    300,
                )
            )
            row["state"] = "incomplete"
            write(out / "packet.json", packet)
            assert (
                row["returncode"] == 0
                and not row["timed_out"]
                and not row["remaining_group_killed"]
            ), "child execution or cleanup failure"
            result = json.loads((measured / "results.json").read_text())
            outcome = result["outcomes"][0]
            row["outcome"] = outcome
            report = json.loads(
                (measured / observation["input_id"] / "report.json").read_text()
            )
            sarif = json.loads(
                (measured / observation["input_id"] / "report.sarif").read_text()
            )
            validate_report_data(report)
            validate_sarif_data(sarif)
            native = report["static_analysis"]["duration_ms"] / 1000
            row["native_seconds"] = native
            assert (
                outcome["state"] == "completed"
                and report["analysisComplete"]
                and report["executionSuccessful"]
            )
            assert native <= 300 and row["elapsed_seconds"] <= 300, (
                "300-second maximum exceeded"
            )
            row["state"] = (
                "completed_within_target"
                if max(native, row["elapsed_seconds"]) <= 120
                else "completed_using_extended_time"
            )
            excluded = set(proposal["correctness"]["excluded_volatile_fields"])
            actual = clean(report, excluded)
            reference = clean(
                json.loads((ASSETS / (observation["input_id"] + ".json")).read_text()),
                excluded,
            )
            row["ordered_reference_equal"] = actual == reference
            row["ordered_repeat_equal"] = (
                observation["input_id"] not in previous
                or actual == previous[observation["input_id"]]
            )
            assert row["ordered_reference_equal"] and row["ordered_repeat_equal"], (
                "ordered report mismatch"
            )
            previous[observation["input_id"]] = actual
            write(out / "packet.json", packet)
            print(json.dumps(row), flush=True)
        packet["passed"] = True
    except BaseException as error:
        packet["stop_reason"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        packet["budget_closed"] = True
        packet["load_after"] = os.getloadavg()
        write(out / "packet.json", packet)


if __name__ == "__main__":
    for key in list(os.environ):
        if key.startswith(("OPENAI_", "SENTINEL_")):
            os.environ.pop(key)
    signal.signal(signal.SIGTERM, stopped)
    mode = sys.argv[1]
    if mode == "child":
        measure_one(sys.argv[2], Path(sys.argv[3]))
    else:
        assert sys.platform == "linux", "supervisor requires Linux subreaper"
        assert ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) == 0
        destination = Path(sys.argv[2]).resolve()
        destination.mkdir(exist_ok=False)
        if mode == "selfcheck":
            selfcheck(destination)
        else:
            assert mode == "run"
            run(destination, Path(sys.argv[3]))
