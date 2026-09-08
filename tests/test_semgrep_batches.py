"""Batch the selected source paths without repeated small-process startup costs."""

import ast
import json
import subprocess
import time
from pathlib import Path
from typing import Any

import pytest

from sentinel.static import semgrep_adapter
from sentinel.static.model import ParsedPythonFile, StaticFileSet


@pytest.mark.parametrize("budget", [100_000, 2_000])
def test_batches_keep_every_selected_path_within_argument_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, budget: int
) -> None:
    files = tuple(
        ParsedPythonFile(
            tmp_path / f"file-{i:04}.py",
            f"file-{i:04}.py",
            "",
            ast.Module(body=[], type_ignores=[]),
        )
        for i in range(500)
    )
    selected = StaticFileSet(files, (), (), len(files), 0, ())
    batches: list[list[str]] = []

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        output = Path(command[command.index("--output") + 1])
        output.write_text(json.dumps({"results": [], "errors": []}), encoding="utf-8")
        batches.append([arg for arg in command if arg.endswith(".py")])
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(semgrep_adapter, "SEMGREP_BATCH_BYTES", budget, raising=False)
    monkeypatch.setattr("sentinel.static.semgrep_adapter.subprocess.run", run)
    semgrep_adapter.run_semgrep(
        selected, ("SENT-005",), tmp_path, deadline=time.monotonic() + 20
    )
    assert [path for batch in batches for path in batch] == [
        str(file.path) for file in files
    ]
    assert all(
        sum(len(path.encode("utf-8")) + 3 for path in batch) <= budget
        for batch in batches
    )
    if budget == 100_000:
        assert len(batches) == 1
