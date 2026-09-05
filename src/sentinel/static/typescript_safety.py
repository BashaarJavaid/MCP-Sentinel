"""Bounded TypeScript checks for consumed values and enforced safety results."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from contextlib import suppress
from dataclasses import dataclass

from sentinel.static.execution import check_deadline
from sentinel.static.model import RuleRunState, StaticContext, TypeScriptSourceFile
from sentinel.static.typescript import (
    _IDENTIFIER,
    TypeScriptTool,
    _functions,
    _import_aliases,
    _literal_constants,
    _match_at,
    _matching,
    _split_top_level,
    _string_literal,
    _tool_match,
    _zod_object_schema,
)
from sentinel.static.typescript_execution import _mask, statement_end


@dataclass(frozen=True)
class Event:
    text: str
    start: int
    kind: str = "statement"
    truth: bool = True


def paths(
    file: TypeScriptSourceFile, start: int, end: int, deadline: float
) -> Iterator[tuple[Event, ...]]:
    source, masked = file.source, _mask(file.source)
    pending: list[tuple[tuple[Event, ...], tuple[tuple[int, int], ...]]] = [
        ((), ((start, end),))
    ]

    def block(index: int, limit: int) -> tuple[int, int, int]:
        while index < limit and masked[index].isspace():
            index += 1
        if index < limit and masked[index] == "{":
            close = _matching(source, index, "{", "}")
            if close is not None:
                return index + 1, close, close + 1
        close = statement_end(source, masked, index, limit, deadline)
        return index, close, close + 1

    while pending:
        check_deadline(deadline)
        prefix, work = pending.pop()
        if not work:
            yield prefix
            continue
        (index, limit), *rest = work
        while index < limit and (masked[index].isspace() or masked[index] == ";"):
            index += 1
        if index >= limit:
            pending.append((prefix, tuple(rest)))
            continue
        conditional = re.match(r"if\s*\(", masked[index:limit])
        if conditional:
            opening = index + conditional.end() - 1
            close = _matching(source, opening, "(", ")")
            if close is not None:
                left_start, left_end, after = block(close + 1, limit)
                otherwise = re.match(r"\s*else\b", masked[after:limit])
                right_start = right_end = after
                if otherwise:
                    right_start, right_end, after = block(
                        after + otherwise.end(), limit
                    )
                for truth, branch in (
                    (True, (left_start, left_end)),
                    (False, (right_start, right_end)),
                ):
                    pending.append(
                        (
                            (
                                *prefix,
                                Event(
                                    source[opening + 1 : close],
                                    opening + 1,
                                    "condition",
                                    truth,
                                ),
                            ),
                            (branch, (after, limit), *rest),
                        )
                    )
                continue
        close = statement_end(source, masked, index, limit, deadline)
        text = source[index:close].strip()
        kind = (
            "return"
            if re.match(r"return\b", text)
            else "throw"
            if re.match(r"throw\b", text)
            else "statement"
        )
        event = Event(text, index, kind)
        if kind in {"return", "throw"}:
            yield (*prefix, event)
        else:
            pending.append(((*prefix, event), ((close + 1, limit), *rest)))


def object_member(expression: str, key: str) -> str | None:
    expression = expression.strip()
    if not expression.startswith("{") or not expression.endswith("}"):
        return None
    fields = _split_top_level(expression[1:-1])
    if any(field.startswith("...") for field in fields):
        return None
    matches = [
        match[1].strip()
        for field in fields
        if (
            match := re.fullmatch(
                rf"(?:{re.escape(key)}|['\"]{re.escape(key)}['\"])\s*:\s*([\s\S]+)",
                field,
            )
        )
    ]
    return matches[0] if len(matches) == 1 else None


def assignment(text: str) -> tuple[str, str] | None:
    match = re.fullmatch(
        rf"(?:(?:const|let|var)\s+)?({_IDENTIFIER})(?:\s*:\s*[^=]+)?\s*=(?!=|>)([\s\S]+)",
        text,
    )
    return (match[1], match[2].strip()) if match else None


def reference(text: str, aliases: dict[str, str]) -> str | None:
    text = re.sub(r"\[\s*['\"]([^'\"]+)['\"]\s*\]", r".\1", text.strip())
    if re.fullmatch(rf"{_IDENTIFIER}(?:\.{_IDENTIFIER})*", text):
        root, separator, tail = text.partition(".")
        return aliases.get(root, root) + separator + tail
    return None


def guard(text: str, truth: bool, aliases: dict[str, str]) -> set[str]:
    text = text.strip()
    if text.startswith("!") and not text.startswith("!="):
        return guard(text[1:].strip(), not truth, aliases)
    match = re.fullmatch(
        rf"typeof\s+({_IDENTIFIER}(?:\.{_IDENTIFIER})*)\s*(===|!==|==|!=)\s*['\"](?:string|number|boolean)['\"]",
        text,
    )
    if match and truth == (match[2] in {"===", "=="}):
        return {reference(match[1], aliases) or match[1]}
    match = re.fullmatch(r"(\[[^\]]+\])\.includes\(([^)]+)\)", text)
    if match and truth:
        members = _split_top_level(match[1][1:-1])
        if members and all(
            _string_literal(member) is not None
            or re.fullmatch(r"-?\d+(?:\.\d+)?", member)
            for member in members
        ):
            ref = reference(match[2], aliases)
            return {ref} if ref else set()
    return set()


def schema_fields(schema: dict[str, object] | None) -> set[str]:
    if not schema or schema.get("type") != "object":
        return set()
    props = schema.get("properties", {})
    required = schema.get("required", [])
    if not isinstance(required, list):
        return set()
    return (
        {
            name
            for name, value in props.items()
            if isinstance(value, dict)
            and value.get("type") in {"string", "number", "integer", "boolean"}
        }
        if isinstance(props, dict)
        else set()
    )


def validation(
    context: StaticContext, state: RuleRunState, tools: tuple[TypeScriptTool, ...]
) -> None:
    for file in context.files.typescript_files:
        source = file.source
        imports = _import_aliases(source)
        schemas: dict[str, set[str]] = {}
        validators: dict[str, set[str]] = {}
        zod = {
            name for name, qualified in imports.items() if qualified in {"zod.z", "zod"}
        }
        for match in re.finditer(
            rf"\b(?:const|let)\s+({_IDENTIFIER})\s*=\s*({_IDENTIFIER})\.object\s*\(",
            source,
        ):
            close = _matching(source, match.end() - 1, "(", ")")
            if close is not None and match[2] in zod:
                schemas[match[1]] = schema_fields(
                    _zod_object_schema(source[match.end() : close], {})
                )
        ajv = {
            name
            for name, qualified in imports.items()
            if qualified in {"ajv", "ajv.default"}
        }
        for match in re.finditer(
            rf"\bconst\s+({_IDENTIFIER})\s*=\s*new\s+({_IDENTIFIER})\(\)\.compile\s*\(",
            source,
        ):
            close = _matching(source, match.end() - 1, "(", ")")
            if close is not None and match[2] in ajv:
                raw = source[match.end() : close]
                raw = re.sub(r"([,{]\s*)([A-Za-z_]\w*)\s*:", r'\1"\2":', raw)
                raw = re.sub(r",\s*([}\]])", r"\1", raw)
                with suppress(ValueError):
                    validators[match[1]] = schema_fields(json.loads(raw))
        helpers: dict[str, tuple[tuple[str, ...], set[str]]] = {}
        for name, params, _, start, end in _functions(source).values():
            outcomes = []
            for path in paths(file, start, end, context.deadline):
                checked: set[str] = set()
                for event in path:
                    if event.kind == "condition":
                        checked.update(guard(event.text, event.truth, {}))
                    elif assignment(event.text):
                        checked.clear()
                if not path or path[-1].kind != "throw":
                    outcomes.append(checked)
            helpers[name] = (params, set.intersection(*outcomes) if outcomes else set())
        for tool in tools:
            if (
                tool.path != file.relative_path
                or tool.name is None
                or not tool.parameters
            ):
                continue
            failed = False
            used = min(
                (
                    m.start()
                    for name in tool.parameters
                    for m in re.finditer(rf"\b{re.escape(name)}\b", tool.handler)
                ),
                default=None,
            )
            if used is None:
                state.exempt("zero_or_unused_input")
                continue
            for path in paths(
                file,
                tool.handler_start,
                tool.handler_start + len(tool.handler),
                context.deadline,
            ):
                aliases = {name: name for name in tool.parameters}
                tracked = set(aliases.values())
                official = schema_fields(tool.input_schema)
                checked = {name for name in tool.parameters if name in official}
                checked.update(
                    f"{name}.{field}" for name in tool.parameters for field in official
                )
                parsed: dict[str, tuple[str, set[str]]] = {}
                succeeded: set[str] = set()

                def consumes(
                    expression: str,
                    aliases: dict[str, str] = aliases,
                    tracked: set[str] = tracked,
                    checked: set[str] = checked,
                ) -> bool:
                    masked = _mask(expression)
                    for match in re.finditer(
                        rf"(?<![\w$.])({_IDENTIFIER}(?:\.{_IDENTIFIER}|\[['\"][^'\"]+['\"]\])*)",
                        expression,
                    ):
                        if masked[match.start()].isspace():
                            continue
                        name = reference(match[1], aliases) or match[1]
                        if any(
                            name == root or name.startswith(root + ".")
                            for root in tracked
                        ) and not any(
                            name == proof or name.startswith(proof + ".")
                            for proof in checked
                        ):
                            return True
                    return False

                for event in path:
                    text = event.text
                    if event.kind == "condition":
                        checked.update(guard(text, event.truth, aliases))
                        positive = text.strip()
                        truth = event.truth
                        if positive.startswith("!"):
                            positive, truth = positive[1:].strip(), not truth
                        if truth:
                            if positive.endswith(".success"):
                                succeeded.add(positive[:-8])
                            call = re.fullmatch(
                                rf"({_IDENTIFIER})\(([^)]+)\)", positive
                            )
                            if call and call[1] in validators:
                                ref = reference(call[2], aliases)
                                checked.update(
                                    f"{ref}.{field}" for field in validators[call[1]]
                                )
                        recognized = (
                            guard(text, True, aliases)
                            or guard(text, False, aliases)
                            or any(
                                re.search(rf"\b{re.escape(name)}\s*\(", text)
                                for name in validators
                            )
                            or any(
                                re.search(rf"\b{re.escape(name)}\.success\b", text)
                                for name in parsed
                            )
                        )
                        if not recognized and consumes(text):
                            failed = True
                        continue
                    if event.kind == "throw":
                        break
                    assigned = assignment(text)
                    if assigned:
                        parsed.pop(assigned[0], None)
                        succeeded.discard(assigned[0])
                    expression = (
                        assigned[1] if assigned else re.sub(r"^return\s+", "", text)
                    )
                    validation = re.fullmatch(
                        rf"({_IDENTIFIER})\.(parse|safeParse)\(([^)]+)\)", expression
                    )
                    if validation and validation[1] in schemas:
                        if assigned:
                            origin = f"@{event.start}"
                            aliases[assigned[0]] = origin
                            tracked.add(origin)
                            if validation[2] == "parse":
                                checked.update(
                                    f"{origin}.{field}"
                                    for field in schemas[validation[1]]
                                )
                            else:
                                parsed[assigned[0]] = (origin, schemas[validation[1]])
                        continue
                    if (
                        assigned
                        and expression.endswith(".data")
                        and expression[:-5] in succeeded
                        and expression[:-5] in parsed
                    ):
                        origin, fields = parsed[expression[:-5]]
                        aliases[assigned[0]] = origin
                        checked.update(f"{origin}.{field}" for field in fields)
                        continue
                    custom = re.fullmatch(rf"({_IDENTIFIER})\(([^)]+)\)", expression)
                    if custom and custom[1] in helpers:
                        params, proofs = helpers[custom[1]]
                        ref = reference(custom[2], aliases)
                        if len(params) == 1 and ref and proofs:
                            checked.update(
                                ref + proof[len(params[0]) :]
                                for proof in proofs
                                if proof == params[0]
                                or proof.startswith(params[0] + ".")
                            )
                            continue
                    ref = reference(expression, aliases)
                    simple_alias = assigned and expression in aliases
                    if not simple_alias and consumes(expression):
                        failed = True
                    changed_field = re.match(
                        rf"({_IDENTIFIER}(?:\.{_IDENTIFIER}|\[['\"][^'\"]+['\"]\])+)\s*=(?!=)",
                        text,
                    )
                    if changed_field:
                        changed = reference(changed_field[1], aliases)
                        if changed:
                            checked.difference_update(
                                proof
                                for proof in tuple(checked)
                                if proof == changed or proof.startswith(changed + ".")
                            )
                    if assigned:
                        if simple_alias and ref:
                            aliases[assigned[0]] = ref
                        elif assigned[0] in aliases:
                            origin = f"@{event.start}"
                            aliases[assigned[0]] = origin
                            tracked.add(origin)
                if failed:
                    break
            if failed:
                state.matches.append(
                    _tool_match("SENT-003", tool, "unchecked-parameter", used)
                )
            else:
                state.exempt("validated_before_use")


def prompt(context: StaticContext, state: RuleRunState) -> None:
    from sentinel.static.typescript import tools_in_file

    configured = set(context.configuration.scanner.rules.sent004.sanitizers)
    for file in context.files.typescript_files:
        imports = _import_aliases(file.source)
        regions = {
            (start, end) for _, _, _, start, end in _functions(file.source).values()
        }
        regions.update(
            (tool.handler_start, tool.handler_start + len(tool.handler))
            for tool in tools_in_file(file)
        )
        for start, end in sorted(regions):
            found = False
            for path in paths(file, start, end, context.deadline):
                tainted: dict[str, bool] = {}

                def value(
                    expression: str,
                    tainted: dict[str, bool] = tainted,
                    imports: dict[str, str] = imports,
                ) -> bool:
                    masked = _mask(expression)
                    for call in reversed(
                        list(
                            re.finditer(
                                rf"\b({_IDENTIFIER}(?:\.{_IDENTIFIER})*)\s*\(", masked
                            )
                        )
                    ):
                        if imports.get(call[1], call[1]) in configured:
                            close = _matching(expression, call.end() - 1, "(", ")")
                            if close is not None:
                                masked = (
                                    masked[: call.start()]
                                    + " " * (close + 1 - call.start())
                                    + masked[close + 1 :]
                                )
                    if re.search(
                        r"\.(?:content|text|description)\b|\b(?:callTool|listTools)\s*\(",
                        masked,
                    ):
                        return True
                    if any(
                        tainted.get(name, False)
                        for name in re.findall(_IDENTIFIER, masked)
                    ):
                        return True
                    return any(
                        value(match[1])
                        for match in re.finditer(r"\$\{([^}]+)\}", expression)
                    )

                for event in path:
                    if event.kind == "condition":
                        continue
                    sink = re.search(
                        r"(?:responses\.create|chat\.completions\.create|requestSampling)\s*\(",
                        _mask(event.text),
                    )
                    if sink and value(event.text[sink.start() :]):
                        state.matches.append(
                            _match_at(
                                "SENT-004",
                                file,
                                event.start + sink.start(),
                                event.text[sink.start() :],
                                "prompt-taint",
                            )
                        )
                        found = True
                        break
                    assigned = assignment(event.text)
                    if assigned:
                        tainted[assigned[0]] = value(assigned[1])
                    else:
                        augmented = re.match(
                            rf"({_IDENTIFIER})\s*\+=([\s\S]+)", event.text
                        )
                        if augmented:
                            tainted[augmented[1]] = tainted.get(
                                augmented[1], False
                            ) or value(augmented[2])
                if found:
                    break


def anchor_constants(source: str) -> dict[str, str]:
    masked = _mask(source)
    depth = 0
    top_level = []
    for index, char in enumerate(masked):
        top_level.append(source[index] if depth == 0 else " ")
        depth += (char in "({[") - (char in ")}]")
    return _literal_constants("".join(top_level))


def trusted(text: str, constants: dict[str, str], *, environment: bool = False) -> bool:
    text = text.strip()
    if _string_literal(text) or constants.get(text):
        return True
    buffer = re.fullmatch(r"Buffer\.from\(([\s\S]+)\)", text)
    if buffer:
        args = _split_top_level(buffer[1])
        return bool(args and trusted(args[0], constants, environment=environment))
    return environment and bool(re.fullmatch(r"process\.env\.[A-Z_][A-Z_0-9]*", text))


def equality(text: str, truth: bool, imports: dict[str, str]) -> tuple[str, str] | None:
    text = text.strip()
    if text.startswith("!") and not text.startswith("!="):
        return equality(
            text[1:].strip().removeprefix("(").removesuffix(")")
            if text.startswith("!(")
            else text[1:].strip(),
            not truth,
            imports,
        )
    call = re.fullmatch(rf"({_IDENTIFIER}(?:\.{_IDENTIFIER})*)\(([\s\S]*)\)", text)
    if (
        truth
        and call
        and imports.get(call[1], call[1])
        in {"node:crypto.timingSafeEqual", "crypto.timingSafeEqual"}
    ):
        args = _split_top_level(call[2])
        return (args[0], args[1]) if len(args) == 2 else None
    match = re.fullmatch(r"([\s\S]+?)\s*(===|!==|==|!=)\s*([\s\S]+)", text)
    if match and truth == (match[2] in {"===", "=="}):
        return match[1].strip(), match[3].strip()
    return None


def authentication(context: StaticContext, state: RuleRunState) -> None:
    from sentinel.static.typescript import _HTTP_METHODS, _http_receivers, _is_public

    for file in context.files.typescript_files:
        source = file.source
        imports, constants = _import_aliases(source), anchor_constants(source)
        functions = _functions(source)
        receivers = _http_receivers(source)
        if not receivers:
            continue

        def verified(
            expression: str,
            imports: dict[str, str] = imports,
            constants: dict[str, str] = constants,
            functions: dict[
                str, tuple[str, tuple[str, ...], str, int, int]
            ] = functions,
            file: TypeScriptSourceFile = file,
        ) -> bool:
            hono = re.fullmatch(rf"({_IDENTIFIER})\(([\s\S]+)\)", expression.strip())
            if hono and imports.get(hono[1]) == "hono.bearer-auth.bearerAuth":
                token = object_member(hono[2], "token")
                return (
                    token is not None
                    and object_member(hono[2], "verifyToken") is None
                    and trusted(token, constants, environment=True)
                )
            function = functions.get(expression.strip())
            if function is None or len(function[1]) < 3:
                return False
            _, params, _, start, end = function
            shadowed = set(params) | set(
                re.findall(
                    rf"\b(?:const|let|var|function)\s+({_IDENTIFIER})",
                    _mask(file.source[start:end]),
                )
            )
            native_imports = {
                name: value for name, value in imports.items() if name not in shadowed
            }
            accepted = False
            for path in paths(file, start, end, context.deadline):
                aliases = {params[0]: "request"}
                anchors_for_path = {
                    name: value
                    for name, value in constants.items()
                    if name not in params
                }
                checked = False
                rejected = False
                for event in path:
                    if event.kind == "condition":
                        # Identity requires the recognized verifier.
                        condition = event.text.lstrip("! ")
                        pair = (
                            equality(event.text, event.truth, native_imports)
                            if re.match(rf"{_IDENTIFIER}\s*\(", condition)
                            else None
                        )
                        if pair:
                            for credential, anchor in (pair, pair[::-1]):
                                credential = re.sub(
                                    r"^Buffer\.from\(([\s\S]+)\)$", r"\1", credential
                                )
                                ref = reference(credential, aliases) or ""
                                if ref.startswith("request.") and trusted(
                                    anchor, anchors_for_path, environment=True
                                ):
                                    checked = True
                        continue
                    if event.kind == "throw":
                        rejected = True
                        break
                    assigned = assignment(event.text)
                    if assigned:
                        anchors_for_path.pop(assigned[0], None)
                        local_anchor = _string_literal(assigned[1])
                        if local_anchor is not None:
                            anchors_for_path[assigned[0]] = local_anchor
                        aliases[assigned[0]] = (
                            reference(assigned[1], aliases) or f"unknown:{event.start}"
                        )
                    if re.search(rf"\b{re.escape(params[2])}\s*\(", event.text):
                        if not checked:
                            return False
                        accepted = True
                    if re.search(
                        rf"\b{re.escape(params[1])}\.status\(\s*(?:401|403)\s*\)\.(?:end|send|json)\s*\(",
                        event.text,
                    ):
                        rejected = True
                    if event.kind == "return" and not rejected and not checked:
                        return False
                if not rejected and not checked:
                    return False
            return accepted

        middlewares = []
        for call in re.finditer(rf"\b({_IDENTIFIER})\.use\s*\(", _mask(source)):
            close = _matching(source, call.end() - 1, "(", ")")
            if close is None:
                continue
            args = _split_top_level(source[call.end() : close])
            pattern = _string_literal(args[0]) if args else None
            handlers = args[1:] if pattern else args
            if any(verified(handler) for handler in handlers):
                middlewares.append((call[1], pattern or "*", call.start()))
        route_pattern = (
            rf"\b({'|'.join(map(re.escape, sorted(receivers)))})\."
            rf"({'|'.join(sorted(_HTTP_METHODS))})\s*\("
        )
        for route in re.finditer(route_pattern, _mask(source)):
            close = _matching(source, route.end() - 1, "(", ")")
            if close is None:
                continue
            args = _split_top_level(source[route.end() : close])
            path = _string_literal(args[0]) if args else None
            if path is None:
                continue
            if _is_public(
                route[2].upper(),
                path,
                context.configuration.scanner.rules.sent006.public_routes,
            ):
                state.exempt("configured_public_route")
            elif any(verified(arg) for arg in args[1:-1]) or any(
                app == route[1]
                and offset < route.start()
                and (
                    pattern == "*"
                    or pattern == path
                    or (pattern.endswith("/*") and path.startswith(pattern[:-1]))
                )
                for app, pattern, offset in middlewares
            ):
                state.exempt("verified_auth")
            else:
                state.matches.append(
                    _match_at(
                        "SENT-006",
                        file,
                        route.start(),
                        source[route.start() : route.end()],
                        "missing-auth",
                    )
                )


def integrity(context: StaticContext, state: RuleRunState) -> None:
    from sentinel.static.rules.sent007 import (
        anchor_content,
        key_algorithm,
        load_integrity_manifest,
    )

    anchors = load_integrity_manifest(context.configuration.scan_root)
    for file in context.files.typescript_files:
        source = file.source
        imports, constants = _import_aliases(source), anchor_constants(source)
        for name, _, _, start, end in _functions(source).values():
            if "manifest" not in name.lower() and name not in {
                "loadTools",
                "registerTools",
            }:
                continue
            loads: dict[int, str] = {}
            unsafe: set[int] = set()
            for path in paths(file, start, end, context.deadline):
                aliases: dict[str, str] = {}
                expressions = {
                    match[1]: match[2].strip()
                    for match in re.finditer(
                        rf"\bconst\s+({_IDENTIFIER})\s*=\s*([^;\n]+)", source[:start]
                    )
                }
                raw_files: dict[str, str] = {}
                digests: dict[str, str] = {}
                signatures: dict[str, str] = {}
                checked: set[str] = set()

                def data(
                    expression: str, aliases: dict[str, str] = aliases
                ) -> str | None:
                    expression = re.sub(r"\.toString\([^)]*\)$", "", expression.strip())
                    if expression.startswith("Buffer.from(") and expression.endswith(
                        ")"
                    ):
                        args = _split_top_level(expression[12:-1])
                        return data(args[0]) if args else None
                    return reference(expression, aliases)

                def digest(
                    expression: str,
                    digests: dict[str, str] = digests,
                    imports: dict[str, str] = imports,
                ) -> str | None:
                    if expression in digests:
                        return digests[expression]
                    match = re.fullmatch(
                        rf"({_IDENTIFIER})\(['\"]sha256['\"]\)\.update\(([\s\S]+)\)\.digest\(['\"]hex['\"]\)",
                        expression,
                    )
                    if match and imports.get(match[1]) in {
                        "node:crypto.createHash",
                        "crypto.createHash",
                    }:
                        return data(match[2])
                    return None

                def signature(
                    expression: str,
                    expressions: dict[str, str] = expressions,
                    imports: dict[str, str] = imports,
                    constants: dict[str, str] = constants,
                    raw_files: dict[str, str] = raw_files,
                ) -> str | None:
                    match = re.fullmatch(rf"({_IDENTIFIER})\(([\s\S]+)\)", expression)
                    if not match or imports.get(match[1]) not in {
                        "node:crypto.verify",
                        "crypto.verify",
                    }:
                        return None
                    args = _split_top_level(match[2])
                    if len(args) != 4 or args[0] not in {
                        "null",
                        '"sha256"',
                        "'sha256'",
                    }:
                        return None
                    key = (
                        object_member(args[2], "key")
                        if args[2].startswith("{")
                        else args[2]
                    )
                    raw = data(args[1])
                    pem: str | bytes | None = (
                        (_string_literal(key) or constants.get(key)) if key else None
                    )
                    if isinstance(pem, str) and "\\" in pem:
                        with suppress(ValueError):
                            pem = json.loads('"' + pem + '"')
                    if pem is None and key:
                        declared = anchor_content(
                            context.configuration.scan_root,
                            anchors,
                            raw_files.get(raw or ""),
                            "public_key",
                        )
                        pem = (
                            declared[1]
                            if declared
                            and file_read(expressions.get(key, key)) == declared[0]
                            else None
                        )
                    algorithm = key_algorithm(pem)
                    signed = expressions.get(args[3], args[3])
                    trusted_signature = trusted(signed, constants)
                    if not trusted_signature:
                        declared = anchor_content(
                            context.configuration.scan_root,
                            anchors,
                            raw_files.get(raw or ""),
                            "signature",
                        )
                        trusted_signature = bool(
                            declared and file_read(signed) == declared[0]
                        )
                    padding = (
                        object_member(args[2], "padding")
                        if args[2].startswith("{")
                        else None
                    )
                    valid_algorithm = (
                        (algorithm == "ed25519" and args[0] == "null")
                        or (
                            algorithm == "ecdsa-sha256"
                            and args[0] in {'"sha256"', "'sha256'"}
                        )
                        or (
                            algorithm == "rsa-pss-sha256"
                            and args[0] in {'"sha256"', "'sha256'"}
                            and padding is not None
                            and imports.get(padding.split(".")[0], "")
                            in {"node:crypto.constants", "crypto.constants"}
                            and padding.endswith(".RSA_PKCS1_PSS_PADDING")
                        )
                    )
                    return raw if trusted_signature and valid_algorithm else None

                def file_read(expression: str) -> str | None:
                    read = re.search(
                        r"(?:readFileSync|readFile)\(\s*(['\"])([^'\"]+)\1", expression
                    )
                    return read[2] if read else None

                for event in path:
                    if event.kind == "condition":
                        pair = equality(event.text, event.truth, imports)
                        if pair:
                            for candidate, anchor in (pair, pair[::-1]):
                                raw = digest(candidate)
                                expected = _string_literal(anchor) or constants.get(
                                    anchor, ""
                                )
                                access = expressions.get(anchor, anchor)
                                sidecar = re.fullmatch(
                                    rf"({_IDENTIFIER})\.manifests\[['\"]([^'\"]+)['\"]\]\.sha256",
                                    access,
                                )
                                if (
                                    sidecar
                                    and anchors
                                    and file_read(expressions.get(sidecar[1], ""))
                                    == "sentinel.integrity.yaml"
                                ):
                                    entry = anchors.manifests.get(sidecar[2])
                                    expected = entry.sha256 or "" if entry else ""
                                if raw and re.fullmatch(r"[0-9a-fA-F]{64}", expected):
                                    checked.add(raw)
                        positive, truth = event.text.strip(), event.truth
                        if positive.startswith("!"):
                            positive, truth = positive[1:].strip(), not truth
                        raw = signatures.get(positive) or signature(positive)
                        if truth and raw:
                            checked.add(raw)
                        continue
                    if event.kind == "throw":
                        break
                    for load in re.finditer(
                        r"\b(?:JSON\.parse|(?:yaml|YAML)\.(?:parse|load))\s*\(",
                        _mask(event.text),
                    ):
                        close = _matching(event.text, load.end() - 1, "(", ")")
                        if close is None:
                            continue
                        argument = event.text[load.end() : close]
                        offset = event.start + load.start()
                        loads[offset] = event.text[
                            load.start() : event.text.find(")", load.end()) + 1
                        ]
                        if data(argument) not in checked:
                            unsafe.add(offset)
                    assigned = assignment(event.text)
                    if assigned:
                        variable, expression = assigned
                        raw_digest, raw_signature = (
                            digest(expression),
                            signature(expression),
                        )
                        aliases[variable] = data(expression) or f"@{event.start}"
                        expressions[variable] = expression
                        filename = file_read(expression)
                        if filename:
                            raw_files[aliases[variable]] = filename
                        digests.pop(variable, None)
                        signatures.pop(variable, None)
                        if raw_digest:
                            digests[variable] = raw_digest
                        if raw_signature:
                            signatures[variable] = raw_signature
                    elif re.match(r"(?:try|for|while|switch)\b", event.text):
                        checked.clear()
            for offset, text in loads.items():
                if offset in unsafe:
                    state.matches.append(
                        _match_at("SENT-007", file, offset, text, "unverified-manifest")
                    )
                else:
                    state.exempt("verified_manifest")
