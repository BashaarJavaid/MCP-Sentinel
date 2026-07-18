"""Static MCP tool metadata extraction; target code is never imported."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import cast

import yaml
from pydantic import JsonValue, field_validator

from sentinel.finding import ContractModel, NonEmptyString
from sentinel.report.model import ReportWarning
from sentinel.static.model import ParsedPythonFile
from sentinel.static.traversal import collect_static_files


class ToolMetadata(ContractModel):
    name: NonEmptyString
    description: str | None
    input_schema: dict[str, JsonValue]
    path: NonEmptyString
    start_line: int
    end_line: int

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class ToolCatalog(ContractModel):
    tools: tuple[ToolMetadata, ...]
    warnings: tuple[ReportWarning, ...]

    def for_location(self, path: str, line: int) -> ToolMetadata | None:
        return next(
            (
                tool
                for tool in self.tools
                if tool.path == path and tool.start_line <= line <= tool.end_line
            ),
            None,
        )


def extract_tool_catalog(root: Path, ignore_paths: tuple[str, ...] = ()) -> ToolCatalog:
    files = collect_static_files(root, ignore_paths)
    tools: dict[str, ToolMetadata] = {}
    for parsed in files.python_files:
        models = _pydantic_models(parsed.tree)
        for tool in _tools_in_file(parsed, models):
            tools.setdefault(tool.name, tool)

    warnings: list[ReportWarning] = []
    manifest = root / "tools.yaml"
    if manifest.is_file() and not manifest.is_symlink():
        _merge_manifest(manifest, tools, warnings)
    return ToolCatalog(
        tools=tuple(sorted(tools.values(), key=lambda item: (item.name, item.path))),
        warnings=tuple(warnings),
    )


def _tools_in_file(
    parsed: ParsedPythonFile, models: dict[str, dict[str, JsonValue]]
) -> tuple[ToolMetadata, ...]:
    found: list[ToolMetadata] = []
    for node in ast.walk(parsed.tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(
            _is_tool_decorator(item) for item in node.decorator_list
        ):
            found.append(
                ToolMetadata(
                    name=node.name,
                    description=ast.get_docstring(node),
                    input_schema=_signature_schema(node, models),
                    path=parsed.relative_path,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                )
            )
        if isinstance(node, ast.If):
            name = _dispatcher_tool_name(node.test)
            if name is not None:
                found.append(
                    ToolMetadata(
                        name=name,
                        description=None,
                        input_schema={
                            "type": "object",
                            "properties": {},
                            "additionalProperties": False,
                        },
                        path=parsed.relative_path,
                        start_line=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                    )
                )
    return tuple(found)


def _is_tool_decorator(node: ast.expr) -> bool:
    value = node.func if isinstance(node, ast.Call) else node
    return isinstance(value, ast.Attribute) and value.attr == "tool"


def _dispatcher_tool_name(node: ast.expr) -> str | None:
    if not isinstance(node, ast.Compare) or len(node.ops) != 1:
        return None
    if not isinstance(node.ops[0], ast.Eq) or len(node.comparators) != 1:
        return None
    sides = (node.left, node.comparators[0])
    variable = next(
        (
            side
            for side in sides
            if isinstance(side, ast.Name) and side.id in {"name", "tool_name"}
        ),
        None,
    )
    literal = next(
        (
            side.value
            for side in sides
            if isinstance(side, ast.Constant) and isinstance(side.value, str)
        ),
        None,
    )
    return literal if variable is not None and isinstance(literal, str) else None


def _pydantic_models(tree: ast.Module) -> dict[str, dict[str, JsonValue]]:
    models: dict[str, dict[str, JsonValue]] = {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or not any(
            _qualified_name(base).endswith("BaseModel") for base in node.bases
        ):
            continue
        properties: dict[str, JsonValue] = {}
        required: list[JsonValue] = []
        for item in node.body:
            if not isinstance(item, ast.AnnAssign) or not isinstance(
                item.target, ast.Name
            ):
                continue
            properties[item.target.id] = _annotation_schema(item.annotation, models)
            if item.value is None:
                required.append(item.target.id)
        models[node.name] = _object_schema(properties, required)
    return models


def _signature_schema(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    models: dict[str, dict[str, JsonValue]],
) -> dict[str, JsonValue]:
    positional = (*node.args.posonlyargs, *node.args.args)
    default_offset = len(positional) - len(node.args.defaults)
    properties: dict[str, JsonValue] = {}
    required: list[JsonValue] = []
    for index, argument in enumerate(positional):
        properties[argument.arg] = _annotation_schema(argument.annotation, models)
        if index < default_offset:
            required.append(argument.arg)
    for argument, default in zip(
        node.args.kwonlyargs, node.args.kw_defaults, strict=True
    ):
        properties[argument.arg] = _annotation_schema(argument.annotation, models)
        if default is None:
            required.append(argument.arg)
    return _object_schema(properties, required)


def _object_schema(
    properties: dict[str, JsonValue], required: list[JsonValue]
) -> dict[str, JsonValue]:
    result: dict[str, JsonValue] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        result["required"] = required
    return result


def _annotation_schema(
    node: ast.expr | None, models: dict[str, dict[str, JsonValue]]
) -> dict[str, JsonValue]:
    if node is None:
        return {}
    name = _qualified_name(node)
    primitive = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "None": "null",
        "NoneType": "null",
    }.get(name)
    if primitive:
        return {"type": primitive}
    if name in models:
        return models[name]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return {
            "anyOf": [
                _annotation_schema(node.left, models),
                _annotation_schema(node.right, models),
            ]
        }
    if isinstance(node, ast.Subscript):
        base = _qualified_name(node.value).split(".")[-1]
        arguments = _subscript_arguments(node.slice)
        if base in {"list", "List", "set", "Set", "tuple", "Tuple"}:
            item = arguments[0] if arguments else None
            return {"type": "array", "items": _annotation_schema(item, models)}
        if base in {"dict", "Dict", "Mapping"}:
            value = arguments[1] if len(arguments) > 1 else None
            return {
                "type": "object",
                "additionalProperties": _annotation_schema(value, models),
            }
        if base in {"Union", "Optional"}:
            choices = [_annotation_schema(item, models) for item in arguments]
            if base == "Optional":
                choices.append({"type": "null"})
            return {"anyOf": cast(JsonValue, choices)}
        if base == "Literal":
            values = [
                item.value
                for item in arguments
                if isinstance(item, ast.Constant)
                and isinstance(item.value, (str, int, float, bool, type(None)))
            ]
            return {"enum": cast(JsonValue, values)}
    return {}


def _subscript_arguments(node: ast.expr) -> tuple[ast.expr, ...]:
    return tuple(node.elts) if isinstance(node, ast.Tuple) else (node,)


def _qualified_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _qualified_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _merge_manifest(
    path: Path, tools: dict[str, ToolMetadata], warnings: list[ReportWarning]
) -> None:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        _manifest_warning(warnings, f"tools.yaml is invalid: {error}")
        return
    if not isinstance(payload, dict) or (
        "version" in payload and payload.get("version") != 1
    ):
        _manifest_warning(warnings, "tools.yaml must use version: 1")
        return
    entries = payload.get("tools")
    if not isinstance(entries, list):
        _manifest_warning(warnings, "tools.yaml tools must be a list")
        return
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            _manifest_warning(warnings, "ignored an invalid tools.yaml entry")
            continue
        name = entry["name"]
        tool = tools.get(name)
        if tool is None:
            _manifest_warning(
                warnings,
                f"tools.yaml entry {name!r} does not match an AST-discovered tool",
            )
            continue
        allowed = {"name", "description", "input_schema"}
        if set(entry) - allowed:
            _manifest_warning(warnings, f"tools.yaml entry {name!r} has unknown keys")
            continue
        description = entry.get("description", tool.description)
        schema = entry.get("input_schema", tool.input_schema)
        if description is not None and not isinstance(description, str):
            _manifest_warning(
                warnings, f"tools.yaml entry {name!r} has bad description"
            )
            continue
        if not isinstance(schema, dict):
            _manifest_warning(warnings, f"tools.yaml entry {name!r} has bad schema")
            continue
        try:
            tools[name] = tool.model_copy(
                update={"description": description, "input_schema": schema}
            )
        except Exception:
            _manifest_warning(
                warnings, f"tools.yaml entry {name!r} has non-JSON schema"
            )


def _manifest_warning(warnings: list[ReportWarning], message: str) -> None:
    warnings.append(ReportWarning(code="tool_manifest_fallback", message=message))
