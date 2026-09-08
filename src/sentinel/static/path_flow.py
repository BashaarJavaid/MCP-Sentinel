"""Bounded Python path flow over the shared source index; no target execution."""

from __future__ import annotations

import ast
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


@dataclass(frozen=True)
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


def combine(values: list[Value], key: str = "") -> Value:
    present = [value for value in values if value.key != "None"]
    if present and len(present) != len(values):
        return replace(combine(present, key), maybe_missing=True)
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

    def __init__(
        self, program: PythonProgram, state: RuleRunState, deadline: float
    ) -> None:
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
        self.record_keys: set[str] = set()
        self.callables: dict[str, Symbol] = {}
        self.bound_receivers: dict[str, Value] = {}
        self.closures: dict[str, dict[str, Value]] = {}
        self.registrations = RegistrationFlow(program)
        self.members: dict[str, dict[object, str]] = {}
        self.member_defaults: dict[str, Value] = {}
        self.call_sites: list[str] = []
        self.yielding: set[tuple[str, str]] = set()

    def entry(self, tool: ToolBinding, bindings: dict[str, Value]) -> None:
        from sentinel.static.lifespan import external, tool_lifespan

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
            and external(self.program, tool.handler, parameter.annotation)
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
        self.function(tool.handler, bindings)

    def function(self, symbol: Symbol, bindings: dict[str, Value]) -> Value:
        check_deadline(self.deadline)
        key = (symbol.file.relative_path, symbol.name)
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
            return combine(returned)
        finally:
            self.exits.pop()
            self.active.remove(key)

    def unresolved(self, symbol: Symbol, node: ast.AST, reason: str) -> None:
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
            check_deadline(self.deadline)
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = self.expression(symbol, node.value, env)
                targets = (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
                for target in targets:
                    if isinstance(target, (ast.Attribute, ast.Subscript)):
                        self.expression(symbol, target.value, env)
                    self.assign(target, value, env)
            elif isinstance(node, ast.Return):
                returned.append(self.expression(symbol, node.value, env))
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
                self.expression(symbol, node.test, env)
                left, right = env.copy(), env.copy()
                self.guard(symbol, node.test, left, True)
                self.guard(symbol, node.test, right, False)
                branches = []
                if self.statements(symbol, node.body, left, returned):
                    branches.append(left)
                if self.statements(symbol, node.orelse, right, returned):
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
        return True

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
        result = env.get(key, fallback)
        self.member_defaults.setdefault(key, fallback)
        return result

    def bound_value(self, node: ast.AST, env: dict[str, Value]) -> Value:
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
        return self.program.resolve(file, owner + "." + name)

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
                    self.member(receiver, label, env)
                    env[self.member_key(receiver, label)] = value
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
                env[self.member_key(receiver, target.attr)] = value

    def merge(self, env: dict[str, Value], branches: list[dict[str, Value]]) -> None:
        for name in set().union(*(b.keys() for b in branches)):
            env[name] = combine(
                [
                    branch.get(name, self.member_defaults.get(name, Value()))
                    for branch in branches
                ]
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
            for name, value in self.global_members.items():
                env.setdefault(name, value)
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
                    env[marker] = value
                    self.member_defaults.setdefault(marker, Value())
            self.mapping_keys.add(mapping_key)
            return replace(
                combine(values, mapping_key), maybe_missing=False, instance=None
            )
        if isinstance(node, ast.Call):
            return self.call(symbol, node, env)
        if isinstance(node, ast.Await):
            return self.expression(symbol, node.value, env)
        if isinstance(node, ast.NamedExpr):
            value = self.expression(symbol, node.value, env)
            self.assign(node.target, value, env)
            return value
        if isinstance(node, ast.IfExp):
            self.expression(symbol, node.test, env)
            branches = []
            for expression, truth in ((node.body, True), (node.orelse, False)):
                local = env.copy()
                self.guard(symbol, node.test, local, truth)
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
                method = self.program.resolve(owner_file, owner_name + "." + node.attr)
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

    def call(self, symbol: Symbol, node: ast.Call, env: dict[str, Value]) -> Value:
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
        args = [self.expression(symbol, arg, env) for arg in node.args]
        keywords: dict[str | None, Value] = {}
        for keyword in node.keywords:
            value = self.expression(symbol, keyword.value, env)
            if keyword.arg is not None:
                if keyword.arg in keywords:
                    keywords[None] = value
                keywords[keyword.arg] = value
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
        receiver = (
            self.expression(symbol, node.func.value, env)
            if isinstance(node.func, ast.Attribute)
            else Value()
        )
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
            return Value(
                sources=frozenset({"http:request"}),
                key=_key(
                    "http-request",
                    symbol.file.relative_path,
                    str(node.lineno),
                    *self.call_sites,
                ),
                locations=frozenset({(symbol.file.relative_path, node.lineno)}),
            )
        values = [*args, *keywords.values()]
        method = name.rsplit(".", 1)[-1]
        result = combine(values + ([receiver] if receiver.sources else []))
        result = replace(
            result,
            locations=result.locations | {(symbol.file.relative_path, node.lineno)},
        )
        if (
            (resolved in {"id", "builtins.id"} and len(args) == 1 and not keywords)
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
            method in {"keys", "items", "values"}
            and receiver.key in self.mapping_keys
            and not args
            and not keywords
        ):
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
                    env[self.member_key(mapping, label)] = value
            return self.aggregate(mapping, env)
        if method == "update" and receiver.key in self.mapping_keys:
            for argument in args:
                self.update_mapping(receiver, argument, env)
            for label, value in keywords.items():
                if label is None:
                    self.update_mapping(receiver, value, env)
                else:
                    env[self.member_key(receiver, label)] = value
            return Value()
        if (
            method == "resolve" and receiver.path_object
        ) or resolved == "os.path.realpath":
            return replace(
                result if args else receiver, resolved=True, locations=result.locations
            )
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
            return (
                replace(result, repository_object=True)
                if resolved == "git.Repo"
                else result
            )
        if method == "get" and (receiver.sources or receiver.key in self.mapping_keys):
            label = member_label(args[0]) if args else UNKNOWN_MEMBER
            if label is not UNKNOWN_MEMBER:
                member = self.member(receiver, label, env)
                if member.maybe_missing:
                    member = combine([member, args[1] if len(args) > 1 else Value()])
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
                combine([member, args[2]])
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
            helper = self.program.resolve(owner_file, owner_name + "." + method)
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
                            env[self.member_key(record, field)] = value
                        return replace(
                            record,
                            instance=(helper.file.relative_path, helper.name),
                            maybe_missing=False,
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
            bound_parameter = (
                positional[0]
                if positional
                and (
                    constructing is not None
                    or ("." in helper.name and positional[0] in {"self", "cls"})
                )
                else None
            )
            if bound_parameter is not None:
                positional = positional[1:]
            bindings = dict(zip(positional, args, strict=False))
            valid = len(args) <= len(positional) and not (
                set(bindings) & keywords.keys()
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
                and not parameters.vararg
                and not parameters.kwarg
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
                    if key.startswith("#member:")
                )
                initial_instances = {
                    value.key
                    for value in bindings.values()
                    if value.instance is not None
                }
                self.call_sites.append(
                    f"{symbol.file.relative_path}:{node.lineno}:{node.col_offset}"
                )
                try:
                    returned = self.function(helper, bindings)
                finally:
                    self.call_sites.pop()
                env.update(
                    (key, value)
                    for key, value in bindings.items()
                    if key.startswith("#member:")
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
                protected = {
                    value.key for value in bindings.values() if value.contained
                }
                for key, value in env.items():
                    if value.key in protected:
                        env[key] = replace(value, contained=True)
                option_checked = {
                    value.key for value in bindings.values() if value.option_safe
                }
                for key, value in env.items():
                    if value.key in option_checked:
                        env[key] = replace(value, option_safe=True)
                for value in bindings.values():
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
        escaped = {
            value.key
            for value in (*values, receiver)
            if value.instance is not None
            or value.key in self.mapping_keys
            or value.key in self.record_keys
        }
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
