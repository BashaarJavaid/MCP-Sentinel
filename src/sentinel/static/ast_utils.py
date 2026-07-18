"""Small bounded AST utilities shared by MCP-specific rules."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from sentinel.finding import SourceRange
from sentinel.static.model import ParsedPythonFile, StaticMatch


@dataclass(frozen=True)
class ToolRegion:
    name: str
    function: ast.AsyncFunctionDef | ast.FunctionDef
    node: ast.AST


def qualified_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = qualified_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def decorator_call(node: ast.AST) -> tuple[str | None, ast.Call | None]:
    if isinstance(node, ast.Call):
        return qualified_name(node.func), node
    return qualified_name(node), None


def discover_tool_regions(file: ParsedPythonFile) -> tuple[ToolRegion, ...]:
    regions: list[ToolRegion] = []
    for node in file.tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            name, call = decorator_call(decorator)
            if name and name.endswith(".tool"):
                tool_name = node.name
                if call:
                    for keyword in call.keywords:
                        if (
                            keyword.arg == "name"
                            and isinstance(keyword.value, ast.Constant)
                            and isinstance(keyword.value.value, str)
                        ):
                            tool_name = keyword.value.value
                regions.append(ToolRegion(tool_name, node, node))
            if name and name.endswith(".call_tool"):
                for branch in ast.walk(node):
                    literal = _dispatcher_literal(branch)
                    if literal is not None:
                        regions.append(ToolRegion(literal, node, branch))
    return tuple(regions)


def discover_prompt_functions(
    file: ParsedPythonFile,
) -> tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]:
    output: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for node in file.tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(
            (name := decorator_call(decorator)[0]) is not None
            and name.endswith(".prompt")
            for decorator in node.decorator_list
        ):
            output.append(node)
    return tuple(output)


def match_from_node(
    rule_id: str,
    file: ParsedPythonFile,
    node: ast.AST,
    kind: str,
    *,
    snippet: str | None = None,
    fingerprint: str | None = None,
) -> StaticMatch:
    source_range = range_for_node(node)
    return StaticMatch(
        rule_id=rule_id,
        path=file.relative_path,
        range=source_range,
        snippet=(
            snippet
            if snippet is not None
            else lines_for_range(file.source, source_range)
        ),
        fingerprint=fingerprint,
        match_kinds=(kind,),
    )


def range_for_node(node: ast.AST) -> SourceRange:
    line = getattr(node, "lineno", 1)
    column = getattr(node, "col_offset", 0) + 1
    end_line = getattr(node, "end_lineno", line)
    end_column = getattr(node, "end_col_offset", column) + 1
    if (end_line, end_column) <= (line, column):
        end_column = column + 1
    return SourceRange(
        start_line=line,
        start_column=column,
        end_line=end_line,
        end_column=end_column,
    )


def lines_for_range(source: str, source_range: SourceRange) -> str:
    lines = source.splitlines()
    return "\n".join(lines[source_range.start_line - 1 : source_range.end_line])


def literal_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def module_name(root: Path, file: ParsedPythonFile) -> str:
    del root
    path = Path(file.relative_path)
    parts = list(path.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def import_aliases(file: ParsedPythonFile) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for node in file.tree.body:
        if isinstance(node, ast.Import):
            for item in node.names:
                aliases[item.asname or item.name.split(".")[0]] = item.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for item in node.names:
                aliases[item.asname or item.name] = f"{node.module}.{item.name}"
    return aliases


def resolve_name(name: str, aliases: dict[str, str]) -> str:
    first, separator, rest = name.partition(".")
    base = aliases.get(first, first)
    return f"{base}.{rest}" if separator else base


def _dispatcher_literal(node: ast.AST) -> str | None:
    if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
        return None
    compare = node.test
    if len(compare.ops) != 1 or not isinstance(compare.ops[0], ast.Eq):
        return None
    candidates = (compare.left, *compare.comparators)
    if not any(isinstance(item, ast.Name) and item.id == "name" for item in candidates):
        return None
    for item in candidates:
        value = literal_string(item)
        if value is not None:
            return value
    return None
