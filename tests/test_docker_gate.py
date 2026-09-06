"""An explicitly selected Docker gate must not succeed by skipping a control."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("selected", [False, True])
def test_selected_docker_skips_fail_the_gate(tmp_path: Path, selected: bool) -> None:
    test = tmp_path / "test_skipped_control.py"
    test.write_text(
        "import pytest\n@pytest.mark.docker\n"
        '@pytest.mark.skip(reason="synthetic unavailable control")\n'
        "def test_control():\n    pass\n"
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "tests.conftest",
            "-c",
            "pyproject.toml",
            "--no-cov",
            "-q",
            str(test),
        ],
        env={**os.environ, "SENTINEL_RUN_DOCKER_TESTS": "1" if selected else "0"},
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == (1 if selected else 0), result.stdout + result.stderr
    if selected:
        assert (
            "required, explicitly selected Docker control was skipped" in result.stdout
        )
    else:
        assert "1 skipped" in result.stdout
