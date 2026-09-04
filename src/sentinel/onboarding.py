"""Static first-run configuration generation."""

from __future__ import annotations

import ast
import os
import shlex
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from packaging.requirements import InvalidRequirement, Requirement

from sentinel.config import (
    SentinelConfig,
    TargetConfig,
    TargetLanguage,
    _detect_target_language,
    _normalize_package_name,
    _read_toml,
    infer_python_version,
    validate_scan_root,
)
from sentinel.errors import ConfigurationError, InfrastructureError, TargetError
from sentinel.llm.tools import extract_tool_catalog
from sentinel.permissions import (
    PermissionsManifest,
    ToolPermissions,
    validate_permission_scopes,
)
from sentinel.report.model import ReportWarning
from sentinel.static.model import ParsedPythonFile
from sentinel.static.traversal import MAX_STATIC_FILE_BYTES, collect_static_files

TARGET_NAME = "sentinel.target.yaml"
PERMISSIONS_NAME = "sentinel.permissions.yaml"
_GENERATED_NAMES = (TARGET_NAME, PERMISSIONS_NAME)
_SUPPORTED_PACKAGES = frozenset({"mcp", "fastmcp"})


@dataclass(frozen=True)
class GeneratedFile:
    name: str
    status: str


@dataclass(frozen=True)
class OnboardingResult:
    files: tuple[GeneratedFile, ...]
    warnings: tuple[ReportWarning, ...]
    language: TargetLanguage = TargetLanguage.PYTHON


@dataclass(frozen=True)
class _DependencyLayout:
    package_roots: frozenset[str]
    install_cmd: tuple[str, ...] | None
    description: str


@dataclass(frozen=True)
class _OriginalFile:
    content: bytes | None
    mode: int


def initialize_repository(scan_path: Path, *, force: bool) -> OnboardingResult:
    """Inspect a repository without execution and atomically write starter files."""

    root = validate_scan_root(scan_path)
    scanner = _project_configuration(root)
    ignore_paths = scanner.scanner.ignore_paths
    try:
        language = _detect_target_language(root, ignore_paths)
    except TargetError as error:
        if not str(error).startswith("unsupported target:"):
            raise
        # Preserve the established, more specific Python onboarding diagnostics.
        language = TargetLanguage.PYTHON
    names = (
        (PERMISSIONS_NAME,)
        if language is TargetLanguage.TYPESCRIPT
        else _GENERATED_NAMES
    )
    destinations = tuple(root / name for name in names)
    originals = _preflight_destinations(destinations, force=force)
    if force:
        ignore_paths = (*ignore_paths, *names)
    files = collect_static_files(root, ignore_paths, language)
    catalog = extract_tool_catalog(root, ignore_paths, language)
    permissions = PermissionsManifest(
        version=1,
        tools={tool.name: ToolPermissions() for tool in catalog.tools},
    )
    validate_permission_scopes(permissions)
    contents: tuple[bytes, ...]
    if language is TargetLanguage.PYTHON:
        dependencies = _dependency_layout(root)
        entry_point = _entry_point(files.python_files, dependencies.package_roots)
        target = TargetConfig.model_validate(
            {
                "language": "python",
                "launch_cmd": ["python", entry_point],
                "install_cmd": list(dependencies.install_cmd)
                if dependencies.install_cmd is not None
                else None,
                "transport": "stdio",
                "working_dir": ".",
                "env": {},
                "env_from": [],
                "python_version": infer_python_version(root),
            }
        )
        contents = (
            _target_yaml(target, dependencies.description),
            _permissions_yaml(permissions),
        )
    else:
        contents = (_permissions_yaml(permissions),)
    statuses = _replace_transaction(destinations, originals, contents)
    warnings = list(catalog.warnings)
    if not catalog.tools:
        warnings.append(
            ReportWarning(
                code="tool_catalog_empty",
                message="No MCP tools were discovered; generated tools: {}.",
            )
        )
    return OnboardingResult(
        files=tuple(
            GeneratedFile(name=name, status=status)
            for name, status in zip(names, statuses, strict=True)
        ),
        warnings=tuple(warnings),
        language=language,
    )


def next_scan_command(path: str, *, static_only: bool = False) -> str:
    command = ("sentinel", "scan", path, *(("--static-only",) if static_only else ()))
    return subprocess.list2cmdline(command) if os.name == "nt" else shlex.join(command)


def display_path(root: str, name: str) -> str:
    return os.path.join(root, name)


def _project_configuration(root: Path) -> SentinelConfig:
    data = _read_toml(root / "sentinel.toml", required=False)
    try:
        return SentinelConfig.model_validate(data)
    except Exception as error:
        raise ConfigurationError(f"invalid scanner configuration: {error}") from error


def _dependency_layout(root: Path) -> _DependencyLayout:
    requirements = root / "requirements.txt"
    if os.path.lexists(requirements):
        if requirements.is_symlink() or not requirements.is_file():
            raise TargetError("requirements.txt must be a regular file")
        entries = _requirement_entries(
            _read_dependency_file(requirements), requirements.name
        )
        roots = _supported_roots(entries)
        if not roots:
            raise TargetError(
                "requirements.txt must declare the official 'mcp' or 'fastmcp' "
                "dependency"
            )
        return _DependencyLayout(
            package_roots=roots,
            install_cmd=("python", "-m", "pip", "install", "-r", "requirements.txt"),
            description=_dependency_description("requirements.txt", entries),
        )

    pyproject = root / "pyproject.toml"
    if pyproject.is_symlink() or (pyproject.exists() and not pyproject.is_file()):
        raise TargetError("pyproject.toml must be a regular file")
    if not pyproject.is_file():
        if _nested_requirements_exist(root):
            raise TargetError(
                "nested requirements files are unsupported; use requirements.txt"
            )
        raise TargetError(
            "missing requirements.txt or pyproject.toml dependency manifest"
        )
    data = _read_toml(pyproject, required=True)
    project = data.get("project")
    dependencies = project.get("dependencies") if isinstance(project, dict) else None
    if not isinstance(dependencies, list) or not all(
        isinstance(item, str) for item in dependencies
    ):
        if _optional_mcp_dependency(data):
            raise TargetError(
                "optional dependency groups are unsupported; declare MCP in "
                "project.dependencies"
            )
        if isinstance(data.get("tool"), dict) and isinstance(
            data["tool"].get("poetry"), dict
        ):
            raise TargetError(
                "Poetry-only dependency configuration is unsupported; use PEP 621"
            )
        if _nested_requirements_exist(root):
            raise TargetError(
                "nested requirements files are unsupported; use requirements.txt"
            )
        raise TargetError("pyproject.toml project.dependencies must be a string list")
    entries = _requirement_entries(dependencies, "pyproject.toml project.dependencies")
    roots = _supported_roots(entries)
    if not roots:
        if _optional_mcp_dependency(data):
            raise TargetError(
                "optional dependency groups are unsupported; declare MCP in "
                "project.dependencies"
            )
        raise TargetError(
            "pyproject.toml project.dependencies must declare the official 'mcp' "
            "or 'fastmcp' dependency"
        )
    return _DependencyLayout(
        package_roots=roots,
        install_cmd=None,
        description=_dependency_description(
            "pyproject.toml project.dependencies", entries
        ),
    )


def _read_dependency_file(path: Path) -> list[str]:
    try:
        if path.stat().st_size > MAX_STATIC_FILE_BYTES:
            raise TargetError("requirements.txt exceeds the 1 MiB limit")
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise TargetError("requirements.txt is not valid UTF-8") from error
    except OSError as error:
        raise TargetError("cannot read requirements.txt") from error


def _requirement_entries(entries: list[Any], label: str) -> tuple[Requirement, ...]:
    parsed: list[Requirement] = []
    for number, value in enumerate(entries, start=1):
        if not isinstance(value, str):
            raise TargetError(f"{label} entry {number} must be a string")
        line = value.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith("\\"):
            raise TargetError(
                f"{label} entry {number} uses an unsupported continuation"
            )
        if line.startswith("-"):
            raise TargetError(
                f"{label} entry {number} uses an unsupported pip directive"
            )
        try:
            requirement = Requirement(line)
        except InvalidRequirement as error:
            raise TargetError(
                f"invalid requirement in {label} entry {number}: {line}"
            ) from error
        if requirement.url is not None:
            raise TargetError(f"{label} entry {number} uses an unsupported direct URL")
        parsed.append(requirement)
    return tuple(parsed)


def _supported_roots(entries: tuple[Requirement, ...]) -> frozenset[str]:
    return frozenset(
        _normalize_package_name(item.name)
        for item in entries
        if _normalize_package_name(item.name) in _SUPPORTED_PACKAGES
    )


def _dependency_description(label: str, entries: tuple[Requirement, ...]) -> str:
    selected = sorted(
        str(item)
        for item in entries
        if _normalize_package_name(item.name) in _SUPPORTED_PACKAGES
    )
    return f"{label} ({', '.join(selected)})"


def _optional_mcp_dependency(data: dict[str, Any]) -> bool:
    project = data.get("project")
    groups = project.get("optional-dependencies") if isinstance(project, dict) else None
    if not isinstance(groups, dict):
        return False
    return any(
        _supported_roots(_requirement_entries(values, "optional dependency group"))
        for values in groups.values()
        if isinstance(values, list)
    )


def _nested_requirements_exist(root: Path) -> bool:
    directory = root / "requirements"
    return (
        directory.is_dir()
        and not directory.is_symlink()
        and any(
            path.is_file() and not path.is_symlink() for path in directory.glob("*.txt")
        )
    )


def _entry_point(
    python_files: tuple[ParsedPythonFile, ...], package_roots: frozenset[str]
) -> str:
    candidates = sorted(
        parsed.relative_path
        for parsed in python_files
        if _has_main_guard(parsed.tree)
        and _constructs_supported_server(parsed.tree, package_roots)
    )
    if not candidates:
        raise TargetError(
            "could not detect an MCP entry point with a canonical __main__ guard"
        )
    if len(candidates) > 1:
        raise TargetError(
            "multiple MCP entry points detected: " + ", ".join(candidates)
        )
    return candidates[0]


def _has_main_guard(tree: ast.Module) -> bool:
    return any(
        isinstance(node, ast.If) and _is_main_comparison(node.test)
        for node in tree.body
    )


def _is_main_comparison(node: ast.expr) -> bool:
    if (
        not isinstance(node, ast.Compare)
        or len(node.ops) != 1
        or not isinstance(node.ops[0], ast.Eq)
        or len(node.comparators) != 1
    ):
        return False
    sides = (node.left, node.comparators[0])
    return any(
        isinstance(side, ast.Name) and side.id == "__name__" for side in sides
    ) and any(
        isinstance(side, ast.Constant) and side.value == "__main__" for side in sides
    )


def _constructs_supported_server(
    tree: ast.Module, package_roots: frozenset[str]
) -> bool:
    imports: dict[str, tuple[str, str]] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.partition(".")[0]
                local = alias.asname or root
                imports[local] = (root, alias.name if alias.asname else root)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            root = node.module.partition(".")[0]
            for alias in node.names:
                if alias.name != "*":
                    imports[alias.asname or alias.name] = (
                        root,
                        f"{node.module}.{alias.name}",
                    )
    for candidate in ast.walk(tree):
        if not isinstance(candidate, ast.Call):
            continue
        resolved = _resolve_import(candidate.func, imports)
        if resolved is None:
            continue
        root, qualified = resolved
        if root in package_roots and qualified.rpartition(".")[2] in {
            "FastMCP",
            "Server",
        }:
            return True
    return False


def _resolve_import(
    node: ast.expr, imports: dict[str, tuple[str, str]]
) -> tuple[str, str] | None:
    if isinstance(node, ast.Name):
        return imports.get(node.id)
    if isinstance(node, ast.Attribute):
        parent = _resolve_import(node.value, imports)
        if parent is not None:
            return parent[0], f"{parent[1]}.{node.attr}"
    return None


def _target_yaml(target: TargetConfig, dependency: str) -> bytes:
    launch = shlex.join(target.launch_cmd)
    comment = (
        "# Sentinel executes this target only inside its Docker sandbox.\n"
        f"# Detected launch: {launch}\n"
        f"# Detected dependencies: {dependency}\n"
    )
    return (
        comment + _dump_yaml(target.model_dump(mode="json", exclude_none=True))
    ).encode()


def _permissions_yaml(permissions: PermissionsManifest) -> bytes:
    comment = (
        "# Permissions start deny-by-default.\n"
        "# Grant only reviewed filesystem and network scopes required by each tool.\n"
    )
    return (
        comment + _dump_yaml(permissions.model_dump(mode="json", exclude_none=True))
    ).encode()


def _dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)


def _preflight_destinations(
    destinations: tuple[Path, ...], *, force: bool
) -> tuple[_OriginalFile, ...]:
    existing = tuple(path for path in destinations if os.path.lexists(path))
    if existing and not force:
        raise ConfigurationError(
            "generated configuration already exists: "
            + ", ".join(path.name for path in existing)
            + "; use --force to replace regular files"
        )
    originals: list[_OriginalFile] = []
    for path in destinations:
        if not os.path.lexists(path):
            originals.append(_OriginalFile(content=None, mode=0o644))
            continue
        try:
            metadata = path.lstat()
            if not stat.S_ISREG(metadata.st_mode):
                raise ConfigurationError(f"{path.name} must be a regular file")
            originals.append(
                _OriginalFile(
                    content=path.read_bytes(), mode=stat.S_IMODE(metadata.st_mode)
                )
            )
        except ConfigurationError:
            raise
        except OSError as error:
            raise ConfigurationError(f"cannot read {path.name}: {error}") from error
    return tuple(originals)


def _replace_transaction(
    destinations: tuple[Path, ...],
    originals: tuple[_OriginalFile, ...],
    contents: tuple[bytes, ...],
) -> tuple[str, ...]:
    changed = tuple(
        index
        for index, (original, content) in enumerate(
            zip(originals, contents, strict=True)
        )
        if original.content != content
    )
    statuses = tuple(
        "Unchanged"
        if original.content == content
        else "Created"
        if original.content is None
        else "Updated"
        for original, content in zip(originals, contents, strict=True)
    )
    if not changed:
        return statuses

    staged: dict[int, Path] = {}
    try:
        for index in changed:
            staged[index] = _temporary_file(
                destinations[index], contents[index], originals[index].mode
            )
    except OSError as error:
        for path in staged.values():
            path.unlink(missing_ok=True)
        raise InfrastructureError(
            f"cannot stage generated configuration: {error}"
        ) from error
    try:
        for index in changed:
            os.replace(staged[index], destinations[index])
    except OSError as error:
        rollback_errors: list[str] = []
        for index in changed:
            destination = destinations[index]
            original = originals[index]
            try:
                if original.content is None:
                    if os.path.lexists(destination):
                        destination.unlink()
                else:
                    restore = _temporary_file(
                        destination, original.content, original.mode
                    )
                    try:
                        os.replace(restore, destination)
                    finally:
                        restore.unlink(missing_ok=True)
            except OSError as rollback_error:
                rollback_errors.append(f"{destination.name}: {rollback_error}")
        detail = (
            f"; rollback failed for {', '.join(rollback_errors)}"
            if rollback_errors
            else ""
        )
        raise InfrastructureError(
            f"configuration transaction failed: {error}{detail}"
        ) from error
    finally:
        for path in staged.values():
            path.unlink(missing_ok=True)
    return statuses


def _temporary_file(destination: Path, content: bytes, mode: int) -> Path:
    descriptor, name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        return temporary
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
