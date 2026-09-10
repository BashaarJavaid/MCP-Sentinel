"""Resolve included Python source bindings without importing target modules."""

from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from sentinel.report.model import ReportWarning
from sentinel.static.ast_utils import (
    discover_tool_regions,
    import_aliases,
    literal_string,
    qualified_name,
    resolve_name,
    scope_nodes,
)
from sentinel.static.execution import check_deadline
from sentinel.static.model import ParsedPythonFile

Function = ast.FunctionDef | ast.AsyncFunctionDef

if TYPE_CHECKING:
    from sentinel.static.launches import Launch


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
    registration_decorator: ast.AST | None = None

    def caller_parameters(self, program: PythonProgram) -> tuple[ast.arg, ...]:
        assert isinstance(self.handler.node, Function)
        parameters = self.handler.node.args
        return tuple(
            parameter
            for parameter in (
                *parameters.posonlyargs,
                *parameters.args,
                *parameters.kwonlyargs,
            )
            if parameter.arg not in {"self", "cls"}
            and not program.is_sdk_context(self.handler, parameter.annotation)
        )


class PythonProgram:
    """A bounded index of unambiguous local imports, exports and static aliases."""

    @cached_property
    def server_parents(self) -> dict[ast.AST, list[Symbol]]:
        from sentinel.static.lifespan import server_parents

        return server_parents(self)

    @cached_property
    def launches(self) -> tuple[Launch, ...]:
        from sentinel.static.launches import launches

        return launches(self)

    def __init__(
        self, files: tuple[ParsedPythonFile, ...], *, deadline: float = float("inf")
    ) -> None:
        self.files = files
        self.deadline = deadline
        self.modules: dict[str, list[ParsedPythonFile]] = defaultdict(list)
        self.bindings: dict[str, dict[str, list[ast.AST]]] = {}
        self.warnings: list[ReportWarning] = []
        self._tools: tuple[ToolBinding, ...] | None = None
        self._method_orders: dict[ast.AST, tuple[Symbol | str, ...]] = {}
        self._instance_methods: dict[
            tuple[ast.AST, str, ast.AST | None], Symbol | None
        ] = {}
        self._plain_instances: dict[tuple[ast.AST, bool], bool] = {}
        self._resolved: dict[tuple[str, str, bool], Symbol | None] = {}
        self._resolved_in: dict[tuple[ast.AST, str, str], Symbol | None] = {}
        self.parents = {
            child: parent
            for file in files
            for parent in ast.walk(file.tree)
            for child in ast.iter_child_nodes(parent)
        }
        self.source_functions = frozenset(
            node for node in self.parents if isinstance(node, Function)
        )
        self.local_bindings: dict[ast.AST, dict[str, list[ast.AST]]] = {}
        self.scope_variables: dict[ast.AST, frozenset[str]] = {}
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

    def resolve_in(
        self,
        symbol: Symbol,
        name: str,
        seen: frozenset[tuple[int, str]] = frozenset(),
        *,
        global_seen: frozenset[tuple[str, str]] = frozenset(),
    ) -> Symbol | None:
        check_deadline(self.deadline)
        if seen or global_seen:
            return self._resolve_in(symbol, name, seen, global_seen=global_seen)
        key = (symbol.node, symbol.name, name)
        if key not in self._resolved_in:
            self._resolved_in[key] = self._resolve_in(symbol, name)
        return self._resolved_in[key]

    def _resolve_in(
        self,
        symbol: Symbol,
        name: str,
        seen: frozenset[tuple[int, str]] = frozenset(),
        *,
        global_seen: frozenset[tuple[str, str]] = frozenset(),
    ) -> Symbol | None:
        """Resolve lexical helpers without treating a shadowed name as a global."""
        check_deadline(self.deadline)
        key = (id(symbol.node), name)
        if key in seen or len(seen) >= 64:
            return None
        first, _, rest = name.partition(".")
        owner: ast.AST | None = symbol.node
        while owner is not None:
            if isinstance(owner, Function):
                if owner not in self.local_bindings:
                    bindings: dict[str, list[ast.AST]] = defaultdict(list)
                    for node in scope_nodes(owner):
                        if isinstance(node, (Function, ast.ClassDef)):
                            bindings[node.name].append(node)
                        elif isinstance(node, ast.Name) and isinstance(
                            node.ctx, ast.Store
                        ):
                            bindings[node.id].append(self.parents[node])
                        elif isinstance(node, ast.arg):
                            bindings[node.arg].append(node)
                        elif isinstance(node, (ast.Import, ast.ImportFrom)):
                            for imported in node.names:
                                bindings[
                                    imported.asname or imported.name.split(".")[0]
                                ].append(node)
                    self.local_bindings[owner] = dict(bindings)
                nodes = self.local_bindings[owner].get(first, [])
                if nodes:
                    if len(nodes) != 1:
                        return None
                    node = nodes[0]
                    names = [first]
                    ancestor: ast.AST | None = owner
                    while ancestor is not None:
                        if isinstance(ancestor, (Function, ast.ClassDef)):
                            names.insert(0, ancestor.name)
                        ancestor = self.parents.get(ancestor)
                    if isinstance(node, Function) and not rest:
                        return Symbol(symbol.file, ".".join(names), node)
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        return self.resolve_import(symbol.file, node, name, global_seen)
                    if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value:
                        alias = qualified_name(node.value)
                        if alias:
                            return self.resolve_in(
                                Symbol(symbol.file, symbol.name, owner),
                                alias + ("." + rest if rest else ""),
                                seen | {key},
                                global_seen=global_seen,
                            )
                    return None
            owner = self.parents.get(owner)
        return self.resolve(symbol.file, name, global_seen)

    def resolve(
        self,
        file: ParsedPythonFile,
        name: str,
        seen: frozenset[tuple[str, str]] = frozenset(),
        *,
        value_binding: bool = False,
    ) -> Symbol | None:
        check_deadline(self.deadline)
        # The source index is immutable. Cache complete queries only: a recursive
        # query's cycle/depth budget must not borrow another traversal's result.
        if seen:
            return self._resolve(file, name, seen, value_binding=value_binding)
        key = (file.relative_path, name, value_binding)
        if key not in self._resolved:
            self._resolved[key] = self._resolve(file, name, value_binding=value_binding)
        return self._resolved[key]

    def _resolve(
        self,
        file: ParsedPythonFile,
        name: str,
        seen: frozenset[tuple[str, str]] = frozenset(),
        *,
        value_binding: bool = False,
    ) -> Symbol | None:
        check_deadline(self.deadline)
        key = (file.relative_path, name)
        if key in seen or len(seen) >= 64:
            return None
        seen = seen | {key}
        first, _, rest = name.partition(".")
        nodes = self.bindings[file.relative_path].get(first, [])
        if len(nodes) > 1 and all(
            isinstance(item, Function)
            and self.parents.get(item) is file.tree
            and not item.decorator_list
            for item in nodes
        ):
            definitions = [item for item in nodes if isinstance(item, Function)]
            if all(
                all(
                    isinstance(statement, ast.Pass)
                    or (
                        isinstance(statement, ast.Expr)
                        and isinstance(statement.value, ast.Constant)
                        and isinstance(statement.value.value, str)
                    )
                    for statement in item.body
                )
                for item in definitions[:-1]
            ):
                # A placeholder can be discarded only if no eager expression
                # observed it before the final unconditional definition.
                pending: list[ast.AST] = list(
                    file.tree.body[: file.tree.body.index(definitions[-1])]
                )
                observed = False
                while pending:
                    check_deadline(self.deadline)
                    item = pending.pop()
                    if isinstance(item, ast.Name) and item.id == first:
                        observed = True
                        break
                    pending.extend(
                        child
                        for child in ast.iter_child_nodes(item)
                        if not isinstance(item, Function) or child not in item.body
                    )
                if not observed:
                    nodes = [definitions[-1]]
        if len(nodes) != 1:
            return None
        node = nodes[0]
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            if value_binding and not rest and isinstance(node.value, ast.Call):
                return Symbol(file, name, node.value)
            value = node.value.func if isinstance(node.value, ast.Call) else node.value
            target = qualified_name(value) if value else None
            if isinstance(node.value, ast.Call):
                constructor = self.resolve(file, target, seen) if target else None
                if constructor and isinstance(constructor.node, Function):
                    factory = constructor.node
                    if (
                        factory.decorator_list
                        or not factory.body
                        or not isinstance(factory.body[-1], ast.Return)
                    ):
                        return None
                    returned = []
                    for statement in scope_nodes(factory):
                        if isinstance(statement, ast.Return):
                            returned_name = (
                                qualified_name(statement.value)
                                if statement.value is not None
                                else None
                            )
                            binding = (
                                self.resolve_in(
                                    constructor, returned_name, global_seen=seen
                                )
                                if returned_name
                                else None
                            )
                            if binding is None:
                                return None
                            returned.append(binding)
                    if (
                        not rest
                        and returned
                        and all(binding == returned[0] for binding in returned)
                        and isinstance(returned[0].node, Function)
                        and not returned[0].node.decorator_list
                    ):
                        return returned[0]
                    return None
                if constructor is None or not self.plain_instance(constructor):
                    return None
            return (
                self.resolve(
                    file,
                    target + ("." + rest if rest else ""),
                    seen,
                    value_binding=value_binding,
                )
                if target
                else Symbol(file, name, node.value)
                if node.value is not None and not rest
                else None
            )
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return self.resolve_import(
                file, node, name, seen, value_binding=value_binding
            )
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

    def resolve_import(
        self,
        file: ParsedPythonFile,
        node: ast.Import | ast.ImportFrom,
        name: str,
        seen: frozenset[tuple[str, str]] = frozenset(),
        *,
        value_binding: bool = False,
    ) -> Symbol | None:
        first, _, rest = name.partition(".")
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
        modules = self.modules.get(imported, [])
        if value_binding and modules:
            return (
                Symbol(modules[0], "", modules[0].tree) if len(modules) == 1 else None
            )
        parts = imported.split(".")
        for stop in range(len(parts) - 1, 0, -1):
            candidates = self.modules.get(".".join(parts[:stop]), [])
            if candidates:
                return (
                    self.resolve(
                        candidates[0],
                        ".".join(parts[stop:]),
                        seen,
                        value_binding=value_binding,
                    )
                    if len(candidates) == 1
                    else None
                )
        return None

    def is_sdk_context(self, symbol: Symbol, annotation: ast.AST | None) -> bool:
        """Only an unreplaced external SDK annotation establishes injection."""
        from sentinel.static.http_discovery import shadowed

        check_deadline(self.deadline)
        if isinstance(annotation, ast.Subscript) and self.external(
            symbol, annotation.value
        ) in {"typing.Annotated", "typing_extensions.Annotated"}:
            if shadowed(
                self,
                annotation.value,
                (qualified_name(annotation.value) or "").split(".")[0],
            ):
                return False
            annotation = (
                annotation.slice.elts[0]
                if isinstance(annotation.slice, ast.Tuple) and annotation.slice.elts
                else None
            )
        return (
            annotation is not None
            and not shadowed(
                self, annotation, (qualified_name(annotation) or "").split(".")[0]
            )
            and self.external(symbol, annotation)
            in {
                "mcp.server.fastmcp.Context",
                "mcp.server.fastmcp.server.Context",
                "fastmcp.Context",
                "fastmcp.server.context.Context",
            }
        )

    def external(self, symbol: Symbol, node: ast.AST) -> str:
        name = qualified_name(node) or ""
        declarations = self.bindings[symbol.file.relative_path].get(
            name.split(".")[0], []
        )
        if len(declarations) != 1 or not isinstance(
            declarations[0], (ast.Import, ast.ImportFrom)
        ):
            return ""
        if isinstance(declarations[0], ast.ImportFrom) and declarations[0].level:
            return ""
        imported = resolve_name(name, import_aliases(symbol.file))
        if any(
            ".".join(imported.split(".")[:end]) in self.modules
            for end in range(1, len(imported.split(".")))
        ):
            return ""
        return imported

    def reachable_files(self, roots: set[str]) -> frozenset[str]:
        """Over-approximate included imports, including ambiguous package matches."""
        files = {file.relative_path: file for file in self.files}
        pending = list(roots)
        reached: set[str] = set()
        while pending:
            path = pending.pop()
            check_deadline(self.deadline)
            if path in reached or path not in files:
                continue
            reached.add(path)
            file = files[path]
            for node in ast.walk(file.tree):
                check_deadline(self.deadline)
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if node.level:
                        parent = list(PurePosixPath(path).parent.parts)
                        if node.level > len(parent):
                            continue
                        module = ".".join(
                            parent[: len(parent) - node.level + 1]
                            + ([module] if module else [])
                        )
                    names = [f"{module}.{alias.name}" for alias in node.names]
                else:
                    continue
                for name in names:
                    parts = name.split(".")
                    for end in range(1, len(parts) + 1):
                        pending.extend(
                            candidate.relative_path
                            for candidate in self.modules.get(".".join(parts[:end]), [])
                            if candidate.relative_path not in reached
                        )
        return frozenset(reached)

    def method_order(
        self, symbol: Symbol, seen: frozenset[ast.AST] = frozenset()
    ) -> tuple[Symbol | str, ...] | None:
        """C3 order for included source classes; never construct target types."""
        check_deadline(self.deadline)
        node = symbol.node
        if not isinstance(node, ast.ClassDef) or node in seen or node.keywords:
            return None
        if node in self._method_orders:
            return self._method_orders[node]
        bases: list[Symbol | str] = []
        orders: list[list[Symbol | str]] = []
        for base in node.bases:
            imported = self.external(symbol, base)
            if isinstance(base, ast.Subscript) and self.external(
                symbol, base.value
            ) in {"fastmcp.FastMCP", "mcp.server.fastmcp.FastMCP"}:
                imported = self.external(symbol, base.value)
            if imported in {
                "typing.Protocol",
                "fastmcp.FastMCP",
                "mcp.server.fastmcp.FastMCP",
                "starlette.middleware.base.BaseHTTPMiddleware",
            }:
                bases.append(imported)
                orders.append([imported])
                continue
            name = qualified_name(base)
            parent = self.resolve(symbol.file, name) if name else None
            order = self.method_order(parent, seen | {node}) if parent else None
            if order is None or parent is None:
                return None
            bases.append(parent)
            orders.append(list(order))
        sequences = [*orders, bases]
        result: list[Symbol | str] = [symbol]
        while any(sequences):
            check_deadline(self.deadline)
            head = next(
                (
                    sequence[0]
                    for sequence in sequences
                    if sequence
                    and not any(sequence[0] in other[1:] for other in sequences)
                ),
                None,
            )
            if head is None:
                return None
            result.append(head)
            for sequence in sequences:
                if sequence and sequence[0] == head:
                    sequence.pop(0)
        self._method_orders[node] = tuple(result)
        return tuple(result)

    def instance_method(
        self, symbol: Symbol, name: str, *, after: Symbol | None = None
    ) -> Symbol | None:
        check_deadline(self.deadline)
        key = (symbol.node, name, after.node if after else None)
        if key not in self._instance_methods:
            self._instance_methods[key] = self._instance_method(
                symbol, name, after=after
            )
        return self._instance_methods[key]

    def _instance_method(
        self, symbol: Symbol, name: str, *, after: Symbol | None = None
    ) -> Symbol | None:
        order = self.method_order(symbol)
        if order is None:
            return None
        if after is not None:
            positions = [
                i
                for i, item in enumerate(order)
                if isinstance(item, Symbol) and item.node is after.node
            ]
            if len(positions) != 1:
                return None
            order = order[positions[0] + 1 :]
        for owner in order:
            if isinstance(owner, str):
                return None
            assert isinstance(owner.node, ast.ClassDef)
            declarations = [
                part
                for part in scope_nodes(owner.node)
                if (isinstance(part, Function) and part.name == name)
                or (
                    isinstance(part, ast.Name)
                    and isinstance(part.ctx, ast.Store)
                    and part.id == name
                )
            ]
            if declarations:
                return (
                    Symbol(owner.file, owner.name + "." + name, declarations[0])
                    if len(declarations) == 1 and isinstance(declarations[0], Function)
                    else None
                )
        return None

    def plain_instance(
        self,
        symbol: Symbol,
        seen: frozenset[tuple[str, str]] = frozenset(),
        *,
        inspect_init: bool = False,
    ) -> bool:
        """With inspect_init, callers must interpret the initializer before binding."""
        check_deadline(self.deadline)
        if seen:
            return self._plain_instance(symbol, seen, inspect_init=inspect_init)
        key = (symbol.node, inspect_init)
        if key not in self._plain_instances:
            self._plain_instances[key] = self._plain_instance(
                symbol, inspect_init=inspect_init
            )
        return self._plain_instances[key]

    def _plain_instance(
        self,
        symbol: Symbol,
        seen: frozenset[tuple[str, str]] = frozenset(),
        *,
        inspect_init: bool = False,
    ) -> bool:
        node = symbol.node
        key = (symbol.file.relative_path, symbol.name)
        if (
            key in seen
            or not isinstance(node, ast.ClassDef)
            or node.keywords
            or any(
                self.external(symbol, decorator) != "typing.runtime_checkable"
                or not any(
                    self.external(symbol, base) == "typing.Protocol"
                    for base in node.bases
                )
                for decorator in node.decorator_list
            )
        ):
            return False
        for child in scope_nodes(node):
            if isinstance(child, Function) and child.name in (
                {
                    "__new__",
                    "__getattribute__",
                    "__getattr__",
                    "__setattr__",
                    "__init_subclass__",
                }
                | (set() if inspect_init else {"__init__"})
            ):
                return False
            if (
                isinstance(child, ast.Name)
                and isinstance(child.ctx, ast.Store)
                and child.id
                in {
                    "__new__",
                    "__init_subclass__",
                    "__init__",
                    "__getattribute__",
                    "__getattr__",
                    "__setattr__",
                }
            ):
                return False
        for base in node.bases:
            if self.external(symbol, base) == "typing.Protocol":
                if not seen:
                    return False
                continue
            name = qualified_name(base)
            parent = self.resolve(symbol.file, name) if name else None
            if parent is None or not self.plain_instance(
                parent, seen | {key}, inspect_init=inspect_init
            ):
                return False
        return True

    def tools(self) -> tuple[ToolBinding, ...]:
        from sentinel.static.registration_flow import RegistrationFlow

        check_deadline(self.deadline)
        if self._tools is not None:
            return self._tools
        registrations = RegistrationFlow(self)
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
                        region.registration_decorator,
                    )
                )
            parents = self.parents
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
                handler = (
                    self.resolve_in(Symbol(file, name, node), name)
                    if name and not shadowed
                    else None
                )
                if handler is None or not isinstance(handler.node, Function):
                    registrations.incomplete = False
                    recovered = registrations.values(
                        Symbol(file, name or "registration", node), expression
                    )
                    for candidate in recovered:
                        if isinstance(candidate.node, Function):
                            found.append(
                                ToolBinding(
                                    candidate.node.name,
                                    Symbol(file, candidate.node.name, node),
                                    candidate,
                                    candidate.node,
                                )
                            )
                    if (
                        recovered
                        and not registrations.incomplete
                        and all(isinstance(item.node, Function) for item in recovered)
                    ):
                        continue
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
        self._tools = tuple(found)
        return self._tools
