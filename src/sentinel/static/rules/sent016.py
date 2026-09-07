"""Caller-to-operator credential selection across discovered HTTP boundaries."""

from __future__ import annotations

import ast
import json
from dataclasses import replace
from typing import Any

from sentinel.static.ast_utils import (
    match_from_node,
    qualified_name,
    range_for_node,
    resolve_name,
)
from sentinel.static.discovery import Symbol
from sentinel.static.http_discovery import handlers
from sentinel.static.model import RuleRunState, StaticContext
from sentinel.static.path_flow import PathFlow, Value, _key, combine


class CredentialFlow(PathFlow):
    rule_id = "SENT-016"

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.credentials: dict[str, Value] = {}

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

    @staticmethod
    def assign(target: ast.AST, value: Value, env: dict[str, Value]) -> None:
        if isinstance(target, ast.Name):
            original = env.get(target.id, Value())
            if (
                value.operator_credential
                and env.get("#absent:" + original.key, Value()).contained
            ):
                value = replace(combine([value, original]), credential_fallback=True)
        PathFlow.assign(target, value, env)

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
                if value.credential_present:
                    break
            result = combine(values)
            if any(v.sources and not v.credential_present for v in values[:-1]) and any(
                v.operator_credential for v in values[1:]
            ):
                result = replace(result, credential_fallback=True)
            return result
        result = super().expression(symbol, node, env)
        if isinstance(node, ast.Dict):
            result = replace(
                result,
                key=_key(
                    "credential-map",
                    symbol.file.relative_path,
                    str(node.lineno),
                    result.key,
                ),
            )
            self.credentials[result.key] = combine(
                [
                    self.expression(symbol, value, env)
                    for key, value in zip(node.keys, node.values, strict=True)
                    if isinstance(key, ast.Constant)
                    and isinstance(key.value, str)
                    and key.value.lower()
                    in {"authorization", "x-api-key", "access_token", "api_key"}
                ]
            )
        return result

    def call(self, symbol: Symbol, node: ast.Call, env: dict[str, Value]) -> Value:
        external = self.external(symbol, node.func, env)
        if external in {"os.getenv", "os.environ.get"}:
            return Value(
                key=_key(symbol.file.relative_path, str(node.lineno), ast.dump(node)),
                operator_credential=True,
                locations=frozenset({(symbol.file.relative_path, node.lineno)}),
            )
        if external in {
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
                if keyword.arg == "auth":
                    credentials.append(value)
                elif keyword.arg in {"headers", "params", "data", "json"}:
                    credentials.append(self.credentials.get(value.key, Value()))
            crossing = combine([v for v in credentials if v.credential_fallback])
            if crossing.credential_fallback:
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
    for binding in handlers(program):
        state.visit(
            binding.registration.file.relative_path,
            range_for_node(binding.registration.node),
        )
        state.visit(
            binding.handler.file.relative_path, range_for_node(binding.handler.node)
        )
        flow.function(
            binding.handler,
            {
                parameter.arg: Value(
                    sources=frozenset({parameter.arg}),
                    key=f"{binding.handler.file.relative_path}:{parameter.lineno}:{parameter.arg}",
                    locations=frozenset(
                        {(binding.handler.file.relative_path, parameter.lineno)}
                    ),
                )
                for parameter in binding.caller_parameters
            },
        )
    state.warnings.extend(program.warnings)
