"""Source-established ASGI middleware state for registered FastMCP tools."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from sentinel.static.ast_utils import qualified_name
from sentinel.static.discovery import Function, Symbol, ToolBinding
from sentinel.static.execution import check_deadline
from sentinel.static.lifespan import tool_servers
from sentinel.static.path_flow import Value, _key

if TYPE_CHECKING:
    from sentinel.static.path_flow import PathFlow


class HTTPContext:
    def __init__(self, flow: PathFlow) -> None:
        self.flow = flow
        self.servers: set[str] = set()
        self.layers: dict[str, tuple[Value, dict[str, Value], Symbol]] = {}
        self.sequences: dict[str, tuple[Value, ...]] = {}
        self.applications: dict[str, tuple[Value, ...]] = {}
        self.continuation: ast.FunctionDef | None = None
        self.states: list[dict[str, Value]] = []
        self.preparing = False
        self.incomplete = False
        self.next_keys: set[str] = set()
        self.middleware_instances: set[str] = set()
        self.state_owners: dict[str, Value] = {}

    def sequence(
        self, symbol: Symbol, node: ast.List | ast.Tuple, values: tuple[Value, ...]
    ) -> Value | None:
        if not values or not all(value.key in self.layers for value in values):
            return None
        value = Value(
            key=_key(
                "http-middleware-sequence",
                symbol.file.relative_path,
                str(node.lineno),
                str(node.col_offset),
                *self.flow.call_sites,
            )
        )
        self.sequences[value.key] = values
        self.flow.record_keys.add(value.key)
        return value

    def request(self, scope: Value, env: dict[str, Value]) -> Value:
        flow = self.flow
        request = Value(key=_key(scope.key, "http-request"))
        flow.record_keys.add(request.key)
        owner = flow.member(scope, "state", env)
        state = Value(key=_key(owner.key, "request-state"))
        self.state_owners[state.key] = owner
        flow.record_keys.add(state.key)
        flow.members[state.key] = flow.members.setdefault(owner.key, {})
        env[flow.member_key(request, "state")] = state
        env[flow.member_key(request, "headers")] = flow.member(scope, "headers", env)
        return request

    def call(
        self,
        symbol: Symbol,
        node: ast.Call,
        external: str,
        receiver: Value,
        args: list[Value],
        keywords: dict[str | None, Value],
        env: dict[str, Value],
        super_owner: Symbol | None,
    ) -> Value | None:
        if not self.preparing:
            return None
        flow = self.flow
        if (
            external == "starlette.middleware.Middleware"
            and flow.program.external(symbol, node.func) == external
            and len(args) == 1
            and None not in keywords
        ):
            layer = Value(
                key=_key(
                    "http-middleware",
                    symbol.file.relative_path,
                    str(node.lineno),
                    str(node.col_offset),
                    *flow.call_sites,
                )
            )
            self.layers[layer.key] = (
                args[0],
                {name: value for name, value in keywords.items() if name is not None},
                Symbol(symbol.file, symbol.name, node),
            )
            flow.record_keys.add(layer.key)
            return layer
        if (
            super_owner is not None
            and receiver.key in self.servers
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "http_app"
            and not args
            and None not in keywords
        ):
            sequence = keywords.get("middleware", Value())
            if (
                sequence.key in self.sequences
                and "#member:unknown:" + sequence.key not in env
            ):
                app = Value(
                    key=_key(
                        "http-application",
                        symbol.file.relative_path,
                        str(node.lineno),
                        receiver.key,
                    )
                )
                self.applications[app.key] = self.sequences[sequence.key]
                return app
            flow.unresolved(symbol, node, "unresolved HTTP middleware sequence")
            return Value()
        if (
            external == "starlette.requests.Request"
            and flow.program.external(symbol, node.func) == external
            and len(args) == 1
            and not keywords
            and args[0].key in flow.mapping_keys
            and flow.member(args[0], "type", env).key == "'http'"
        ):
            return self.request(args[0], env)
        return None

    def continued(self, symbol: Symbol, bindings: dict[str, Value]) -> bool:
        if symbol.node is not self.continuation:
            return False
        bindings["#http:request"] = self.request(bindings["scope"], bindings)
        self.states.append(bindings.copy())
        return True

    def unknown_call(
        self, node: ast.Call, values: tuple[Value, ...], env: dict[str, Value]
    ) -> None:
        if not self.preparing or self.continuation is None:
            return
        pending = list(values)
        seen: set[str] = set()
        while pending:
            check_deadline(self.flow.deadline)
            value = pending.pop()
            if value.key in seen:
                continue
            seen.add(value.key)
            if value.key in self.next_keys or (
                value.key in self.middleware_instances
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "app"
            ):
                self.incomplete = True
                return
            pending.extend(
                env[key]
                for key in self.flow.members.get(value.key, {}).values()
                if key in env
            )
            if value.key in self.flow.bound_receivers:
                pending.append(self.flow.bound_receivers[value.key])

    def prepare(self, tool: ToolBinding) -> list[dict[str, Value]] | None:
        flow = self.flow
        roots = tool_servers(flow.program, tool)
        if len(roots) != 1:
            return None
        root = roots[0]
        assert isinstance(root.node, ast.Call)
        owner = flow.program.resolve(root.file, qualified_name(root.node.func) or "")
        method = flow.program.instance_method(owner, "http_app") if owner else None
        if (
            owner is None
            or method is None
            or not isinstance(method.node, Function)
            or method.node.decorator_list
        ):
            return None
        from sentinel.static.launches import instance as server_instance

        def reachable(node: ast.AST, seen: frozenset[ast.AST] = frozenset()) -> bool:
            enclosing = flow.program.parents.get(node)
            while enclosing is not None and not isinstance(enclosing, Function):
                enclosing = flow.program.parents.get(enclosing)
            if enclosing is None or enclosing is method.node:
                return True
            if enclosing in seen or len(seen) >= 64:
                return False
            return any(
                reachable(caller.node, seen | {enclosing})
                for caller in flow.registrations.callers(enclosing)
            )

        for file in flow.program.files:
            for node in ast.walk(file.tree):
                check_deadline(flow.deadline)
                mutation = (
                    isinstance(node, ast.Attribute)
                    and node.attr == "http_app"
                    and isinstance(node.ctx, (ast.Store, ast.Del))
                )
                values = (
                    [node.value]
                    if mutation and isinstance(node, ast.Attribute)
                    else [*node.args, *(kw.value for kw in node.keywords)]
                    if isinstance(node, ast.Call)
                    else []
                )
                for value in values:
                    context = Symbol(file, "HTTP application mutation", node)
                    server_value = server_instance(flow.program, context, value)
                    class_value = flow.program.resolve_in(
                        context, qualified_name(value) or ""
                    )
                    if (
                        (server_value is not None and server_value.node is root.node)
                        or (class_value is not None and class_value.node is owner.node)
                    ) and reachable(node):
                        flow.unresolved(
                            context, node, "replaced or escaped HTTP application"
                        )
                        return None
        parameters = method.node.args
        if not parameters.args or parameters.posonlyargs:
            return None
        server = Value(
            key=_key("http-server", root.file.relative_path, str(root.node.lineno)),
            instance=(owner.file.relative_path, owner.name),
        )
        self.servers.add(server.key)
        flow.record_keys.add(server.key)
        env = {parameters.args[0].arg: server}
        positional = parameters.args[len(parameters.args) - len(parameters.defaults) :]
        for parameter, default in [
            *zip(positional, parameters.defaults, strict=True),
            *zip(parameters.kwonlyargs, parameters.kw_defaults, strict=True),
        ]:
            if default is None:
                return None
            env[parameter.arg] = flow.expression(method, default, {})
        if any(parameter.arg not in env for parameter in parameters.args):
            return None
        if parameters.kwarg:
            mapping = Value(key=_key(server.key, "http-options"))
            flow.mapping_keys.add(mapping.key)
            env[parameters.kwarg.arg] = mapping
        if parameters.vararg:
            return None
        self.preparing = True
        self.incomplete = False
        self.next_keys = set()
        self.middleware_instances = set()
        try:
            app = flow.function(method, env)
            layers = self.applications.get(app.key)
            if layers is None:
                return None
            self.continuation = ast.FunctionDef(
                name="http_next",
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg=name) for name in ("scope", "receive", "send")],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=[],
                decorator_list=[],
            )
            ast.copy_location(self.continuation, method.node)
            next_value = Value(key=_key(server.key, "http-next"))
            self.next_keys.add(next_value.key)
            flow.callables[next_value.key] = Symbol(
                method.file, "http_next", self.continuation
            )
            for layer in reversed(layers):
                if "#member:unknown:" + layer.key in env:
                    return None
                factory, options, registration = self.layers[layer.key]
                env.update({"#http-factory": factory, "#http-next": next_value})
                names = {
                    f"#http-option:{name}": value for name, value in options.items()
                }
                env.update(names)
                call = ast.copy_location(
                    ast.Call(
                        func=ast.Name(id="#http-factory", ctx=ast.Load()),
                        args=[ast.Name(id="#http-next", ctx=ast.Load())],
                        keywords=[
                            ast.keyword(
                                arg=name,
                                value=ast.Name(
                                    id=f"#http-option:{name}", ctx=ast.Load()
                                ),
                            )
                            for name in options
                        ],
                    ),
                    registration.node,
                )
                instance = flow.expression(registration, call, env)
                if instance.instance is None:
                    return None
                self.middleware_instances.add(instance.key)
                env["#http-layer"] = instance
                next_value = flow.expression(
                    registration,
                    ast.Attribute(
                        value=ast.Name(id="#http-layer", ctx=ast.Load()),
                        attr="__call__",
                        ctx=ast.Load(),
                    ),
                    env,
                )
                if next_value.key not in flow.callables:
                    return None
            scope = Value(key=_key(server.key, "http-scope"))
            state = Value(key=_key(scope.key, "state"))
            flow.mapping_keys.update((scope.key, state.key))
            for name, scope_value in {
                "type": Value(key="'http'"),
                "method": Value(key="'POST'"),
                "path": Value(
                    sources=frozenset({"http:path"}), key=_key(scope.key, "path")
                ),
                "headers": Value(
                    sources=frozenset({"http:headers"}), key=_key(scope.key, "headers")
                ),
                "state": state,
            }.items():
                env[flow.member_key(scope, name)] = scope_value
            env.update({"#http-app": next_value, "#http-scope": scope})
            self.states = []
            call = ast.copy_location(
                ast.Call(
                    func=ast.Name(id="#http-app", ctx=ast.Load()),
                    args=[
                        ast.Name(id="#http-scope", ctx=ast.Load()),
                        ast.Constant(None),
                        ast.Constant(None),
                    ],
                    keywords=[],
                ),
                method.node,
            )
            flow.expression(method, call, env)
            return None if self.incomplete else self.states.copy()
        finally:
            self.continuation = None
            self.preparing = False
