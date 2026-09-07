"""Resolve included Python source bindings without importing target modules."""

from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import PurePosixPath

from sentinel.report.model import ReportWarning
from sentinel.static.ast_utils import (
    discover_tool_regions,
    import_aliases,
    literal_string,
    qualified_name,
    resolve_name,
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

    @property
    def caller_parameters(self) -> tuple[ast.arg, ...]:
        assert isinstance(self.handler.node, Function)
        aliases = import_aliases(self.handler.file)
        for node in scope_nodes(self.handler.file.tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                aliases.pop(node.id, None)
            elif isinstance(node, (Function, ast.ClassDef)):
                aliases.pop(node.name, None)
        parameters = self.handler.node.args
        caller = []
        for parameter in (
            *parameters.posonlyargs,
            *parameters.args,
            *parameters.kwonlyargs,
        ):
            annotation = parameter.annotation
            if isinstance(annotation, ast.Subscript) and resolve_name(
                qualified_name(annotation.value) or "", aliases
            ) in {"typing.Annotated", "typing_extensions.Annotated"}:
                annotation = (
                    annotation.slice.elts[0]
                    if isinstance(annotation.slice, ast.Tuple) and annotation.slice.elts
                    else None
                )
            annotation_name = (
                (qualified_name(annotation) or "") if annotation is not None else ""
            )
            injected = annotation_name.split(".")[0] in aliases and resolve_name(
                annotation_name, aliases
            ) in {
                "mcp.server.fastmcp.Context",
                "mcp.server.fastmcp.server.Context",
                "fastmcp.Context",
                "fastmcp.server.context.Context",
            }
            if parameter.arg not in {"self", "cls"} and not injected:
                caller.append(parameter)
        return tuple(caller)


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
                if constructor is None or not self.plain_instance(constructor):
                    return None
            return (
                self.resolve(file, target + ("." + rest if rest else ""), seen)
                if target
                else Symbol(file, name, node.value)
                if node.value is not None and not rest
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
                for child in scope_nodes(node)
                if isinstance(child, Function) and child.name == rest
            ]
            for child in scope_nodes(node):
                targets = (
                    child.targets
                    if isinstance(child, ast.Assign)
                    else ([child.target] if isinstance(child, ast.AnnAssign) else [])
                )
                if any(
                    isinstance(target, ast.Name) and target.id == rest
                    for target in targets
                ):
                    return None
            if members:
                return Symbol(file, name, members[0]) if len(members) == 1 else None
            # Only follow a single recoverable implementation across local bases.
            inherited: dict[tuple[str, int], Symbol] = {}
            for base in node.bases:
                base_name = qualified_name(base)
                member = (
                    self.resolve(file, base_name + "." + rest, seen)
                    if base_name
                    else None
                )
                if member is not None:
                    inherited[
                        (member.file.relative_path, getattr(member.node, "lineno", 0))
                    ] = member
            return next(iter(inherited.values())) if len(inherited) == 1 else None
        if not rest and isinstance(node, (Function, ast.ClassDef)):
            return Symbol(file, name, node)
        return None

    def plain_instance(
        self, symbol: Symbol, seen: frozenset[tuple[str, str]] = frozenset()
    ) -> bool:
        """Only infer instances whose construction cannot replace methods or state."""
        node = symbol.node
        key = (symbol.file.relative_path, symbol.name)
        if (
            key in seen
            or not isinstance(node, ast.ClassDef)
            or node.keywords
            or node.decorator_list
        ):
            return False
        for child in scope_nodes(node):
            if isinstance(child, Function) and child.name in {"__new__", "__init__"}:
                return False
            if (
                isinstance(child, ast.Name)
                and isinstance(child.ctx, ast.Store)
                and child.id in {"__new__", "__init__"}
            ):
                return False
        for base in node.bases:
            name = qualified_name(base)
            parent = self.resolve(symbol.file, name) if name else None
            if parent is None or not self.plain_instance(parent, seen | {key}):
                return False
        return True

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
