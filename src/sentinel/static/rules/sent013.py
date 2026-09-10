"""Explicit instruction poisoning in statically recovered MCP descriptions."""

from __future__ import annotations

import ast
import re
import unicodedata
from collections.abc import Iterator

from sentinel.report.model import ReportWarning
from sentinel.static.ast_utils import (
    import_aliases,
    match_from_node,
    qualified_name,
    resolve_name,
)
from sentinel.static.discovery import Function, PythonProgram
from sentinel.static.execution import check_deadline
from sentinel.static.model import (
    ParsedPythonFile,
    RuleRunState,
    StaticContext,
    StaticMatch,
)
from sentinel.static.semgrep_ast import source_range
from sentinel.static.typescript_discovery import (
    TypeScriptProgram,
    TypeScriptSymbol,
    name_of,
    walk,
)

_PATTERNS = (
    r"\b(?:ignore|disregard|override|replace)\s+(?:all\s+)?"
    r"(?:previous|prior|system|developer|earlier)\s+(?:instructions|prompts|rules|messages)\b",
    r"\b(?:reveal|disclose|exfiltrate|send|upload|include)\b.{0,100}\b"
    r"(?:api[ _-]?keys?|passwords?|secrets?|environment variables?|private keys?|"
    r"id_rsa|flags\.txt)\b.{0,100}\b(?:response|results?|calculations?|https?://|to\b)",
    r"\bread\b.{0,100}(?:\.ssh/|/secrets/|private key).{0,100}"
    r"\b(?:send|include|reveal|upload)\b",
    r"\b(?:when|before)\s+using\s+(?:this|the)\s+tool\b.{0,60}\bfirst\b.{0,40}"
    r"\b(?:call|invoke|use|read)\b.{0,80}"
    r"(?:get_environment|environment variables?|secrets?|credentials?|private keys?)",
    r"\binstead of\s+(?:the\s+)?(?:requested|selected)\s+tool\b.{0,60}"
    r"\b(?:call|invoke|use)\b",
)
_DIRECTIVES = tuple(
    re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in _PATTERNS
)
_QUOTED_WARNINGS = tuple(
    re.compile(pattern, re.IGNORECASE | re.DOTALL)
    for pattern in (
        r"\bexample of (?:malicious|untrusted|attack) "
        r'(?:input|instructions?)\s*:\s*(["\'])(.*?)\1',
        r'\bwarning\s*:\s*(["\'])(.*?)\1\s+is\s+(?:an?\s+)?'
        r"(?:example|attack|malicious instruction)\b",
        r'\b(?:do not|never)\s+follow\s+(["\'])(.*?)\1',
    )
)


def poisoned(text: str) -> bool:
    # Semgrep retains JavaScript escape spelling in literal tokens.
    text = re.sub(
        r"\\(?:u([0-9a-fA-F]{4})|x([0-9a-fA-F]{2}))",
        lambda m: chr(int(m[1] or m[2], 16)),
        text,
    )
    text = "".join(
        c
        for c in unicodedata.normalize("NFKC", text)
        if unicodedata.category(c) != "Cf"
    )
    text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
    for warning in _QUOTED_WARNINGS:
        text = warning.sub("", text)
    for pattern in _DIRECTIVES:
        for match in pattern.finditer(text):
            prefix = text[max(0, match.start() - 40) : match.start()]
            if not re.search(
                r"\b(?:do not|must not|never|avoid|not to)\s*$", prefix, re.I
            ):
                return True
    return False


def python_text(
    program: PythonProgram,
    file: ParsedPythonFile,
    node: ast.AST,
    depth: int = 0,
) -> tuple[ParsedPythonFile, ast.AST, str] | None:
    if depth >= 64:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return file, node, node.value
    if isinstance(node, (ast.Name, ast.Attribute)):
        symbol = program.resolve(file, qualified_name(node) or "")
        if symbol:
            return python_text(program, symbol.file, symbol.node, depth + 1)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = python_text(program, file, node.left, depth + 1)
        right = python_text(program, file, node.right, depth + 1)
        if left and right:
            return file, node, left[2] + right[2]
    return None


def python_descriptions(
    context: StaticContext,
) -> Iterator[tuple[ParsedPythonFile, ast.AST]]:
    program = context.python_program
    for binding in program.tools():
        handler = binding.handler.node
        if not isinstance(handler, Function):
            continue
        if (
            handler.body
            and isinstance(handler.body[0], ast.Expr)
            and isinstance(handler.body[0].value, ast.Constant)
        ):
            yield binding.handler.file, handler.body[0].value
        roots = [
            (binding.handler.file, root)
            for root in [*handler.decorator_list, handler.args]
        ]
        roots.append((binding.registration.file, binding.registration.node))
        for file, root in roots:
            # A registration function's body is not description metadata.
            if isinstance(root, Function):
                continue
            for node in ast.walk(root):
                if isinstance(node, ast.keyword) and node.arg == "description":
                    yield file, node.value
    for file in context.files.python_files:
        imports = import_aliases(file)
        for node in file.nodes:
            if (
                isinstance(node, ast.Call)
                and resolve_name(qualified_name(node.func) or "", imports)
                == "mcp.types.Tool"
            ):
                for keyword in node.keywords:
                    if keyword.arg == "description":
                        yield file, keyword.value
                    elif keyword.arg == "inputSchema":
                        for schema in ast.walk(keyword.value):
                            if isinstance(schema, ast.Dict):
                                for key, value in zip(
                                    schema.keys, schema.values, strict=True
                                ):
                                    if (
                                        isinstance(key, ast.Constant)
                                        and key.value == "description"
                                    ):
                                        yield file, value


def typescript_descriptions(program: TypeScriptProgram) -> Iterator[TypeScriptSymbol]:
    metadata = list(program.listed_tools())
    for binding in program.tools():
        if binding.description:
            yield binding.description
        if binding.schema:
            metadata.append(binding.schema)
    for root in metadata:
        for node in walk(root.node):
            definition = node.get("F", {}).get("DefStmt")
            if definition and name_of(definition[0]["name"]) == "description":
                value = (definition[1].get("FieldDefColon", {}).get("vinit") or {}).get(
                    "some"
                )
                if value:
                    resolved = program.resolve_node(root.file, value)
                    if resolved:
                        yield resolved
            call = node.get("Call")
            if call and (name_of(call[0]) or "").endswith(".describe"):
                for argument in call[1][1][:1]:
                    if "Arg" in argument:
                        resolved = program.resolve_node(root.file, argument["Arg"])
                        if resolved:
                            yield resolved


def detect(context: StaticContext, state: RuleRunState) -> None:
    for file, node in python_descriptions(context):
        check_deadline(context.deadline)
        recovered = python_text(context.python_program, file, node)
        if recovered:
            source, expression, text = recovered
            match = match_from_node(
                "SENT-013", source, expression, "description-directive"
            )
            state.visit(match.path, match.range)
            if poisoned(text):
                state.matches.append(match)
        else:
            state.warnings.append(
                ReportWarning(
                    code="static_description_unresolved",
                    message=f"SENT-013 at {file.relative_path}:"
                    f"{getattr(node, 'lineno', 1)}: "
                    "dynamic tool description was not evaluated",
                )
            )
    if context.files.typescript_files:
        program = context.typescript_program
        for description in typescript_descriptions(program):
            check_deadline(context.deadline)
            ts_text = program.literal(description)
            if ts_text is None:
                program.unresolved(description.file, "dynamic tool description")
                continue
            location = source_range(description.node, description.file)
            state.visit(description.file.relative_path, location)
            if poisoned(ts_text):
                state.matches.append(
                    StaticMatch(
                        rule_id="SENT-013",
                        path=description.file.relative_path,
                        range=location,
                        snippet=program.text(description.file, description.node),
                        match_kinds=("description-directive",),
                    )
                )
        state.warnings.extend(program.warnings)
