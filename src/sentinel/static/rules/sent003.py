"""SENT-003 validation must cover the consumed value on every continuing path."""

from __future__ import annotations

import ast

from sentinel.static.ast_utils import (
    discover_tool_regions,
    import_aliases,
    match_from_node,
    qualified_name,
    resolve_name,
)
from sentinel.static.model import ParsedPythonFile, RuleRunState, StaticContext
from sentinel.static.safety import (
    Condition,
    constants,
    literal,
    paths,
    reference,
    type_guard,
)

_PRIMITIVES = {"str", "int", "float", "bool", "bytes"}


def _typed(annotation: ast.expr | None) -> bool:
    return (qualified_name(annotation) if annotation is not None else "") in _PRIMITIVES


def _models(file: ParsedPythonFile) -> dict[str, set[str]]:
    imports = import_aliases(file)
    return {
        node.name: {
            item.target.id
            for item in node.body
            if isinstance(item, ast.AnnAssign)
            and isinstance(item.target, ast.Name)
            and _typed(item.annotation)
        }
        for node in file.tree.body
        if isinstance(node, ast.ClassDef)
        and any(
            resolve_name(qualified_name(base) or "", imports) == "pydantic.BaseModel"
            for base in node.bases
        )
    }


def _schema_fields(node: ast.AST | None, values: dict[str, ast.expr]) -> set[str]:
    schema = literal(node, values)
    if not isinstance(schema, dict) or schema.get("type") != "object":
        return set()
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    return (
        {
            name
            for name, spec in properties.items()
            if name in required
            and isinstance(spec, dict)
            and spec.get("type") in {"string", "integer", "number", "boolean"}
        }
        if isinstance(properties, dict)
        else set()
    )


def _helper_guards(
    function: ast.FunctionDef | ast.AsyncFunctionDef, deadline: float
) -> set[str]:
    outcomes = []
    for path in paths(function.body, deadline):
        proved: set[str] = set()
        for event in path:
            if isinstance(event, Condition):
                proved.update(type_guard(event.test, event.truth, {}))
            elif isinstance(event, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                # A mutation invalidates a custom guard's input relationship.
                proved.clear()
        if not path or not isinstance(path[-1], ast.Raise):
            outcomes.append(proved)
    return set.intersection(*outcomes) if outcomes else set()


def detect(context: StaticContext, state: RuleRunState) -> None:
    for file in context.files.python_files:
        models, values, imports = (
            _models(file),
            constants(file.tree),
            import_aliases(file),
        )
        helpers = {
            node.name: node
            for node in file.tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not node.decorator_list
        }
        guards = {
            name: _helper_guards(fn, context.deadline) for name, fn in helpers.items()
        }
        for region in discover_tool_regions(file):
            function = region.function
            parameters = (
                *function.args.posonlyargs,
                *function.args.args,
                *function.args.kwonlyargs,
                *([function.args.kwarg] if function.args.kwarg else []),
            )
            unsafe = [
                p
                for p in parameters
                if p.arg not in {"self", "ctx", "context", "name"}
                and not _typed(p.annotation)
            ]
            if not unsafe:
                continue
            body = function.body if region.node is function else [region.node]
            failed = False
            for path in paths(body, context.deadline):
                aliases = {p.arg: p.arg for p in unsafe}
                tracked = set(aliases.values())
                checked = {
                    f"{p.arg}.{field}"
                    for p in unsafe
                    for field in models.get(
                        (qualified_name(p.annotation) or "")
                        if p.annotation is not None
                        else "",
                        set(),
                    )
                }

                def fields(
                    call: ast.Call, models: dict[str, set[str]] = models
                ) -> set[str]:
                    if isinstance(call.func, ast.Attribute) and call.func.attr in {
                        "model_validate",
                        "parse_obj",
                    }:
                        return models.get(qualified_name(call.func.value) or "", set())
                    return set()

                def consumes(
                    node: ast.AST | None,
                    aliases: dict[str, str] = aliases,
                    tracked: set[str] = tracked,
                    checked: set[str] = checked,
                ) -> bool:
                    if node is None:
                        return False
                    ref = reference(node, aliases)
                    if ref and any(
                        ref == root or ref.startswith(root + ".") for root in tracked
                    ):
                        return not any(
                            ref == proof or ref.startswith(proof + ".")
                            for proof in checked
                        )
                    if isinstance(node, ast.Call) and fields(node):
                        return (
                            False  # Parsing is a check; only its output is protected.
                        )
                    return any(consumes(child) for child in ast.iter_child_nodes(node))

                for event in path:
                    if isinstance(event, Condition):
                        checked.update(type_guard(event.test, event.truth, aliases))
                        if not (
                            type_guard(event.test, True, aliases)
                            or type_guard(event.test, False, aliases)
                        ) and consumes(event.test):
                            failed = True
                        continue
                    if isinstance(event, ast.Raise):
                        break
                    if isinstance(event, ast.Expr) and isinstance(
                        event.value, ast.Call
                    ):
                        call = event.value
                        name = qualified_name(call.func) or ""
                        if (
                            name.split(".")[0] in imports
                            and resolve_name(name, imports) == "jsonschema.validate"
                            and len(call.args) >= 2
                        ):
                            ref = reference(call.args[0], aliases)
                            if ref:
                                checked.update(
                                    f"{ref}.{field}"
                                    for field in _schema_fields(call.args[1], values)
                                )
                            continue
                        if name in helpers and call.args and helpers[name].args.args:
                            ref = reference(call.args[0], aliases)
                            parameter = helpers[name].args.args[0].arg
                            if ref:
                                checked.update(
                                    ref + proof[len(parameter) :]
                                    for proof in guards[name]
                                    if proof == parameter
                                    or proof.startswith(parameter + ".")
                                )
                            if guards[name]:
                                continue
                        if fields(call):
                            continue
                    if isinstance(event, (ast.Assign, ast.AnnAssign)):
                        value = event.value
                        targets = (
                            event.targets
                            if isinstance(event, ast.Assign)
                            else [event.target]
                        )
                        parsed = value
                        if (
                            isinstance(parsed, ast.Call)
                            and isinstance(parsed.func, ast.Attribute)
                            and parsed.func.attr in {"model_dump", "dict"}
                        ):
                            parsed = parsed.func.value
                        parsed_fields = (
                            fields(parsed) if isinstance(parsed, ast.Call) else set()
                        )
                        ref = reference(value, aliases)
                        simple_alias = isinstance(value, ast.Name) and ref in tracked
                        if not simple_alias and not parsed_fields and consumes(value):
                            failed = True
                        for target in targets:
                            if isinstance(target, ast.Name):
                                if simple_alias and ref:
                                    aliases[target.id] = ref
                                elif parsed_fields or target.id in aliases:
                                    origin = f"@{event.lineno}:{target.id}"
                                    aliases[target.id] = origin
                                    tracked.add(origin)
                                    checked.update(
                                        f"{origin}.{field}" for field in parsed_fields
                                    )
                            else:
                                changed = reference(target, aliases)
                                if changed:
                                    checked.difference_update(
                                        proof
                                        for proof in tuple(checked)
                                        if proof == changed
                                        or proof.startswith(changed + ".")
                                    )
                    elif consumes(event):
                        failed = True
                    if failed:
                        break
                if failed:
                    break
            if failed:
                location = (
                    unsafe[0]
                    if region.node is function
                    else next(
                        (
                            node
                            for node in ast.walk(region.node)
                            if isinstance(node, ast.Subscript)
                        ),
                        region.node,
                    )
                )
                state.matches.append(
                    match_from_node(
                        "SENT-003",
                        file,
                        location,
                        "untyped-parameter"
                        if region.node is function
                        else "unchecked-dispatch-arguments",
                    )
                )
            else:
                state.exempt("validated_before_use")
