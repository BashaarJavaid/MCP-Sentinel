"""Read declared local workspace directories without running package managers."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from sentinel.errors import TargetError


@dataclass(frozen=True)
class WorkspaceIssue:
    path: str
    reason: str


@dataclass(frozen=True)
class WorkspaceLayout:
    members: tuple[str, ...]
    declarations: tuple[str, ...]
    issues: tuple[WorkspaceIssue, ...]


def _metadata(path: Path) -> dict[str, Any] | None:
    from sentinel.config import MAX_MANIFEST_BYTES, _read_toml, _read_yaml

    if path.is_symlink():
        raise TargetError(f"workspace metadata cannot be a symbolic link: {path.name}")
    try:
        if not path.exists():
            return None
        if not path.is_file() or path.stat().st_size > MAX_MANIFEST_BYTES:
            raise TargetError(
                f"workspace metadata must be a regular file below 1 MiB: {path.name}"
            )
        if path.suffix == ".toml":
            return _read_toml(path, required=True)
        if path.suffix == ".yaml":
            return _read_yaml(path)
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise TargetError(f"{path.name} must contain strict JSON: {error}") from error
    except (OSError, ValueError) as error:
        raise TargetError(f"cannot read workspace metadata: {path.name}") from error
    if not isinstance(value, dict):
        raise TargetError(f"workspace metadata must contain an object: {path.name}")
    return value


def _patterns(value: Any, source: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise TargetError(f"{source}: workspace patterns must be nonempty strings")
    patterns = []
    for raw in value:
        negative, pattern = (True, raw[1:]) if raw.startswith("!") else (False, raw)
        normalized = pattern.replace("\\", "/")
        if (
            not normalized
            or PurePosixPath(normalized).is_absolute()
            or PureWindowsPath(pattern).is_absolute()
            or PureWindowsPath(pattern).drive
            or ".." in normalized.split("/")
        ):
            raise TargetError(
                f"{source}: workspace declaration escapes the scan boundary"
            )
        normalized = str(PurePosixPath(normalized))
        patterns.append(("!" if negative else "") + normalized)
    return tuple(patterns)


def _matches(path: str, pattern: str) -> bool:
    parts, patterns = path.split("/"), pattern.split("/")
    positions = {0}
    for component in patterns:
        if component == "**":
            positions = (
                set(range(min(positions), len(parts) + 1)) if positions else set()
            )
        else:
            positions = {
                i + 1
                for i in positions
                if i < len(parts) and fnmatchcase(parts[i], component)
            }
    return len(parts) in positions


def discover_workspace(root: Path) -> WorkspaceLayout | None:
    from sentinel.config import DEFAULT_IGNORES

    if root.is_symlink():
        raise TargetError("workspace root cannot be a symbolic link")
    declarations: list[tuple[str, tuple[str, ...], str]] = []
    project = _metadata(root / "pyproject.toml")
    if project:
        tool = project.get("tool", {})
        if not isinstance(tool, dict) or not isinstance(tool.get("uv", {}), dict):
            raise TargetError("tool.uv must be a table")
        uv = tool.get("uv", {})
        if "workspace" in uv:
            workspace = uv["workspace"]
            if not isinstance(workspace, dict):
                raise TargetError("tool.uv.workspace must be a table")
            uv_members = _patterns(
                workspace.get("members", []), "tool.uv.workspace.members"
            )
            excludes = _patterns(
                workspace.get("exclude", []), "tool.uv.workspace.exclude"
            )
            declarations.append(
                (
                    "pyproject.toml",
                    (*uv_members, *("!" + item for item in excludes)),
                    "pyproject.toml",
                )
            )
    package = _metadata(root / "package.json")
    if package is not None and "workspaces" in package:
        workspaces = package["workspaces"]
        if isinstance(workspaces, dict):
            workspaces = workspaces.get("packages")
        declarations.append(
            (
                "package.json",
                _patterns(workspaces, "package.json workspaces"),
                "package.json",
            )
        )
    pnpm = _metadata(root / "pnpm-workspace.yaml")
    if pnpm is not None:
        declarations.append(
            (
                "pnpm-workspace.yaml",
                _patterns(pnpm.get("packages", []), "pnpm packages"),
                "package.json",
            )
        )
    if not declarations:
        return None

    directories: dict[str, str | None] = {".": None}
    ignored = {item.rstrip("/") for item in DEFAULT_IGNORES}

    def inaccessible(error: OSError) -> None:
        path = Path(error.filename or root)
        directories[path.relative_to(root).as_posix()] = "inaccessible member directory"

    for directory, names, _ in os.walk(root, followlinks=False, onerror=inaccessible):
        for name in sorted(names):
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                directories[relative] = "symbolic-link member is not traversed"
                names.remove(name)
            elif name in ignored:
                directories[relative] = (
                    "member is excluded by the default traversal boundary"
                )
                names.remove(name)
            else:
                directories[relative] = None
        names.sort()

    members = {"."}
    issues: set[WorkspaceIssue] = set()
    for source, patterns, manifest in declarations:
        unsupported = {
            pattern
            for pattern in patterns
            if any(
                token in pattern for token in ("{", "}", "@(", "+(", "!(", "?(", "*(")
            )
        }
        issues.update(
            WorkspaceIssue(
                pattern.removeprefix("!"), f"{source}: unsupported workspace glob"
            )
            for pattern in unsupported
        )
        patterns = tuple(pattern for pattern in patterns if pattern not in unsupported)
        positive = [pattern for pattern in patterns if not pattern.startswith("!")]
        negative = [pattern[1:] for pattern in patterns if pattern.startswith("!")]
        for pattern in positive:
            matched = [path for path in directories if _matches(path, pattern)]
            if not matched:
                issues.add(
                    WorkspaceIssue(
                        pattern,
                        f"{source}: member is missing or cannot be reached",
                    )
                )
            for relative in matched:
                if any(_matches(relative, exclude) for exclude in negative):
                    continue
                if directories[relative]:
                    issues.add(
                        WorkspaceIssue(
                            relative, directories[relative] or "inaccessible member"
                        )
                    )
                    continue
                path = root / relative / manifest
                if relative == "." or (not path.is_symlink() and path.is_file()):
                    members.add(relative)
                else:
                    issues.add(
                        WorkspaceIssue(
                            relative, f"{source}: member lacks a regular {manifest}"
                        )
                    )
    return WorkspaceLayout(
        tuple(sorted(members)),
        tuple(source for source, _, _ in declarations),
        tuple(sorted(issues, key=lambda issue: (issue.path, issue.reason))),
    )
