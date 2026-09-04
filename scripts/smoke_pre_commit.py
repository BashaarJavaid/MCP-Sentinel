"""Exercise the public pre-commit hook against the paired fixtures."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT)
    parser.add_argument("--revision")
    args = parser.parse_args()
    source = args.source.resolve()
    revision = (
        args.revision or _run(("git", "rev-parse", "HEAD"), cwd=source).stdout.strip()
    )
    with tempfile.TemporaryDirectory(prefix="sentinel-pre-commit-") as raw:
        temporary = Path(raw)
        cache = temporary / "cache"
        cases = (
            ("clean", ROOT / "tests/fixtures/clean_server", 0),
            ("vulnerable", ROOT / "tests/fixtures/vulnerable_server", 1),
            ("suppressed", ROOT / "tests/fixtures/vulnerable_server", 0),
        )
        for name, fixture, expected in cases:
            target = temporary / name
            shutil.copytree(fixture, target)
            if name == "suppressed":
                server = target / "server.py"
                server.write_text(
                    server.read_text(encoding="utf-8").replace(
                        'api_key = "ghp_0123456789abcdefghijklmnop"',
                        'api_key = "ghp_0123456789abcdefghijklmnop"  '
                        "# sentinel: ignore[SENT-005] reason=fixture credential",
                    ),
                    encoding="utf-8",
                )
            (target / ".pre-commit-config.yaml").write_text(
                yaml.safe_dump(
                    {
                        "minimum_pre_commit_version": "4.6.2",
                        "repos": [
                            {
                                "repo": source.as_uri(),
                                "rev": revision,
                                "hooks": [
                                    {
                                        "id": "mcp-sentinel",
                                        "args": ["--rules", "SENT-005"],
                                        "verbose": True,
                                    }
                                ],
                            }
                        ],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            _initialize(target)
            completed = _run(
                (
                    sys.executable,
                    "-m",
                    "pre_commit",
                    "run",
                    "--all-files",
                    "--show-diff-on-failure",
                ),
                cwd=target,
                env={**os.environ, "PRE_COMMIT_HOME": str(cache)},
                check=False,
            )
            output = completed.stdout + completed.stderr
            if completed.returncode != expected:
                raise RuntimeError(
                    f"{name} pre-commit exit {completed.returncode}, expected "
                    f"{expected}:\n{output}"
                )
            if name == "suppressed" and "Inline suppression:" not in output:
                raise RuntimeError("suppressed pre-commit case hid its audit reason")
            print(f"{name}: exit {completed.returncode}")
    return 0


def _initialize(target: Path) -> None:
    _run(("git", "init", "-q"), cwd=target)
    _run(("git", "config", "user.name", "MCP Sentinel CI"), cwd=target)
    _run(("git", "config", "user.email", "sentinel@example.invalid"), cwd=target)
    _run(("git", "add", "."), cwd=target)
    _run(("git", "commit", "-qm", "fixture"), cwd=target)


def _run(
    command: tuple[str, ...],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=check,
        text=True,
        capture_output=True,
    )


if __name__ == "__main__":
    raise SystemExit(main())
