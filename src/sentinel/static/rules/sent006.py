"""SENT-006 HTTP route authentication analysis."""

from __future__ import annotations

import ast

from pathspec import GitIgnoreSpec

from sentinel.static.ast_utils import match_from_node, qualified_name
from sentinel.static.model import RuleRunState, StaticContext

_HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def detect(context: StaticContext, state: RuleRunState) -> None:
    public = context.configuration.scanner.rules.sent006.public_routes
    for file in context.files.python_files:
        functions = {
            node.name: node
            for node in file.tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        global_auth = _has_global_auth(file.tree)
        for function in functions.values():
            for decorator in function.decorator_list:
                call = decorator if isinstance(decorator, ast.Call) else None
                name = qualified_name(call.func) if call else qualified_name(decorator)
                if not name:
                    continue
                method = name.rsplit(".", 1)[-1].lower()
                if method not in _HTTP_METHODS and method != "api_route":
                    continue
                route = _literal(call.args[0]) if call and call.args else None
                if route is None:
                    continue
                methods = [method.upper()]
                if method == "api_route" and call:
                    methods = _api_route_methods(call)
                if all(_is_public(item, route, public) for item in methods):
                    state.exempt("configured_public_route")
                    continue
                if global_auth or _decorator_has_verified_auth(call, functions):
                    state.exempt("verified_auth")
                    continue
                state.matches.append(
                    match_from_node("SENT-006", file, decorator, "missing-auth")
                )


def _has_global_auth(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = qualified_name(node.func) or ""
        if name.endswith("add_middleware") and any(
            "AuthenticationMiddleware" in (qualified_name(arg) or "")
            for arg in node.args
        ):
            return True
    return False


def _decorator_has_verified_auth(
    call: ast.Call | None,
    functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef],
) -> bool:
    if call is None:
        return False
    candidates: set[str] = set()
    for keyword in call.keywords:
        if keyword.arg not in {"dependencies", "dependency"}:
            continue
        for item in ast.walk(keyword.value):
            dependency = isinstance(item, ast.Call) and (
                qualified_name(item.func) or ""
            ).endswith(("Depends", "Security"))
            if (
                dependency
                and isinstance(item, ast.Call)
                and item.args
                and isinstance(item.args[0], ast.Name)
            ):
                candidates.add(item.args[0].id)
    return any(_verified_function(functions.get(name)) for name in candidates)


def _verified_function(node: ast.AST | None) -> bool:
    if node is None:
        return False
    reads = any(
        isinstance(item, ast.Name)
        and any(
            token in item.id.lower()
            for token in ("token", "credential", "authorization", "session")
        )
        for item in ast.walk(node)
    )
    verifies = any(
        isinstance(item, ast.Call)
        and any(
            token in (qualified_name(item.func) or "").lower()
            for token in ("jwt.decode", "compare_digest", ".verify")
        )
        for item in ast.walk(node)
    )
    rejects = any(isinstance(item, ast.Raise) for item in ast.walk(node))
    return reads and verifies and rejects


def _is_public(method: str, route: str, configured: tuple[str, ...]) -> bool:
    for item in configured:
        expected_method, pattern = item.split(" ", 1)
        if method != expected_method:
            continue
        spec = GitIgnoreSpec.from_lines([pattern.lstrip("/")])
        if spec.match_file(route.lstrip("/")):
            return True
    return False


def _api_route_methods(call: ast.Call) -> list[str]:
    for keyword in call.keywords:
        if keyword.arg == "methods" and isinstance(
            keyword.value, (ast.List, ast.Tuple)
        ):
            values = [_literal(item) for item in keyword.value.elts]
            return [value.upper() for value in values if value]
    return ["GET"]


def _literal(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None
