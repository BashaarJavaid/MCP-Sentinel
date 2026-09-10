"""One approved stdlib throughput probe; no scanner or corpus imports."""

import argparse
import hashlib
import json
import os
import platform
import signal
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

KEYS = [f"k{i:03d}" for i in range(512)]
ORDER = [1, 3, 4, 6] * 3
SEED = 1729
ITERATIONS = 100_000


def write(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def helper(a, b):
    return (a * 31 + b) & 0xFFFF


def unit(acc, iterations=ITERATIONS):
    env = {}
    for i in range(iterations):
        key = KEYS[i & 511]
        prev = env.get(key)
        acc = (
            acc * 1103515245 + 12345 + (prev[0] if prev is not None else 0)
        ) & 0xFFFFFFFF
        env[key] = (acc, i)
        parts = frozenset((acc & 15, i & 15, 3))
        acc ^= len(parts) + helper(acc, i)
    return acc


def workload(units, iterations=ITERATIONS):
    acc = SEED
    for _ in range(units):
        acc = unit(acc, iterations)
    return acc


def child(directory, units, iterations):
    write(directory / "ready.json", {"pid": os.getpid(), "ready_at": time.monotonic()})
    start_at = float(sys.stdin.readline())
    time.sleep(max(0, start_at - time.monotonic()))
    started, cpu = time.monotonic(), time.process_time()
    checksum = workload(units, iterations)
    ended = time.monotonic()
    write(
        directory / "result.json",
        {
            "pid": os.getpid(),
            "units": units,
            "iterations_per_unit": iterations,
            "checksum": checksum,
            "start_at": start_at,
            "started_at": started,
            "ended_at": ended,
            "wall_seconds": ended - started,
            "cpu_seconds": time.process_time() - cpu,
        },
    )


def observation(directory, count, units, expected, deadline, iterations=ITERATIONS):
    directory.mkdir()
    started = time.monotonic()
    end = min(deadline, started + 180)
    row = {
        "count": count,
        "units": units,
        "started_at": started,
        "load_before": os.getloadavg(),
        "state": "started",
        "children": [],
    }
    write(directory / "observation.json", row)
    processes, logs = [], []
    try:
        for index in range(count):
            folder = directory / str(index)
            folder.mkdir()
            log = (folder / "child.log").open("wb")
            logs.append(log)
            processes.append(
                subprocess.Popen(
                    [
                        sys.executable,
                        "-I",
                        str(Path(__file__).resolve()),
                        "child",
                        str(folder),
                        str(units),
                        str(iterations),
                    ],
                    stdin=subprocess.PIPE,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )
            )
        while not all(
            (directory / str(i) / "ready.json").exists() for i in range(count)
        ):
            if time.monotonic() >= end:
                raise TimeoutError(
                    "Child readiness exceeded observation/internal deadline"
                )
            if any(p.poll() is not None for p in processes):
                raise RuntimeError("Child exited before readiness")
            time.sleep(0.01)
        row["readiness"] = [
            json.loads((directory / str(i) / "ready.json").read_text())
            for i in range(count)
        ]
        start_at = time.monotonic() + 0.25
        if start_at >= end:
            raise TimeoutError("No observation time remains after readiness")
        row["common_start_monotonic"] = start_at
        write(directory / "observation.json", row)
        for process in processes:
            process.stdin.write((str(start_at) + "\n").encode())
            process.stdin.close()
        for process in processes:
            process.wait(timeout=max(0.001, end - time.monotonic()))
            if process.returncode != 0:
                raise RuntimeError(f"Child exited {process.returncode}")
        rows = [
            json.loads((directory / str(i) / "result.json").read_text())
            for i in range(count)
        ]
        if any(
            r["checksum"] != expected
            or r["units"] != units
            or r["iterations_per_unit"] != iterations
            for r in rows
        ):
            raise ValueError("Child workload/checksum mismatch")
        if any(r["started_at"] < start_at or r["ended_at"] > end for r in rows):
            raise ValueError("Child timing outside approved observation bounds")
        wall = max(r["ended_at"] for r in rows) - start_at
        row.update(
            state="completed",
            children=rows,
            throughput_units_per_second=count * units / wall,
            wall_seconds=wall,
            checksum=expected,
            maximum_start_lag_seconds=max(r["started_at"] - start_at for r in rows),
        )
    except BaseException as error:
        row.update(state="invalid", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
        for process in processes:
            process.wait()
            if process.stdin and not process.stdin.closed:
                process.stdin.close()
        for log in logs:
            log.close()
        row.update(
            ended_at=time.monotonic(),
            load_after=os.getloadavg(),
            all_children_reaped=all(p.poll() is not None for p in processes),
            child_returncodes=[p.returncode for p in processes],
        )
        row["outer_seconds"] = row["ended_at"] - started
        write(directory / "observation.json", row)
    return row


def assess(rows):
    if (
        len(rows) != 12
        or [r["count"] for r in rows] != ORDER
        or any(r["state"] != "completed" for r in rows)
    ):
        return {"decision": "invalid_or_incomplete", "partitioning_authorized": False}
    medians = {
        n: statistics.median(
            r["throughput_units_per_second"] for r in rows if r["count"] == n
        )
        for n in [1, 3, 4, 6]
    }
    scaling = {n: medians[n] / medians[1] for n in medians}
    if scaling[3] < 2.7:
        decision = "premise_not_supported_E3_below_2.7"
    elif scaling[4] >= 3.4 and scaling[6] >= 0.95 * scaling[4]:
        decision = "supports_separately_proposed_partitioning_experiment"
    elif scaling[4] < 3.2:
        decision = "close_current_partitioning_proposal_E4_below_3.2"
    else:
        decision = "inconclusive_no_implementation"
    return {
        "decision": decision,
        "median_throughput": medians,
        "E": scaling,
        "T4_over_T3": medians[4] / medians[3],
        "T6_over_T3": medians[6] / medians[3],
        "partitioning_authorized": False,
        "limits": (
            "Synthetic workload on this runner only. No scanner gain, timing pass, "
            "general impossibility of parallelism, or implementation approval "
            "is established."
        ),
    }


def run(directory, deadline_file):
    directory.mkdir(parents=True, exist_ok=False)
    write(
        directory / "attempt.json",
        {
            "state": "started",
            "run_id": os.getenv("GITHUB_RUN_ID"),
            "source": os.getenv("GITHUB_SHA"),
            "paid_calls": 0,
        },
    )
    packet_path = Path(__file__).with_name("packet.json")
    packet = json.loads(packet_path.read_text())
    assert (
        packet["approved"]
        and packet["probe_sha256"]
        == hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    )
    assert os.getenv("GITHUB_REF") == "refs/heads/phase22/integration"
    assert os.getenv("GITHUB_RUN_ATTEMPT") == "1" and sys.platform == "linux"
    deadline = min(float(deadline_file.read_text()), time.monotonic() + 600)

    def expired(signum, frame):
        raise TimeoutError(
            "Internal probe deadline reached; reserve time for artifact upload"
        )

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, max(0.001, deadline - time.monotonic()))
    result = {
        "rows": [],
        "state": "started",
        "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "model_calls": 0,
        "scanner_runs": 0,
        "target_execution": False,
    }
    try:
        environment = {
            "python": sys.version,
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "load": os.getloadavg(),
            "identity": {
                k: os.getenv(k)
                for k in [
                    "ImageOS",
                    "ImageVersion",
                    "RUNNER_NAME",
                    "GITHUB_RUN_ID",
                    "GITHUB_SHA",
                    "GITHUB_RUN_ATTEMPT",
                ]
            },
        }
        for command in ["nproc", "lscpu"]:
            environment[command] = subprocess.check_output(
                [command], text=True, timeout=10
            )
        environment["cpuinfo"] = Path("/proc/cpuinfo").read_text()
        environment["meminfo"] = Path("/proc/meminfo").read_text()
        write(directory / "environment.json", environment)
        before = time.monotonic()
        calibration_checksum = unit(SEED)
        calibration_seconds = time.monotonic() - before
        units = 20 if calibration_seconds > 1.0 else 40
        expected = workload(units)
        write(
            directory / "calibration.json",
            {
                "seconds": calibration_seconds,
                "checksum": calibration_checksum,
                "units": units,
                "expected_checksum": expected,
                "seed": SEED,
                "iterations_per_unit": ITERATIONS,
                "not_a_scaling_observation": True,
                "reference_workloads": 1,
            },
        )
        for index, count in enumerate(ORDER):
            if time.monotonic() >= deadline:
                raise TimeoutError("No internal budget remains")
            row = observation(
                directory / f"observation-{index + 1:02}",
                count,
                units,
                expected,
                deadline,
            )
            result["rows"].append(row)
            write(directory / "result.json", result)
        result.update(state="completed", assessment=assess(result["rows"]))
    except BaseException as error:
        result.update(
            state="invalid_or_incomplete",
            error=f"{type(error).__name__}: {error}",
            assessment={
                "decision": "invalid_or_incomplete",
                "partitioning_authorized": False,
            },
        )
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        result["finished_monotonic"] = time.monotonic()
        write(directory / "result.json", result)


def selfcheck():
    # Tiny implementation controls, not scaling observations or scanner runs.
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        row = observation(
            root / "success", 2, 1, workload(1, 32), time.monotonic() + 10, 32
        )
        assert row["all_children_reaped"] and len(row["children"]) == 2
        try:
            observation(root / "mismatch", 2, 1, -1, time.monotonic() + 10, 32)
            raise AssertionError("Mismatching checksum accepted")
        except ValueError:
            assert json.loads((root / "mismatch/observation.json").read_text())[
                "all_children_reaped"
            ]
        try:
            observation(root / "timeout", 2, 1, 0, time.monotonic() - 1, 32)
            raise AssertionError("Expired deadline accepted")
        except TimeoutError:
            assert json.loads((root / "timeout/observation.json").read_text())[
                "all_children_reaped"
            ]
    for values, expected in [
        ({1: 1, 3: 2.8, 4: 3.5, 6: 3.4}, "supports_"),
        ({1: 1, 3: 2.8, 4: 3.1, 6: 3}, "close_"),
        ({1: 1, 3: 2.5, 4: 3.5, 6: 3.4}, "premise_"),
        ({1: 1, 3: 2.8, 4: 3.3, 6: 3.2}, "inconclusive"),
        ({1: 1, 3: 2.8, 4: 3.5, 6: 3}, "inconclusive"),
    ]:
        rows = [
            {"count": n, "state": "completed", "throughput_units_per_second": values[n]}
            for n in ORDER
        ]
        assert assess(rows)["decision"].startswith(expected)
    assert assess([])["decision"] == "invalid_or_incomplete"
    print(
        "PASS: tiny readiness/checksum/deadline/cleanup controls and decision "
        "boundaries; no scaling measurements"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["run", "child", "selfcheck"])
    parser.add_argument("arguments", nargs="*")
    args = parser.parse_args()
    if args.mode == "child":
        child(Path(args.arguments[0]), int(args.arguments[1]), int(args.arguments[2]))
    elif args.mode == "run":
        run(Path(args.arguments[0]), Path(args.arguments[1]))
    else:
        selfcheck()
