"""Caller-to-operator credential selection across discovered HTTP boundaries."""

from __future__ import annotations

import ast
import json
from dataclasses import replace
from typing import Any

from sentinel.static.ast_utils import (
    match_from_node,
    qualified_name,
    resolve_name,
)
from sentinel.static.discovery import PythonProgram, Symbol
from sentinel.static.model import (
    RuleRunState,
    StaticContext,
    StaticMatch,
    TypeScriptSourceFile,
)
from sentinel.static.path_flow import PathFlow, Value, _key, combine, member_label
from sentinel.static.rules.sent012 import analyze
from sentinel.static.semgrep_ast import source_range
from sentinel.static.typescript_discovery import name_of
from sentinel.static.typescript_path_flow import TypeScriptPathFlow
from sentinel.static.typescript_path_flow import analyze as analyze_typescript


class CredentialFlow(PathFlow):
    rule_id = "SENT-016"
    helper_state_prefixes = (
        *PathFlow.helper_state_prefixes,
        "#absent:",
        "#credential:",
    )

    def __init__(
        self, program: PythonProgram, state: RuleRunState, deadline: float
    ) -> None:
        super().__init__(program, state, deadline)
        self.evaluated: dict[ast.AST, Value] = {}
        self.environment_text: dict[str, tuple[str, str]] = {}
        self.operator_predicates: dict[str, tuple[str, bool]] = {}

    def function(self, symbol: Symbol, bindings: dict[str, Value]) -> Value:
        if any(
            source.startswith("http:")
            for value in bindings.values()
            for source in value.sources
        ):
            bindings["#credential:http"] = Value(contained=True)
        return super().function(symbol, bindings)

    def external(self, symbol: Symbol, node: ast.AST, env: dict[str, Value]) -> str:
        name = qualified_name(node) or ""
        root = name.split(".")[0]
        declarations = self.program.bindings[symbol.file.relative_path].get(root, [])
        if root in env or (
            declarations
            and not (
                len(declarations) == 1
                and isinstance(declarations[0], (ast.Import, ast.ImportFrom))
            )
        ):
            return ""
        return resolve_name(name, self.aliases[symbol.file.relative_path])

    def assign(self, target: ast.AST, value: Value, env: dict[str, Value]) -> None:
        if isinstance(target, ast.Name):
            original = env.get(target.id, Value())
            if (
                value.operator_credential
                and env.get("#absent:" + original.key, Value()).contained
            ):
                value = replace(combine([value, original]), credential_fallback=True)
        super().assign(target, value, env)

    def merge(self, env: dict[str, Value], branches: list[dict[str, Value]]) -> None:
        http = [
            branch
            for branch in branches
            if branch.get("#credential:http", Value()).contained
        ]
        # ponytail: follow the successful HTTP getter path; exception-prefix
        # correlation needs separate state. Keep the stdio alternative distinct.
        branches = http or branches
        super().merge(env, branches)
        if http:
            env["#credential:http"] = Value(contained=True)
        for name in env:
            if name.startswith(
                ("#absent:", "#credential:excluded:", "#credential:opt-in:")
            ):
                env[name] = (
                    replace(
                        combine([branch[name] for branch in branches]), contained=True
                    )
                    if all(branch.get(name, Value()).contained for branch in branches)
                    else Value()
                )

    def guard(
        self, symbol: Symbol, node: ast.AST, env: dict[str, Value], truth: bool
    ) -> None:
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            self.guard(symbol, node.operand, env, not truth)
            return
        if isinstance(node, ast.BoolOp):
            conjunctive = isinstance(node.op, ast.And)
            for child in node.values:
                if truth == conjunctive or all(
                    other is child
                    or self.truth_value(self.evaluated.get(other, Value()), env)
                    is conjunctive
                    for other in node.values
                ):
                    self.guard(symbol, child, env, truth)
        if (
            isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.comparators[0], ast.Constant)
            and node.comparators[0].value is None
        ):
            if isinstance(node.ops[0], (ast.Is, ast.Eq)):
                self.guard(symbol, node.left, env, not truth)
            elif isinstance(node.ops[0], (ast.IsNot, ast.NotEq)):
                self.guard(symbol, node.left, env, truth)
            return
        value = self.evaluated.get(node, Value())
        predicate = self.operator_predicates.get(value.key)
        if predicate is not None and truth != predicate[1]:
            env["#credential:opt-in:" + predicate[0]] = Value(
                contained=True,
                locations=value.locations
                | {(symbol.file.relative_path, getattr(node, "lineno", 1))},
            )
        if not isinstance(node, (ast.Name, ast.Attribute, ast.Subscript)):
            if not truth and value.sources:
                env["#credential:excluded:" + value.key] = replace(
                    value,
                    contained=True,
                    locations=value.locations
                    | {(symbol.file.relative_path, getattr(node, "lineno", 1))},
                )
            return
        if value.sources:
            if not truth:
                env["#absent:" + value.key] = replace(
                    value,
                    contained=True,
                    locations=value.locations
                    | {(symbol.file.relative_path, getattr(node, "lineno", 1))},
                )
            for name, current in env.items():
                if current.key == value.key:
                    env[name] = replace(
                        current,
                        credential_present=truth,
                        locations=current.locations
                        | {(symbol.file.relative_path, getattr(node, "lineno", 1))},
                    )

    def expression(
        self, symbol: Symbol, node: ast.AST | None, env: dict[str, Value]
    ) -> Value:
        result = self._expression(symbol, node, env)
        if node is not None:
            self.evaluated[node] = result
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            selected = self.environment_text.get(
                self.evaluated.get(node.left, Value()).key
            )
            if selected and isinstance(node.ops[0], (ast.In, ast.NotIn)):
                try:
                    accepted = ast.literal_eval(node.comparators[0])
                except (ValueError, TypeError, SyntaxError):
                    accepted = None
                if isinstance(accepted, (tuple, list, set)) and all(
                    isinstance(item, str) for item in accepted
                ):
                    self.operator_predicates[result.key] = (
                        selected[0],
                        (selected[1] in accepted) != isinstance(node.ops[0], ast.NotIn),
                    )
        return result

    def _expression(
        self, symbol: Symbol, node: ast.AST | None, env: dict[str, Value]
    ) -> Value:
        if (
            isinstance(node, ast.Subscript)
            and self.external(symbol, node.value, env) == "os.environ"
            and self.program.external(symbol, node.value) == "os.environ"
        ):
            return Value(
                key=_key(symbol.file.relative_path, str(node.lineno), ast.dump(node)),
                operator_credential=True,
                locations=frozenset({(symbol.file.relative_path, node.lineno)}),
            )
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            values = []
            for expression in node.values:
                value = self.expression(symbol, expression, env)
                values.append(value)
                if value.credential_present or self.truth_value(value, env) is True:
                    break
            result = combine(values)
            if any(v.sources and not v.credential_present for v in values[:-1]) and any(
                v.operator_credential for v in values[1:]
            ):
                result = replace(result, credential_fallback=True)
            return result
        return super().expression(symbol, node, env)

    def call(self, symbol: Symbol, node: ast.Call, env: dict[str, Value]) -> Value:
        external = self.external(symbol, node.func, env)
        service_client = external in {"atlassian.Jira", "atlassian.Confluence"} and (
            self.program.external(symbol, node.func) == external
        )
        if external in {"os.getenv", "os.environ.get"} and (
            self.program.external(symbol, node.func) == external
        ):
            args = [self.expression(symbol, arg, env) for arg in node.args]
            result = Value(
                key=_key(
                    symbol.file.relative_path,
                    str(node.lineno),
                    ast.dump(node),
                    *self.call_sites,
                    *(arg.key for arg in args),
                ),
                operator_credential=True,
                locations=frozenset({(symbol.file.relative_path, node.lineno)}),
            )
            if len(args) == 2 and not node.keywords:
                name, default = (member_label(arg) for arg in args)
                if isinstance(name, str) and isinstance(default, str):
                    self.environment_text[result.key] = (name, default)
            return result
        if service_client or external in {
            f"{library}.{method}"
            for library in ("requests", "httpx")
            for method in (
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "head",
                "options",
                "request",
            )
        }:
            credentials = []
            for keyword in node.keywords:
                value = self.expression(symbol, keyword.value, env)
                if (service_client and keyword.arg in {"token", "password"}) or (
                    not service_client and keyword.arg == "auth"
                ):
                    credentials.append(value)
                elif not service_client and keyword.arg in {
                    "headers",
                    "params",
                    "data",
                    "json",
                }:
                    credentials.extend(
                        env[marker]
                        for field, marker in self.members.get(value.key, {}).items()
                        if isinstance(field, str)
                        and field.lower()
                        in {"authorization", "x-api-key", "access_token", "api_key"}
                        and marker in env
                    )
            absent = combine(
                [
                    value
                    for key, value in env.items()
                    if key.startswith(("#absent:", "#credential:excluded:"))
                    and value.contained
                ]
            )
            crossing = combine(
                [
                    replace(combine([value, absent]), credential_fallback=True)
                    if value.operator_credential and absent.sources
                    else value
                    for value in credentials
                    if value.credential_fallback
                    or (value.operator_credential and absent.sources)
                ]
            )
            if crossing.credential_fallback and any(
                source.startswith("http:") for source in crossing.sources
            ):
                settings = {
                    key.removeprefix("#credential:opt-in:"): value
                    for key, value in env.items()
                    if key.startswith("#credential:opt-in:") and value.contained
                }
                locations = crossing.locations | frozenset().union(
                    *(value.locations for value in settings.values())
                )
                self.state.matches.append(
                    replace(
                        match_from_node(
                            self.rule_id, symbol.file, node, "credential-fallback"
                        ),
                        captures={
                            "sink_name": qualified_name(node.func) or "request",
                            **(
                                {
                                    "credential_operator_opt_in": json.dumps(
                                        sorted(settings)
                                    )
                                }
                                if settings
                                else {}
                            ),
                            "flow_locations": json.dumps(
                                sorted(
                                    locations
                                    | {(symbol.file.relative_path, node.lineno)}
                                )
                            ),
                        },
                    )
                )
            return Value()
        result = super().call(symbol, node, env)
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "lower"
            and not node.args
            and not node.keywords
        ):
            original = self.evaluated.get(node.func.value, Value())
            selected = self.environment_text.get(original.key)
            if selected:
                result = replace(
                    original,
                    key=_key(original.key, "lower"),
                    locations=original.locations
                    | {(symbol.file.relative_path, node.lineno)},
                )
                self.environment_text[result.key] = (selected[0], selected[1].lower())
        if (
            external == "fastmcp.server.dependencies.get_http_request"
            and self.program.external(symbol, node.func) == external
            and not node.args
            and not node.keywords
        ):
            env["#credential:http"] = Value(contained=True)
        return result


def detect(context: StaticContext, state: RuleRunState) -> None:
    program = context.python_program
    flow = CredentialFlow(program, state, context.deadline)
    analyze(
        program,
        state,
        context.deadline,
        flow=flow,
        entries=(*program.tools(), *context.python_http_handlers),
    )
    if context.files.typescript_files:
        analyze_typescript(
            context.typescript_program,
            state,
            flow=TypeScriptCredentialFlow(context.typescript_program, state),
            entries=(
                *context.typescript_program.tools(),
                *context.typescript_http_handlers,
            ),
        )


class TypeScriptCredentialFlow(TypeScriptPathFlow):
    rule_id = "SENT-016"

    def expression(
        self, file: TypeScriptSourceFile, node: Any, env: dict[str, Value]
    ) -> Value:
        name = name_of(node) if isinstance(node, dict) else None
        if (
            name is not None
            and name.startswith("process.env.")
            and "process" not in env
            and "process" not in self.program.bindings[file.relative_path]
        ):
            return Value(
                key=_key(file.relative_path, name),
                operator_credential=True,
                locations=frozenset(
                    {(file.relative_path, source_range(node, file).start_line)}
                ),
            )
        result = super().expression(file, node, env)
        if result.credential_present:
            result = replace(result, key=_key(result.key, "credential-present"))
            self.conditions[result.key] = (None, frozenset())
        elif result.sources and result.key not in self.conditions:
            self.conditions[result.key] = (
                frozenset({f"#guard:credential:absent:{result.key}"}),
                frozenset({f"#guard:credential:present:{result.key}"}),
            )
        return result

    def member(self, value: Value, name: str) -> Value:
        if (
            name in self.objects.get(value.key, {})
            and value.key not in self.invalidated_objects
        ):
            return self.objects[value.key][name]
        return replace(
            super().member(value, name),
            credential_present=False,
            credential_fallback=False,
        )

    def pattern(self, node: Any, value: Value, env: dict[str, Value]) -> None:
        name = name_of(node) if isinstance(node, dict) else None
        original = env.get(name or "", Value())
        if (
            value.operator_credential
            and env.get(f"#guard:credential:absent:{original.key}", Value()).contained
        ):
            value = replace(combine([value, original]), credential_fallback=True)
        super().pattern(node, value, env)

    def guard(self, value: Value, env: dict[str, Value], truth: bool) -> None:
        super().guard(value, env, truth)
        for name, current in env.items():
            if env.get(f"#guard:credential:present:{current.key}", Value()).contained:
                env[name] = replace(current, credential_present=True)

    def call(
        self, file: TypeScriptSourceFile, node: dict[str, Any], env: dict[str, Value]
    ) -> Value:
        callee, arguments = node["Call"]
        operator = callee.get("Special", [{}])[0]
        if isinstance(operator, dict) and operator.get("Op") in {"Or", "Nullish"}:
            values = []
            for argument in arguments[1]:
                value = self.expression(file, argument.get("Arg", argument), env)
                values.append(value)
                if value.credential_present:
                    break
            result = combine(values)
            if any(v.sources and not v.credential_present for v in values[:-1]) and any(
                v.operator_credential for v in values[1:]
            ):
                result = replace(result, credential_fallback=True)
            return result
        name = name_of(callee) or ""
        binding = (
            self.callables.get(self.expression(file, callee, env).key)
            if "Special" not in callee
            else None
        )
        external = binding.external if binding else None
        is_fetch = (
            name == "fetch"
            and "fetch" not in env
            and "fetch" not in self.program.bindings[file.relative_path]
        ) or external in {"node-fetch", "node-fetch.default", "undici.fetch"}
        if is_fetch:
            args = [
                self.expression(file, argument.get("Arg", argument), env)
                for argument in arguments[1]
            ]
            options = self.objects.get(args[1].key, {}) if len(args) > 1 else {}
            headers = self.objects.get(options.get("headers", Value()).key, {})
            credentials = [
                value
                for field, value in headers.items()
                if field.lower() in {"authorization", "x-api-key"}
                and value.credential_fallback
            ]
            crossing = combine(credentials)
            if crossing.credential_fallback and any(
                source.startswith("http:") for source in crossing.sources
            ):
                location = source_range(node, file)
                self.state.matches.append(
                    StaticMatch(
                        self.rule_id,
                        file.relative_path,
                        location,
                        self.program.text(file, node),
                        match_kinds=("credential-fallback",),
                        captures={
                            "sink_name": name,
                            "flow_locations": json.dumps(
                                sorted(
                                    crossing.locations
                                    | {(file.relative_path, location.start_line)}
                                )
                            ),
                        },
                    )
                )
            return Value()
        return super().call(file, node, env)
