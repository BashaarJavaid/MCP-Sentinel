"""Install one wheel through pip and pipx, then verify packaged resources."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel_dir", type=Path)
    args = parser.parse_args()
    wheels = tuple(args.wheel_dir.glob("*.whl"))
    if len(wheels) != 1:
        parser.error(
            f"expected exactly one wheel in {args.wheel_dir}, found {len(wheels)}"
        )
    wheel = wheels[0].resolve()

    _run(sys.executable, "-m", "pip", "install", str(wheel))
    with tempfile.TemporaryDirectory(prefix="sentinel-wheel-smoke-") as directory:
        cwd = Path(directory)
        _run(sys.executable, "-m", "sentinel", "--version", cwd=cwd)
        _run(sys.executable, "-m", "sentinel", "scan", "--help", cwd=cwd)
        _run(sys.executable, "-c", _RESOURCE_CHECK, cwd=cwd)

    with tempfile.TemporaryDirectory(prefix="sentinel-pipx-smoke-") as directory:
        root = Path(directory)
        environment = os.environ.copy()
        environment.update(
            {
                "PIPX_HOME": str(root / "home"),
                "PIPX_BIN_DIR": str(root / "bin"),
                "PIPX_MAN_DIR": str(root / "man"),
            }
        )
        _run(
            sys.executable,
            "-m",
            "pipx",
            "install",
            str(wheel),
            "--force",
            "--backend",
            "pip",
            env=environment,
        )
        _run(
            sys.executable,
            "-m",
            "pipx",
            "runpip",
            "mcp-sentinel",
            "show",
            "mcp-sentinel",
            env=environment,
        )
    return 0


def _run(
    *command: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> None:
    subprocess.run(command, cwd=cwd, env=env, check=True)


_RESOURCE_CHECK = """
from importlib import resources

root = resources.files("sentinel")
schemas = root.joinpath("_schemas")
for name in (
    "finding.schema.json",
    "report.schema.json",
    "gpt-review.schema.json",
    "sarif-2.1.0.schema.json",
):
    assert schemas.joinpath(name).is_file(), name
fixtures = root.joinpath("_fixtures")
assert fixtures.joinpath("clean_server", "server.py").is_file()
assert fixtures.joinpath("vulnerable_server", "server.py").is_file()
assert root.joinpath("_cassettes", "demo", "manifest.json").is_file()
"""


if __name__ == "__main__":
    raise SystemExit(main())
