"""Bounded TypeScript bindings over the installed Semgrep source tree."""

from __future__ import annotations

import posixpath
from collections import OrderedDict, defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from sentinel.finding import SourceRange
from sentinel.report.model import ReportWarning
from sentinel.static.execution import check_deadline
from sentinel.static.model import TypeScriptSourceFile
from sentinel.static.semgrep_ast import parse_typescript, source_range
from sentinel.static.typescript_modules import TypeScriptModules


def walk(tree: Any) -> Iterator[dict[str, Any]]:
    pending = [tree]
    while pending:
        node = pending.pop()
        if isinstance(node, dict):
            yield node
            pending.extend(
                v
                for k, v in reversed(tuple(node.items()))
                if k not in {"token", "pinfo"} and not k.startswith("id_")
            )
        elif isinstance(node, list):
            pending.extend(reversed(node))


def name_of(node: dict[str, Any]) -> str | None:
    for wrapper in ("N", "EN", "FN"):
        if wrapper in node:
            return name_of(node[wrapper])
    if "Id" in node:
        value = node["Id"][0][0]
        return value if isinstance(value, str) else None
    if "IdSpecial" in node and node["IdSpecial"][0][0] == "This":
        return "this"
    if "DotAccess" in node:
        receiver, _, field = node["DotAccess"]
        left, right = name_of(receiver), name_of(field)
        if left and right:
            return left + "." + right
    return None


@dataclass(frozen=True)
class TypeScriptSymbol:
    file: TypeScriptSourceFile
    node: dict[str, Any]
    external: str | None = None

    @property
    def function(self) -> dict[str, Any] | None:
        value = self.node.get("FuncDef", self.node.get("Lambda"))
        return value if isinstance(value, dict) else None


@dataclass(frozen=True)
class TypeScriptBinding:
    name: str | None
    registration: TypeScriptSymbol
    handler: TypeScriptSymbol | None
    schema: TypeScriptSymbol | None
    description: TypeScriptSymbol | None
    factory: TypeScriptSymbol | None = None
    sdk_registration: TypeScriptSymbol | None = None


class TypeScriptProgram:
    def __init__(
        self,
        files: tuple[TypeScriptSourceFile, ...],
        *,
        deadline: float,
        modules: TypeScriptModules | None = None,
    ) -> None:
        self.files = {file.relative_path: file for file in files}
        self.deadline = deadline
        self.modules = modules
        self.trees: dict[str, dict[str, Any]] = {}
        self.bindings: dict[str, dict[str, list[dict[str, Any]]]] = {}
        self.exports: dict[str, set[str]] = {}
        self.class_attributes: dict[int, list[dict[str, Any]]] = {}
        self.source_ranges: OrderedDict[
            tuple[int, int], tuple[Any, TypeScriptSourceFile, SourceRange]
        ] = OrderedDict()
        self.warnings: list[ReportWarning] = modules.warnings if modules else []
        for file in files:
            tree = parse_typescript(file, deadline=deadline)
            self.trees[file.relative_path] = tree
            bindings: dict[str, list[dict[str, Any]]] = defaultdict(list)
            exports: set[str] = set()
            for node in tree["Pr"]:
                if "DefStmt" in node:
                    entity, definition = node["DefStmt"]
                    if "ClassDef" in definition:
                        self.class_attributes[id(definition)] = entity.get("attrs", [])
                    name = name_of(entity["name"])
                    if name:
                        variable = definition.get("VarDef", {})
                        bindings[name].append(
                            (variable.get("vinit") or {}).get("some", definition)
                        )
                directive = node.get("DirectiveStmt", {}).get("d", {})
                if "ImportFrom" in directive:
                    _, module, names = directive["ImportFrom"]
                    for item in names:
                        if "Aliased" in item:
                            original, alias = item["Aliased"]
                            local = alias[0][0]
                        elif "Direct" in item:
                            original, _ = item["Direct"]
                            local = original[0]
                        else:
                            continue
                        bindings[local].append(
                            {"import": (module["FileName"][0], original[0])}
                        )
                elif "ImportAs" in directive:
                    _, module, alias = directive["ImportAs"]
                    if alias:
                        bindings[alias["some"][0][0]].append(
                            {"import": (module["FileName"][0], "")}
                        )
                other = directive.get("OtherDirective")
                if other and other[0][0] == "Export":
                    exports.update(item["I"][0] for item in other[1] if "I" in item)
            # A write anywhere can rebind a module-level handler at runtime.
            for node in walk(tree):
                assignment = node.get("Assign", node.get("AssignOp"))
                if assignment:
                    name = name_of(assignment[0])
                    if name and name.split(".")[0] in bindings:
                        bindings[name.split(".")[0]].append({"rebound": True})
            self.bindings[file.relative_path] = dict(bindings)
            self.exports[file.relative_path] = exports

    def property(
        self,
        symbol: TypeScriptSymbol,
        name: str,
        seen: frozenset[tuple[str, str]] = frozenset(),
    ) -> TypeScriptSymbol | None:
        if "Record" not in symbol.node:
            return None
        matches = []
        for field in symbol.node["Record"][1]:
            definition = field.get("F", {}).get("DefStmt")
            if not definition or name_of(definition[0]["name"]) is None:
                self.unresolved(symbol.file, "computed or spread object member")
                return None
            if name_of(definition[0]["name"]) == name:
                matches.append(definition[1])
        if len(matches) != 1:
            return None
        definition = matches[0]
        value = (definition.get("FieldDefColon", {}).get("vinit") or {}).get(
            "some", definition
        )
        return self.resolve_node(symbol.file, value, seen=seen)

    def literal(self, symbol: TypeScriptSymbol | None, depth: int = 0) -> str | None:
        if symbol is None or depth >= 64:
            return None
        string = symbol.node.get("L", {}).get("String")
        if string:
            return str(string[1][0])
        call = symbol.node.get("Call")
        if call:
            operation = call[0].get("Special", [{}])[0]
            if isinstance(operation, dict) and (
                "ConcatString" in operation or operation.get("Op") == "Plus"
            ):
                values = [
                    self.literal(self.resolve_node(symbol.file, arg["Arg"]), depth + 1)
                    for arg in call[1][1]
                    if "Arg" in arg
                ]
                if values and all(value is not None for value in values):
                    return "".join(value for value in values if value is not None)
        return None

    def listed_tools(self) -> tuple[TypeScriptSymbol, ...]:
        """Recover metadata returned to the SDK's low-level tools/list schema."""
        found = []
        for file in self.files.values():
            for node in walk(self.trees[file.relative_path]):
                call = node.get("Call")
                if not call or not (name_of(call[0]) or "").endswith(
                    ".setRequestHandler"
                ):
                    continue
                args = [item["Arg"] for item in call[1][1] if "Arg" in item]
                if len(args) != 2:
                    continue
                schema = self.resolve_node(file, args[0])
                if not schema or schema.external != (
                    "@modelcontextprotocol/sdk/types.js.ListToolsRequestSchema"
                ):
                    continue
                handler = self.resolve_node(file, args[1])
                if not handler or not handler.function:
                    self.unresolved(file, "tools/list handler")
                    continue
                for returned in walk(handler.function["fbody"]):
                    if "Return" not in returned:
                        continue
                    value = (returned["Return"][1] or {}).get("some")
                    result = self.resolve_node(handler.file, value) if value else None
                    listing = self.property(result, "tools") if result else None
                    if listing is None or "Container" not in listing.node:
                        self.unresolved(file, "tools/list metadata")
                        continue
                    for item in listing.node["Container"][1][1]:
                        metadata = self.resolve_node(listing.file, item)
                        if metadata and "Record" in metadata.node:
                            found.append(metadata)
                        else:
                            self.unresolved(listing.file, "tools/list entry")
        return tuple(found)

    def tools(self) -> tuple[TypeScriptBinding, ...]:
        found: list[TypeScriptBinding] = []
        for file in self.files.values():
            for node in walk(self.trees[file.relative_path]):
                check_deadline(self.deadline)
                if "New" in node:
                    _, type_, _, arguments = node["New"]
                    constructor_name = name_of(type_.get("t", {}).get("TyExpr", {}))
                    if (
                        not constructor_name
                        or constructor_name.split(".")[0]
                        not in self.bindings[file.relative_path]
                    ):
                        continue
                    constructor = self.resolve_node(
                        file, type_.get("t", {}).get("TyExpr", {})
                    )
                    if (
                        not constructor
                        or constructor.external != "@mastra/mcp.MCPServer"
                    ):
                        continue
                    args = [item["Arg"] for item in arguments[1] if "Arg" in item]
                    config = self.resolve_node(file, args[0]) if args else None
                    tools = self.property(config, "tools") if config else None
                    if tools and "Record" in tools.node:
                        for field in tools.node["Record"][1]:
                            definition = field.get("F", {}).get("DefStmt")
                            name = (
                                name_of(definition[0]["name"]) if definition else None
                            )
                            tool = self.property(tools, name) if name else None
                            if tool:
                                found.append(
                                    TypeScriptBinding(
                                        name,
                                        TypeScriptSymbol(file, node),
                                        self.property(tool, "execute"),
                                        self.property(tool, "parameters"),
                                        self.property(tool, "description"),
                                    )
                                )
                    else:
                        self.unresolved(file, "MCPServer tools")
                if "Call" not in node:
                    continue
                callee, arguments = node["Call"]
                name = name_of(callee)
                if not name or not name.endswith(
                    (".registerTool", ".tool", ".setRequestHandler")
                ):
                    continue
                receiver_name, _, method = name.rpartition(".")
                receiver = self.resolve(file, receiver_name)
                if not receiver or "New" not in receiver.node:
                    continue
                constructor_expression = (
                    receiver.node["New"][1].get("t", {}).get("TyExpr", {})
                )
                constructor = self.resolve_node(receiver.file, constructor_expression)
                if not constructor or constructor.external not in {
                    "@modelcontextprotocol/sdk/server/mcp.js.McpServer",
                    "@modelcontextprotocol/sdk/server/index.js.Server",
                }:
                    continue
                args = [
                    self.resolve_node(file, item["Arg"]) if "Arg" in item else None
                    for item in arguments[1]
                ]
                if len(args) < 2:
                    self.unresolved(file, name)
                    continue
                if method == "setRequestHandler":
                    if (
                        args[0]
                        and args[0].external
                        == "@modelcontextprotocol/sdk/types.js.CallToolRequestSchema"
                    ):
                        found.append(
                            TypeScriptBinding(
                                None, TypeScriptSymbol(file, node), args[1], None, None
                            )
                        )
                    continue
                tool_name = self.literal(args[0])
                config = args[1]
                if method == "registerTool":
                    schema = self.property(config, "inputSchema") if config else None
                    description = (
                        self.property(config, "description") if config else None
                    )
                    handler = args[2] if len(args) == 3 else None
                else:
                    middle = args[1:-1]
                    description = (
                        middle.pop(0)
                        if middle and self.literal(middle[0]) is not None
                        else None
                    )
                    schema = middle[0] if middle else None
                    handler = args[-1]
                found.append(
                    TypeScriptBinding(
                        tool_name,
                        TypeScriptSymbol(file, node),
                        handler,
                        schema,
                        description,
                    )
                )
        from sentinel.static.typescript_registration_flow import factory_tools

        wrapped = factory_tools(self)
        registrations = {id(tool.registration.node) for tool in wrapped}
        return (
            tuple(
                tool
                for tool in found
                if id(tool.registration.node) not in registrations
            )
            + wrapped
        )

    def source_range(self, node: Any, file: TypeScriptSourceFile) -> SourceRange:
        # Source syntax stays immutable within a program. Retain both objects so
        # identity reuse cannot confuse a synthetic node or another source snapshot.
        key = (id(node), id(file))
        if key not in self.source_ranges:
            self.source_ranges[key] = (node, file, source_range(node, file))
            # ponytail: bound retained locations; evicted nodes are revalidated.
            if len(self.source_ranges) > 4096:
                self.source_ranges.popitem(last=False)
        self.source_ranges.move_to_end(key)
        return self.source_ranges[key][2]

    def text(self, file: TypeScriptSourceFile, node: Any) -> str:
        location = self.source_range(node, file)
        lines = file.source.splitlines(keepends=True)
        start = (
            sum(map(len, lines[: location.start_line - 1])) + location.start_column - 1
        )
        end = sum(map(len, lines[: location.end_line - 1])) + location.end_column - 1
        return file.source[start:end]

    def unresolved(self, file: TypeScriptSourceFile, name: str) -> None:
        warning = ReportWarning(
            code="static_binding_unresolved",
            message=f"{file.relative_path}: cannot resolve TypeScript binding {name!r}",
        )
        if warning not in self.warnings:
            self.warnings.append(warning)

    def resolve(
        self,
        file: TypeScriptSourceFile,
        name: str,
        seen: frozenset[tuple[str, str]] = frozenset(),
    ) -> TypeScriptSymbol | None:
        check_deadline(self.deadline)
        key = (file.relative_path, name)
        if key in seen or len(seen) >= 64:
            self.unresolved(file, name)
            return None
        first, _, rest = name.partition(".")
        nodes = self.bindings[file.relative_path].get(first, [])
        if len(nodes) != 1:
            self.unresolved(file, name)
            return None
        return self.resolve_node(file, nodes[0], rest, seen | {key})

    def resolve_node(
        self,
        file: TypeScriptSourceFile,
        node: dict[str, Any],
        rest: str = "",
        seen: frozenset[tuple[str, str]] = frozenset(),
    ) -> TypeScriptSymbol | None:
        check_deadline(self.deadline)
        if "import" in node:
            module, imported = node["import"]
            target = ".".join(part for part in (imported, rest) if part)
            local, bases = (
                self.modules.resolve(file.relative_path, module)
                if self.modules is not None
                else (
                    module.startswith("."),
                    (
                        posixpath.normpath(
                            posixpath.join(
                                posixpath.dirname(file.relative_path), module
                            )
                        ),
                    ),
                )
            )
            if not local:
                # These Node default exports are the built-in module object.
                if imported == "default" and module.removeprefix("node:") in {
                    "fs",
                    "fs/promises",
                    "path",
                    "path/posix",
                    "path/win32",
                    "child_process",
                }:
                    target = rest
                return TypeScriptSymbol(
                    file, node, module + ("." + target if target else "")
                )
            included_paths = set()
            for base in bases:
                if base == ".." or base.startswith("../") or base.startswith("/"):
                    self.unresolved(file, module)
                    return None
                stem, extension = posixpath.splitext(base)
                candidates = {base}
                if extension in {".js", ".mjs", ".cjs"}:
                    candidates.update(
                        stem + ext for ext in (".ts", ".mts", ".cts", ".tsx")
                    )
                elif not extension:
                    candidates.update(
                        base + ext for ext in (".ts", ".mts", ".cts", ".tsx")
                    )
                    candidates.update(
                        base + "/index" + ext for ext in (".ts", ".mts", ".cts", ".tsx")
                    )
                matches = candidates.intersection(self.files)
                if len(matches) != 1:
                    self.unresolved(file, module + ":" + target)
                    return None
                included_paths.update(matches)
            included = [self.files[path] for path in sorted(included_paths)]
            if (
                len(included) != 1
                or target.split(".")[0] not in self.exports[included[0].relative_path]
            ):
                self.unresolved(file, module + ":" + target)
                return None
            return self.resolve(included[0], target, seen)
        alias = name_of(node)
        if alias:
            return self.resolve(file, alias + ("." + rest if rest else ""), seen)
        if rest and "Record" in node:
            first, _, tail = rest.partition(".")
            member = self.property(TypeScriptSymbol(file, node), first, seen)
            if member:
                return self.resolve_node(member.file, member.node, tail, seen)
        if not rest:
            return TypeScriptSymbol(file, node)
        self.unresolved(file, rest)
        return None
