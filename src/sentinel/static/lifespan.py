"""Connect explicit local FastMCP registrations to their lifespan callback."""

from __future__ import annotations

import ast

from sentinel.static.ast_utils import (
    qualified_name,
    scope_nodes,
)
from sentinel.static.discovery import Function, PythonProgram, Symbol, ToolBinding
from sentinel.static.execution import check_deadline


def server_class(
    program: PythonProgram,
    symbol: Symbol,
    node: ast.AST,
    seen: frozenset[ast.AST] = frozenset(),
) -> bool:
    check_deadline(program.deadline)
    node = node.value if isinstance(node, ast.Subscript) else node
    if program.external(symbol, node) in {
        "fastmcp.FastMCP",
        "mcp.server.fastmcp.FastMCP",
    }:
        return True
    name = qualified_name(node)
    target = program.resolve(symbol.file, name) if name else None
    if (
        target is None
        or target.node in seen
        or not isinstance(target.node, ast.ClassDef)
    ):
        return False
    cls = target.node
    if cls.decorator_list or cls.keywords or len(cls.bases) != 1:
        return False
    hooks = {
        "__init__",
        "__new__",
        "__getattr__",
        "__getattribute__",
        "__setattr__",
        "mount",
        "tool",
        "add_tool",
        "register_tool",
        "run",
    }
    for part in scope_nodes(cls):
        if (isinstance(part, Function) and part.name in hooks) or (
            isinstance(part, ast.Name)
            and isinstance(part.ctx, ast.Store)
            and part.id in hooks
        ):
            return False
    return server_class(program, target, cls.bases[0], seen | {cls})


def tool_lifespan(program: PythonProgram, tool: ToolBinding) -> Symbol | None:
    def instance(context: Symbol, node: ast.AST) -> Symbol | None:
        name = qualified_name(node)
        owner = program.parents.get(node)
        while owner is not None:
            if isinstance(owner, Function) and name:
                root = name.split(".")[0]
                parameters = (
                    *owner.args.posonlyargs,
                    *owner.args.args,
                    *owner.args.kwonlyargs,
                )
                if any(p.arg == root for p in parameters) or any(
                    isinstance(part, ast.Name)
                    and isinstance(part.ctx, ast.Store)
                    and part.id == root
                    for part in scope_nodes(owner)
                ):
                    return None
            owner = program.parents.get(owner)
        value = (
            program.resolve(context.file, name, value_binding=True) if name else None
        )
        if (
            value
            and isinstance(value.node, ast.Call)
            and server_class(program, value, value.node.func)
        ):
            return value
        return None

    registrations = (
        tool.handler.node.decorator_list
        if isinstance(tool.handler.node, Function)
        else []
    )
    registration_calls = [item for item in registrations if isinstance(item, ast.Call)]
    if isinstance(tool.registration.node, ast.Call):
        registration_calls.append(tool.registration.node)
    servers = []
    for call in registration_calls:
        if isinstance(call.func, ast.Attribute) and call.func.attr in {
            "tool",
            "add_tool",
            "register_tool",
        }:
            server = instance(tool.registration, call.func.value)
            if server:
                servers.append(server)
    if len(servers) != 1:
        return None
    parents: dict[ast.AST, list[Symbol]] = {}
    for file in program.files:
        for part in scope_nodes(file.tree):
            mount_call = part if isinstance(part, ast.Call) else None
            check_deadline(program.deadline)
            if not (
                isinstance(mount_call, ast.Call)
                and isinstance(mount_call.func, ast.Attribute)
                and mount_call.func.attr == "mount"
                and mount_call.args
            ):
                continue
            context = Symbol(file, "mount", mount_call)
            parent = instance(context, mount_call.func.value)
            child = instance(context, mount_call.args[0])
            if parent and child:
                parents.setdefault(child.node, []).append(parent)
    pending = servers
    seen: set[ast.AST] = set()
    callbacks = []
    while pending:
        server = pending.pop()
        if server.node in seen:
            return None
        seen.add(server.node)
        assert isinstance(server.node, ast.Call)
        lifespan = [kw.value for kw in server.node.keywords if kw.arg == "lifespan"]
        if lifespan:
            if len(lifespan) != 1:
                return None
            name = qualified_name(lifespan[0])
            callback = program.resolve(server.file, name) if name else None
            if not callback or not isinstance(callback.node, Function):
                return None
            decorators = callback.node.decorator_list
            if (
                len(decorators) != 1
                or program.external(callback, decorators[0])
                != "contextlib.asynccontextmanager"
            ):
                return None
            callbacks.append(callback)
        else:
            pending.extend(parents.get(server.node, []))
    return callbacks[0] if len(callbacks) == 1 else None
