"""Verify built or indexed distributions through pip, pipx, and uv."""

from __future__ import annotations

import argparse
import configparser
import os
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from email.message import Message
from email.parser import BytesParser
from pathlib import Path

DIST_NAME = "portunusmcp-sentinel"
VERSION = "1.2.0"
WHEEL_NAME = "portunusmcp_sentinel-1.2.0-py3-none-any.whl"
SDIST_NAME = "portunusmcp_sentinel-1.2.0.tar.gz"
CLASSIFIERS = {
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Security",
    "Topic :: Software Development :: Quality Assurance",
}
KEYWORDS = {
    "ai-agents",
    "dynamic-analysis",
    "mcp",
    "model-context-protocol",
    "owasp",
    "sarif",
    "security",
    "static-analysis",
}
PROJECT_URLS = {
    "Repository": "https://github.com/BashaarJavaid/MCP-Sentinel",
    "Documentation": "https://bashaarjavaid.github.io/MCP-Sentinel/",
    "Changelog": (
        "https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/CHANGELOG.md"
    ),
    "Issues": "https://github.com/BashaarJavaid/MCP-Sentinel/issues",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    artifacts = commands.add_parser("artifacts")
    artifacts.add_argument("distribution_dir", type=Path)
    artifacts.add_argument("--install-sdist", action="store_true")
    index = commands.add_parser("index")
    index.add_argument("distribution")
    args = parser.parse_args()

    if args.command == "index":
        expected = f"{DIST_NAME}=={VERSION}"
        if args.distribution != expected:
            parser.error(f"expected exact distribution {expected}")
        _check_pipx(args.distribution)
        _check_uv(args.distribution)
        return 0

    wheel = _one(args.distribution_dir, "*.whl", WHEEL_NAME)
    sdist = _one(args.distribution_dir, "*.tar.gz", SDIST_NAME)
    _check_archives(wheel, sdist)
    _check_pip(wheel)
    if args.install_sdist:
        _check_pip(sdist)
    _check_pipx(wheel)
    _check_uv(wheel)
    return 0


def _one(directory: Path, pattern: str, expected_name: str) -> Path:
    matches = tuple(directory.glob(pattern))
    if len(matches) != 1:
        raise SystemExit(
            f"expected exactly one {pattern} in {directory}, found {len(matches)}"
        )
    artifact = matches[0].resolve()
    if artifact.name != expected_name:
        raise SystemExit(f"expected {expected_name}, found {artifact.name}")
    return artifact


def _check_archives(wheel: Path, sdist: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        metadata_name = _one_name(names, ".dist-info/METADATA")
        metadata = BytesParser().parsebytes(archive.read(metadata_name))
        entry_points_name = _one_name(names, ".dist-info/entry_points.txt")
        entry_points = archive.read(entry_points_name).decode("utf-8")
    _check_metadata(metadata)
    _check_entry_points(entry_points)
    for name in (
        "sentinel/_schemas/finding.schema.json",
        "sentinel/_schemas/report.schema.json",
        "sentinel/_schemas/gpt-review.schema.json",
        "sentinel/_schemas/sarif-2.1.0.schema.json",
        "sentinel/_fixtures/clean_server/server.py",
        "sentinel/_fixtures/vulnerable_server/server.py",
        "sentinel/_cassettes/demo/manifest.json",
    ):
        assert name in names, name
    assert not any("typescript_clean_server" in name for name in names)
    assert not any("typescript_vulnerable_server" in name for name in names)
    assert not any(name.endswith("/CHANGELOG.md") for name in names)
    assert not any(name.endswith(".pre-commit-hooks.yaml") for name in names)
    assert not any(name.endswith("phase12-gpt-smoke.json") for name in names)

    with tarfile.open(sdist, "r:gz") as archive:
        names = {member.name for member in archive.getmembers()}
        metadata_name = _one_name(names, "/PKG-INFO")
        metadata_file = archive.extractfile(metadata_name)
        assert metadata_file is not None
        sdist_metadata = BytesParser().parsebytes(metadata_file.read())
    _check_metadata(sdist_metadata)
    for suffix in (
        "/CHANGELOG.md",
        "/LICENSE",
        "/README.md",
        "/schemas/finding.schema.json",
        "/src/sentinel/_cassettes/demo/manifest.json",
        "/tests/fixtures/clean_server/server.py",
        "/tests/fixtures/vulnerable_server/server.py",
        "/tests/fixtures/typescript_clean_server/server.ts",
        "/tests/fixtures/typescript_vulnerable_server/server.ts",
    ):
        assert any(name.endswith(suffix) for name in names), suffix


def _one_name(names: set[str], suffix: str) -> str:
    matches = tuple(name for name in names if name.endswith(suffix))
    assert len(matches) == 1, (suffix, matches)
    return matches[0]


def _check_metadata(metadata: Message) -> None:
    assert metadata["Name"] == DIST_NAME
    assert metadata["Version"] == VERSION
    assert _csv(metadata["Requires-Python"]) == {">=3.10", "<3.14"}
    assert metadata["License-Expression"] == "MIT"
    assert "LICENSE" in (metadata.get_all("License-File") or [])
    assert set(metadata.get_all("Classifier") or []) == CLASSIFIERS
    assert _csv(metadata["Keywords"]) == KEYWORDS
    urls = {
        label.strip(): url.strip()
        for value in metadata.get_all("Project-URL") or []
        for label, separator, url in (value.partition(","),)
        if separator
    }
    assert urls == PROJECT_URLS
    requirements = metadata.get_all("Requires-Dist") or []
    _requirement(requirements, "mcp", (">=1.29.0", "<2"))
    _requirement(requirements, "openai", (">=2.46.0", "<3"))
    _requirement(requirements, "semgrep", ("==1.176.0",))


def _csv(value: str | None) -> set[str]:
    assert value is not None
    return {item.strip() for item in value.split(",")}


def _requirement(
    requirements: list[str], name: str, specifiers: tuple[str, ...]
) -> None:
    matches = tuple(value for value in requirements if value.startswith(name))
    assert len(matches) == 1, (name, matches)
    assert all(specifier in matches[0] for specifier in specifiers), matches[0]


def _check_entry_points(raw: str) -> None:
    parser = configparser.ConfigParser()
    parser.read_string(raw)
    assert dict(parser["console_scripts"]) == {"sentinel": "sentinel.cli:app"}


def _check_pip(wheel: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="sentinel-pip-smoke-") as directory:
        root = Path(directory)
        environment = root / "environment"
        _run(sys.executable, "-m", "venv", str(environment))
        python = _venv_python(environment)
        _run(str(python), "-m", "pip", "install", str(wheel))
        _check_install(python, _venv_bin(environment), resources=True)
        _check_typescript_scans(_venv_bin(environment))


def _check_pipx(distribution: str | Path) -> None:
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
            str(distribution),
            "--force",
            "--backend",
            "pip",
            "--python",
            sys.executable,
            env=environment,
        )
        tool = _tool_environment(root / "home" / "venvs")
        _check_install(_venv_python(tool), root / "bin", resources=True)


def _check_uv(distribution: str | Path) -> None:
    with tempfile.TemporaryDirectory(prefix="sentinel-uv-smoke-") as directory:
        root = Path(directory)
        environment = os.environ.copy()
        environment.update(
            {
                "UV_TOOL_DIR": str(root / "tools"),
                "UV_TOOL_BIN_DIR": str(root / "bin"),
                "UV_CACHE_DIR": str(root / "cache"),
            }
        )
        _run(
            "uv",
            "tool",
            "install",
            str(distribution),
            "--force",
            "--python",
            sys.executable,
            env=environment,
        )
        tool = _tool_environment(root / "tools")
        _check_install(_venv_python(tool), root / "bin", resources=True)


def _tool_environment(root: Path) -> Path:
    matches = tuple(path.parent for path in root.glob("*/pyvenv.cfg"))
    assert len(matches) == 1, matches
    return matches[0]


def _venv_bin(environment: Path) -> Path:
    return environment / ("Scripts" if os.name == "nt" else "bin")


def _venv_python(environment: Path) -> Path:
    return _venv_bin(environment) / ("python.exe" if os.name == "nt" else "python")


def _check_install(
    python: Path, executable_dir: Path, *, resources: bool = False
) -> None:
    sentinel = executable_dir / ("sentinel.exe" if os.name == "nt" else "sentinel")
    alias = executable_dir / ("mcp-sentinel.exe" if os.name == "nt" else "mcp-sentinel")
    assert sentinel.is_file(), sentinel
    assert not alias.exists(), alias
    _run(str(sentinel), "--version")
    _run(str(sentinel), "init", "--help")
    _run(str(sentinel), "scan", "--help")
    check = _IDENTITY_CHECK + (_RESOURCE_CHECK if resources else "")
    _run(str(python), "-c", check)


def _check_typescript_scans(executable_dir: Path) -> None:
    sentinel = executable_dir / ("sentinel.exe" if os.name == "nt" else "sentinel")
    fixtures = Path(__file__).resolve().parents[1] / "tests" / "fixtures"
    with tempfile.TemporaryDirectory(prefix="sentinel-typescript-smoke-") as directory:
        output = Path(directory) / "report.json"
        clean = subprocess.run(
            (
                str(sentinel),
                "scan",
                str(fixtures / "typescript_clean_server"),
                "--static-only",
                "--allow-degraded",
                "--format",
                "json",
                "--output",
                str(output),
            ),
            check=False,
        )
        assert clean.returncode == 0
        vulnerable = subprocess.run(
            (
                str(sentinel),
                "scan",
                str(fixtures / "typescript_vulnerable_server"),
                "--static-only",
                "--allow-degraded",
                "--format",
                "json",
                "--output",
                str(output),
            ),
            check=False,
        )
        assert vulnerable.returncode == 1


def _run(
    *command: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> None:
    subprocess.run(command, cwd=cwd, env=env, check=True)


_IDENTITY_CHECK = """
from importlib import metadata
import sentinel

distribution = metadata.distribution("portunusmcp-sentinel")
assert sentinel.__version__ == "1.2.0"
assert distribution.version == "1.2.0"
scripts = {
    item.name: item.value
    for item in distribution.entry_points
    if item.group == "console_scripts"
}
assert scripts == {"sentinel": "sentinel.cli:app"}
"""

_RESOURCE_CHECK = """
from importlib import resources
from sentinel.schema import schema_texts

root = resources.files("sentinel")
schemas = root.joinpath("_schemas")
for name, expected in schema_texts().items():
    assert schemas.joinpath(name).read_text(encoding="utf-8") == expected, name
assert schemas.joinpath("sarif-2.1.0.schema.json").is_file()
fixtures = root.joinpath("_fixtures")
assert fixtures.joinpath("clean_server", "server.py").is_file()
assert fixtures.joinpath("vulnerable_server", "server.py").is_file()
assert root.joinpath("_cassettes", "demo", "manifest.json").is_file()
"""


if __name__ == "__main__":
    raise SystemExit(main())
