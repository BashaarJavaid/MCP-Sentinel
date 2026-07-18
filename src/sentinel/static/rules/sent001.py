"""SENT-001 overly broad permission analysis."""

from __future__ import annotations

import ast
from urllib.parse import urlparse

import yaml
from pydantic import Field, field_validator

from sentinel.errors import UsageError
from sentinel.finding import ContractModel
from sentinel.static.ast_utils import (
    discover_tool_regions,
    literal_string,
    match_from_node,
    qualified_name,
)
from sentinel.static.model import RuleRunState, StaticContext


class Capability(ContractModel):
    scopes: tuple[str, ...] = ()
    broad_scope_justification: str | None = None

    @field_validator("scopes", mode="before")
    @classmethod
    def list_to_tuple(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @field_validator("broad_scope_justification")
    @classmethod
    def normalize_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not value.strip():
            raise ValueError("broad scope justification cannot be empty")
        return value.strip()


class FilesystemPermissions(ContractModel):
    read: Capability = Field(default_factory=Capability)
    write: Capability = Field(default_factory=Capability)


class ToolPermissions(ContractModel):
    filesystem: FilesystemPermissions = Field(default_factory=FilesystemPermissions)
    network: Capability = Field(default_factory=Capability)


class PermissionsManifest(ContractModel):
    version: int
    tools: dict[str, ToolPermissions]

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: int) -> int:
        if value != 1:
            raise ValueError("permissions manifest version must be 1")
        return value


def detect(context: StaticContext, state: RuleRunState) -> None:
    path = context.configuration.scan_root / "sentinel.permissions.yaml"
    if not path.exists():
        state.skip_reason = "sentinel.permissions.yaml is absent"
        return
    if path.is_symlink() or not path.is_file():
        raise UsageError("sentinel.permissions.yaml must be a regular file")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        manifest = PermissionsManifest.model_validate(raw)
    except Exception as error:
        raise UsageError(f"invalid sentinel.permissions.yaml: {error}") from error
    _validate_scopes(manifest)

    for file in context.files.python_files:
        for region in discover_tool_regions(file):
            declared = manifest.tools.get(region.name)
            if declared is None:
                state.matches.append(
                    match_from_node(
                        "SENT-001", file, region.node, "missing-tool-permissions"
                    )
                )
                continue
            actual = _actual_usage(region.node)
            capabilities = (
                ("filesystem.read", declared.filesystem.read, actual[0]),
                ("filesystem.write", declared.filesystem.write, actual[1]),
                ("network", declared.network, actual[2]),
            )
            for name, capability, used in capabilities:
                broad = _is_broader(capability.scopes, used)
                if not broad:
                    continue
                if capability.broad_scope_justification:
                    state.exempt(f"justified_{name}")
                    continue
                node = actual[3].get(name, region.node)
                state.matches.append(
                    match_from_node("SENT-001", file, node, f"broad-{name}")
                )


def _actual_usage(
    node: ast.AST,
) -> tuple[set[str], set[str], set[str], dict[str, ast.AST]]:
    reads: set[str] = set()
    writes: set[str] = set()
    hosts: set[str] = set()
    evidence: dict[str, ast.AST] = {}
    for item in ast.walk(node):
        if not isinstance(item, ast.Call):
            continue
        name = qualified_name(item.func) or ""
        if name in {"open", "Path.open"} or name.endswith(
            (".open", ".read_text", ".write_text")
        ):
            argument = (
                item.args[0]
                if item.args and name == "open"
                else (item.func.value if isinstance(item.func, ast.Attribute) else None)
            )
            path = literal_string(argument)
            mode = literal_string(item.args[1]) if len(item.args) > 1 else None
            is_write = name.endswith(".write_text") or bool(
                mode and any(character in mode for character in "wax+")
            )
            target = writes if is_write else reads
            target.add(path if path is not None else "<dynamic>")
            evidence["filesystem.write" if is_write else "filesystem.read"] = item
        elif name.startswith(("os.", "shutil.", "pathlib.")):
            path = literal_string(item.args[0]) if item.args else None
            write_tokens = ("remove", "unlink", "move", "copy", "mkdir", "write")
            is_write = any(token in name for token in write_tokens)
            target = writes if is_write else reads
            target.add(path if path is not None else "<dynamic>")
            evidence["filesystem.write" if is_write else "filesystem.read"] = item
        elif name.startswith(
            ("requests.", "httpx.", "aiohttp.", "urllib.")
        ) or name in {"socket.create_connection"}:
            value = literal_string(item.args[0]) if item.args else None
            if value is None:
                host = "<dynamic>"
            else:
                parsed = urlparse(value)
                host = parsed.netloc or value
            hosts.add(host)
            evidence["network"] = item
    return reads, writes, hosts, evidence


def _is_broader(declared: tuple[str, ...], actual: set[str]) -> bool:
    if "<dynamic>" in actual:
        return True
    if declared and not actual:
        return True
    if not actual:
        return False
    return set(declared) != actual


def _validate_scopes(manifest: PermissionsManifest) -> None:
    for tool in manifest.tools.values():
        for capability in (tool.filesystem.read, tool.filesystem.write):
            for scope in capability.scopes:
                normalized = scope.replace("\\", "/")
                if normalized.startswith("/") or ".." in normalized.split("/"):
                    raise UsageError("filesystem permission scopes must be relative")
                if normalized.startswith("$") and not normalized.startswith("$TMP/"):
                    raise UsageError("only the $TMP filesystem token is supported")
        for scope in tool.network.scopes:
            if "://" in scope or "@" in scope or "/" in scope:
                raise UsageError("network scopes must use host[:port] patterns")
