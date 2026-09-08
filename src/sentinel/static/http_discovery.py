"""Source-established Python HTTP entry points shared by boundary detectors."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sentinel.static.ast_utils import (
    import_aliases,
    qualified_name,
    resolve_name,
    scope_nodes,
)
from sentinel.static.discovery import Function, PythonProgram, Symbol
from sentinel.static.execution import check_deadline

if TYPE_CHECKING:
    from sentinel.static.typescript_discovery import TypeScriptProgram, TypeScriptSymbol


@dataclass(frozen=True)
class TypeScriptHTTPBinding:
    registration: TypeScriptSymbol
    handler: TypeScriptSymbol | None


def typescript_handlers(
    program: TypeScriptProgram,
) -> tuple[TypeScriptHTTPBinding, ...]:
    """Explicit module-level Express routes, using the existing module resolver."""
    from sentinel.static.typescript_discovery import TypeScriptSymbol, name_of

    found = []
    for path, tree in program.trees.items():
        file = program.files[path]
        for statement in tree["Pr"]:
            check_deadline(program.deadline)
            expression = statement.get("ExprStmt", [None])[0]
            if not isinstance(expression, dict) or "Call" not in expression:
                continue
            callee, arguments = expression["Call"]
            name = name_of(callee) or ""
            receiver, _, method = name.rpartition(".")
            if method not in {"get", "post", "put", "patch", "delete", "head", "all"}:
                continue
            app = program.resolve(file, receiver)
            if app is None or "Call" not in app.node:
                continue
            constructor = program.resolve_node(app.file, app.node["Call"][0])
            if constructor is None or constructor.external not in {
                "express.default",
                "express.Router",
                "express.default.Router",
            }:
                continue
            args = arguments[1]
            if len(args) != 2 or any("Arg" not in arg for arg in args):
                program.unresolved(file, "HTTP route middleware sequence or arguments")
                continue
            found.append(
                TypeScriptHTTPBinding(
                    TypeScriptSymbol(file, expression),
                    program.resolve_node(file, args[1]["Arg"]),
                )
            )
    return tuple(found)


@dataclass(frozen=True)
class HTTPBinding:
    registration: Symbol
    handler: Symbol
    caller_parameters: tuple[ast.arg, ...]
    continuation: str | None = None


def shadowed(program: PythonProgram, node: ast.AST, name: str) -> bool:
    child = node
    owner = program.parents.get(node)
    while owner is not None:
        if (
            isinstance(owner, (Function, ast.ClassDef))
            and not (
                isinstance(owner, Function)
                and (child in owner.decorator_list or child is owner.args)
            )
            and any(
                (isinstance(part, ast.arg) and part.arg == name)
                or (
                    isinstance(part, ast.Name)
                    and isinstance(part.ctx, ast.Store)
                    and part.id == name
                )
                for part in scope_nodes(owner)
            )
        ):
            return True
        child, owner = owner, program.parents.get(owner)
    return False


def injected_parameters(
    node: ast.FunctionDef | ast.AsyncFunctionDef, imports: dict[str, str]
) -> set[str]:
    positional = (*node.args.posonlyargs, *node.args.args)
    defaults = dict(
        zip(
            (p.arg for p in positional[len(positional) - len(node.args.defaults) :]),
            node.args.defaults,
            strict=True,
        )
    )
    defaults.update(
        (p.arg, default)
        for p, default in zip(node.args.kwonlyargs, node.args.kw_defaults, strict=True)
        if default is not None
    )
    return {
        parameter.arg
        for parameter in (*positional, *node.args.kwonlyargs)
        if any(
            isinstance(part, ast.Call)
            and resolve_name(qualified_name(part.func) or "", imports)
            in {"fastapi.Depends", "fastapi.Security"}
            for expression in (parameter.annotation, defaults.get(parameter.arg))
            if expression is not None
            for part in ast.walk(expression)
        )
    }


def handlers(program: PythonProgram) -> tuple[HTTPBinding, ...]:
    found: list[HTTPBinding] = []
    for file in program.files:
        imports = import_aliases(file)
        imports = {
            name: target
            for name, target in imports.items()
            if len(program.bindings[file.relative_path].get(name, [])) == 1
            and isinstance(
                program.bindings[file.relative_path][name][0],
                (ast.Import, ast.ImportFrom),
            )
        }
        applications = {
            name
            for name, declarations in program.bindings[file.relative_path].items()
            if len(declarations) == 1
            and isinstance(declarations[0], (ast.Assign, ast.AnnAssign))
            and isinstance(declarations[0].value, ast.Call)
            and resolve_name(qualified_name(declarations[0].value.func) or "", imports)
            in {
                "fastapi.FastAPI",
                "fastapi.APIRouter",
                "starlette.applications.Starlette",
            }
        }
        for node in ast.walk(file.tree):
            check_deadline(program.deadline)
            if isinstance(node, Function):
                for decorator in node.decorator_list:
                    if not isinstance(decorator, ast.Call):
                        continue
                    name = qualified_name(decorator.func) or ""
                    if shadowed(program, decorator, name.split(".")[0]):
                        continue
                    if name.split(".")[0] in applications and name.rsplit(".", 1)[
                        -1
                    ] in {
                        "get",
                        "post",
                        "put",
                        "patch",
                        "delete",
                        "head",
                        "options",
                        "route",
                        "api_route",
                    }:
                        found.append(
                            HTTPBinding(
                                Symbol(file, name, decorator),
                                Symbol(file, node.name, node),
                                tuple(
                                    p
                                    for p in (
                                        *node.args.posonlyargs,
                                        *node.args.args,
                                        *node.args.kwonlyargs,
                                    )
                                    if p.arg not in {"self", "cls"}
                                    and p.arg not in injected_parameters(node, imports)
                                ),
                            )
                        )
            elif isinstance(node, ast.Call):
                name = qualified_name(node.func) or ""
                external = resolve_name(name, imports)
                callback = None
                middleware = external == "starlette.middleware.Middleware"
                if middleware and node.args:
                    callback = node.args[0]
                elif external == "starlette.routing.Route" or (
                    name.split(".")[0] in applications and name.endswith(".add_route")
                ):
                    callback = (
                        node.args[1]
                        if len(node.args) > 1
                        else next(
                            (kw.value for kw in node.keywords if kw.arg == "endpoint"),
                            None,
                        )
                    )
                elif (
                    name.split(".")[0] in applications
                    and name.endswith(".add_middleware")
                    and node.args
                ):
                    callback = node.args[0]
                    middleware = True
                if callback is None or shadowed(program, node, name.split(".")[0]):
                    continue
                target = (
                    program.resolve_in(
                        Symbol(file, name, node), qualified_name(callback) or ""
                    )
                    if callback
                    else None
                )
                if target and middleware and isinstance(target.node, ast.ClassDef):
                    methods = [
                        child
                        for child in target.node.body
                        if isinstance(child, Function)
                    ]
                    bases = import_aliases(target.file)
                    base_http = any(
                        resolve_name(qualified_name(base) or "", bases)
                        == "starlette.middleware.base.BaseHTTPMiddleware"
                        for base in target.node.bases
                    )
                    method = next(
                        (
                            child
                            for child in methods
                            if child.name == ("dispatch" if base_http else "__call__")
                        ),
                        None,
                    )
                    if method:
                        target = Symbol(
                            target.file, target.name + "." + method.name, method
                        )
                if target and isinstance(target.node, Function):
                    parameters = [
                        p
                        for p in (*target.node.args.posonlyargs, *target.node.args.args)
                        if p.arg not in {"self", "cls"}
                    ]
                    if parameters:
                        continuation = (
                            parameters[1].arg
                            if middleware
                            and target.node.name == "dispatch"
                            and len(parameters) > 1
                            else "self.app"
                            if middleware
                            else None
                        )
                        found.append(
                            HTTPBinding(
                                Symbol(file, name, node),
                                target,
                                (parameters[0],),
                                continuation,
                            )
                        )
    return tuple(found)
