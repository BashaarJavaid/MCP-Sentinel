"""Bounded Python path flow over the shared source index; no target execution."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
from dataclasses import dataclass, replace

from sentinel.report.model import ReportWarning
from sentinel.static.ast_utils import (
    import_aliases,
    match_from_node,
    qualified_name,
    resolve_name,
    scope_nodes,
)
from sentinel.static.discovery import Function, PythonProgram, Symbol, ToolBinding
from sentinel.static.execution import Sources, check_deadline, union
from sentinel.static.model import RuleRunState
from sentinel.static.registration_flow import RegistrationFlow


@dataclass(frozen=True, slots=True)
class Value:
    sources: Sources = frozenset()
    key: str = ""
    resolved: bool = False
    contained: bool = False
    locations: frozenset[tuple[str, int]] = frozenset()
    path_object: bool = False
    repository_object: bool = False
    instance: tuple[str, str] | None = None
    option_safe: bool = False
    url_checks: frozenset[str] = frozenset()
    operator_credential: bool = False
    credential_fallback: bool = False
    credential_present: bool = False
    maybe_missing: bool = False
    maybe_none: bool = False


def combine(values: list[Value], key: str = "") -> Value:
    if values:
        first = values[0]
        if all(value is first or value == first for value in values[1:]) and (
            first.sources
            or not (first.contained or first.option_safe or first.url_checks)
        ):
            return replace(first, key=key) if key and key != first.key else first
    present = [value for value in values if value.key not in {"None", "#missing"}]
    if present and len(present) != len(values):
        return replace(
            combine(present, key),
            maybe_none=any(value.maybe_none or value.key == "None" for value in values),
            maybe_missing=any(value.maybe_missing for value in values),
        )
    tainted = [v for v in values if v.sources]
    keys = sorted({v.key for v in values})
    return Value(
        union(v.sources for v in values),
        key or (keys[0] if len(keys) == 1 else _key("merge", *keys)),
        bool(values) and all(v.resolved for v in values),
        bool(tainted) and all(v.contained for v in tainted),
        frozenset().union(*(v.locations for v in values)),
        bool(values) and all(v.path_object for v in values),
        bool(values) and all(v.repository_object for v in values),
        values[0].instance
        if values and all(v.instance == values[0].instance for v in values)
        else None,
        bool(tainted) and all(v.option_safe for v in tainted),
        frozenset.intersection(*(v.url_checks for v in tainted))
        if tainted
        else frozenset(),
        any(v.operator_credential for v in values),
        any(v.credential_fallback for v in values),
        bool(values) and all(v.credential_present for v in values),
        any(v.maybe_missing for v in values),
        any(v.maybe_none for v in values),
    )


def _key(*parts: str) -> str:
    return hashlib.sha256(json.dumps(parts).encode()).hexdigest()


UNKNOWN_MEMBER = object()


def member_label(value: Value) -> object:
    if value.sources:
        return UNKNOWN_MEMBER
    try:
        label = ast.literal_eval(value.key)
        hash(label)
        return label
    except (ValueError, SyntaxError, TypeError):
        return UNKNOWN_MEMBER


class PathFlow:
    rule_id = "SENT-012"
    helper_state_prefixes: tuple[str, ...] = (
        "#member:",
        "#global-value:",
        "#literal-choices:",
        "#context:",
        "#http:",
    )

    def __init__(
        self, program: PythonProgram, state: RuleRunState, deadline: float
    ) -> None:
        from sentinel.static.http_context import HTTPContext

        self.program = program
        self.state = state
        self.deadline = deadline
        self.active: set[tuple[str, str]] = set()
        self.exits: list[list[dict[str, Value]]] = []
        self.aliases = {
            file.relative_path: import_aliases(file) for file in program.files
        }
        self.globals: dict[tuple[str, str], Value] = {}
        self.global_members: dict[str, Value] = {}
        self.mapping_keys: set[str] = set()
        self.optional_mappings: dict[str, Value] = {}
        self.record_keys: set[str] = set()
        self.callables: dict[str, Symbol] = {}
        self.bound_receivers: dict[str, Value] = {}
        self.closures: dict[str, dict[str, Value]] = {}
        self.registrations = RegistrationFlow(program)
        self.members: dict[str, dict[object, str]] = {}
        self.member_defaults: dict[str, Value] = {}
        self.call_sites: list[str] = []
        self.yielding: set[tuple[str, str]] = set()
        self.argument_tuples: dict[str, tuple[Value, ...]] = {}
        self.path_conditions: dict[
            str, tuple[frozenset[str] | None, frozenset[str] | None]
        ] = {}
        self.common_paths: dict[str, tuple[Value, ...]] = {}
        self.path_arrays: dict[ast.AST, tuple[Value, ...]] = {}
        self.launch_call: ast.Call | None = None
        self.launch_states: list[dict[tuple[str, str], Value]] = []
        self.non_none: set[str] = set()
        self.workbooks: set[str] = set()
        self.http_clients: dict[str, str] = {}
        self.context_variables: dict[str, Value | None] = {}
        self.context_tokens: dict[str, str] = {}
        self.call_receivers: dict[ast.AST, Value] | None = None
        self.reported_warnings: set[tuple[str, int, str]] = set()
        self.http_context = HTTPContext(self)

    def entry(self, tool: ToolBinding, bindings: dict[str, Value]) -> None:
        from sentinel.static.launches import for_tool

        launches = for_tool(self.program, tool)
        if not launches:
            self.entry_handler(tool, bindings)
            return
        original = self.globals.copy()
        try:
            for launch in launches:
                self.globals = original.copy()
                if not isinstance(launch.function.node, Function):
                    self.entry_handler(tool, bindings.copy())
                    continue
                self.launch_call = launch.call
                self.launch_states = []
                self.function(launch.function, {})
                self.launch_call = None
                for globals_ in self.launch_states:
                    self.globals = globals_.copy()
                    start = len(self.state.matches)
                    self.entry_handler(tool, bindings.copy())
                    for index in range(start, len(self.state.matches)):
                        match = self.state.matches[index]
                        locations = json.loads(
                            match.captures.get("flow_locations", "[]")
                        )
                        locations.append(
                            [launch.function.file.relative_path, launch.call.lineno]
                        )
                        self.state.matches[index] = replace(
                            match,
                            captures={
                                **match.captures,
                                "launch_transports": json.dumps([launch.transport]),
                                "flow_locations": json.dumps(locations),
                            },
                        )
        finally:
            self.globals = original
            self.launch_call = None

    def entry_handler(self, tool: ToolBinding, bindings: dict[str, Value]) -> None:
        from sentinel.static.lifespan import tool_lifespan

        if (
            self.rule_id in {"SENT-015", "SENT-016"}
            and "#http:prepared" not in bindings
        ):
            states = self.http_context.prepare(tool)
            if states is not None:
                for state in states:
                    prepared = {
                        **bindings,
                        **{
                            key: value
                            for key, value in state.items()
                            if key.startswith(self.helper_state_prefixes)
                        },
                        "#http:prepared": Value(key="True"),
                    }
                    self.entry_handler(tool, prepared)
                self.entry_handler(
                    tool,
                    {
                        **bindings,
                        "#http:prepared": Value(key="True"),
                        "#http:no-request": Value(key="True"),
                    },
                )
                return
        node = tool.handler.node
        assert isinstance(node, Function)
        contexts = [
            parameter.arg
            for parameter in (
                *node.args.posonlyargs,
                *node.args.args,
                *node.args.kwonlyargs,
            )
            if parameter.arg not in bindings
            and parameter.annotation is not None
            and self.program.external(tool.handler, parameter.annotation)
            in {
                "fastmcp.Context",
                "fastmcp.server.context.Context",
                "mcp.server.fastmcp.Context",
                "mcp.server.fastmcp.server.Context",
            }
        ]
        lifespan = tool_lifespan(self.program, tool) if contexts else None
        if lifespan is not None:
            local: dict[str, Value] = {}
            identity = (lifespan.file.relative_path, lifespan.name)
            self.yielding.add(identity)
            try:
                value = self.function(lifespan, local)
            finally:
                self.yielding.remove(identity)
            bindings.update(
                (key, value)
                for key, value in local.items()
                if key.startswith("#member:")
            )
            for name in contexts:
                context = Value(
                    key=_key(
                        "sdk-context",
                        tool.handler.file.relative_path,
                        str(node.lineno),
                        name,
                    )
                )
                request = Value(key=_key(context.key, "request_context"))
                self.record_keys.update((context.key, request.key))
                bindings[name] = context
                bindings[self.member_key(context, "request_context")] = request
                bindings[self.member_key(request, "lifespan_context")] = value
        decorators = node.decorator_list
        if (
            tool.registration_decorator is not None
            and tool.registration_decorator in decorators
        ):
            decorators = decorators[decorators.index(tool.registration_decorator) + 1 :]
        if not decorators:
            self.function(tool.handler, bindings)
            return
        original = copy.copy(node)
        original.decorator_list = []
        key = _key(
            "registered-original", tool.handler.file.relative_path, tool.handler.name
        )
        self.callables[key] = Symbol(tool.handler.file, tool.handler.name, original)
        local = bindings.copy()
        local["#registered"] = self.decorate(
            tool.handler, Value(key=key), decorators, local
        )
        if local["#registered"].key not in self.callables:
            return
        positional = {p.arg for p in node.args.posonlyargs}
        invocation = ast.copy_location(
            ast.Call(
                func=ast.Name(id="#registered", ctx=ast.Load()),
                args=[
                    ast.Name(id=p.arg, ctx=ast.Load()) for p in node.args.posonlyargs
                ],
                keywords=[
                    ast.keyword(arg=name, value=ast.Name(id=name, ctx=ast.Load()))
                    for name in bindings
                    if not name.startswith("#") and name not in positional
                ],
            ),
            node,
        )
        self.expression(tool.handler, invocation, local)

    def decorate(
        self,
        symbol: Symbol,
        value: Value,
        decorators: list[ast.expr],
        env: dict[str, Value],
    ) -> Value:
        evaluated: list[tuple[ast.expr, Value]] = []
        for decorator in decorators:
            if (
                isinstance(decorator, ast.Call)
                and len(decorator.args) == 1
                and not decorator.keywords
                and (qualified_name(decorator.func) or "").split(".")[0] not in env
                and self.program.external(symbol, decorator.func) == "functools.wraps"
            ):
                wrapped = self.expression(symbol, decorator.args[0], env)
                if wrapped.key in self.callables:
                    continue
                evaluated.append((decorator, Value()))
                continue
            evaluated.append((decorator, self.expression(symbol, decorator, env)))
        for decorator, factory in reversed(evaluated):
            env["#decorator-factory"] = factory
            env["#decorator-value"] = value
            application = ast.copy_location(
                ast.Call(
                    func=ast.Name(id="#decorator-factory", ctx=ast.Load()),
                    args=[ast.Name(id="#decorator-value", ctx=ast.Load())],
                    keywords=[],
                ),
                decorator,
            )
            value = self.expression(symbol, application, env)
            if value.key not in self.callables:
                self.unresolved(symbol, decorator, "source decorator result unresolved")
                return value
        return value

    def function(self, symbol: Symbol, bindings: dict[str, Value]) -> Value:
        check_deadline(self.deadline)
        if self.http_context.continued(symbol, bindings):
            return Value()
        key = (
            symbol.file.relative_path,
            symbol.name + ":" + bindings.get("#callable-origin", Value()).key,
        )
        # ponytail: bound recursive interpretation; use summaries for deeper flows.
        if (
            key in self.active
            or len(self.active) >= 64
            or not isinstance(symbol.node, Function)
        ):
            self.unresolved(
                symbol,
                symbol.node,
                "recursive, deeper than 64 calls, or unsupported helper",
            )
            return combine(list(bindings.values()))
        self.active.add(key)
        self.exits.append([])
        try:
            for parameter in (
                *symbol.node.args.posonlyargs,
                *symbol.node.args.args,
                *symbol.node.args.kwonlyargs,
            ):
                value = bindings.get(parameter.arg)
                if (
                    value is not None
                    and not value.sources
                    and parameter.annotation is not None
                    and any(
                        resolve_name(
                            qualified_name(part) or "",
                            self.aliases[symbol.file.relative_path],
                        )
                        == "pathlib.Path"
                        for part in ast.walk(parameter.annotation)
                    )
                ):
                    bindings[parameter.arg] = replace(value, path_object=True)
            returned: list[Value] = []
            if self.statements(symbol, symbol.node.body, bindings, returned):
                self.exits[-1].append(bindings.copy())
            if self.exits[-1]:
                self.merge(bindings, self.exits[-1])
            result = combine(returned)
            if any(value.key in self.path_conditions for value in returned):
                pairs = [self.path_condition(value) for value in returned]
                false = [pair[0] for pair in pairs if pair[0] is not None]
                true = [pair[1] for pair in pairs if pair[1] is not None]
                self.path_conditions[result.key] = (
                    frozenset.intersection(*false) if false else None,
                    frozenset.intersection(*true) if true else None,
                )
            return result
        finally:
            self.exits.pop()
            self.active.remove(key)

    def unresolved(self, symbol: Symbol, node: ast.AST, reason: str) -> None:
        identity = (symbol.file.relative_path, getattr(node, "lineno", 1), reason)
        if identity in self.reported_warnings:
            return
        self.reported_warnings.add(identity)
        self.state.warnings.append(
            ReportWarning(
                code="static_flow_unresolved",
                message=(
                    f"{self.rule_id} at {symbol.file.relative_path}:"
                    f"{getattr(node, 'lineno', 1)}: {reason}; "
                    "protection is not established"
                ),
            )
        )

    def statements(
        self,
        symbol: Symbol,
        body: list[ast.stmt],
        env: dict[str, Value],
        returned: list[Value],
    ) -> bool:
        for node in body:
            if env.get("#http:stop", Value()).key == "True":
                return False
            check_deadline(self.deadline)
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = self.expression(symbol, node.value, env)
                targets = (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
                for target in targets:
                    if isinstance(target, (ast.Attribute, ast.Subscript)):
                        owner = self.expression(symbol, target.value, env)
                        env[f"#bound-expression:{id(target.value)}"] = owner
                        self.workbooks.discard(owner.key)
                    self.assign(target, value, env)
                    if isinstance(target, ast.Name) and env.get("#global:" + target.id):
                        env[
                            f"#global-value:{symbol.file.relative_path}:{target.id}"
                        ] = value
            elif isinstance(node, Function):
                original = copy.copy(node)
                original.decorator_list = []
                key = _key(
                    "closure",
                    symbol.file.relative_path,
                    str(node.lineno),
                    *self.call_sites,
                )
                self.callables[key] = Symbol(
                    symbol.file,
                    symbol.name + "." + node.name,
                    original,
                )
                self.closures[key] = env
                env[node.name] = self.decorate(
                    symbol, Value(key=key), node.decorator_list, env
                )
            elif isinstance(node, ast.Global):
                for name in node.names:
                    env["#global:" + name] = Value(key=name)
            elif isinstance(node, ast.Return):
                value = self.expression(symbol, node.value, env)
                facts = frozenset(
                    key.removeprefix("#path:")
                    for key, item in env.items()
                    if key.startswith("#path:") and item.contained
                )
                if value.key in self.path_conditions or (
                    facts and value.key in {"True", "False", "None"}
                ):
                    pair = self.path_condition(value)
                    result = replace(
                        value, key=_key("path-return", value.key, *sorted(facts))
                    )
                    self.path_conditions[result.key] = (
                        pair[0] | facts if pair[0] is not None else None,
                        pair[1] | facts if pair[1] is not None else None,
                    )
                    value = result
                returned.append(value)
                self.exits[-1].append(env.copy())
                return False
            elif isinstance(node, ast.Raise):
                return False
            elif isinstance(node, ast.Expr):
                if (
                    isinstance(node.value, ast.Yield)
                    and (symbol.file.relative_path, symbol.name) in self.yielding
                ):
                    returned.append(self.expression(symbol, node.value.value, env))
                else:
                    self.expression(symbol, node.value, env)
            elif isinstance(node, ast.If):
                if self.disabled_boundary(symbol, node, env):
                    # Analyze the configured-boundary condition. An operator's
                    # absent optional root does not promise a containment policy.
                    continue
                condition = self.expression(symbol, node.test, env)
                known = self.truth_value(condition, env)
                left, right = env.copy(), env.copy()
                if known is not False:
                    self.guard(symbol, node.test, left, True)
                    self.narrow(symbol, node.test, left, True)
                if known is not True:
                    self.guard(symbol, node.test, right, False)
                    self.narrow(symbol, node.test, right, False)
                branches = []
                if known is not False and self.statements(
                    symbol, node.body, left, returned
                ):
                    branches.append(left)
                if known is not True and self.statements(
                    symbol, node.orelse, right, returned
                ):
                    branches.append(right)
                if not branches:
                    return False
                self.merge(env, branches)
            elif isinstance(node, ast.Try):
                branches = []
                final_states = []
                success = env.copy()
                if self.statements(
                    symbol, node.body, success, returned
                ) and self.statements(symbol, node.orelse, success, returned):
                    branches.append(success)
                final_states.append(success)
                for handler in node.handlers:
                    failure = env.copy()
                    if self.statements(symbol, handler.body, failure, returned):
                        branches.append(failure)
                    final_states.append(failure)
                self.merge(env, branches or final_states)
                if not self.statements(symbol, node.finalbody, env, returned):
                    return False
                if not branches:
                    return False
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                for item in node.items:
                    value = self.expression(symbol, item.context_expr, env)
                    if item.optional_vars:
                        self.assign(item.optional_vars, value, env)
                if not self.statements(symbol, node.body, env, returned):
                    return False
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
                branch = env.copy()
                if isinstance(node, (ast.For, ast.AsyncFor)):
                    self.assign(
                        node.target, self.expression(symbol, node.iter, env), branch
                    )
                else:
                    self.expression(symbol, node.test, env)
                self.statements(symbol, node.body, branch, returned)
                self.merge(env, [env.copy(), branch])
                self.statements(symbol, node.orelse, env, returned)
            elif isinstance(node, ast.Match):
                self.expression(symbol, node.subject, env)
                branches = []
                for case in node.cases:
                    branch = env.copy()
                    if self.statements(symbol, case.body, branch, returned):
                        branches.append(branch)
                if not branches:
                    return False
                self.merge(env, branches)
            elif isinstance(node, ast.AugAssign):
                self.assign(
                    node.target,
                    combine(
                        [
                            self.expression(symbol, node.target, env),
                            self.expression(symbol, node.value, env),
                        ]
                    ),
                    env,
                )
            elif isinstance(node, ast.Assert):
                self.expression(symbol, node.test, env)
        return env.get("#http:stop", Value()).key != "True"

    @staticmethod
    def disabled_boundary(symbol: Symbol, node: ast.If, env: dict[str, Value]) -> bool:
        test = node.test
        if not (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Is)
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value is None
            and len(node.body) == 1
            and isinstance(node.body[0], ast.Return)
            and node.body[0].value is None
            and not node.orelse
        ):
            return False
        value = env.get(test.left.id)
        if value is None or value.sources or value.key == "None":
            return False
        definitions = {
            target.id: statement.value
            for statement in scope_nodes(symbol.node)
            if isinstance(statement, ast.Assign)
            for target in statement.targets
            if isinstance(target, ast.Name)
        }
        for call in scope_nodes(symbol.node):
            if not (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and call.func.attr in {"relative_to", "is_relative_to"}
                and call.args
            ):
                continue
            pending: list[ast.AST] = [call.args[0]]
            seen: set[str] = set()
            while pending:
                expression = pending.pop()
                if isinstance(expression, ast.Name):
                    if expression.id == test.left.id:
                        return True
                    if expression.id in definitions and expression.id not in seen:
                        seen.add(expression.id)
                        pending.append(definitions[expression.id])
                else:
                    pending.extend(ast.iter_child_nodes(expression))
        return False

    def member_key(self, value: Value, member: object) -> str:
        if value.key in self.http_context.state_owners:
            return self.member_key(self.http_context.state_owners[value.key], member)
        if value.key in self.optional_mappings:
            return self.member_key(self.optional_mappings[value.key], member)
        return self.members.setdefault(value.key, {}).setdefault(
            member, "#member:" + _key(value.key, repr(member))
        )

    def aggregate(self, value: Value, env: dict[str, Value]) -> Value:
        pending = [value]
        seen: set[str] = set()
        leaves = []
        while pending:
            check_deadline(self.deadline)
            current = pending.pop()
            if current.key in self.mapping_keys or current.key in self.record_keys:
                if current.key in seen:
                    continue
                seen.add(current.key)
                pending.extend(
                    env[key]
                    for key in self.members.get(current.key, {}).values()
                    if key in env
                )
                unknown = env.get("#member:unknown:" + current.key)
                if unknown is not None:
                    pending.append(unknown)
            else:
                leaves.append(current)
        return replace(
            value,
            sources=union(item.sources for item in leaves),
            locations=value.locations
            | frozenset().union(*(item.locations for item in leaves)),
        )

    def update_mapping(
        self, destination: Value, source: Value, env: dict[str, Value]
    ) -> None:
        unknown = env.get("#member:unknown:" + source.key)
        if source.key not in self.mapping_keys:
            unknown = source
        if unknown is not None:
            marker = "#member:unknown:" + destination.key
            env[marker] = combine([env.get(marker, Value()), unknown])
            for existing in self.members.get(destination.key, {}).values():
                if existing in env:
                    env[existing] = combine([env[existing], unknown])
        if source.key in self.mapping_keys:
            for label, existing in tuple(self.members.get(source.key, {}).items()):
                if existing in env:
                    env[self.member_key(destination, label)] = env[existing]

    def member(self, value: Value, member: object, env: dict[str, Value]) -> Value:
        if value.key in self.http_context.state_owners:
            return self.member(self.http_context.state_owners[value.key], member, env)
        if value.key in self.optional_mappings:
            return replace(
                self.member(self.optional_mappings[value.key], member, env),
                maybe_missing=True,
            )
        key = self.member_key(value, member)
        fallback = replace(
            env.get("#member:unknown:" + value.key, Value())
            if value.key in self.mapping_keys or value.key in self.record_keys
            else value,
            key=_key(value.key, repr(member)),
            contained=False,
            option_safe=False,
            url_checks=frozenset(),
            credential_present=False,
            maybe_missing=True,
        )
        if value.key in self.mapping_keys and "#member:unknown:" + value.key not in env:
            fallback = Value(key="#missing", maybe_missing=True)
        result = env.get(key, fallback)
        self.member_defaults.setdefault(key, fallback)
        return result

    def with_default(
        self, value: Value, default: Value, node: ast.AST, env: dict[str, Value]
    ) -> Value:
        if value.key == "#missing":
            return default
        if not value.maybe_missing:
            return value
        if (
            isinstance(node, ast.Dict)
            and not node.keys
            and value.key in self.mapping_keys
            and "#member:unknown:" + value.key not in env
        ):
            # ponytail: only fresh empty defaults; ambiguous writes weakly update
            # the populated alias. General mapping unions need branch identities.
            original = self.optional_mappings.get(value.key, value)
            result = replace(value, key=_key("optional-mapping", original.key))
            self.optional_mappings[result.key] = original
            self.mapping_keys.add(result.key)
            self.members[result.key] = self.members.setdefault(original.key, {})
            return result
        return combine([value, default])

    def http_client(self, value: Value, method: str, env: dict[str, Value]) -> bool:
        marker = self.members.get(value.key, {}).get(method)
        intact = (
            value.key in self.http_clients
            and "#member:unknown:" + value.key not in env
            and (marker is None or marker not in env)
        )
        if intact and self.http_clients[value.key] in {
            "atlassian.Jira",
            "atlassian.Confluence",
        }:
            session = self.member(value, "_session", env)
            return self.http_clients.get(
                session.key
            ) == "requests.Session" and self.http_client(session, "request", env)
        return intact

    def bound_value(self, node: ast.AST, env: dict[str, Value]) -> Value:
        evaluated = env.get(f"#bound-expression:{id(node)}")
        if evaluated is not None:
            return evaluated
        if isinstance(node, ast.Constant):
            return Value(key=repr(node.value))
        if isinstance(node, ast.Name):
            return env.get(node.id, Value())
        if isinstance(node, ast.Subscript):
            label = member_label(self.bound_value(node.slice, env))
            if label is not UNKNOWN_MEMBER:
                return self.member(self.bound_value(node.value, env), label, env)
        if isinstance(node, ast.Attribute):
            return self.member(self.bound_value(node.value, env), node.attr, env)
        return Value()

    def instance_member(self, value: Value, name: str) -> Symbol | None:
        if value.instance is None:
            return None
        path, owner = value.instance
        file = next(file for file in self.program.files if file.relative_path == path)
        symbol = self.program.resolve(file, owner)
        return self.program.instance_method(symbol, name) if symbol else None

    def assign(self, target: ast.AST, value: Value, env: dict[str, Value]) -> None:
        if isinstance(target, ast.Name):
            env[target.id] = value
        elif isinstance(target, (ast.Tuple, ast.List)):
            for child in target.elts:
                self.assign(child, value, env)
        elif isinstance(target, ast.Subscript):
            receiver = self.bound_value(target.value, env)
            if receiver.key:
                label = member_label(self.bound_value(target.slice, env))
                if label is not UNKNOWN_MEMBER:
                    previous = self.member(receiver, label, env)
                    if receiver.key in self.optional_mappings:
                        value = combine([previous, value])
                    env[self.member_key(receiver, label)] = replace(
                        value, maybe_missing=False
                    )
                else:
                    self.update_mapping(receiver, value, env)
        elif isinstance(target, ast.Attribute):
            receiver = self.bound_value(target.value, env)
            if receiver.instance is not None and (
                target.attr.startswith("__")
                or self.instance_member(receiver, target.attr) is not None
            ):
                for name, current in env.items():
                    if current.key == receiver.key:
                        env[name] = replace(current, instance=None)
            if receiver.key:
                self.member(receiver, target.attr, env)
                env[self.member_key(receiver, target.attr)] = replace(
                    value, maybe_missing=False
                )

    def merge(self, env: dict[str, Value], branches: list[dict[str, Value]]) -> None:
        if len(branches) == 1:
            # Most helper exits have one surviving branch. Avoid re-combining
            # every unchanged member, preserving the same protection semantics.
            env.update(branches[0])
            for name, value in branches[0].items():
                if name.startswith("#path:"):
                    env[name] = Value(contained=value.contained)
                elif not value.sources and (
                    value.contained or value.option_safe or value.url_checks
                ):
                    env[name] = replace(
                        value,
                        contained=False,
                        option_safe=False,
                        url_checks=frozenset(),
                    )
            return
        unknown = Value()
        first, *rest = branches or [{}]
        second = rest[0] if len(rest) == 1 else None
        for name in set().union(*(b.keys() for b in branches)):
            default = self.member_defaults.get(name, unknown)
            value = first.get(name, default)
            if (
                not name.startswith("#path:")
                and (
                    value.sources
                    or not (value.contained or value.option_safe or value.url_checks)
                )
                and (
                    second.get(name, default) is value
                    if second is not None
                    else all(branch.get(name, default) is value for branch in rest)
                )
            ):
                env[name] = value
                continue
            values = [branch.get(name, default) for branch in branches]
            env[name] = (
                Value(contained=all(value.contained for value in values))
                if name.startswith("#path:")
                else combine(values)
            )

    def truth_value(self, value: Value, env: dict[str, Value]) -> bool | None:
        if value.key in self.optional_mappings:
            return None
        if value.key in self.path_conditions:
            false, true = self.path_conditions[value.key]
            if false is None:
                return True
            if true is None:
                return False
        if value.maybe_missing or value.maybe_none:
            return None
        if value.key in self.record_keys and value.instance is not None:
            path, name = value.instance
            file = next(
                file for file in self.program.files if file.relative_path == path
            )
            owner = self.program.resolve(file, name)
            order = self.program.method_order(owner) if owner else None
            if order is not None and not any(
                (isinstance(part, Function) and part.name in {"__bool__", "__len__"})
                or (
                    isinstance(part, ast.Name)
                    and isinstance(part.ctx, ast.Store)
                    and part.id in {"__bool__", "__len__"}
                )
                for parent in order
                if isinstance(parent, Symbol)
                for part in scope_nodes(parent.node)
            ):
                return True
        if value.key in self.mapping_keys and "#member:unknown:" + value.key not in env:
            return any(
                marker in env for marker in self.members.get(value.key, {}).values()
            )
        literal = member_label(value)
        if literal is None or isinstance(literal, (str, bytes, bool, int, float)):
            return bool(literal)
        return None

    def path_condition(
        self, value: Value
    ) -> tuple[frozenset[str] | None, frozenset[str] | None]:
        return self.path_conditions.get(
            value.key,
            (
                None if value.key == "True" else frozenset(),
                None if value.key in {"False", "None"} else frozenset(),
            ),
        )

    def guard(
        self, symbol: Symbol, node: ast.AST, env: dict[str, Value], truth: bool
    ) -> None:
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            self.guard(symbol, node.operand, env, not truth)
        elif truth and isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
            for value in node.values:
                self.guard(symbol, value, env, True)
        elif (
            truth
            and isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "is_relative_to"
        ):
            self.protect(symbol, node, env)
        else:
            evaluated = (
                self.expression(symbol, node, env)
                if isinstance(node, ast.Name)
                else None
            )
            # Calls/comparisons are recorded at their actual evaluation, so a
            # guard never invokes a validator a second time.
            evaluated = evaluated or env.get(f"#path-expression:{id(node)}")
            if evaluated is not None:
                facts = self.path_condition(evaluated)[int(truth)] or frozenset()
                for key in facts:
                    env["#path:" + key] = Value(contained=True)
                for key, current in env.items():
                    if current.key in facts:
                        env[key] = replace(current, contained=True)

    def narrow(
        self, symbol: Symbol, node: ast.AST, env: dict[str, Value], truth: bool
    ) -> None:
        """Retain enforced presence and literal choices on this branch only."""
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            self.narrow(symbol, node.operand, env, not truth)
        elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And) and truth:
            for child in node.values:
                self.narrow(symbol, child, env, True)
        elif (
            isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.ops[0], (ast.Eq, ast.NotEq, ast.In, ast.NotIn))
            and (choices := self.compared_strings(node)) is not None
        ):
            value = self.bound_value(node.left, env)
            if value.key and value.instance is None:
                previous = self.literal_choices(value, env)
                positive = truth != isinstance(node.ops[0], (ast.NotEq, ast.NotIn))
                remaining = (
                    (choices if previous is None else previous & choices)
                    if positive
                    else (previous - choices if previous is not None else None)
                )
                if remaining is not None:
                    env["#literal-choices:" + value.key] = Value(
                        key=repr(tuple(sorted(remaining)))
                    )
        elif (
            isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.comparators[0], ast.Constant)
            and node.comparators[0].value is None
            and isinstance(node.ops[0], (ast.Is, ast.IsNot, ast.Eq, ast.NotEq))
        ):
            present = truth == isinstance(node.ops[0], (ast.IsNot, ast.NotEq))
            if present:
                self.narrow(symbol, node.left, env, True)
        elif truth and isinstance(node, (ast.Name, ast.Attribute, ast.Subscript)):
            value = self.bound_value(node, env)
            if value.key and (value.maybe_none or value.maybe_missing):
                for name, current in env.items():
                    if current.key == value.key:
                        env[name] = replace(
                            current,
                            maybe_none=False,
                            maybe_missing=False,
                            locations=current.locations
                            | {(symbol.file.relative_path, node.lineno)},
                        )

    @staticmethod
    def compared_strings(node: ast.Compare) -> frozenset[str] | None:
        try:
            literal = ast.literal_eval(node.comparators[0])
        except (ValueError, SyntaxError, TypeError):
            return None
        if isinstance(node.ops[0], (ast.Eq, ast.NotEq)) and isinstance(literal, str):
            return frozenset({literal})
        if (
            isinstance(node.ops[0], (ast.In, ast.NotIn))
            and isinstance(literal, (list, tuple, set))
            and all(isinstance(item, str) for item in literal)
        ):
            return frozenset(literal)
        return None

    @staticmethod
    def literal_choices(value: Value, env: dict[str, Value]) -> frozenset[str] | None:
        recorded = env.get("#literal-choices:" + value.key)
        if recorded is None:
            return None
        choices = member_label(recorded)
        return frozenset(choices) if isinstance(choices, tuple) else None

    def protect(self, symbol: Symbol, node: ast.Call, env: dict[str, Value]) -> None:
        assert isinstance(node.func, ast.Attribute)
        if len(node.args) != 1 or any(
            keyword.arg != "walk_up"
            or node.func.attr != "relative_to"
            or not isinstance(keyword.value, ast.Constant)
            or keyword.value.value is not False
            for keyword in node.keywords
        ):
            return
        value = self.expression(symbol, node.func.value, env)
        base = self.expression(symbol, node.args[0], env) if node.args else Value()
        if value.path_object and value.resolved and base.resolved and not base.sources:
            for name, current in env.items():
                if current.key == value.key:
                    env[name] = replace(
                        current,
                        contained=True,
                        locations=current.locations
                        | {(symbol.file.relative_path, node.lineno)},
                    )

    def expression(
        self, symbol: Symbol, node: ast.AST | None, env: dict[str, Value]
    ) -> Value:
        check_deadline(self.deadline)
        if node is None:
            return Value()
        if self.call_receivers is not None and node in self.call_receivers:
            return self.call_receivers[node]
        if isinstance(node, ast.Constant):
            return Value(key=repr(node.value))
        if isinstance(node, ast.Lambda):
            callable_key = _key(
                "lambda",
                symbol.file.relative_path,
                str(node.lineno),
                str(node.col_offset),
                *self.call_sites,
            )
            function = ast.copy_location(
                ast.FunctionDef(
                    name="lambda_body",
                    args=node.args,
                    body=[ast.copy_location(ast.Return(value=node.body), node.body)],
                    decorator_list=[],
                ),
                node,
            )
            self.callables[callable_key] = Symbol(symbol.file, "lambda_body", function)
            self.closures[callable_key] = env
            return Value(key=callable_key)
        if isinstance(node, ast.Name):
            if node.id in env:
                value = env[node.id]
                return (
                    self.aggregate(value, env)
                    if value.key in self.mapping_keys or value.key in self.record_keys
                    else value
                )
            target = self.program.resolve_in(
                Symbol(symbol.file, symbol.name, node), node.id
            )
            if target and isinstance(target.node, (Function, ast.ClassDef)):
                binding_key = _key("callable", target.file.relative_path, target.name)
                self.callables[binding_key] = target
                return Value(key=binding_key)
            key = (symbol.file.relative_path, node.id)
            if f"#global-value:{key[0]}:{key[1]}" in env:
                return env[f"#global-value:{key[0]}:{key[1]}"]
            if key not in self.globals:
                self.globals[key] = Value(key=":".join(key))
                declarations = self.program.bindings[symbol.file.relative_path].get(
                    node.id, []
                )
                if len(declarations) == 1 and isinstance(
                    declarations[0], (ast.Assign, ast.AnnAssign)
                ):
                    global_env: dict[str, Value] = {}
                    self.globals[key] = self.expression(
                        symbol, declarations[0].value, global_env
                    )
                    self.global_members.update(
                        (name, value)
                        for name, value in global_env.items()
                        if name.startswith("#member:")
                    )
            pending = [self.globals[key]]
            reached: set[str] = set()
            while pending:
                check_deadline(self.deadline)
                current = pending.pop()
                if current.key in reached:
                    continue
                reached.add(current.key)
                for marker in (
                    *self.members.get(current.key, {}).values(),
                    "#member:unknown:" + current.key,
                ):
                    if marker in self.global_members:
                        env.setdefault(marker, self.global_members[marker])
                        pending.append(env[marker])
            return self.globals[key]
        if isinstance(node, ast.Dict):
            mapping_key = _key(
                "mapping",
                symbol.file.relative_path,
                str(node.lineno),
                str(node.col_offset),
                *self.call_sites,
            )
            values = []
            for field, expression in zip(node.keys, node.values, strict=True):
                value = self.expression(symbol, expression, env)
                values.append(value)
                if field is None:
                    self.update_mapping(Value(key=mapping_key), value, env)
                if isinstance(field, ast.Constant):
                    marker = self.member_key(Value(key=mapping_key), field.value)
                    env[marker] = replace(value, maybe_missing=False)
                    self.member_defaults.setdefault(marker, Value())
            self.mapping_keys.add(mapping_key)
            return replace(
                combine(values, mapping_key),
                maybe_missing=False,
                maybe_none=False,
                instance=None,
            )
        if isinstance(node, ast.Call):
            previous = self.call_receivers
            self.call_receivers = {}
            try:
                value = self.call(symbol, node, env)
                if value.key in self.path_conditions:
                    env[f"#path-expression:{id(node)}"] = value
                return value
            finally:
                self.call_receivers = previous
        if isinstance(node, (ast.List, ast.Tuple)):
            elements = tuple(self.expression(symbol, child, env) for child in node.elts)
            middleware = self.http_context.sequence(symbol, node, elements)
            if middleware is not None:
                return middleware
            value = combine(list(elements))
            self.path_arrays[node] = elements
            return value
        if isinstance(node, ast.Await):
            return self.expression(symbol, node.value, env)
        if isinstance(node, ast.NamedExpr):
            value = self.expression(symbol, node.value, env)
            self.assign(node.target, value, env)
            return value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            value = self.expression(symbol, node.operand, env)
            known = self.truth_value(value, env)
            return (
                Value(key=repr(not known))
                if known is not None
                else replace(value, key=_key("not", value.key))
            )
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            left = self.expression(symbol, node.left, env)
            right = self.expression(symbol, node.comparators[0], env)
            possible = self.literal_choices(left, env)
            if possible and (choices := self.compared_strings(node)) is not None:
                outcomes = {item in choices for item in possible}
                if len(outcomes) == 1:
                    return Value(
                        key=repr(
                            outcomes.pop()
                            != isinstance(node.ops[0], (ast.NotEq, ast.NotIn))
                        )
                    )
            first, second = member_label(left), member_label(right)
            if (
                isinstance(node.ops[0], (ast.In, ast.NotIn))
                and first is not UNKNOWN_MEMBER
                and right.key in self.mapping_keys
                and "#member:unknown:" + right.key not in env
            ):
                member = self.member(right, first, env)
                if member.key == "#missing" or not member.maybe_missing:
                    return Value(
                        key=repr(
                            (member.key != "#missing")
                            != isinstance(node.ops[0], ast.NotIn)
                        )
                    )
            if isinstance(node.ops[0], (ast.Is, ast.IsNot)) and (
                (left.key in self.non_none and right.key == "None")
                or (right.key in self.non_none and left.key == "None")
            ):
                return Value(key=repr(isinstance(node.ops[0], ast.IsNot)))
            if second is UNKNOWN_MEMBER and not right.sources:
                try:
                    second = ast.literal_eval(node.comparators[0])
                except (ValueError, SyntaxError, TypeError):
                    second = UNKNOWN_MEMBER
            if first is not UNKNOWN_MEMBER and second is not UNKNOWN_MEMBER:
                operator = node.ops[0]
                if isinstance(operator, (ast.Eq, ast.NotEq)) or (
                    isinstance(operator, (ast.Is, ast.IsNot))
                    and (first is None or second is None)
                ):
                    equal = first == second
                    return Value(
                        key=repr(equal != isinstance(operator, (ast.NotEq, ast.IsNot)))
                    )
                if isinstance(operator, (ast.In, ast.NotIn)) and isinstance(
                    second, (list, tuple, set, dict, str, bytes)
                ):
                    try:
                        included = first in second
                    except TypeError:
                        pass
                    else:
                        return Value(
                            key=repr(included != isinstance(operator, ast.NotIn))
                        )
            result = combine([left, Value(), right])
            facts: set[str] = set()
            if isinstance(node.ops[0], (ast.Eq, ast.NotEq)):
                for checked, base in ((left, right), (right, left)):
                    paths = self.common_paths.get(checked.key, (checked,))
                    if (
                        base.resolved
                        and not base.sources
                        and all(value.resolved for value in paths)
                    ):
                        facts.update(value.key for value in paths if value.sources)
            if facts:
                result = replace(
                    result,
                    key=_key("path-comparison", ast.dump(node), left.key, right.key),
                )
                pair: tuple[frozenset[str], frozenset[str]] = (
                    frozenset(),
                    frozenset(facts),
                )
                self.path_conditions[result.key] = (
                    pair[::-1] if isinstance(node.ops[0], ast.NotEq) else pair
                )
                env[f"#path-expression:{id(node)}"] = result
            return result
        if isinstance(node, ast.BoolOp):
            values = []
            stopping = isinstance(node.op, ast.Or)
            for index, operand in enumerate(node.values):
                value = self.expression(symbol, operand, env)
                truth = self.truth_value(value, env)
                if truth is None or truth is stopping or index == len(node.values) - 1:
                    values.append(value)
                if truth is stopping:
                    break
            return combine(values)
        if isinstance(node, ast.IfExp):
            conditional_value = self.expression(symbol, node.test, env)
            known = self.truth_value(conditional_value, env)
            branches = []
            for expression, truth in ((node.body, True), (node.orelse, False)):
                if known is not None and known is not truth:
                    continue
                local = env.copy()
                self.guard(symbol, node.test, local, truth)
                self.narrow(symbol, node.test, local, truth)
                local["#conditional-result"] = self.expression(
                    symbol, expression, local
                )
                branches.append(local)
            self.merge(env, branches)
            return env.pop("#conditional-result")
        if isinstance(
            node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
        ):
            local = env.copy()
            for generator in node.generators:
                self.assign(
                    generator.target,
                    self.expression(symbol, generator.iter, local),
                    local,
                )
                for condition in generator.ifs:
                    self.expression(symbol, condition, local)
                    self.guard(symbol, condition, local, True)
                    self.narrow(symbol, condition, local, True)
            if isinstance(node, ast.DictComp):
                return combine(
                    [
                        self.expression(symbol, node.key, local),
                        self.expression(symbol, node.value, local),
                    ]
                )
            return self.expression(symbol, node.elt, local)
        if isinstance(node, ast.Subscript):
            value = self.expression(symbol, node.value, env)
            label = member_label(self.expression(symbol, node.slice, env))
            if label is not UNKNOWN_MEMBER:
                return self.member(value, label, env)
            return replace(
                value,
                key=value.key + "[" + ast.dump(node.slice) + "]",
                contained=False,
                option_safe=False,
                url_checks=frozenset(),
                credential_present=False,
            )
        if isinstance(node, ast.Attribute):
            value = self.expression(symbol, node.value, env)
            if self.member_key(value, node.attr) in env:
                return self.member(value, node.attr, env)
            if value.instance:
                owner_path, owner_name = value.instance
                owner_file = next(
                    file
                    for file in self.program.files
                    if file.relative_path == owner_path
                )
                owner = self.program.resolve(owner_file, owner_name)
                method = (
                    self.program.instance_method(owner, node.attr) if owner else None
                )
                if method and isinstance(method.node, Function):
                    method_key = _key("bound-method", value.key, node.attr)
                    self.callables[method_key] = method
                    self.bound_receivers[method_key] = value
                    return Value(key=method_key)
            return replace(
                value,
                key=value.key + "." + node.attr,
                contained=False,
                instance=None,
                option_safe=False,
                url_checks=frozenset(),
                credential_present=False,
            )
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            left = self.expression(symbol, node.left, env)
            right = self.expression(symbol, node.right, env)
            return replace(
                combine([left, right], _key("path-join", left.key, right.key)),
                path_object=left.path_object,
                resolved=False,
                contained=False,
            )
        if isinstance(node, (ast.Lambda, ast.FunctionDef, ast.AsyncFunctionDef)):
            return Value()
        values = [
            self.expression(symbol, child, env) for child in ast.iter_child_nodes(node)
        ]
        result = combine(values)
        return (
            replace(
                result,
                key=_key(type(node).__name__, ast.dump(node), result.key),
                contained=False,
                resolved=False,
            )
            if isinstance(node, (ast.BinOp, ast.JoinedStr))
            else result
        )

    def call_receiver(
        self, symbol: Symbol, node: ast.Call, env: dict[str, Value]
    ) -> Value:
        if not isinstance(node.func, ast.Attribute):
            return Value()
        receiver = node.func.value
        if self.call_receivers is not None and receiver in self.call_receivers:
            return self.call_receivers[receiver]
        value = self.expression(symbol, receiver, env)
        if self.call_receivers is not None:
            self.call_receivers[receiver] = value
        return value

    def call(self, symbol: Symbol, node: ast.Call, env: dict[str, Value]) -> Value:
        if node is self.launch_call:
            self.launch_states.append(
                {
                    **self.globals,
                    **{
                        (path, name): value
                        for key, value in env.items()
                        if key.startswith("#global-value:")
                        for path, name in [
                            key.removeprefix("#global-value:").rsplit(":", 1)
                        ]
                    },
                }
            )
            return Value()
        name = qualified_name(node.func) or "dynamic call"
        resolved = resolve_name(name, self.aliases[symbol.file.relative_path])
        root = name.split(".")[0]
        declarations = self.program.bindings[symbol.file.relative_path].get(root, [])
        if root in env or (
            declarations
            and not (
                len(declarations) == 1
                and isinstance(declarations[0], (ast.Import, ast.ImportFrom))
            )
        ):
            resolved = ""
        receiver = self.call_receiver(symbol, node, env)
        args = []
        unknown_args = False
        for arg in node.args:
            value = self.expression(
                symbol, arg.value if isinstance(arg, ast.Starred) else arg, env
            )
            if isinstance(arg, ast.Starred):
                expanded = self.argument_tuples.get(value.key)
                if expanded is None:
                    unknown_args = True
                    args.append(value)
                else:
                    args.extend(expanded)
            else:
                args.append(value)
        keywords: dict[str | None, Value] = {}
        for keyword in node.keywords:
            value = self.expression(symbol, keyword.value, env)
            if keyword.arg is not None:
                if keyword.arg in keywords:
                    keywords[None] = value
                keywords[keyword.arg] = replace(value, maybe_missing=False)
            elif (
                value.key in self.mapping_keys
                and "#member:unknown:" + value.key not in env
            ):
                for label, marker in self.members.get(value.key, {}).items():
                    if marker not in env:
                        continue
                    if (
                        not isinstance(label, str)
                        or label in keywords
                        or env[marker].maybe_missing
                    ):
                        keywords[None] = value
                    else:
                        keywords[label] = env[marker]
            else:
                keywords[None] = value
        if (
            resolved == "contextvars.ContextVar"
            and self.program.external(symbol, node.func) == resolved
            and len(args) == 1
            and not unknown_args
            and keywords.keys() <= {"default"}
            and isinstance(member_label(args[0]), str)
        ):
            value = Value(
                key=_key(
                    "context-variable",
                    symbol.file.relative_path,
                    str(node.lineno),
                    str(node.col_offset),
                    *self.call_sites,
                )
            )
            self.context_variables[value.key] = keywords.get("default")
            self.record_keys.add(value.key)
            self.member_defaults["#context:" + value.key] = Value(
                key="#context-unset", maybe_missing=True
            )
            return value
        if receiver.key in self.context_variables and isinstance(
            node.func, ast.Attribute
        ):
            marker = "#context:" + receiver.key
            method = node.func.attr
            method_marker = self.members.get(receiver.key, {}).get(method)
            current = env.get(marker, self.member_defaults[marker])
            if (
                not keywords
                and not unknown_args
                and "#member:unknown:" + receiver.key not in env
                and (method_marker is None or method_marker not in env)
            ):
                if method == "get" and len(args) <= 1:
                    context_default = (
                        args[0] if args else self.context_variables[receiver.key]
                    )
                    if not current.maybe_missing:
                        return current
                    if context_default is not None:
                        return (
                            context_default
                            if current.key == "#context-unset"
                            else combine(
                                [replace(current, maybe_missing=False), context_default]
                            )
                        )
                elif method == "set" and len(args) == 1:
                    token = Value(
                        key=_key(
                            "context-token",
                            symbol.file.relative_path,
                            str(node.lineno),
                            str(node.col_offset),
                            *self.call_sites,
                        )
                    )
                    self.context_tokens[token.key] = receiver.key
                    self.record_keys.add(token.key)
                    env["#context:token:" + token.key] = current
                    env["#context:valid:" + token.key] = Value(key="True")
                    env[marker] = replace(args[0], maybe_missing=False)
                    return token
                elif method == "reset" and len(args) == 1:
                    token_marker = "#context:token:" + args[0].key
                    previous = env.get(token_marker)
                    if (
                        self.context_tokens.get(args[0].key) == receiver.key
                        and "#member:unknown:" + args[0].key not in env
                        and previous is not None
                        and env.get("#context:valid:" + args[0].key, Value()).key
                        == "True"
                    ):
                        env[marker] = previous
                        env["#context:valid:" + args[0].key] = Value(key="False")
                        return Value(key="None")
            self.unresolved(symbol, node, "unresolved ContextVar operation")
            env[marker] = Value()
            return Value()
        if (
            resolved
            in {
                "httpx.Client",
                "httpx.AsyncClient",
                "requests.Session",
                "aiohttp.ClientSession",
                "atlassian.Jira",
                "atlassian.Confluence",
            }
            and self.program.external(symbol, node.func) == resolved
        ):
            value = Value(
                key=_key(
                    "http-client",
                    symbol.file.relative_path,
                    str(node.lineno),
                    str(node.col_offset),
                    *self.call_sites,
                )
            )
            self.http_clients[value.key] = resolved
            self.record_keys.add(value.key)
            if resolved in {"atlassian.Jira", "atlassian.Confluence"}:
                if (
                    unknown_args
                    or None in keywords
                    or len(args) > 1
                    or (args and "url" in keywords)
                    or not (args or "url" in keywords)
                ):
                    self.unresolved(
                        symbol, node, "unresolved service constructor arguments"
                    )
                    return Value()
                base_url = keywords.get("url", args[0] if args else Value())
                env[self.member_key(value, "url")] = replace(
                    base_url,
                    locations=base_url.locations
                    | {(symbol.file.relative_path, node.lineno)},
                )
                session = keywords.get("session", Value(key="None"))
                if session.key == "None":
                    session = Value(key=_key(value.key, "default-session"))
                    self.http_clients[session.key] = "requests.Session"
                    self.record_keys.add(session.key)
                env[self.member_key(value, "_session")] = session
            return value
        if (
            resolved == "dataclasses.replace"
            and self.program.external(symbol, node.func) == resolved
            and len(args) == 1
            and not unknown_args
            and args[0].instance is not None
            and not args[0].maybe_missing
        ):
            original = args[0]
            assert original.instance is not None
            owner_path, owner_name = original.instance
            owner_file = next(
                file for file in self.program.files if file.relative_path == owner_path
            )
            record_class = self.program.resolve(owner_file, owner_name)
            fields = self.registrations.fields(record_class) if record_class else None
            if fields is not None and keywords.keys() <= set(fields):
                field_values = {
                    field: keywords.get(field, self.member(original, field, env))
                    for field in fields
                }
                if not any(value.maybe_missing for value in field_values.values()):
                    copied = replace(
                        combine(
                            list(field_values.values()),
                            _key(
                                "dataclass-replacement",
                                symbol.file.relative_path,
                                str(node.lineno),
                                str(node.col_offset),
                                *self.call_sites,
                            ),
                        ),
                        instance=original.instance,
                        maybe_none=False,
                        maybe_missing=False,
                    )
                    self.record_keys.add(copied.key)
                    for field, value in field_values.items():
                        marker = self.member_key(copied, field)
                        env[marker] = value
                        self.member_defaults[marker] = Value()
                    return copied
        super_owner = None
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Call)
            and isinstance(node.func.value.func, ast.Name)
            and node.func.value.func.id == "super"
            and not node.func.value.args
            and not node.func.value.keywords
            and "super" not in env
            and "super" not in self.program.bindings[symbol.file.relative_path]
            and isinstance(symbol.node, Function)
        ):
            enclosing_class = self.program.parents.get(symbol.node)
            method_parameters = (*symbol.node.args.posonlyargs, *symbol.node.args.args)
            if isinstance(enclosing_class, ast.ClassDef) and method_parameters:
                super_owner = Symbol(symbol.file, enclosing_class.name, enclosing_class)
                receiver = env.get(method_parameters[0].arg, Value())
        http_value = self.http_context.call(
            symbol, node, resolved, receiver, args, keywords, env, super_owner
        )
        if http_value is not None:
            return http_value
        if (
            resolved == "fastmcp.server.dependencies.get_http_request"
            and not any(
                module in self.program.modules
                for module in (
                    "fastmcp",
                    "fastmcp.server",
                    "fastmcp.server.dependencies",
                )
            )
            and not args
            and not keywords
        ):
            if env.get("#http:no-request", Value()).key == "True":
                env["#http:stop"] = Value(key="True")
                return Value()
            if "#http:request" in env:
                return env["#http:request"]
            request = Value(
                sources=frozenset({"http:request"}),
                key=_key(
                    "http-request",
                    symbol.file.relative_path,
                    str(node.lineno),
                    *self.call_sites,
                ),
                locations=frozenset({(symbol.file.relative_path, node.lineno)}),
            )
            env["#http:request"] = request
            env[self.member_key(request, "state")] = replace(
                request, key=_key(request.key, "state")
            )
            return request
        values = [*args, *keywords.values()]
        method = name.rsplit(".", 1)[-1]
        result = combine(values + ([receiver] if receiver.sources else []))
        result = replace(
            result,
            locations=result.locations | {(symbol.file.relative_path, node.lineno)},
        )
        if (
            resolved in {"os.getenv", "os.environ.get"}
            and self.program.external(symbol, node.func) == resolved
            and len(args) == 2
            and member_label(args[1]) is not UNKNOWN_MEMBER
            and args[1].key != "None"
        ):
            self.non_none.add(result.key)
            return result
        if (
            resolved in {"hasattr", "builtins.hasattr"}
            and root not in env
            and not declarations
            and len(args) == 2
            and not keywords
            and args[0].key in self.http_context.state_owners
            and isinstance(member_label(args[1]), str)
        ):
            member = self.member(args[0], member_label(args[1]), env)
            if member.key == "#missing" or not member.maybe_missing:
                return Value(key=repr(member.key != "#missing"))
            return Value()
        if (
            (resolved in {"id", "builtins.id"} and len(args) == 1 and not keywords)
            or (
                resolved in {"hasattr", "builtins.hasattr"}
                and len(args) == 2
                and not keywords
                and args[0].key in self.record_keys
                and args[0].instance is not None
                and isinstance(member_label(args[1]), str)
                and self.member_key(args[0], member_label(args[1])) in env
                and self.instance_member(args[0], str(member_label(args[1]))) is None
            )
            or (
                resolved in {"len", "builtins.len"}
                and len(args) == 1
                and args[0].key in self.mapping_keys
                and not keywords
            )
            or (
                resolved in {"isinstance", "builtins.isinstance"}
                and len(args) == 2
                and args[0].key in self.mapping_keys
                and qualified_name(node.args[1]) == "dict"
                and "dict" not in env
                and "dict" not in self.program.bindings[symbol.file.relative_path]
                and not keywords
            )
        ):
            return Value()
        if (
            resolved in {"isinstance", "builtins.isinstance"}
            and len(args) == 2
            and not keywords
            and args[0].key in self.record_keys
            and args[0].instance is not None
        ):
            class_info = self.callables.get(args[1].key)
            if class_info and self.registrations.fields(class_info) is not None:
                # Source-established dataclasses have no custom instance check or
                # attribute hooks. The builtin inspection does not mutate them.
                instance_path, instance_name = args[0].instance
                instance_file = next(
                    file
                    for file in self.program.files
                    if file.relative_path == instance_path
                )
                actual_class = self.program.resolve(instance_file, instance_name)
                order = (
                    self.program.method_order(actual_class) if actual_class else None
                )
                if order is not None:
                    matches_type = any(
                        isinstance(parent, Symbol) and parent.node is class_info.node
                        for parent in order
                    )
                    if not matches_type or not (
                        args[0].maybe_none or args[0].maybe_missing
                    ):
                        return Value(key=repr(matches_type))
                return Value()
        if (
            method in {"keys", "items", "values"}
            and receiver.key in self.mapping_keys
            and not args
            and not keywords
        ):
            if method == "keys":
                return replace(
                    env.get("#member:unknown:" + receiver.key, Value()),
                    key=_key("mapping-keys", receiver.key),
                    instance=None,
                )
            return replace(self.aggregate(receiver, env), instance=None)
        if (
            resolved in {"dict", "builtins.dict"}
            and root not in env
            and not any(
                not isinstance(declaration, (ast.Import, ast.ImportFrom))
                for declaration in declarations
            )
        ) or (
            method == "copy"
            and receiver.key in self.mapping_keys
            and not args
            and not keywords
        ):
            mapping = Value(
                key=_key(
                    "mapping-call",
                    symbol.file.relative_path,
                    str(node.lineno),
                    str(node.col_offset),
                    *self.call_sites,
                )
            )
            self.mapping_keys.add(mapping.key)
            if method == "copy":
                self.update_mapping(mapping, receiver, env)
            elif args:
                self.update_mapping(mapping, args[0], env)
            for label, value in keywords.items():
                if label is None:
                    self.update_mapping(mapping, value, env)
                else:
                    env[self.member_key(mapping, label)] = replace(
                        value, maybe_missing=False
                    )
            return self.aggregate(mapping, env)
        if method == "update" and receiver.key in self.mapping_keys:
            if receiver.key in self.optional_mappings:
                # A write may target the empty fallback or the populated alias.
                self.update_mapping(
                    self.optional_mappings[receiver.key],
                    combine(
                        [receiver, *args, *keywords.values()],
                        _key("ambiguous-update", receiver.key),
                    ),
                    env,
                )
                return Value()
            for argument in args:
                self.update_mapping(receiver, argument, env)
            for label, value in keywords.items():
                if label is None:
                    self.update_mapping(receiver, value, env)
                else:
                    env[self.member_key(receiver, label)] = replace(
                        value, maybe_missing=False
                    )
            return Value()
        if (method == "resolve" and receiver.path_object) or (
            resolved == "os.path.realpath"
            and self.program.external(symbol, node.func) == resolved
        ):
            return replace(
                result if args else receiver, resolved=True, locations=result.locations
            )
        if (
            resolved == "os.path.commonpath"
            and len(args) == 1
            and not keywords
            and self.program.external(symbol, node.func) == resolved
        ):
            path_values = self.path_arrays.get(node.args[0])
            if path_values:
                result = replace(
                    result, key=_key("commonpath", *(v.key for v in path_values))
                )
                self.common_paths[result.key] = path_values
            return result
        if resolved == "pathlib.Path" and name.split(".")[0] not in env:
            return replace(result, path_object=True)
        if resolved in {"str", "os.fspath"} and name.split(".")[0] not in env:
            return replace(result, path_object=False)
        if method in {"expanduser", "absolute"} and receiver.path_object:
            return replace(
                receiver,
                key=_key("expanduser", receiver.key)
                if method == "expanduser"
                else receiver.key,
                contained=False,
            )
        if method == "relative_to" and isinstance(node.func, ast.Attribute):
            self.protect(symbol, node, env)
            return result
        if method in {
            "is_relative_to",
            "is_absolute",
            "startswith",
            "exists",
            "is_file",
            "is_dir",
        }:
            return Value()
        sink: Value | None = None
        workbook = (
            resolved
            in {
                "openpyxl.Workbook",
                "openpyxl.workbook.Workbook",
                "openpyxl.workbook.workbook.Workbook",
                "openpyxl.load_workbook",
                "openpyxl.reader.excel.load_workbook",
            }
            and self.program.external(symbol, node.func) == resolved
        )
        if workbook and resolved.endswith("Workbook"):
            value = Value(
                key=_key(
                    "workbook",
                    symbol.file.relative_path,
                    str(node.lineno),
                    str(node.col_offset),
                    *self.call_sites,
                )
            )
            self.workbooks.add(value.key)
            return value
        if resolved in {
            "open",
            "builtins.open",
            "io.open",
            "os.open",
            "git.Repo",
            "os.remove",
            "os.unlink",
            "os.rmdir",
            "os.mkdir",
            "os.makedirs",
            "shutil.rmtree",
        }:
            sink = args[0] if args else keywords.get("file", keywords.get("path"))
        elif workbook or (receiver.key in self.workbooks and method == "save"):
            sink = args[0] if args else keywords.get("filename")
        elif (
            method
            in {
                "read_text",
                "read_bytes",
                "write_text",
                "write_bytes",
                "open",
                "unlink",
                "rmdir",
                "mkdir",
                "iterdir",
            }
            and receiver.sources
            and receiver.path_object
        ):
            sink = receiver
        elif name.endswith(".index.add") and receiver.repository_object:
            sink = args[0] if args else keywords.get("items")
        if sink is not None:
            if self.rule_id == "SENT-012" and sink.sources and not sink.contained:
                match = match_from_node("SENT-012", symbol.file, node, "path-flow")
                self.state.matches.append(
                    replace(
                        match,
                        captures={
                            "sink_name": name,
                            "flow_locations": json.dumps(
                                sorted(
                                    sink.locations
                                    | {(symbol.file.relative_path, node.lineno)}
                                )
                            ),
                        },
                    )
                )
            if workbook:
                value = Value(
                    key=_key(
                        "workbook",
                        symbol.file.relative_path,
                        str(node.lineno),
                        str(node.col_offset),
                        *self.call_sites,
                    )
                )
                self.workbooks.add(value.key)
                return value
            return (
                replace(result, repository_object=True)
                if resolved == "git.Repo"
                else result
            )
        if receiver.key in self.workbooks and method in {
            "create_sheet",
            "close",
            "remove",
        }:
            return Value()
        if method == "get" and (receiver.sources or receiver.key in self.mapping_keys):
            label = member_label(args[0]) if args else UNKNOWN_MEMBER
            if label is not UNKNOWN_MEMBER:
                member = self.member(receiver, label, env)
                get_default = args[1] if len(args) > 1 else Value(key="None")
                member = self.with_default(
                    member,
                    get_default,
                    node.args[1] if len(node.args) > 1 else ast.Constant(None),
                    env,
                )
                return replace(member, maybe_missing=False)
            return replace(
                receiver,
                key=receiver.key
                + "["
                + (ast.dump(node.args[0]) if node.args else "?")
                + "]",
                contained=False,
            )
        if (
            resolved in {"getattr", "builtins.getattr"}
            and root not in env
            and len(node.args) in {2, 3}
            and member_label(args[1]) is not UNKNOWN_MEMBER
            and not str(member_label(args[1])).startswith("__")
            and not any(
                not isinstance(declaration, (ast.Import, ast.ImportFrom))
                for declaration in declarations
            )
        ):
            member = self.member(args[0], member_label(args[1]), env)
            return (
                self.with_default(member, args[2], node.args[2], env)
                if member.maybe_missing and len(args) == 3
                else member
            )
        helper_name = name
        if name.startswith(("self.", "cls.")) and "." in symbol.name:
            helper_name = symbol.name.rsplit(".", 1)[0] + "." + name.split(".", 1)[1]
        helper = self.program.resolve_in(symbol, helper_name)
        callable_value = self.expression(symbol, node.func, env)
        bound_callable = self.callables.get(callable_value.key)
        if bound_callable:
            helper = bound_callable
        if receiver.instance and not bound_callable:
            owner_path, owner_name = receiver.instance
            owner_file = next(
                file for file in self.program.files if file.relative_path == owner_path
            )
            owner_symbol = self.program.resolve(owner_file, owner_name)
            helper = (
                self.program.instance_method(owner_symbol, method, after=super_owner)
                if owner_symbol
                else None
            )
        constructing: Value | None = None
        if (
            helper
            and isinstance(helper.node, ast.ClassDef)
            and (root not in env or bound_callable)
        ):
            fields = self.registrations.fields(helper)
            if fields is not None and len(args) <= len(fields) and None not in keywords:
                bindings = dict(zip(fields, args, strict=False))
                if not (bindings.keys() & keywords.keys()) and keywords.keys() <= set(
                    fields
                ):
                    bindings.update(
                        (key, value)
                        for key, value in keywords.items()
                        if key is not None
                    )
                    for field, default in self.registrations.defaults(helper).items():
                        if field not in bindings:
                            bindings[field] = self.expression(default, default.node, {})
                    if set(bindings) == set(fields):
                        record = combine(
                            list(bindings.values()),
                            _key(
                                "record",
                                symbol.file.relative_path,
                                str(node.lineno),
                                str(node.col_offset),
                                *self.call_sites,
                            ),
                        )
                        self.record_keys.add(record.key)
                        for field, value in bindings.items():
                            marker = self.member_key(record, field)
                            env[marker] = replace(value, maybe_missing=False)
                            # A branch without this allocation does not make a
                            # declared field optional on the constructed record.
                            self.member_defaults[marker] = Value()
                        return replace(
                            record,
                            instance=(helper.file.relative_path, helper.name),
                            maybe_missing=False,
                            maybe_none=False,
                        )
            instance = replace(
                result,
                key=_key(
                    "instance",
                    symbol.file.relative_path,
                    str(node.lineno),
                    str(node.col_offset),
                    *self.call_sites,
                ),
                instance=(helper.file.relative_path, helper.name),
                maybe_missing=False,
                maybe_none=False,
            )
            if self.program.plain_instance(helper):
                return instance
            initializer = self.instance_member(instance, "__init__")
            if not (
                self.program.plain_instance(helper, inspect_init=True)
                and initializer is not None
                and isinstance(initializer.node, Function)
                and not initializer.node.decorator_list
                and not any(
                    isinstance(part, ast.Attribute)
                    and part.attr in {"__dict__", "__class__"}
                    for part in ast.walk(initializer.node)
                )
            ):
                self.unresolved(symbol, node, "custom construction or instance state")
                return replace(result, instance=None)
            constructing = instance
            receiver = instance
            self.record_keys.add(instance.key)
            helper = initializer
        if (
            helper
            and isinstance(helper.node, Function)
            and any(
                not (
                    isinstance(decorator, ast.Name)
                    and decorator.id in {"staticmethod", "classmethod"}
                    and not self.program.bindings[helper.file.relative_path].get(
                        decorator.id
                    )
                )
                and not (
                    isinstance(decorator, ast.Call)
                    and len(decorator.args) == 1
                    and not decorator.keywords
                    and self.program.external(helper, decorator.func)
                    == "functools.wraps"
                )
                for decorator in helper.node.decorator_list
            )
        ):
            self.unresolved(symbol, node, "decorated helper may replace behavior")
            helper = None
        if (
            helper
            and isinstance(helper.node, Function)
            and (
                name.split(".")[0] not in env
                or receiver.instance is not None
                or bound_callable is not None
            )
        ):
            parameters = helper.node.args
            positional = [p.arg for p in (*parameters.posonlyargs, *parameters.args)]
            descriptors = {
                decorator.id
                for decorator in helper.node.decorator_list
                if isinstance(decorator, ast.Name)
            }
            bound_parameter = (
                positional[0]
                if positional
                and "staticmethod" not in descriptors
                and (
                    constructing is not None
                    or "classmethod" in descriptors
                    or super_owner is not None
                    or callable_value.key in self.bound_receivers
                    or ("." in helper.name and positional[0] in {"self", "cls"})
                )
                else None
            )
            if bound_parameter is not None:
                positional = positional[1:]
            bindings = dict(zip(positional, args, strict=False))
            valid = (
                not unknown_args
                and (len(args) <= len(positional) or parameters.vararg is not None)
                and not (set(bindings) & keywords.keys())
            )
            bindings.update(
                (key, value) for key, value in keywords.items() if key is not None
            )
            defaults = (
                dict(
                    zip(
                        positional[-len(parameters.defaults) :],
                        parameters.defaults,
                        strict=False,
                    )
                )
                if parameters.defaults
                else {}
            )
            defaults.update(
                (parameter.arg, default)
                for parameter, default in zip(
                    parameters.kwonlyargs, parameters.kw_defaults, strict=True
                )
                if default is not None
            )
            all_parameters = [
                *positional,
                *(parameter.arg for parameter in parameters.kwonlyargs),
            ]
            if parameters.vararg is not None:
                tuple_key = _key(
                    "arguments",
                    symbol.file.relative_path,
                    str(node.lineno),
                    *self.call_sites,
                )
                extra_args = tuple(args[len(positional) :])
                self.argument_tuples[tuple_key] = extra_args
                bindings[parameters.vararg.arg] = combine(list(extra_args), tuple_key)
                all_parameters.append(parameters.vararg.arg)
            if parameters.kwarg is not None:
                extra = {
                    key: value
                    for key, value in bindings.items()
                    if key not in all_parameters
                }
                for key in extra:
                    del bindings[key]
                mapping = Value(
                    key=_key(
                        "keywords",
                        symbol.file.relative_path,
                        str(node.lineno),
                        *self.call_sites,
                    )
                )
                self.mapping_keys.add(mapping.key)
                for key, value in extra.items():
                    env[self.member_key(mapping, key)] = value
                bindings[parameters.kwarg.arg] = mapping
                all_parameters.append(parameters.kwarg.arg)
            for parameter in all_parameters:
                if parameter not in bindings and parameter in defaults:
                    bindings[parameter] = self.expression(
                        helper, defaults[parameter], {}
                    )
            if (
                valid
                and set(bindings) == set(all_parameters)
                and not (
                    {parameter.arg for parameter in parameters.posonlyargs}
                    & keywords.keys()
                )
                and None not in keywords
            ):
                for name, value in self.closures.get(callable_value.key, {}).items():
                    bindings.setdefault(name, value)
                if bound_parameter is not None:
                    bindings[bound_parameter] = self.bound_receivers.get(
                        callable_value.key, receiver
                    )
                bindings.update(
                    (key, value)
                    for key, value in env.items()
                    if key.startswith(self.helper_state_prefixes)
                    and not key.startswith("#member:")
                )
                # Carry reachable object state, not every temporary object from
                # the caller. Globals, closures and bound methods remain roots.
                pending = [(value, False) for value in self.globals.values()] + [
                    (value, True) for value in bindings.values()
                ]
                reached: set[str] = set()
                while pending:
                    check_deadline(self.deadline)
                    current, from_argument = pending.pop()
                    if current.key in reached:
                        continue
                    reached.add(current.key)
                    pending.extend(
                        (value, from_argument)
                        for value in self.argument_tuples.get(current.key, ())
                    )
                    pending.extend(
                        (value, from_argument)
                        for value in self.closures.get(current.key, {}).values()
                    )
                    if current.key in self.bound_receivers:
                        pending.append(
                            (self.bound_receivers[current.key], from_argument)
                        )
                    for marker in (
                        *self.members.get(current.key, {}).values(),
                        "#member:unknown:" + current.key,
                    ):
                        if marker in env:
                            value = env[marker]
                            # Unchanged globals load on use; carry caller mutations.
                            if from_argument or value is not self.global_members.get(
                                marker
                            ):
                                bindings[marker] = value
                            pending.append((value, from_argument))
                initial_instances = {
                    value.key
                    for value in bindings.values()
                    if value.instance is not None
                }
                self.call_sites.append(
                    f"{symbol.file.relative_path}:{node.lineno}:{node.col_offset}"
                )
                try:
                    bindings["#callable-origin"] = callable_value
                    returned = self.function(helper, bindings)
                finally:
                    self.call_sites.pop()
                env.update(
                    (key, value)
                    for key, value in bindings.items()
                    if key.startswith(self.helper_state_prefixes)
                )
                invalidated = {
                    value.key
                    for value in bindings.values()
                    if value.key in initial_instances and value.instance is None
                }
                for key, value in env.items():
                    if value.key in invalidated:
                        env[key] = replace(value, instance=None)
                if constructing is not None and bound_parameter is not None:
                    initialized = bindings[bound_parameter]
                    if initialized.instance is None:
                        self.unresolved(
                            symbol,
                            node,
                            "custom construction replaced methods "
                            "or exposed instance state",
                        )
                    return self.aggregate(initialized, env)
                # Propagate facts about actual values, not internal control markers.
                # Markers can share an empty key with unrelated unknown values.
                bound_values = [
                    value
                    for name, value in bindings.items()
                    if value.key
                    and not value.maybe_missing
                    and not value.maybe_none
                    and (
                        not name.startswith("#")
                        or name.startswith(("#member:", "#global-value:"))
                    )
                ]
                protected = {value.key for value in bound_values if value.contained}
                for key, value in env.items():
                    if value.key in protected:
                        env[key] = replace(value, contained=True)
                option_checked = {
                    value.key for value in bound_values if value.option_safe
                }
                for key, value in env.items():
                    if value.key in option_checked:
                        env[key] = replace(value, option_safe=True)
                for value in bound_values:
                    if value.url_checks:
                        for key, current in env.items():
                            if current.key == value.key:
                                env[key] = replace(
                                    current,
                                    url_checks=current.url_checks | value.url_checks,
                                    locations=current.locations | value.locations,
                                )
                return replace(
                    returned, locations=returned.locations | result.locations
                )
        self.http_context.unknown_call(node, (*values, receiver), env)
        self.workbooks.difference_update(value.key for value in (*values, receiver))
        escaped = {
            value.key
            for value in (*values, receiver)
            if value.instance is not None
            or value.key in self.mapping_keys
            or value.key in self.record_keys
        }
        escaped.update(
            alias_owner.key
            for key in tuple(escaped)
            if (
                alias_owner := self.optional_mappings.get(key)
                or self.http_context.state_owners.get(key)
            )
            is not None
        )
        if escaped:
            changed = replace(
                combine(values),
                contained=False,
                option_safe=False,
                url_checks=frozenset(),
                credential_present=False,
                instance=None,
            )
            for owner in escaped:
                for marker in self.members.get(owner, {}).values():
                    if marker in env:
                        env[marker] = replace(
                            combine([env[marker], changed]),
                            contained=False,
                            option_safe=False,
                            url_checks=frozenset(),
                            credential_present=False,
                            instance=None,
                        )
                env["#member:unknown:" + owner] = changed
            for key, value in env.items():
                if value.key in escaped:
                    env[key] = replace(value, instance=None)
        if result.sources:
            self.unresolved(symbol, node, f"unresolved call to {name}")
        return replace(
            result,
            key=_key(
                symbol.file.relative_path,
                str(node.lineno),
                str(node.col_offset),
                name,
                result.key,
            ),
            contained=False,
            path_object=False,
            repository_object=False,
            instance=None,
            option_safe=False,
            url_checks=frozenset(),
            credential_present=False,
        )
