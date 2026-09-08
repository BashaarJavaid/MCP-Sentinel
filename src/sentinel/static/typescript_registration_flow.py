"""Interpret bounded source factory registrations using the shared TypeScript flow."""

from __future__ import annotations

from typing import Any

from sentinel.static.http_discovery import TypeScriptHTTPBinding
from sentinel.static.model import RuleRunState, TypeScriptSourceFile
from sentinel.static.path_flow import Value
from sentinel.static.typescript_discovery import (
    TypeScriptBinding,
    TypeScriptProgram,
    TypeScriptSymbol,
    walk,
)
from sentinel.static.typescript_path_flow import TypeScriptPathFlow


class RegistrationFlow(TypeScriptPathFlow):
    def __init__(self, program: TypeScriptProgram, factory: TypeScriptSymbol) -> None:
        super().__init__(program, RuleRunState())
        self.factory = factory
        self.values: dict[str, TypeScriptSymbol] = {}
        self.found: list[TypeScriptBinding] = []

    def expression(
        self, file: TypeScriptSourceFile, node: Any, env: dict[str, Value]
    ) -> Value:
        result = super().expression(file, node, env)
        if isinstance(node, dict) and any(
            key in node for key in ("L", "Record", "Call")
        ):
            self.values.setdefault(result.key, TypeScriptSymbol(file, node))
        return result

    def registered(
        self, file: TypeScriptSourceFile, node: dict[str, Any], args: list[Value]
    ) -> None:
        if len(args) != 3:
            self.program.unresolved(file, "factory registration arguments")
            return
        config = self.objects.get(args[1].key, {})
        self.found.append(
            TypeScriptBinding(
                self.program.literal(self.values.get(args[0].key)),
                self.call_sites[0] if self.call_sites else TypeScriptSymbol(file, node),
                self.callables.get(args[2].key),
                self.values.get(config.get("inputSchema", Value()).key),
                self.values.get(config.get("description", Value()).key),
                self.factory,
                TypeScriptSymbol(file, node),
            )
        )


def factory_tools(program: TypeScriptProgram) -> tuple[TypeScriptBinding, ...]:
    found = []
    for path, bindings in program.bindings.items():
        file = program.files[path]
        for declarations in bindings.values():
            if len(declarations) != 1:
                continue
            factory = TypeScriptSymbol(file, declarations[0])
            if factory.function is None:
                continue
            constructors = [
                program.resolve_node(
                    file, node["New"][1].get("t", {}).get("TyExpr", {})
                )
                for node in walk(factory.node)
                if "New" in node
            ]
            if not any(
                constructor
                and constructor.external
                == "@modelcontextprotocol/sdk/server/mcp.js.McpServer"
                for constructor in constructors
            ):
                continue
            flow = RegistrationFlow(program, factory)
            flow.function(factory, [])
            found.extend(flow.found)
            program.warnings.extend(
                warning
                for warning in flow.state.warnings
                if warning not in program.warnings
            )
    return tuple(found)


class HTTPRegistrationFlow(TypeScriptPathFlow):
    def __init__(self, program: TypeScriptProgram, factory: TypeScriptSymbol) -> None:
        super().__init__(program, RuleRunState())
        self.factory = factory
        self.found: list[TypeScriptHTTPBinding] = []

    def http_registered(
        self, file: TypeScriptSourceFile, node: dict[str, Any], args: list[Value]
    ) -> None:
        if len(args) < 2:
            self.warning(file, node, "unsupported HTTP middleware sequence")
            return
        self.found.append(
            TypeScriptHTTPBinding(
                TypeScriptSymbol(file, node),
                self.callables.get(args[-1].key),
                self.factory,
            )
        )


def source_http_handlers(
    program: TypeScriptProgram,
) -> tuple[TypeScriptHTTPBinding, ...]:
    found = []
    for path, bindings in program.bindings.items():
        file = program.files[path]
        initializers = [TypeScriptSymbol(file, program.trees[path])]
        initializers.extend(
            symbol
            for declarations in bindings.values()
            if len(declarations) == 1
            for symbol in [TypeScriptSymbol(file, declarations[0])]
            if symbol.function is not None
        )
        for factory in initializers:
            if not any(
                constructor is not None
                and constructor.external
                in {"express.default", "express.Router", "express.default.Router"}
                for node in walk(factory.node)
                if "Call" in node
                for constructor in [program.resolve_node(file, node["Call"][0])]
            ):
                continue
            flow = HTTPRegistrationFlow(program, factory)
            flow.http_initialize(factory)
            found.extend(flow.found)
            program.warnings.extend(
                warning
                for warning in flow.state.warnings
                if warning not in program.warnings
            )
    return tuple(found)
