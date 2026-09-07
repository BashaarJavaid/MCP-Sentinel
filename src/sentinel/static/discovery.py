"""Resolve included Python source bindings without importing target modules."""

from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import PurePosixPath

from sentinel.report.model import ReportWarning
from sentinel.static.ast_utils import (
    discover_tool_regions,
    literal_string,
    qualified_name,
    scope_nodes,
)
from sentinel.static.model import ParsedPythonFile

Function = ast.FunctionDef | ast.AsyncFunctionDef


@dataclass(frozen=True)
class Symbol:
    file: ParsedPythonFile
    name: str
    node: ast.AST


@dataclass(frozen=True)
class ToolBinding:
    name: str
    registration: Symbol
    handler: Symbol
    region: ast.AST


class PythonProgram:
    """A bounded index of unambiguous local imports, exports and static aliases."""

    def __init__(self, files: tuple[ParsedPythonFile, ...]) -> None:
        self.files = files
        self.modules: dict[str, list[ParsedPythonFile]] = defaultdict(list)
        self.bindings: dict[str, dict[str, list[ast.AST]]] = {}
        self.warnings: list[ReportWarning] = []
        for file in files:
            parts = list(PurePosixPath(file.relative_path).with_suffix("").parts)
            if parts[-1] == "__init__":
                parts.pop()
            for start in range(len(parts)):
                self.modules[".".join(parts[start:])].append(file)
            bindings: dict[str, list[ast.AST]] = defaultdict(list)
            for node in scope_nodes(file.tree):
                if isinstance(node, (Function, ast.ClassDef)):
                    bindings[node.name].append(node)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    for alias in node.names:
                        bindings[alias.asname or alias.name.split(".")[0]].append(node)
                elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                    targets = (
                        node.targets if isinstance(node, ast.Assign) else [node.target]
                    )
                    for target in targets:
                        if isinstance(target, ast.Name):
                            bindings[target.id].append(node)
            self.bindings[file.relative_path] = dict(bindings)

    def resolve(
        self,
        file: ParsedPythonFile,
        name: str,
        seen: frozenset[tuple[str, str]] = frozenset(),
    ) -> Symbol | None:
        key = (file.relative_path, name)
        if key in seen or len(seen) >= 64:
            return None
        seen = seen | {key}
        first, _, rest = name.partition(".")
        nodes = self.bindings[file.relative_path].get(first, [])
        if len(nodes) != 1:
            return None
        node = nodes[0]
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value.func if isinstance(node.value, ast.Call) else node.value
            target = qualified_name(value) if value else None
            if isinstance(node.value, ast.Call):
                constructor = self.resolve(file, target, seen) if target else None
                if constructor is None or not isinstance(
                    constructor.node, ast.ClassDef
                ):
                    return None
            return (
                self.resolve(file, target + ("." + rest if rest else ""), seen)
                if target
                else None
            )
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            alias = next(
                item
                for item in node.names
                if (item.asname or item.name.split(".")[0]) == first
            )
            if isinstance(node, ast.Import):
                imported = (
                    alias.name + ("." + rest if rest else "") if alias.asname else name
                )
            else:
                module = node.module or ""
                if node.level:
                    parent = list(PurePosixPath(file.relative_path).parent.parts)
                    if node.level > len(parent):
                        return None
                    module = ".".join(
                        parent[: len(parent) - node.level + 1]
                        + ([module] if module else [])
                    )
                imported = ".".join(part for part in (module, alias.name, rest) if part)
            parts = imported.split(".")
            for stop in range(len(parts) - 1, 0, -1):
                candidates = self.modules.get(".".join(parts[:stop]), [])
                if candidates:
                    return (
                        self.resolve(candidates[0], ".".join(parts[stop:]), seen)
                        if len(candidates) == 1
                        else None
                    )
            return None
        if isinstance(node, ast.ClassDef) and rest:
            members = [
                child
                for child in node.body
                if isinstance(child, (Function, ast.AnnAssign))
                and getattr(child, "name", None) == rest
            ]
            return Symbol(file, name, members[0]) if len(members) == 1 else None
        if not rest and isinstance(node, (Function, ast.ClassDef)):
            return Symbol(file, name, node)
        return None

    def tools(self) -> tuple[ToolBinding, ...]:
        found: list[ToolBinding] = []
        self.warnings.clear()
        for file in self.files:
            for region in discover_tool_regions(file):
                decorated = Symbol(file, region.function.name, region.function)
                found.append(
                    ToolBinding(
                        region.name,
                        Symbol(file, region.name, region.node),
                        decorated,
                        region.node,
                    )
                )
            parents = {
                child: node
                for node in ast.walk(file.tree)
                for child in ast.iter_child_nodes(node)
            }
            for node in ast.walk(file.tree):
                if not isinstance(node, ast.Call):
                    continue
                method = qualified_name(node.func) or ""
                if not method.endswith((".add_tool", ".register_tool")):
                    continue
                expression = (
                    node.args[0]
                    if node.args
                    else next(
                        (
                            kw.value
                            for kw in node.keywords
                            if kw.arg in {"fn", "handler"}
                        ),
                        None,
                    )
                )
                name = qualified_name(expression) if expression else None
                owner = parents.get(node)
                shadowed = False
                while owner is not None:
                    if isinstance(owner, Function):
                        parameters = (
                            *owner.args.posonlyargs,
                            *owner.args.args,
                            *owner.args.kwonlyargs,
                        )
                        shadowed |= any(
                            arg.arg == (name or "").split(".")[0] for arg in parameters
                        )
                    owner = parents.get(owner)
                handler = self.resolve(file, name) if name and not shadowed else None
                if handler is None or not isinstance(handler.node, Function):
                    self.warnings.append(
                        ReportWarning(
                            code="static_handler_unresolved",
                            message=(
                                f"{file.relative_path}:{node.lineno}: imported, "
                                "rebound or dynamic handler cannot be resolved"
                            ),
                        )
                    )
                    continue
                tool_name = next(
                    (
                        literal_string(kw.value)
                        for kw in node.keywords
                        if kw.arg == "name"
                    ),
                    handler.node.name,
                )
                if tool_name is not None:
                    found.append(
                        ToolBinding(
                            tool_name,
                            Symbol(file, tool_name, node),
                            handler,
                            handler.node,
                        )
                    )
        return tuple(found)
