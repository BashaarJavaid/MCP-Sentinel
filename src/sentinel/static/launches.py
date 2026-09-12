"""Explicit FastMCP launch sites and their module-global initialization flow."""

from __future__ import annotations

import ast
from dataclasses import dataclass

from sentinel.report.model import ReportWarning
from sentinel.static.ast_utils import qualified_name
from sentinel.static.discovery import Function, PythonProgram, Symbol, ToolBinding
from sentinel.static.execution import check_deadline
from sentinel.static.http_discovery import shadowed
from sentinel.static.lifespan import server_class


@dataclass(frozen=True)
class Launch:
    function: Symbol
    call: ast.Call
    server: ast.AST
    transport: str


def instance(program: PythonProgram, context: Symbol, node: ast.AST) -> Symbol | None:
    name = qualified_name(node)
    if not name or shadowed(program, node, name.split(".")[0]):
        return None
    value = program.resolve(context.file, name, value_binding=True)
    if (
        value
        and isinstance(value.node, ast.Call)
        and server_class(program, value, value.node.func)
    ):
        return value
    return None


def launches(program: PythonProgram) -> tuple[Launch, ...]:
    found = []
    replaced: set[ast.AST] = set()
    for file in program.files:
        for node in ast.walk(file.tree):
            check_deadline(program.deadline)
            receivers = (
                [node.value]
                if isinstance(node, ast.Attribute)
                and node.attr == "run"
                and isinstance(node.ctx, (ast.Store, ast.Del))
                else [*node.args, *(kw.value for kw in node.keywords)]
                if isinstance(node, ast.Call)
                else []
            )
            # Escaped server instances may have their launch method replaced.
            # Source-bound wrapper execution is not established by this index.
            for receiver in receivers:
                value = instance(
                    program, Symbol(file, "launch mutation", node), receiver
                )
                if value is not None:
                    replaced.add(value.node)
    for file in program.files:
        for call in ast.walk(file.tree):
            check_deadline(program.deadline)
            if not (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and call.func.attr == "run"
            ):
                continue
            owner = program.parents.get(call)
            while owner is not None and not isinstance(owner, Function):
                owner = program.parents.get(owner)
            context = Symbol(
                file,
                owner.name if isinstance(owner, Function) else "launch",
                owner or call,
            )
            server = instance(program, context, call.func.value)
            if server is None:
                continue
            transport = next(
                (kw.value for kw in call.keywords if kw.arg == "transport"),
                ast.Constant("stdio"),
            )
            supported = (
                server.node not in replaced
                and isinstance(owner, Function)
                and not owner.decorator_list
                and not (
                    owner.args.args
                    or owner.args.kwonlyargs
                    or owner.args.posonlyargs
                    or owner.args.vararg
                    or owner.args.kwarg
                )
                and not call.args
                and all(kw.arg is not None for kw in call.keywords)
                and isinstance(transport, ast.Constant)
                and isinstance(transport.value, str)
                and transport.value in {"stdio", "sse", "streamable-http"}
            )
            found.append(
                Launch(
                    context if supported else Symbol(file, "unresolved launch", call),
                    call,
                    server.node,
                    str(transport.value)
                    if isinstance(transport, ast.Constant)
                    else "unresolved",
                )
            )
    return tuple(found)


def for_tool(program: PythonProgram, tool: ToolBinding) -> tuple[Launch, ...]:
    node = tool.registration.node
    calls = node.decorator_list if isinstance(node, Function) else [node]
    servers = [
        server
        for call in calls
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr in {"tool", "add_tool", "register_tool"}
        for server in [instance(program, tool.registration, call.func.value)]
        if server is not None
    ]
    if len(servers) != 1:
        return ()
    found = tuple(
        launch for launch in program.launches if launch.server is servers[0].node
    )
    if any(not isinstance(launch.function.node, Function) for launch in found):
        warning = ReportWarning(
            code="static_binding_unresolved",
            message=(
                f"{tool.registration.file.relative_path}: unresolved launch state; "
                "analyzing the unconfigured handler as well"
            ),
        )
        if warning not in program.warnings:
            program.warnings.append(warning)
    return found
