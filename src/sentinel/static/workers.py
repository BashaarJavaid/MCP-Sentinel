"""Bounded source-flow workers over scanner-owned parsed snapshots."""

from __future__ import annotations

import os
import pickle
import subprocess
import sys
import time
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentinel.static.model import RuleRunState, StaticContext

FLOW_RULES = frozenset({"SENT-012", "SENT-014", "SENT-015", "SENT-016"})
MIN_SOURCE_SIZE = 128 * 1024
WORKER = Path(__file__).resolve()


def run_flow_rules(
    context: StaticContext, selected: tuple[str, ...]
) -> dict[str, RuleRunState]:
    from sentinel.errors import InfrastructureError, SentinelError
    from sentinel.static.execution import check_deadline
    from sentinel.static.model import RuleRunState

    rules = tuple(rule for rule in selected if rule in FLOW_RULES)
    # ponytail: four workers only for large inputs; small scans avoid spawn cost.
    if (
        len(rules) < 2
        or (os.cpu_count() or 1) < 2
        or sum(len(file.source) for file in context.files.python_files)
        + sum(len(file.source) for file in context.files.typescript_files)
        < MIN_SOURCE_SIZE
    ):
        return {}
    # Parse once in the parent. Workers rebuild identity-keyed indexes, and their
    # rule traversals launch no subprocesses, so each worker can be reaped directly.
    trees = context.typescript_program.trees if context.files.typescript_files else {}
    check_deadline(context.deadline)
    processes: dict[str, subprocess.Popen[bytes]] = {}
    states = {}
    try:
        with (
            TemporaryDirectory(prefix="sentinel-static-") as directory,
            ExitStack() as stack,
        ):
            root = Path(directory)
            source = root / "input.pickle"
            source.write_bytes(
                pickle.dumps(
                    (context.configuration, context.files, context.deadline, trees)
                )
            )
            try:
                for rule in rules:
                    check_deadline(context.deadline)
                    log = stack.enter_context((root / f"{rule}.log").open("wb"))
                    processes[rule] = subprocess.Popen(
                        [
                            sys.executable,
                            "-I",
                            str(WORKER),
                            str(source),
                            str(root / f"{rule}.pickle"),
                            rule,
                        ],
                        cwd=WORKER.parent,
                        stdin=subprocess.DEVNULL,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                    )
                for rule, process in processes.items():
                    process.wait(
                        timeout=max(0.001, context.deadline - time.monotonic())
                    )
                    if process.returncode:
                        detail = (root / f"{rule}.log").read_text(errors="replace")[
                            -2000:
                        ]
                        raise InfrastructureError(
                            f"{rule} static worker exited {process.returncode}: "
                            f"{detail}"
                        )
                    # Both files are private IPC produced by this scanner, never target
                    # inputs. Pickle retains the existing canonical internal types.
                    result = pickle.loads((root / f"{rule}.pickle").read_bytes())
                    if isinstance(result, SentinelError):
                        raise result
                    if not isinstance(result, RuleRunState):
                        raise InfrastructureError(
                            f"{rule} static worker returned invalid state"
                        )
                    states[rule] = result
                check_deadline(context.deadline)
            finally:
                for process in processes.values():
                    if process.poll() is None:
                        process.kill()
                for process in processes.values():
                    process.wait()
    except subprocess.TimeoutExpired as error:
        raise InfrastructureError(
            "static analysis timeout: deadline exceeded"
        ) from error
    except (OSError, pickle.UnpicklingError, EOFError) as error:
        raise InfrastructureError("static worker communication failed") from error
    return states


def _worker() -> None:
    # Isolated Python ignores target CWD/PYTHONPATH. Only this installed scanner's
    # package root is added, including when checking an uninstalled source tree.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from sentinel.errors import InfrastructureError, SentinelError
    from sentinel.static.engine import _AST_DETECTORS
    from sentinel.static.model import RuleRunState, StaticContext

    source, destination, rule = sys.argv[1:]
    try:
        configuration, files, deadline, trees = pickle.loads(Path(source).read_bytes())
        context = StaticContext(configuration, files, deadline, trees)
        state = RuleRunState()
        _AST_DETECTORS[rule](context, state)
        result: RuleRunState | SentinelError = state
    except SentinelError as error:
        result = error
    except Exception as error:
        result = InfrastructureError(f"{rule} static worker failed: {error}")
    Path(destination).write_bytes(pickle.dumps(result))


if __name__ == "__main__":
    _worker()
