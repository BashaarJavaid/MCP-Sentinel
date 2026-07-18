"""SENT-001 overly broad permission analysis."""

from __future__ import annotations

import ast
from urllib.parse import urlparse

from sentinel.permissions import load_permissions_manifest
from sentinel.static.ast_utils import (
    discover_tool_regions,
    literal_string,
    match_from_node,
    qualified_name,
)
from sentinel.static.model import RuleRunState, StaticContext


def detect(context: StaticContext, state: RuleRunState) -> None:
    manifest = load_permissions_manifest(
        context.configuration.scan_root, required=False
    )
    if manifest is None:
        state.skip_reason = "sentinel.permissions.yaml is absent"
        return

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
