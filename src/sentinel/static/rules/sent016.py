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
from sentinel.static.discovery import Symbol
from sentinel.static.model import (
    RuleRunState,
    StaticContext,
    StaticMatch,
    TypeScriptSourceFile,
)
from sentinel.static.path_flow import PathFlow, Value, _key, combine
from sentinel.static.rules.sent012 import analyze
from sentinel.static.semgrep_ast import source_range
from sentinel.static.typescript_discovery import name_of
from sentinel.static.typescript_path_flow import TypeScriptPathFlow
from sentinel.static.typescript_path_flow import analyze as analyze_typescript


class CredentialFlow(PathFlow):
    rule_id = "SENT-016"

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
        super().merge(env, branches)
        for name in env:
            if name.startswith("#absent:"):
                env[name] = Value(
                    contained=all(
                        branch.get(name, Value()).contained for branch in branches
                    )
                )

    def guard(
        self, symbol: Symbol, node: ast.AST, env: dict[str, Value], truth: bool
    ) -> None:
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            self.guard(symbol, node.operand, env, not truth)
            return
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
        if not isinstance(node, (ast.Name, ast.Attribute, ast.Subscript)):
            return
        value = self.expression(symbol, node, env)
        if value.sources:
            if not truth:
                env["#absent:" + value.key] = Value(contained=True)
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
        if (
            isinstance(node, ast.Subscript)
            and self.external(symbol, node.value, env) == "os.environ"
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
        if external in {"os.getenv", "os.environ.get"}:
            return Value(
                key=_key(symbol.file.relative_path, str(node.lineno), ast.dump(node)),
                operator_credential=True,
                locations=frozenset({(symbol.file.relative_path, node.lineno)}),
            )
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
            crossing = combine([v for v in credentials if v.credential_fallback])
            if crossing.credential_fallback and any(
                source.startswith("http:") for source in crossing.sources
            ):
                self.state.matches.append(
                    replace(
                        match_from_node(
                            self.rule_id, symbol.file, node, "credential-fallback"
                        ),
                        captures={
                            "sink_name": qualified_name(node.func) or "request",
                            "flow_locations": json.dumps(
                                sorted(
                                    crossing.locations
                                    | {(symbol.file.relative_path, node.lineno)}
                                )
                            ),
                        },
                    )
                )
            return Value()
        return super().call(symbol, node, env)


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
