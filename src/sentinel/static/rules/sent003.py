"""SENT-003 missing tool input validation analysis."""

from __future__ import annotations

import ast

from sentinel.static.ast_utils import (
    discover_tool_regions,
    match_from_node,
    qualified_name,
)
from sentinel.static.model import RuleRunState, StaticContext


def detect(context: StaticContext, state: RuleRunState) -> None:
    for file in context.files.python_files:
        for region in discover_tool_regions(file):
            if region.node is region.function:
                unsafe = _unsafe_parameter(region.function)
                if unsafe is not None:
                    validation = _first_validation(region.function)
                    first_use = _first_name_use(region.function, unsafe.arg)
                    if validation is not None and (
                        first_use is None or validation.lineno <= first_use.lineno
                    ):
                        state.exempt("validated_before_use")
                    else:
                        state.matches.append(
                            match_from_node(
                                "SENT-003", file, unsafe, "untyped-parameter"
                            )
                        )
            else:
                dispatcher_first_use = _first_arguments_use(region.node)
                validation = _first_validation(region.node)
                if dispatcher_first_use is not None and (
                    validation is None
                    or validation.lineno > getattr(dispatcher_first_use, "lineno", 0)
                ):
                    state.matches.append(
                        match_from_node(
                            "SENT-003",
                            file,
                            dispatcher_first_use,
                            "unchecked-dispatch-arguments",
                        )
                    )


def _unsafe_parameter(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> ast.arg | None:
    if node.args.kwarg is not None:
        return node.args.kwarg
    parameters = (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
    for parameter in parameters:
        if parameter.arg in {"self", "ctx", "context"}:
            continue
        annotation = parameter.annotation
        if annotation is None:
            return parameter
        base = annotation.value if isinstance(annotation, ast.Subscript) else annotation
        name = qualified_name(base) or ""
        if name in {"Any", "typing.Any", "dict", "typing.Dict"}:
            return parameter
    return None


def _first_arguments_use(node: ast.AST) -> ast.AST | None:
    uses = [
        item
        for item in ast.walk(node)
        if (
            isinstance(item, ast.Subscript)
            and isinstance(item.value, ast.Name)
            and item.value.id in {"arguments", "kwargs"}
        )
        or (
            isinstance(item, ast.Call)
            and isinstance(item.func, ast.Attribute)
            and isinstance(item.func.value, ast.Name)
            and item.func.value.id in {"arguments", "kwargs"}
            and item.func.attr == "get"
        )
    ]
    return min(uses, key=lambda item: item.lineno) if uses else None


def _first_name_use(node: ast.AST, name: str) -> ast.Name | None:
    uses = [
        item
        for item in ast.walk(node)
        if isinstance(item, ast.Name) and item.id == name
    ]
    return min(uses, key=lambda item: item.lineno) if uses else None


def _first_validation(node: ast.AST) -> ast.Call | None:
    validations: list[ast.Call] = []
    for item in ast.walk(node):
        if not isinstance(item, ast.Call):
            continue
        name = qualified_name(item.func) or ""
        if name.endswith((".model_validate", ".parse_obj", ".validate")) or name in {
            "jsonschema.validate",
        }:
            validations.append(item)
    return min(validations, key=lambda item: item.lineno) if validations else None
