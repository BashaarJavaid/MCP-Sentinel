"""Boundary-safe deterministic static file traversal."""

from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

import yaml
from pathspec import GitIgnoreSpec

from sentinel.config import DEFAULT_IGNORES
from sentinel.errors import ConfigurationError, TargetError
from sentinel.report.model import ReportWarning
from sentinel.static.model import ParsedPythonFile, StaticFileSet

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - exercised on the Python 3.10 CI job
    import tomli as tomllib

MAX_STATIC_FILE_BYTES = 1024 * 1024
_CONFIG_SUFFIXES = {".json", ".yaml", ".yml", ".toml"}
_DEFAULT_DIRS = {item.rstrip("/") for item in DEFAULT_IGNORES}


def collect_static_files(root: Path, ignore_paths: tuple[str, ...]) -> StaticFileSet:
    """Return parsed supported files without importing or executing target code."""

    python_files: list[ParsedPythonFile] = []
    config_files: list[Path] = []
    ignored = 0
    symlinks: list[str] = []
    ignore_specs: dict[Path, GitIgnoreSpec] = {}
    configured = GitIgnoreSpec.from_lines(ignore_paths)

    def visit(directory: Path) -> None:
        nonlocal ignored
        gitignore = directory / ".gitignore"
        if gitignore.is_file() and not gitignore.is_symlink():
            ignore_specs[directory] = _read_gitignore(gitignore)
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as error:
            raise TargetError(
                f"cannot traverse target directory: {directory}"
            ) from error
        for entry in entries:
            path = Path(entry.path)
            relative = path.relative_to(root).as_posix()
            if entry.is_symlink():
                ignored += 1
                symlinks.append(relative)
                continue
            if entry.is_dir(follow_symlinks=False):
                if entry.name in _DEFAULT_DIRS or _is_ignored(
                    relative + "/", path, root, ignore_specs, configured
                ):
                    continue
                visit(path)
                continue
            if not entry.is_file(follow_symlinks=False) or not _is_supported(path):
                continue
            if _is_ignored(relative, path, root, ignore_specs, configured):
                ignored += 1
                continue
            source = _read_supported(path)
            if path.suffix == ".py":
                try:
                    tree = ast.parse(source, filename=relative)
                except SyntaxError as error:
                    raise TargetError(
                        f"cannot parse Python source {relative}: {error.msg}"
                    ) from error
                python_files.append(
                    ParsedPythonFile(
                        path=path,
                        relative_path=relative,
                        source=source,
                        tree=tree,
                    )
                )
            else:
                _validate_config(path, relative, source)
                config_files.append(path)

    visit(root)
    warnings: list[ReportWarning] = []
    if symlinks:
        shown = ", ".join(symlinks[:20])
        suffix = "" if len(symlinks) <= 20 else ", ..."
        warnings.append(
            ReportWarning(
                code="static_symlinks_skipped",
                message=(f"Skipped {len(symlinks)} symlink entries: {shown}{suffix}"),
            )
        )
    return StaticFileSet(
        python_files=tuple(python_files),
        config_files=tuple(config_files),
        scanned_file_count=len(python_files) + len(config_files),
        ignored_file_count=ignored,
        warnings=tuple(warnings),
    )


def _is_supported(path: Path) -> bool:
    return (
        path.suffix == ".py"
        or path.suffix in _CONFIG_SUFFIXES
        or (path.name == ".env" or path.name.startswith(".env."))
    )


def _read_supported(path: Path) -> str:
    try:
        size = path.stat().st_size
    except OSError as error:
        raise TargetError(f"cannot stat supported file: {path.name}") from error
    if size > MAX_STATIC_FILE_BYTES:
        raise TargetError(f"supported file exceeds 1 MiB limit: {path.name}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise TargetError(f"supported file is not valid UTF-8: {path.name}") from error
    except OSError as error:
        raise TargetError(f"cannot read supported file: {path.name}") from error


def _read_gitignore(path: Path) -> GitIgnoreSpec:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise TargetError(f"cannot read .gitignore: {path}") from error
    return GitIgnoreSpec.from_lines(content.splitlines())


def _is_ignored(
    relative: str,
    path: Path,
    root: Path,
    specs: dict[Path, GitIgnoreSpec],
    configured: GitIgnoreSpec,
) -> bool:
    ignored = False
    ancestors = (path.parent, *path.parents)
    for directory in reversed(ancestors):
        if directory == root.parent:
            continue
        try:
            directory.relative_to(root)
        except ValueError:
            continue
        spec = specs.get(directory)
        if spec is None:
            continue
        scoped = path.relative_to(directory).as_posix()
        if relative.endswith("/") and not scoped.endswith("/"):
            scoped += "/"
        result = spec.check_file(scoped)
        if result.include is not None:
            ignored = result.include
    if configured.match_file(relative):
        return True
    return ignored


def _validate_config(path: Path, relative: str, source: str) -> None:
    try:
        if path.suffix == ".json":
            json.loads(source)
        elif path.suffix in {".yaml", ".yml"}:
            yaml.safe_load(source)
        elif path.suffix == ".toml":
            tomllib.loads(source)
        else:
            _validate_dotenv(source)
    except (json.JSONDecodeError, yaml.YAMLError, tomllib.TOMLDecodeError) as error:
        raise ConfigurationError(
            f"cannot parse configuration {relative}: {error}"
        ) from error


def _validate_dotenv(source: str) -> None:
    for number, raw in enumerate(source.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise ConfigurationError(f"invalid dotenv syntax on line {number}")
        name, value = line.split("=", 1)
        if not name.strip().isidentifier():
            raise ConfigurationError(f"invalid dotenv name on line {number}")
        value = value.strip()
        if value.startswith(("'", '"')) and (len(value) < 2 or value[-1] != value[0]):
            raise ConfigurationError(f"unterminated dotenv quote on line {number}")
