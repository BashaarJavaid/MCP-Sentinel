"""SENT-006 HTTP route authentication analysis."""

from __future__ import annotations

import ast

from pathspec import GitIgnoreSpec

from sentinel.static.ast_utils import (
    import_aliases,
    match_from_node,
    qualified_name,
    resolve_name,
)
from sentinel.static.model import RuleRunState, StaticContext
from sentinel.static.safety import (
    Condition,
    constants,
    equal_operands,
    literal,
    paths,
    reference,
    trusted,
)

_HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def detect(context: StaticContext, state: RuleRunState) -> None:
    public = context.configuration.scanner.rules.sent006.public_routes
    for file in context.files.python_files:
        functions = {
            node.name: node
            for node in file.tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        values, imports = constants(file.tree), import_aliases(file)
        applications = {
            target.id
            for statement in file.tree.body
            if isinstance(statement, ast.Assign)
            and isinstance(statement.value, ast.Call)
            and resolve_name(qualified_name(statement.value.func) or "", imports)
            in {"fastapi.FastAPI", "fastapi.APIRouter"}
            for target in statement.targets
            if isinstance(target, ast.Name)
        }
        for function in functions.values():
            for decorator in function.decorator_list:
                call = decorator if isinstance(decorator, ast.Call) else None
                name = qualified_name(call.func) if call else qualified_name(decorator)
                if not name or name.split(".")[0] not in applications:
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
                if _decorator_has_verified_auth(
                    call, functions, values, imports, context.deadline
                ):
                    state.exempt("verified_auth")
                    continue
                state.matches.append(
                    match_from_node("SENT-006", file, decorator, "missing-auth")
                )

        backends = {
            cls.name: method
            for cls in file.tree.body
            if isinstance(cls, ast.ClassDef)
            for method in cls.body
            if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
            and method.name == "authenticate"
        }
        for application in ast.walk(file.tree):
            if (
                not isinstance(application, ast.Call)
                or resolve_name(qualified_name(application.func) or "", imports)
                != "starlette.applications.Starlette"
            ):
                continue
            keywords = {kw.arg: kw.value for kw in application.keywords}
            middleware = keywords.get("middleware")
            verified_backend = False
            if middleware is not None:
                for item in ast.walk(middleware):
                    if (
                        not isinstance(item, ast.Call)
                        or resolve_name(qualified_name(item.func) or "", imports)
                        != "starlette.middleware.Middleware"
                        or not item.args
                    ):
                        continue
                    if resolve_name(qualified_name(item.args[0]) or "", imports) != (
                        "starlette.middleware.authentication.AuthenticationMiddleware"
                    ):
                        continue
                    for kw in item.keywords:
                        if (
                            kw.arg == "backend"
                            and isinstance(kw.value, ast.Call)
                            and isinstance(kw.value.func, ast.Name)
                            and kw.value.func.id in backends
                        ):
                            verified_backend |= _verified_function(
                                backends[kw.value.func.id],
                                values,
                                imports,
                                context.deadline,
                                backend=True,
                            )
            routes = keywords.get("routes")
            if routes is None:
                continue
            for route_node in ast.walk(routes):
                if (
                    not isinstance(route_node, ast.Call)
                    or resolve_name(qualified_name(route_node.func) or "", imports)
                    != "starlette.routing.Route"
                    or len(route_node.args) < 2
                ):
                    continue
                route_path = _literal(route_node.args[0])
                handler = functions.get(qualified_name(route_node.args[1]) or "")
                if route_path is None or handler is None:
                    continue
                permission = any(
                    isinstance(dec, ast.Call)
                    and resolve_name(qualified_name(dec.func) or "", imports)
                    == "starlette.authentication.requires"
                    and dec.args
                    and literal(dec.args[0], values) == "authenticated"
                    for dec in handler.decorator_list
                )
                if _is_public("GET", route_path, public):
                    state.exempt("configured_public_route")
                elif permission and verified_backend:
                    state.exempt("verified_auth")
                else:
                    state.matches.append(
                        match_from_node("SENT-006", file, route_node, "missing-auth")
                    )


def _decorator_has_verified_auth(
    call: ast.Call | None,
    functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef],
    values: dict[str, ast.expr],
    imports: dict[str, str],
    deadline: float,
) -> bool:
    if call is None:
        return False
    candidates: set[str] = set()
    for keyword in call.keywords:
        if keyword.arg not in {"dependencies", "dependency"}:
            continue
        for item in ast.walk(keyword.value):
            dependency = isinstance(item, ast.Call) and resolve_name(
                qualified_name(item.func) or "", imports
            ) in {"fastapi.Depends", "fastapi.Security"}
            if (
                dependency
                and isinstance(item, ast.Call)
                and item.args
                and isinstance(item.args[0], ast.Name)
            ):
                candidates.add(item.args[0].id)
    return any(
        _verified_function(functions[name], values, imports, deadline)
        for name in candidates
        if name in functions
    )


def _verified_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    values: dict[str, ast.expr],
    imports: dict[str, str],
    deadline: float,
    *,
    backend: bool = False,
) -> bool:
    from sentinel.static.rules.sent002 import _locals

    imports = {
        name: value for name, value in imports.items() if name not in _locals(node)
    }
    accepted = False
    for path in paths(node.body, deadline):
        aliases = {arg.arg: f"request:{arg.arg}" for arg in node.args.args}
        local = {name: value for name, value in values.items() if name not in aliases}
        verified = False
        for event in path:
            if isinstance(event, Condition):
                check = (
                    event.test.operand
                    if isinstance(event.test, ast.UnaryOp)
                    else event.test
                )
                pair = (
                    equal_operands(event.test, event.truth, imports)
                    if isinstance(check, ast.Call)
                    else None
                )
                if pair:
                    for credential, anchor in (pair, pair[::-1]):
                        ref = reference(credential, aliases) or ""
                        if ref.startswith("request:") and trusted(
                            anchor, local, imports, environment=True
                        ):
                            verified = True
            elif (
                isinstance(event, (ast.Assign, ast.AnnAssign))
                and event.value is not None
            ):
                targets = (
                    event.targets if isinstance(event, ast.Assign) else [event.target]
                )
                for target in targets:
                    if isinstance(target, ast.Name):
                        aliases[target.id] = (
                            reference(event.value, aliases) or f"unknown:{event.lineno}"
                        )
                        local[target.id] = event.value
            elif isinstance(event, ast.Raise):
                break
            elif isinstance(event, ast.Return):
                if (
                    backend
                    and literal(event.value, local) is None
                    and (event.value is None or isinstance(event.value, ast.Constant))
                ):
                    break
                if not verified:
                    return False
                accepted = True
                break
            elif isinstance(event, (ast.Try, ast.For, ast.While)):
                return False
        else:
            if not verified:
                return False
            accepted = True
    return accepted


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
