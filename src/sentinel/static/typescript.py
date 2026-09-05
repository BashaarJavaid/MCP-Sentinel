"""Small, non-executing TypeScript recognizer for the official MCP high-level APIs."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any
from urllib.parse import urlparse

from pathspec import GitIgnoreSpec

from sentinel.finding import SourceRange
from sentinel.permissions import load_permissions_manifest
from sentinel.report.model import ReportWarning
from sentinel.static.model import (
    RuleRunState,
    StaticContext,
    StaticMatch,
    TypeScriptSourceFile,
)

_IDENTIFIER = r"[A-Za-z_$][\w$]*"
_HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


@dataclass(frozen=True)
class TypeScriptTool:
    name: str | None
    description: str | None
    input_schema: dict[str, Any] | None
    schema_present: bool
    path: str
    start_line: int
    end_line: int
    start: int
    end: int
    handler: str
    handler_start: int
    parameters: tuple[str, ...]
    aliases: tuple[tuple[str, str], ...]


def tools_in_file(file: TypeScriptSourceFile) -> tuple[TypeScriptTool, ...]:
    source = file.source
    constants = _literal_constants(source)
    expressions = _constant_expressions(source)
    aliases = _import_aliases(source)
    functions = _functions(source)
    receivers = _mcp_server_receivers(source)
    if not receivers:
        return ()
    found: list[TypeScriptTool] = []
    call_pattern = re.compile(
        rf"\b(?P<server>{'|'.join(map(re.escape, sorted(receivers)))})\s*\.\s*"
        r"(?P<method>registerTool|tool)\s*\("
    )
    for match in call_pattern.finditer(source):
        close = _matching(source, match.end() - 1, "(", ")")
        if close is None:
            continue
        args = _split_top_level(source[match.end() : close])
        if not args:
            continue
        name = _literal_or_constant(args[0], constants)
        method = match.group("method")
        description: str | None = None
        schema_expr: str | None = None
        handler_expr = ""
        if method == "registerTool" and len(args) >= 2:
            description = _object_literal(args[1], "description", constants)
            schema_expr = _object_expression(args[1], "inputSchema")
            handler_expr = args[2] if len(args) >= 3 else ""
        elif method == "tool":
            middle = list(args[1:-1])
            handler_expr = args[-1] if len(args) >= 2 else ""
            if middle:
                possible_description = _literal_or_constant(middle[0], constants)
                if possible_description is not None:
                    description = possible_description
                    middle.pop(0)
            if middle:
                schema_expr = middle[0]
        handler, parameters, handler_offset = _resolve_handler(
            handler_expr, source, functions
        )
        if schema_expr:
            schema_expr = expressions.get(schema_expr.strip(), schema_expr)
        schema_present = schema_expr is not None
        schema = _zod_object_schema(schema_expr, expressions) if schema_expr else None
        found.append(
            TypeScriptTool(
                name=name,
                description=description,
                input_schema=schema,
                schema_present=schema_present,
                path=file.relative_path,
                start_line=_line(source, match.start()),
                end_line=_line(source, close),
                start=match.start(),
                end=close + 1,
                handler=handler,
                handler_start=handler_offset,
                parameters=parameters,
                aliases=tuple(sorted(aliases.items())),
            )
        )
    return tuple(found)


def catalog_warnings(tool: TypeScriptTool) -> tuple[ReportWarning, ...]:
    if tool.name is None:
        return (
            ReportWarning(
                code="typescript_tool_name_dynamic",
                message=(
                    "Skipped a computed TypeScript tool name at "
                    f"{tool.path}:{tool.start_line}"
                ),
            ),
        )
    warnings: list[ReportWarning] = []
    if tool.description is None:
        warnings.append(
            ReportWarning(
                code="typescript_tool_description_unavailable",
                message=f"Tool {tool.name!r} has no literal TypeScript description",
            )
        )
    if tool.schema_present and tool.input_schema is None:
        warnings.append(
            ReportWarning(
                code="typescript_tool_schema_unsupported",
                message=f"Tool {tool.name!r} uses an unsupported TypeScript schema",
            )
        )
    return tuple(warnings)


def route_warnings(file: TypeScriptSourceFile) -> tuple[ReportWarning, ...]:
    warnings: list[ReportWarning] = []
    receivers = _http_receivers(file.source)
    if not receivers:
        return ()
    pattern = re.compile(
        rf"\b(?:{'|'.join(map(re.escape, sorted(receivers)))})\s*\.\s*"
        rf"(?:{'|'.join(sorted(_HTTP_METHODS))})\s*\("
    )
    for route in pattern.finditer(file.source):
        close = _matching(file.source, route.end() - 1, "(", ")")
        if close is None:
            continue
        args = _split_top_level(file.source[route.end() : close])
        if args and _string_literal(args[0]) is None:
            warnings.append(
                ReportWarning(
                    code="typescript_route_path_dynamic",
                    message=(
                        "Skipped a computed route path at "
                        f"{file.relative_path}:{_line(file.source, route.start())}"
                    ),
                )
            )
    return tuple(warnings)


def detect(
    rule_id: str,
    context: StaticContext,
    state: RuleRunState,
    candidates: list[StaticMatch] | None = None,
) -> None:
    files = context.files.typescript_files
    if candidates is not None and rule_id != "SENT-002":
        paths = {candidate.path for candidate in candidates}
        files = tuple(file for file in files if file.relative_path in paths)
        context = StaticContext(
            configuration=context.configuration,
            files=replace(context.files, typescript_files=files),
            deadline=context.deadline,
        )
    tools = tuple(tool for file in files for tool in tools_in_file(file))
    for tool in tools:
        if tool.name is None:
            _warn(state, *catalog_warnings(tool))
    if rule_id == "SENT-001":
        _sent001(context, state, tools)
    elif rule_id == "SENT-002":
        _sent002(context, state, tools)
    elif rule_id == "SENT-003":
        _sent003(context, state, tools)
    elif rule_id == "SENT-004":
        _sent004(context, state)
    elif rule_id == "SENT-006":
        _sent006(context, state)
    elif rule_id == "SENT-007":
        _sent007(context, state)


def _sent001(
    context: StaticContext, state: RuleRunState, tools: tuple[TypeScriptTool, ...]
) -> None:
    manifest = load_permissions_manifest(
        context.configuration.scan_root, required=False
    )
    if manifest is None:
        state.skip_reason = "sentinel.permissions.yaml is absent"
        return
    for tool in tools:
        if tool.name is None:
            continue
        declared = manifest.tools.get(tool.name)
        if declared is None:
            state.matches.append(
                _tool_match("SENT-001", tool, "missing-tool-permissions")
            )
            continue
        reads, writes, hosts, offsets = _typescript_capabilities(
            tool.handler, dict(tool.aliases)
        )
        for name, capability, actual in (
            ("filesystem.read", declared.filesystem.read, reads),
            ("filesystem.write", declared.filesystem.write, writes),
            ("network", declared.network, hosts),
        ):
            if not _broader(capability.scopes, actual):
                continue
            if capability.broad_scope_justification:
                state.exempt(f"justified_{name}")
                continue
            state.matches.append(
                _tool_match("SENT-001", tool, f"broad-{name}", offsets.get(name, 0))
            )


def _typescript_capabilities(
    body: str, aliases: dict[str, str]
) -> tuple[set[str], set[str], set[str], dict[str, int]]:
    reads: set[str] = set()
    writes: set[str] = set()
    hosts: set[str] = set()
    offsets: dict[str, int] = {}
    read_ops = (
        "readFile",
        "readFileSync",
        "readdir",
        "readdirSync",
        "stat",
        "statSync",
        "lstat",
        "lstatSync",
        "access",
        "accessSync",
        "realpath",
        "realpathSync",
        "createReadStream",
        "opendir",
        "opendirSync",
        "existsSync",
        "readlink",
        "readlinkSync",
    )
    write_ops = (
        "writeFile",
        "writeFileSync",
        "appendFile",
        "appendFileSync",
        "truncate",
        "truncateSync",
        "copyFile",
        "copyFileSync",
        "rename",
        "renameSync",
        "mkdir",
        "mkdirSync",
        "rm",
        "rmSync",
        "rmdir",
        "rmdirSync",
        "unlink",
        "unlinkSync",
        "createWriteStream",
        "chmod",
        "chmodSync",
        "chown",
        "chownSync",
        "cp",
        "cpSync",
        "link",
        "linkSync",
        "symlink",
        "symlinkSync",
    )
    for kind, operations, values in (
        ("filesystem.read", read_ops, reads),
        ("filesystem.write", write_ops, writes),
    ):
        local_operations = set(operations)
        local_operations.update(
            local
            for local, qualified in aliases.items()
            if qualified.startswith("node:fs")
            and qualified.rsplit(".", 1)[-1] in operations
        )
        pattern = re.compile(
            rf"\b(?:\w+\.)*(?:{'|'.join(sorted(map(re.escape, local_operations)))})"
            r"\s*\(\s*([^,\n)]+)"
        )
        for match in pattern.finditer(body):
            values.add(_string_literal(match.group(1)) or "<dynamic>")
            offsets[kind] = match.start()
    for match in re.finditer(
        r"\b(?:open|openSync)\s*\(\s*([^,\n)]+),\s*([^,\n)]+)", body
    ):
        path = _string_literal(match.group(1)) or "<dynamic>"
        flags = _string_literal(match.group(2))
        kind = (
            "filesystem.write"
            if flags is None or any(token in flags for token in ("w", "a", "x", "+"))
            else "filesystem.read"
        )
        (writes if kind.endswith("write") else reads).add(path)
        offsets[kind] = match.start()
    for match in re.finditer(r"(?<!\.)\bfetch\s*\(\s*([^,\n)]+)", body):
        value = _string_literal(match.group(1))
        hosts.add(urlparse(value).netloc or value if value else "<dynamic>")
        offsets["network"] = match.start()
    return reads, writes, hosts, offsets


def _sent002(
    context: StaticContext, state: RuleRunState, tools: tuple[TypeScriptTool, ...]
) -> None:
    from sentinel.static.typescript_execution import detect

    detect(context, state, tools)


def _sent003(
    context: StaticContext, state: RuleRunState, tools: tuple[TypeScriptTool, ...]
) -> None:
    from sentinel.static.typescript_safety import validation

    validation(context, state, tools)


def _sent004(context: StaticContext, state: RuleRunState) -> None:
    from sentinel.static.typescript_safety import prompt

    prompt(context, state)


def _sent006(context: StaticContext, state: RuleRunState) -> None:
    from sentinel.static.typescript_safety import authentication

    authentication(context, state)


def _sent007(context: StaticContext, state: RuleRunState) -> None:
    from sentinel.static.typescript_safety import integrity

    integrity(context, state)


def _functions(source: str) -> dict[str, tuple[str, tuple[str, ...], str, int, int]]:
    found: dict[str, tuple[str, tuple[str, ...], str, int, int]] = {}
    patterns = (
        re.compile(
            rf"(?:export\s+)?(?:async\s+)?function\s+(?P<name>{_IDENTIFIER})\s*\((?P<params>[^)]*)\)[^{{;]*{{"
        ),
        re.compile(
            rf"(?:export\s+)?const\s+(?P<name>{_IDENTIFIER})\s*=\s*(?:async\s*)?\((?P<params>[^)]*)\)\s*(?::[^=]+)?=>\s*{{"
        ),
        re.compile(
            rf"(?:export\s+)?const\s+(?P<name>{_IDENTIFIER})\s*=\s*(?:async\s*)?(?P<params>{_IDENTIFIER})\s*=>\s*{{"
        ),
    )
    for pattern in patterns:
        for match in pattern.finditer(source):
            open_brace = match.end() - 1
            close = _matching(source, open_brace, "{", "}")
            if close is None:
                continue
            params = _parameter_names(match.group("params"))
            found.setdefault(
                match.group("name"),
                (
                    match.group("name"),
                    params,
                    source[open_brace + 1 : close],
                    open_brace + 1,
                    close,
                ),
            )
    expression_pattern = re.compile(
        rf"(?:export\s+)?const\s+(?P<name>{_IDENTIFIER})\s*=\s*"
        rf"(?:async\s*)?(?:\((?P<many>[^)]*)\)|(?P<one>{_IDENTIFIER}))\s*=>\s*"
        r"(?P<body>(?!{)[^;]+);"
    )
    for match in expression_pattern.finditer(source):
        params = _parameter_names(match.group("many") or match.group("one") or "")
        found.setdefault(
            match.group("name"),
            (
                match.group("name"),
                params,
                match.group("body"),
                match.start("body"),
                match.end("body"),
            ),
        )
    return found


def _resolve_handler(
    expression: str,
    source: str,
    functions: dict[str, tuple[str, tuple[str, ...], str, int, int]],
) -> tuple[str, tuple[str, ...], int]:
    expression = expression.strip()
    if expression in functions:
        _, params, body, start, _ = functions[expression]
        return body, params, start
    arrow = re.search(
        rf"(?:async\s*)?(?:\((?P<many>[^)]*)\)|(?P<one>{_IDENTIFIER}))\s*=>", expression
    )
    function = re.search(r"(?:async\s*)?function\s*\((?P<many>[^)]*)\)", expression)
    signature = arrow or function
    if signature is None:
        return "", (), 0
    params = _parameter_names(
        signature.groupdict().get("many") or signature.groupdict().get("one") or ""
    )
    brace = expression.find("{", signature.end())
    if brace < 0:
        body = expression[signature.end() :]
        return body, params, source.find(expression) + signature.end()
    close = _matching(expression, brace, "{", "}")
    body = expression[brace + 1 : close if close is not None else len(expression)]
    expression_start = source.find(expression)
    return body, params, max(0, expression_start) + brace + 1


def _parameter_names(raw: str) -> tuple[str, ...]:
    raw = raw.strip()
    if raw.startswith("{") and "}" in raw:
        raw = raw[1 : raw.index("}")]
    names: list[str] = []
    for part in _split_top_level(raw):
        name = part.split(":", 1)[0].split("=", 1)[0].strip()
        if re.fullmatch(_IDENTIFIER, name):
            names.append(name)
    return tuple(names)


def _literal_constants(source: str) -> dict[str, str]:
    return {
        match.group("name"): match.group("value")
        for match in re.finditer(
            rf"\bconst\s+(?P<name>{_IDENTIFIER})\s*=\s*['\"](?P<value>[^'\"\n]*)['\"]\s*;?",
            source,
        )
    }


def _import_aliases(source: str) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for match in re.finditer(
        rf"import\s+(?P<name>{_IDENTIFIER})\s+from\s*"
        r"['\"](?P<module>[^'\"]+)['\"]",
        source,
    ):
        aliases[match.group("name")] = match.group("module").replace("/", ".")
    for match in re.finditer(
        r"import\s*{([^}]+)}\s*from\s*['\"]([^'\"]+)['\"]", source
    ):
        module = match.group(2).removeprefix("./").replace("/", ".")
        for item in match.group(1).split(","):
            parts = re.split(r"\s+as\s+", item.strip())
            aliases[parts[-1]] = f"{module}.{parts[0]}"
    for match in re.finditer(
        r"(?:const|let|var)\s*{([^}]+)}\s*=\s*require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
        source,
    ):
        module = match.group(2).removeprefix("./").replace("/", ".")
        for item in match.group(1).split(","):
            parts = [part.strip() for part in item.split(":", 1)]
            aliases[parts[-1]] = f"{module}.{parts[0]}"
    for match in re.finditer(
        rf"(?:import\s*\*\s*as|(?:const|let|var))\s+(?P<name>{_IDENTIFIER})"
        r"\s*(?:from|=\s*require\s*\()\s*['\"](?P<module>[^'\"]+)['\"]\s*\)?",
        source,
    ):
        aliases[match.group("name")] = match.group("module").replace("/", ".")
    changed = True
    while changed:
        changed = False
        for match in re.finditer(
            rf"\b(?:const|let|var)\s+(?P<name>{_IDENTIFIER})\s*=\s*"
            rf"(?P<value>{_IDENTIFIER}(?:\.{_IDENTIFIER})*)\s*;",
            source,
        ):
            value = aliases.get(match.group("value"))
            if value is not None and aliases.get(match.group("name")) != value:
                aliases[match.group("name")] = value
                changed = True
    return aliases


def _mcp_server_receivers(source: str) -> set[str]:
    aliases = _import_aliases(source)
    classes = {"McpServer"}
    classes.update(
        local
        for local, qualified in aliases.items()
        if qualified.startswith("@modelcontextprotocol.")
        and qualified.endswith(".McpServer")
    )
    modules = {
        local
        for local, qualified in aliases.items()
        if qualified.startswith("@modelcontextprotocol.")
        and not qualified.endswith(".McpServer")
    }
    class_pattern = "|".join(map(re.escape, sorted(classes)))
    module_pattern = "|".join(map(re.escape, sorted(modules)))
    constructors = class_pattern
    if module_pattern:
        constructors += rf"|(?:{module_pattern})\.McpServer"
    receivers = {
        match.group("name")
        for match in re.finditer(
            rf"\b(?:const|let|var)\s+(?P<name>{_IDENTIFIER})\s*=\s*"
            rf"new\s+(?:{constructors})\s*\(",
            source,
        )
    }
    receivers.update(
        match.group("name")
        for match in re.finditer(
            rf"\b(?P<name>{_IDENTIFIER})\s*:\s*(?:{constructors})\b", source
        )
    )
    _expand_receiver_aliases(source, receivers)
    return receivers


def _http_receivers(source: str) -> set[str]:
    aliases = _import_aliases(source)
    express_factories: set[str] = set()
    hono_classes: set[str] = set()
    express_factories.update(
        local for local, qualified in aliases.items() if qualified == "express"
    )
    hono_classes.update(
        local for local, qualified in aliases.items() if qualified == "hono.Hono"
    )
    express_pattern = "|".join(map(re.escape, sorted(express_factories))) or r"(?!)"
    hono_pattern = "|".join(map(re.escape, sorted(hono_classes))) or r"(?!)"
    receivers = {
        match.group("name")
        for match in re.finditer(
            rf"\b(?:const|let|var)\s+(?P<name>{_IDENTIFIER})\s*=\s*"
            rf"(?:(?:{express_pattern})\s*\(|(?:{express_pattern})\.Router\s*\(|"
            rf"new\s+(?:{hono_pattern})\s*\()",
            source,
        )
    }
    _expand_receiver_aliases(source, receivers)
    return receivers


def _expand_receiver_aliases(source: str, receivers: set[str]) -> None:
    changed = True
    while changed:
        changed = False
        for match in re.finditer(
            rf"\b(?:const|let|var)\s+(?P<name>{_IDENTIFIER})\s*=\s*"
            rf"(?P<value>{_IDENTIFIER})\s*;",
            source,
        ):
            if (
                match.group("value") in receivers
                and match.group("name") not in receivers
            ):
                receivers.add(match.group("name"))
                changed = True


def _constant_expressions(source: str) -> dict[str, str]:
    expressions: dict[str, str] = {}
    pattern = re.compile(rf"\bconst\s+(?P<name>{_IDENTIFIER})\s*=")
    for match in pattern.finditer(source):
        start = match.end()
        parts = _split_top_level(source[start:])
        if not parts:
            continue
        value = parts[0].split(";", 1)[0].strip()
        if value:
            expressions[match.group("name")] = value
    return expressions


def _zod_object_schema(
    expression: str, constants: dict[str, str]
) -> dict[str, Any] | None:
    expression = expression.strip()
    expression = constants.get(expression, expression)
    object_match = re.search(r"(?:\bz\.)?object\s*\(\s*{", expression)
    if object_match:
        open_brace = expression.find("{", object_match.start())
    elif expression.startswith("{"):
        open_brace = 0
    else:
        reference = re.fullmatch(r"\s*z\.object\s*\(\s*(\w+)\s*\)\s*", expression)
        if reference and reference.group(1) in constants:
            return _zod_object_schema(constants[reference.group(1)], constants)
        return None
    close = _matching(expression, open_brace, "{", "}")
    if close is None:
        return None
    properties: dict[str, Any] = {}
    required: list[str] = []
    for item in _split_top_level(expression[open_brace + 1 : close]):
        if ":" not in item:
            return None
        raw_name, value = item.split(":", 1)
        name = raw_name.strip().strip("'\"")
        if not re.fullmatch(_IDENTIFIER, name):
            return None
        schema = _zod_type(value.strip(), constants)
        if schema is None:
            return None
        properties[name] = schema
        if not re.search(r"\.(?:optional|default)\s*\(", value):
            required.append(name)
    result: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        result["required"] = required
    return result


def _zod_type(value: str, constants: dict[str, str]) -> dict[str, Any] | None:
    array = re.search(r"\bz\.array\s*\((.*)\)", value, re.DOTALL)
    if array:
        item = _zod_type(array.group(1), constants)
        return {"type": "array", "items": item} if item else None
    nested = _zod_object_schema(value, constants)
    if nested:
        return nested
    for name, json_type in (
        ("string", "string"),
        ("number", "number"),
        ("boolean", "boolean"),
    ):
        if re.search(rf"\bz\.{name}\s*\(", value):
            return {"type": json_type}
    return None


def _object_literal(expression: str, key: str, constants: dict[str, str]) -> str | None:
    literal = re.search(
        rf"(?:['\"]{re.escape(key)}['\"]|\b{re.escape(key)}\b)\s*:\s*"
        r"(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
        expression,
        re.DOTALL,
    )
    if literal:
        return literal.group("value")
    value = _object_expression(expression, key)
    return _literal_or_constant(value, constants) if value else None


def _object_expression(expression: str, key: str) -> str | None:
    match = re.search(
        rf"(?:['\"]{re.escape(key)}['\"]|\b{re.escape(key)}\b)\s*:\s*", expression
    )
    if not match:
        return None
    tail = expression[match.end() :]
    stripped = tail.lstrip()
    if not stripped:
        return None
    if stripped[0] in "{[(":
        closing = {"{": "}", "[": "]", "(": ")"}[stripped[0]]
        end = _matching(stripped, 0, stripped[0], closing)
        return stripped[: end + 1] if end is not None else None
    call = stripped.find("(")
    if call >= 0:
        end = _matching(stripped, call, "(", ")")
        return stripped[: end + 1] if end is not None else None
    identifier = re.match(_IDENTIFIER, stripped)
    return identifier.group(0) if identifier else None


def _literal_or_constant(expression: str, constants: dict[str, str]) -> str | None:
    return _string_literal(expression) or constants.get(expression.strip())


def _string_literal(expression: str) -> str | None:
    match = re.fullmatch(r"\s*(['\"])(.*?)\1\s*", expression, re.DOTALL)
    return match.group(2) if match else None


def _split_top_level(text: str) -> tuple[str, ...]:
    parts: list[str] = []
    start = 0
    stack: list[str] = []
    quote: str | None = None
    escaped = False
    pairs = {")": "(", "]": "[", "}": "{"}
    for index, character in enumerate(text):
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in "'\"`":
            quote = character
        elif character in "([{":
            stack.append(character)
        elif character in pairs and stack and stack[-1] == pairs[character]:
            stack.pop()
        elif character == "," and not stack:
            parts.append(text[start:index].strip())
            start = index + 1
    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return tuple(parts)


def _matching(text: str, start: int, opening: str, closing: str) -> int | None:
    depth = 0
    quote: str | None = None
    escaped = False
    index = start
    while index < len(text):
        character = text[index]
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
        elif character in "'\"`":
            quote = character
        elif text.startswith("//", index):
            newline = text.find("\n", index + 2)
            index = len(text) if newline < 0 else newline
            continue
        elif text.startswith("/*", index):
            end = text.find("*/", index + 2)
            index = len(text) if end < 0 else end + 2
            continue
        elif character == opening:
            depth += 1
        elif character == closing:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def _broader(declared: tuple[str, ...], actual: set[str]) -> bool:
    if "<dynamic>" in actual:
        return bool(declared)
    if declared and not actual:
        return True
    return bool(actual) and not set(declared).issubset(actual)


def _contains_name(text: str, names: set[str]) -> bool:
    return any(re.search(rf"\b{re.escape(name)}\b", text) for name in names)


def _is_public(method: str, route: str, configured: tuple[str, ...]) -> bool:
    for item in configured:
        expected, pattern = item.split(" ", 1)
        if method == expected and GitIgnoreSpec.from_lines(
            [pattern.lstrip("/")]
        ).match_file(route.lstrip("/")):
            return True
    return False


def _line(source: str, offset: int) -> int:
    return source.count("\n", 0, max(0, offset)) + 1


def _tool_match(
    rule_id: str, tool: TypeScriptTool, kind: str, offset: int = 0
) -> StaticMatch:
    line = tool.handler[:offset].count("\n") + tool.start_line
    snippet = (
        tool.handler[offset:].splitlines()[0][:400]
        if tool.handler[offset:]
        else tool.name or "tool"
    )
    return StaticMatch(
        rule_id=rule_id,
        path=tool.path,
        range=SourceRange(
            start_line=line,
            start_column=1,
            end_line=line,
            end_column=max(2, len(snippet) + 1),
        ),
        snippet=snippet,
        match_kinds=(kind,),
    )


def _match_at(
    rule_id: str, file: TypeScriptSourceFile, offset: int, snippet: str, kind: str
) -> StaticMatch:
    line = _line(file.source, offset)
    first = snippet.strip().splitlines()[0][:400]
    return StaticMatch(
        rule_id=rule_id,
        path=file.relative_path,
        range=SourceRange(
            start_line=line,
            start_column=1,
            end_line=line,
            end_column=max(2, len(first) + 1),
        ),
        snippet=first,
        match_kinds=(kind,),
    )


def _warn(state: RuleRunState, *warnings: ReportWarning) -> None:
    existing = {(item.code, item.message) for item in state.warnings}
    state.warnings.extend(
        item for item in warnings if (item.code, item.message) not in existing
    )
