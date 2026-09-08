"""Source-established ASGI middleware state for registered FastMCP tools."""

from __future__ import annotations

import ast
from collections.abc import Iterator
from typing import TYPE_CHECKING

from sentinel.static.ast_utils import qualified_name, scope_nodes
from sentinel.static.discovery import Function, Symbol, ToolBinding
from sentinel.static.execution import check_deadline
from sentinel.static.lifespan import tool_servers
from sentinel.static.path_flow import UNKNOWN_VALUE, Value, _key, member_label

if TYPE_CHECKING:
    from sentinel.static.launches import Launch
    from sentinel.static.path_flow import PathFlow


class HTTPContext:
    def __init__(self, flow: PathFlow) -> None:
        self.flow = flow
        self.servers: set[str] = set()
        self.methods: dict[ast.AST, tuple[Symbol, Symbol] | None] = {}
        self.layers: dict[str, tuple[Value, dict[str, Value], Symbol]] = {}
        self.sequences: dict[str, tuple[Value, ...]] = {}
        self.applications: dict[str, tuple[Value, ...]] = {}
        self.base_dispatches: dict[
            tuple[ast.AST, frozenset[ast.AST], frozenset[ast.Call]], Symbol | None
        ] = {}
        self.base_requests: set[ast.Call] = set()
        self.base_next_calls: set[ast.Call] = set()
        self.continuation: ast.FunctionDef | None = None
        self.states: list[dict[str, Value]] = []
        self.preparing = False
        self.incomplete = False
        self.next_keys: set[str] = set()
        self.middleware_instances: set[str] = set()
        self.state_owners: dict[str, Value] = {}
        self.prepared_states: dict[ast.AST, list[dict[str, Value]]] = {}
        self.sdk_records: set[str] = set()
        self.sdk_apps: set[str] = set()
        self.sdk_primitives: dict[ast.Call, tuple[Value, str]] = {}
        self.sdk_preparing = False
        self.sdk_skipped_calls: set[ast.Call] = set()
        self.launch_paths: dict[ast.Call, dict[ast.If, bool]] = {}
        self.sdk_path: dict[ast.If, bool] = {}
        self.sdk_entries: list[
            tuple[Value | None, Value, Symbol, dict[str, Value]]
        ] = []
        self.attached_registrations: set[ast.Call] = set()
        self.sdk_class_intact: dict[ast.AST, bool] = {}
        self.decisions: dict[ast.If | ast.Try, bool] = {}
        self.decision_sources: dict[ast.If | ast.Try, Symbol] = {}
        self.pending_decisions: list[dict[ast.If | ast.Try, bool]] = []
        self.executed_functions: set[ast.AST] = set()
        self.initialization_states: list[dict[str, Value]] = []

    def reachable(
        self, node: ast.AST, roots: set[ast.AST], seen: frozenset[ast.AST] = frozenset()
    ) -> bool:
        flow = self.flow
        enclosing = flow.program.parents.get(node)
        while enclosing is not None and not isinstance(enclosing, Function):
            enclosing = flow.program.parents.get(enclosing)
        if enclosing is None or enclosing in roots:
            return True
        if enclosing in seen or len(seen) >= 64:
            return False
        return any(
            self.reachable(caller.node, roots, seen | {enclosing})
            for caller in flow.registrations.callers(enclosing)
        )

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

    def sdk_record_intact(self, value: Value, env: dict[str, Value]) -> bool:
        fields = self.flow.members.get(value.key, {})
        return (
            value.key in self.sdk_records
            and "#member:unknown:" + value.key not in env
            and not any(fields.get(name) in env for name in ("__class__", "__dict__"))
        )

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
        primitive = self.sdk_primitives.get(node)
        if primitive is not None:
            server, operation = primitive
            if not self.sdk_record_intact(server, env):
                flow.unresolved(symbol, node, "replaced or escaped SDK server")
                return UNKNOWN_VALUE
            if operation != "run":
                app = Value(
                    key=_key(server.key, operation, "application", *flow.call_sites)
                )
                self.sdk_apps.add(app.key)
                self.sdk_records.add(app.key)
                flow.record_keys.add(app.key)
                self.applications[app.key] = ()
                env[flow.member_key(app, "user_middleware")] = flow.expression(
                    symbol,
                    ast.copy_location(ast.List(elts=[], ctx=ast.Load()), node),
                    env,
                )
                return app
            transport = member_label(args[0]) if args else None
            if transport == "stdio":
                self.sdk_entries.append((None, server, symbol, env.copy()))
                return UNKNOWN_VALUE
            if transport not in {"sse", "streamable-http"}:
                flow.unresolved(symbol, node, "unresolved SDK launch transport")
                return UNKNOWN_VALUE
            provider = "sse_app" if transport == "sse" else "streamable_http_app"
            for marker in flow.members.get(server.key, {}).values():
                if marker in flow.global_members:
                    env.setdefault(marker, flow.global_members[marker])
            settings = flow.member(server, "settings", env)
            if not self.sdk_record_intact(settings, env) or any(
                (marker := flow.member_key(record, field)) in env
                and env[marker].key != "None"
                for record, field in (
                    (server, "_auth_server_provider"),
                    (server, "_token_verifier"),
                    (settings, "auth"),
                )
            ):
                flow.unresolved(
                    symbol, node, "SDK authentication configuration is not modeled"
                )
                return UNKNOWN_VALUE
            env["#sdk-server"] = server
            env["#sdk-mount-path"] = args[1] if len(args) > 1 else Value(key="None")
            call = ast.copy_location(
                ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="#sdk-server", ctx=ast.Load()),
                        attr=provider,
                        ctx=ast.Load(),
                    ),
                    args=[ast.Name(id="#sdk-mount-path", ctx=ast.Load())]
                    if transport == "sse"
                    else [],
                    keywords=[],
                ),
                node,
            )
            app = flow.expression(symbol, call, env)
            if app.key in self.sdk_apps and self.sdk_record_intact(app, env):
                self.sdk_entries.append((app, server, symbol, env.copy()))
            else:
                flow.unresolved(symbol, node, "unresolved SDK application provider")
            return UNKNOWN_VALUE
        if (
            receiver.key in self.sdk_apps
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_middleware"
        ):
            if (
                len(args) != 1
                or None in keywords
                or "#member:unknown:" + receiver.key in env
            ):
                return None
            layer = Value(key=_key(receiver.key, str(node.lineno), *flow.call_sites))
            self.layers[layer.key] = (
                args[0],
                {name: value for name, value in keywords.items() if name is not None},
                symbol,
            )
            previous = env.get(flow.member_key(receiver, "#middleware"), receiver)
            layers = self.applications.get(previous.key)
            if layers is None:
                return None
            layout = Value(key=_key(previous.key, layer.key))
            self.applications[layout.key] = (layer, *layers)
            env[flow.member_key(receiver, "#middleware")] = layout
            members = flow.member(receiver, "user_middleware", env)
            elements = flow.sequence_elements(members, env)
            if elements is None:
                flow.unresolved(symbol, node, "unresolved SDK middleware list")
                return None
            flow.record_keys.add(layer.key)
            env[flow.member_key(layer, "cls")] = args[0]
            for index, value in enumerate((layer, *elements)):
                env[flow.member_key(members, index)] = value
            env[flow.member_key(members, "#length")] = Value(
                key=repr(len(elements) + 1)
            )
            self.attached_registrations.add(node)
            return Value(key="None")
        builtin = (
            external
            if not external.startswith("builtins.")
            or flow.program.external(symbol, node.func) == external
            else ""
        )
        if (
            args
            and builtin in {"callable", "builtins.callable"}
            and len(args) == 1
            and not keywords
            and args[0].key in flow.callables
            and not args[0].maybe_missing
            and not args[0].maybe_none
        ):
            return Value(key="True")
        if args and args[0].key in self.sdk_records and not keywords:
            if (
                builtin in {"type", "builtins.type", "id", "builtins.id"}
                and len(args) == 1
            ):
                return UNKNOWN_VALUE
            if builtin in {
                "getattr",
                "builtins.getattr",
                "hasattr",
                "builtins.hasattr",
                "setattr",
                "builtins.setattr",
            } and len(args) in {2, 3}:
                field = member_label(args[1])
                if isinstance(field, str) and not field.startswith("__"):
                    value = flow.member(args[0], field, env)
                    if external.endswith("setattr") and len(args) == 3:
                        env[flow.member_key(args[0], field)] = args[2]
                        return Value(key="None")
                    if not value.maybe_missing:
                        return (
                            Value(key="True") if external.endswith("hasattr") else value
                        )
        if node in self.base_requests:
            return self.request(args[0], env)
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
        if node in self.base_next_calls:
            self.incomplete = True
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
            pending.extend(self.flow.closures.get(value.key, {}).values())
            if value.key in self.flow.bound_receivers:
                pending.append(self.flow.bound_receivers[value.key])

    def base_http_layer(self, factory: Value, next_value: Value) -> Value | None:
        """Lower the genuine BaseHTTPMiddleware pre-continuation dispatch contract."""
        flow = self.flow
        owner = flow.callables.get(factory.key)
        if owner is None or not isinstance(owner.node, ast.ClassDef):
            return None
        check_deadline(flow.deadline)
        key = (
            owner.node,
            frozenset(self.executed_functions & flow.program.source_functions),
            frozenset(self.attached_registrations),
        )
        if key not in self.base_dispatches:
            self.base_dispatches[key] = self.resolve_base_http_dispatch(owner)
        dispatch = self.base_dispatches[key]
        if dispatch is None:
            return None
        assert isinstance(dispatch.node, Function)
        parameters = dispatch.node.args
        instance = Value(
            key=_key("base-http-instance", factory.key, next_value.key),
            instance=(owner.file.relative_path, owner.name),
        )
        method = Value(key=_key(instance.key, "dispatch"))
        flow.record_keys.add(instance.key)
        flow.callables[method.key] = dispatch
        flow.bound_receivers[method.key] = instance
        # This adapter is scanner-owned syntax, never imported or executed target code.
        wrapper = ast.parse(
            "async def base_http(scope, receive, send):\n"
            "    request = source_request(scope)\n"
            "    async def call_next(request):\n"
            "        return await next_layer(scope, receive, send)\n"
            "    return await dispatch(request, call_next)\n"
        ).body[0]
        assert isinstance(wrapper, ast.AsyncFunctionDef)
        flow.program.parents.update(
            (child, parent)
            for parent in ast.walk(wrapper)
            for child in ast.iter_child_nodes(parent)
        )
        for part in ast.walk(wrapper):
            if (
                isinstance(part, ast.Call)
                and isinstance(part.func, ast.Name)
                and part.func.id == "source_request"
            ):
                self.base_requests.add(part)
        self.base_next_calls.update(
            part
            for part in ast.walk(dispatch.node)
            if isinstance(part, ast.Call)
            and isinstance(part.func, ast.Name)
            and part.func.id == parameters.args[2].arg
        )
        value = Value(key=_key(instance.key, "asgi-adapter"))
        flow.callables[value.key] = Symbol(dispatch.file, "base_http", wrapper)
        flow.closures[value.key] = {"dispatch": method, "next_layer": next_value}
        self.next_keys.add(value.key)
        return value

    def resolve_base_http_dispatch(self, owner: Symbol) -> Symbol | None:
        flow = self.flow
        order = flow.program.method_order(owner)
        if order is None or order[-1] != "starlette.middleware.base.BaseHTTPMiddleware":
            return None
        classes = {parent.node for parent in order if isinstance(parent, Symbol)}
        roots = self.executed_functions | {
            part
            for owner_class in classes
            for part in scope_nodes(owner_class)
            if isinstance(part, Function)
        }
        for file in flow.program.files:
            for node in ast.walk(file.tree):
                check_deadline(flow.deadline)
                values = (
                    [node.value]
                    if isinstance(node, ast.Attribute)
                    and isinstance(node.ctx, (ast.Store, ast.Del))
                    else [*node.args, *(kw.value for kw in node.keywords)]
                    if isinstance(node, ast.Call)
                    else []
                )
                context = Symbol(file, "middleware mutation", node)
                if isinstance(node, ast.Call) and (
                    node in self.attached_registrations
                    or flow.program.external(context, node.func)
                    == "starlette.middleware.Middleware"
                ):
                    continue
                if any(
                    resolved is not None and resolved.node in classes
                    for value in values
                    for resolved in [
                        flow.program.resolve_in(context, qualified_name(value) or "")
                    ]
                ) and self.reachable(node, roots):
                    flow.unresolved(
                        context, node, "replaced or escaped HTTP middleware"
                    )
                    return None
        hooks = {
            "__init__",
            "__new__",
            "__call__",
            "__getattr__",
            "__getattribute__",
            "__setattr__",
            "dispatch_func",
        }
        for parent in order[:-1]:
            if not isinstance(parent, Symbol) or not isinstance(
                parent.node, ast.ClassDef
            ):
                return None
            if parent.node.decorator_list or any(
                (isinstance(part, Function) and part.name in hooks)
                or (
                    isinstance(part, ast.Name)
                    and isinstance(part.ctx, ast.Store)
                    and part.id in hooks
                )
                for part in scope_nodes(parent.node)
            ):
                return None
        dispatch = flow.program.instance_method(owner, "dispatch")
        if (
            dispatch is None
            or not isinstance(dispatch.node, Function)
            or dispatch.node.decorator_list
        ):
            return None
        parameters = dispatch.node.args
        if (
            len(parameters.args) != 3
            or parameters.posonlyargs
            or parameters.vararg
            or parameters.kwarg
            or parameters.kwonlyargs
        ):
            return None
        return dispatch

    def application_method(self, root: Symbol) -> tuple[Symbol, Symbol] | None:
        check_deadline(self.flow.deadline)
        if root.node not in self.methods:
            self.methods[root.node] = self.resolve_application_method(root)
        return self.methods[root.node]

    def resolve_application_method(self, root: Symbol) -> tuple[Symbol, Symbol] | None:
        flow = self.flow
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
                    ) and self.reachable(node, {method.node}):
                        flow.unresolved(
                            context, node, "replaced or escaped HTTP application"
                        )
                        return None
        return owner, method

    def prepare_launch(
        self, tool: ToolBinding, launch: Launch
    ) -> list[dict[str, Value]] | None:
        flow = self.flow
        if flow.rule_id not in {"SENT-012", "SENT-015", "SENT-016"}:
            return None
        roots = tool_servers(flow.program, tool)
        if len(roots) != 1 or roots[0].node is not launch.server:
            return None
        root = roots[0]
        assert isinstance(root.node, ast.Call)
        if flow.program.external(root, root.node.func) != "mcp.server.fastmcp.FastMCP":
            return None
        if launch.call.args or any(
            keyword.arg is None for keyword in launch.call.keywords
        ):
            flow.unresolved(root, launch.call, "unresolved SDK launch argument binding")
            return None
        if len(root.node.args) > 4 or any(
            keyword.arg is None
            or (
                keyword.arg in {"auth", "auth_server_provider", "token_verifier"}
                and not (
                    isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is None
                )
            )
            for keyword in root.node.keywords
        ):
            flow.unresolved(
                root, root.node, "SDK authentication configuration is not modeled"
            )
            return None
        if root.node not in self.sdk_class_intact:
            from sentinel.static.launches import instance as server_instance

            intact = True
            reachable_files = flow.program.reachable_files(
                {root.file.relative_path, launch.function.file.relative_path}
            )
            for file in flow.program.files:
                if file.relative_path not in reachable_files:
                    continue
                for node in ast.walk(file.tree):
                    check_deadline(flow.deadline)
                    values = (
                        [node.value]
                        if isinstance(node, (ast.Assign, ast.AnnAssign))
                        or (
                            isinstance(node, ast.Attribute)
                            and isinstance(node.ctx, (ast.Store, ast.Del))
                        )
                        else [*node.args, *(keyword.value for keyword in node.keywords)]
                        if isinstance(node, ast.Call)
                        else []
                    )
                    if any(
                        value is not None
                        and flow.program.external(
                            Symbol(file, "SDK class mutation", node), value
                        )
                        == "mcp.server.fastmcp.FastMCP"
                        for value in values
                    ):
                        intact = False
                    enclosing = flow.program.parents.get(node)
                    while enclosing is not None and not isinstance(enclosing, Function):
                        enclosing = flow.program.parents.get(enclosing)
                    if (
                        enclosing is None
                        and not isinstance(node, (ast.Assign, ast.AnnAssign))
                        and any(
                            value is not None
                            and (
                                selected := server_instance(
                                    flow.program,
                                    Symbol(file, "module server mutation", node),
                                    value,
                                )
                            )
                            is not None
                            and selected.node is root.node
                            for value in values
                        )
                    ):
                        intact = False
            self.sdk_class_intact[root.node] = intact
        if not self.sdk_class_intact[root.node]:
            flow.unresolved(
                root, root.node, "replaced SDK class or module-level server state"
            )
            return None
        owner = flow.program.parents.get(launch.call)
        while owner is not None and not isinstance(owner, Function):
            owner = flow.program.parents.get(owner)
        if (
            not isinstance(owner, Function)
            or owner.decorator_list
            or any(
                (
                    owner.args.args,
                    owner.args.posonlyargs,
                    owner.args.kwonlyargs,
                    owner.args.vararg,
                    owner.args.kwarg,
                )
            )
        ):
            return None
        context = Symbol(launch.function.file, owner.name, owner)
        if launch.call not in self.launch_paths:
            self.launch_paths[launch.call] = self.source_launch_path(
                owner.body, launch.call
            )
        self.sdk_path = self.launch_paths[launch.call]
        server = Value(key=_key("sdk-server", root.file.relative_path, root.name))
        self.sdk_records.add(server.key)
        flow.record_keys.add(server.key)
        flow.globals[(root.file.relative_path, root.name)] = server
        env: dict[str, Value] = {}
        settings = Value(key=_key(server.key, "settings"))
        self.sdk_records.add(settings.key)
        flow.record_keys.add(settings.key)
        env[flow.member_key(server, "settings")] = settings
        env[flow.member_key(settings, "json_response")] = Value(key="False")
        for keyword in root.node.keywords:
            if keyword.arg == "json_response":
                env[flow.member_key(settings, "json_response")] = flow.expression(
                    root, keyword.value, env
                )
        for name in ("run", "sse_app", "streamable_http_app"):
            arguments = (
                "transport='stdio', mount_path=None"
                if name == "run"
                else "mount_path=None"
                if name == "sse_app"
                else ""
            )
            passed = "transport, mount_path" if name == "run" else ""
            function = ast.parse(
                f"def {name}({arguments}):\n    return sdk_primitive({passed})\n"
            ).body[0]
            assert isinstance(function, ast.FunctionDef)
            ast.copy_location(function, root.node)
            flow.program.parents.update(
                (child, parent)
                for parent in ast.walk(function)
                for child in ast.iter_child_nodes(parent)
            )
            for part in ast.walk(function):
                if hasattr(part, "lineno"):
                    ast.copy_location(part, root.node)
                if isinstance(part, ast.Call):
                    self.sdk_primitives[part] = (server, name)
            callback = Value(key=_key(server.key, name))
            flow.callables[callback.key] = Symbol(root.file, name, function)
            env[flow.member_key(server, name)] = callback
        flow.global_members.update(env)
        self.sdk_entries = []
        self.sdk_skipped_calls = {
            item.call
            for item in flow.program.launches
            if item.server is root.node and item.call is not launch.call
        }
        self.sdk_preparing = self.preparing = True
        self.incomplete = False
        self.next_keys = set()
        self.middleware_instances = set()
        try:
            flow.function(context, env)
            if not self.sdk_entries:
                flow.unresolved(
                    context,
                    launch.call,
                    "SDK launch did not establish a served application",
                )
                return None
            self.initialization_states = [
                local.copy() for _, _, _, local in self.sdk_entries
            ]
            states = []
            for app, actual_server, source, local in self.sdk_entries:
                if app is None:
                    continue
                layout = local.get(flow.member_key(app, "#middleware"), app)
                layers = self.applications.get(layout.key)
                if layers is None:
                    return None
                prepared = self.middleware_states(actual_server, source, layers, local)
                if prepared is None:
                    return None
                states.extend(prepared)
            return states
        finally:
            self.sdk_preparing = self.preparing = False
            self.continuation = None
            self.sdk_skipped_calls = set()
            self.sdk_path = {}

    def source_launch_path(
        self, statements: list[ast.stmt], call: ast.Call
    ) -> dict[ast.If, bool]:
        """Constrain plain startup branches to paths that reach this launch."""
        selected = {}
        for statement in statements:
            check_deadline(self.flow.deadline)
            contains = any(part is call for part in ast.walk(statement))
            if isinstance(statement, ast.If):
                if contains:
                    truth = any(
                        part is call
                        for child in statement.body
                        for part in ast.walk(child)
                    )
                    selected[statement] = truth
                    selected.update(
                        self.source_launch_path(
                            statement.body if truth else statement.orelse, call
                        )
                    )
                else:
                    terminals = [
                        bool(branch) and isinstance(branch[-1], (ast.Return, ast.Raise))
                        for branch in (statement.body, statement.orelse)
                    ]
                    if terminals[0] != terminals[1]:
                        selected[statement] = not terminals[0]
            if contains:
                # Do not infer termination through try/finally, loops or helpers.
                break
        return selected

    def launch_variants(
        self, tool: ToolBinding, launch: Launch
    ) -> Iterator[list[dict[str, Value]] | None]:
        flow = self.flow
        original, members = flow.globals.copy(), flow.global_members.copy()
        self.pending_decisions = [{}]
        attempts = 0
        while self.pending_decisions and attempts < 16:
            self.decisions = self.pending_decisions.pop()
            flow.globals = original.copy()
            flow.global_members = members.copy()
            attempts += 1
            yield self.prepare_launch(tool, launch)
        if self.pending_decisions:
            flow.unresolved(
                launch.function,
                launch.call,
                "SDK initialization exceeds 16 source paths",
            )
        self.pending_decisions = []

    def startup_branch(
        self, symbol: Symbol, node: ast.If | ast.Try, env: dict[str, Value]
    ) -> bool | None:
        if not self.sdk_preparing:
            return None
        flow = self.flow
        if isinstance(node, ast.If):
            if node in self.sdk_path:
                return self.sdk_path[node]
            selector = (
                node.test.operand
                if isinstance(node.test, ast.UnaryOp)
                and isinstance(node.test.op, ast.Not)
                else node.test
            )
            relevant = (
                isinstance(selector, ast.Attribute)
                and selector.attr == "json_response"
                and flow.bound_value(selector.value, env).key in self.sdk_records
            )
        else:
            relevant = any(
                isinstance(part, ast.Name)
                and env.get(
                    part.id,
                    flow.globals.get(
                        (symbol.file.relative_path, part.id), UNKNOWN_VALUE
                    ),
                ).key
                in self.sdk_records
                for statement in node.body
                for part in ast.walk(statement)
            )
        if not relevant:
            return None
        self.decision_sources[node] = symbol
        if node not in self.decisions:
            self.pending_decisions.append({**self.decisions, node: False})
            self.decisions[node] = True
        return self.decisions[node]

    def prepare(self, tool: ToolBinding) -> list[dict[str, Value]] | None:
        flow = self.flow
        roots = tool_servers(flow.program, tool)
        if len(roots) != 1:
            return None
        root = roots[0]
        assert isinstance(root.node, ast.Call)
        if not flow.launch_states and root.node in self.prepared_states:
            return [state.copy() for state in self.prepared_states[root.node]]
        application = self.application_method(root)
        if application is None:
            return None
        owner, method = application
        assert isinstance(method.node, Function)
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
            states = self.middleware_states(server, method, layers, env)
            if states is None:
                return None
            if not flow.launch_states and all(
                flow.reusable_state(
                    [
                        value
                        for key, value in state.items()
                        if key.startswith(flow.helper_state_prefixes)
                        and not key.startswith("#member:")
                    ],
                    state,
                )
                for state in self.states
            ):
                self.prepared_states[root.node] = [
                    state.copy() for state in self.states
                ]
            return self.states.copy()
        finally:
            self.continuation = None
            self.preparing = False

    def middleware_states(
        self,
        server: Value,
        method: Symbol,
        layers: tuple[Value, ...],
        env: dict[str, Value],
    ) -> list[dict[str, Value]] | None:
        flow = self.flow
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
            adapted = self.base_http_layer(factory, next_value) if not options else None
            if adapted is not None:
                next_value = adapted
                continue
            env.update({"#http-factory": factory, "#http-next": next_value})
            names = {f"#http-option:{name}": value for name, value in options.items()}
            env.update(names)
            call = ast.copy_location(
                ast.Call(
                    func=ast.Name(id="#http-factory", ctx=ast.Load()),
                    args=[ast.Name(id="#http-next", ctx=ast.Load())],
                    keywords=[
                        ast.keyword(
                            arg=name,
                            value=ast.Name(id=f"#http-option:{name}", ctx=ast.Load()),
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
        if self.incomplete:
            return None
        return self.states.copy()
