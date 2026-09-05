"""Bounded named-helper flow recognition; never load or execute TypeScript."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from sentinel.finding import SourceRange
from sentinel.static.execution import (
    UNKNOWN,
    Call,
    Sources,
    Summary,
    check_deadline,
    dependency_order,
    emit,
    substitute,
    union,
)
from sentinel.static.model import (
    RuleRunState,
    StaticContext,
    StaticMatch,
    TypeScriptSourceFile,
)
from sentinel.static.typescript import (
    _IDENTIFIER,
    TypeScriptTool,
    _functions,
    _import_aliases,
    _line,
    _match_at,
    _matching,
    _split_top_level,
    _tool_match,
)


def _mask(source: str) -> str:
    """Blank comments and quoted contents without moving any source offsets."""
    pattern = (
        r"//[^\n]*|/\*[\s\S]*?\*/|'(?:\\[\s\S]|[^'\\])*'|"
        r'"(?:\\[\s\S]|[^"\\])*"|`(?:\\[\s\S]|[^`\\])*`'
    )

    def blank(match: re.Match[str]) -> str:
        value = match[0]
        masked = "".join("\n" if c == "\n" else " " for c in value)
        return value[0] + masked[1:-1] + value[-1] if value[0] in "'\"`" else masked

    return re.sub(pattern, blank, source)


def statement_end(
    source: str, masked: str, start: int, end: int, deadline: float
) -> int:
    index = start
    while index < end:
        check_deadline(deadline)
        char = masked[index]
        if char in "'\"`":
            quote_end = masked.find(char, index + 1, end)
            index = quote_end + 1 if quote_end >= 0 else end
        elif char in "([{":
            close = _matching(source, index, char, {"(": ")", "[": "]", "{": "}"}[char])
            if close is None:
                return end
            index = close + 1
        elif char == "\n":
            before = masked[start:index].rstrip()
            after = masked[index + 1 : end].lstrip()
            if before not in {"return", "throw"} and (
                before.endswith(tuple("=+-*/?,.:|&"))
                or after.startswith((".", "(", "[", "+", "&&", "||", "?"))
            ):
                index += 1
                continue
            return index
        elif char == ";":
            return index
        else:
            index += 1
    return end


@dataclass
class _Function:
    parameters: tuple[str, ...]
    arguments: tuple[tuple[tuple[str | None, str], ...], ...]
    start: int
    end: int
    expression: bool
    asynchronous: bool


def _helpers(source: str, masked: str, deadline: float) -> dict[str, _Function]:
    depths = [0]
    for char in masked:
        depths.append(depths[-1] + (char in "({[") - (char in ")}]"))
    found = {}
    # ponytail: per-name scans; index declarations if large files hit the deadline.
    for name, (_, _, _, start, end) in _functions(masked).items():
        check_deadline(deadline)
        declarations = list(
            re.finditer(
                rf"\b(?:function\s+{re.escape(name)}\s*\(|const\s+{re.escape(name)}\s*=)",
                masked,
            )
        )
        if len(declarations) != 1 or depths[declarations[0].start()] != 0:
            continue
        declaration = declarations[0]
        if any(
            not declaration.start() <= match.start() < declaration.end()
            for match in re.finditer(
                rf"(?<![\w$.]){re.escape(name)}\s*=(?!=|>)", masked
            )
        ):
            continue
        header = source[declaration.start() : start]
        signature = re.search(
            rf"(?:function\s+{re.escape(name)}\s*|=\s*(?:async\s*)?)\((?P<params>[^)]*)\)|=\s*(?:async\s*)?(?P<one>{_IDENTIFIER})\s*=>",
            header,
        )
        if signature is None:
            continue
        raw = signature.group("params") or signature.group("one") or ""
        arguments: list[tuple[tuple[str | None, str], ...]] = []
        valid = True
        for arg in _split_top_level(raw):
            members: list[tuple[str | None, str]] = []
            if arg.startswith("{"):
                close = _matching(arg, 0, "{", "}")
                if close is None or "=" in arg or "..." in arg:
                    valid = False
                    break
                for field in _split_top_level(arg[1:close]):
                    match = re.fullmatch(
                        rf"\s*({_IDENTIFIER})(?:\s*:\s*({_IDENTIFIER}))?\s*", field
                    )
                    if match is None:
                        valid = False
                        break
                    members.append((match[1], match[2] or match[1]))
            else:
                match = re.fullmatch(
                    rf"\s*({_IDENTIFIER})(?:\s*:\s*[^=]+)?\s*", arg.split("=", 1)[0]
                )
                if match is None:
                    valid = False
                    break
                members.append((None, match[1]))
            arguments.append(tuple(members))
        if valid:
            found[name] = _Function(
                tuple(local for argument in arguments for _, local in argument),
                tuple(arguments),
                start,
                end,
                source[start - 1] != "{",
                bool(
                    re.search(
                        r"\basync\b", source[max(0, declaration.start() - 6) : start]
                    )
                ),
            )
    return found


def detect(
    context: StaticContext, state: RuleRunState, tools: tuple[TypeScriptTool, ...]
) -> None:
    for file in context.files.typescript_files:
        masked = _mask(file.source)
        functions = _helpers(file.source, masked, context.deadline)
        graph = {
            name: set(re.findall(rf"\b({_IDENTIFIER})\s*\(", masked[fn.start : fn.end]))
            & functions.keys()
            for name, fn in functions.items()
        }
        summaries: dict[str, Summary] = {}
        for name in dependency_order(graph):
            analyzer = _Analyzer(file, masked, functions, summaries, context.deadline)
            summaries[name] = analyzer.analyze(functions[name])
        for tool in tools:
            if (
                tool.path != file.relative_path
                or tool.name is None
                or not tool.parameters
            ):
                continue
            root = _Function(
                tool.parameters,
                (),
                tool.handler_start,
                tool.handler_start + len(tool.handler),
                file.source[tool.handler_start - 1 : tool.handler_start] != "{",
                False,
            )
            analyzer = _Analyzer(
                file, masked, functions, summaries, context.deadline, tool
            )
            emit(
                analyzer.analyze(root),
                summaries,
                state,
                deadline=context.deadline,
                first_direct_only=True,
            )


class _Analyzer:
    def __init__(
        self,
        file: TypeScriptSourceFile,
        masked: str,
        functions: dict[str, _Function],
        summaries: dict[str, Summary],
        deadline: float,
        tool: TypeScriptTool | None = None,
    ) -> None:
        self.file = file
        self.source = file.source
        self.masked = masked
        self.functions = functions
        self.summaries = summaries
        self.deadline = deadline
        self.tool = tool
        self.aliases = _import_aliases(file.source)
        self.summary = Summary(())
        self.shadowed: set[str] = set()

    def analyze(self, function: _Function) -> Summary:
        self.summary = Summary(function.parameters)
        self.summary.lines.update(
            range(
                _line(self.source, function.start), _line(self.source, function.end) + 1
            )
        )
        self.shadowed = set(function.parameters) | set(
            re.findall(
                rf"\b(?:const|let|var|function|class)\s+({_IDENTIFIER})",
                self.masked[function.start : function.end],
            )
        )
        self.shadowed.update(
            re.findall(
                rf"(?<![\w$.])({_IDENTIFIER})\s*(?:\+?=)(?!=|>)",
                self.masked[function.start : function.end],
            )
        )
        env = {name: frozenset({name}) for name in function.parameters}
        if function.expression:
            self.summary.returned = self._expression(function.start, function.end, env)
        else:
            self._statements(function.start, function.end, env)
        return self.summary

    def _site(self, start: int, end: int, *, sink: bool = False) -> StaticMatch:
        if sink and self.tool:
            return _tool_match(
                "SENT-002",
                self.tool,
                "typescript-taint",
                start - self.tool.handler_start,
            )
        site = _match_at(
            "SENT-002", self.file, start, self.source[start:end], "typescript-flow"
        )
        return replace(
            site,
            range=SourceRange(
                start_line=_line(self.source, start),
                start_column=start - self.source.rfind("\n", 0, start),
                end_line=_line(self.source, end),
                end_column=end - self.source.rfind("\n", 0, end),
            ),
        )

    def _end(self, start: int, end: int) -> int:
        return statement_end(self.source, self.masked, start, end, self.deadline)

    def _branch(
        self, start: int, end: int, env: dict[str, Sources]
    ) -> tuple[int, bool]:
        while start < end and self.masked[start].isspace():
            start += 1
        if start < end and self.masked[start] == "{":
            close = _matching(self.source, start, "{", "}")
            if close is not None:
                return close + 1, self._statements(start + 1, close, env)
        close = self._end(start, end)
        return close + 1, self._statements(start, close, env)

    def _statements(self, start: int, end: int, env: dict[str, Sources]) -> bool:
        index = start
        while index < end:
            check_deadline(self.deadline)
            if self.masked[index].isspace() or self.masked[index] == ";":
                index += 1
                continue
            conditional = re.match(r"if\s*\(", self.masked[index:end])
            if conditional:
                opening = index + conditional.end() - 1
                close = _matching(self.source, opening, "(", ")")
                if close is None:
                    self._unsupported(index, end, env)
                    return True
                self._expression(opening + 1, close, env)
                left, right = env.copy(), env.copy()
                index, left_continues = self._branch(close + 1, end, left)
                otherwise = re.match(r"\s*else\b", self.masked[index:end])
                right_continues = True
                if otherwise:
                    index, right_continues = self._branch(
                        index + otherwise.end(), end, right
                    )
                branches = [
                    branch
                    for branch, continues in (
                        (left, left_continues),
                        (right, right_continues),
                    )
                    if continues
                ]
                if not branches:
                    return False
                for name in set().union(*(branch.keys() for branch in branches)):
                    env[name] = union(branch.get(name, UNKNOWN) for branch in branches)
                continue
            close = self._end(index, end)
            text = self.masked[index:close]
            returned = re.match(r"(return|throw)\b", text)
            assignment = re.match(
                rf"(?:(?:const|let|var)\s+)?({_IDENTIFIER})(?:\s*:\s*[^=]+)?\s*(\+?=)(?!=|>)",
                text,
            )
            if returned:
                value = self._expression(index + returned.end(), close, env)
                if returned[1] == "return":
                    self.summary.returned |= value
                return False
            if (
                re.match(r"(?:for|while|do|try|switch|function|class)\b", text)
                or "=>" in text
            ):
                self._unsupported(index, close, env)
            elif assignment:
                value = self._expression(index + assignment.end(), close, env)
                env[assignment[1]] = value | (
                    env.get(assignment[1], UNKNOWN)
                    if assignment[2] == "+="
                    else frozenset()
                )
            else:
                self._expression(index, close, env)
            index = close + 1
        return True

    def _unsupported(self, start: int, end: int, env: dict[str, Sources]) -> Sources:
        sources = union(env.values()) | UNKNOWN
        self.summary.issues.append(
            (self._site(start, end), sources, "unsupported TypeScript flow")
        )
        self.summary.returned |= sources
        for name in env:
            env[name] |= sources
        if (
            self.tool
            and "=>" not in self.masked[start:end]
            and not re.search(r"\b(?:function|class)\b", self.masked[start:end])
        ):
            # Keep direct sinks visible in opaque loops/try blocks.
            self._expression(start, end, env)
        return sources

    def _expression(self, start: int, end: int, env: dict[str, Sources]) -> Sources:
        check_deadline(self.deadline)
        if "=>" in self.masked[start:end] or re.search(
            r"\bfunction\b", self.masked[start:end]
        ):
            return self._unsupported(start, end, env)
        sources: Sources = frozenset()
        index = start
        pattern = re.compile(
            rf"(?<![\w$])({_IDENTIFIER}(?:\s*\.\s*{_IDENTIFIER})*)\s*(\()?"
        )
        while index < end:
            match = pattern.search(self.masked, index, end)
            if match is None:
                break
            name = re.sub(r"\s+", "", match[1])
            if match[2]:
                opening = match.end() - 1
                close = _matching(self.source, opening, "(", ")")
                if close is None or close > end:
                    return sources | self._unsupported(match.start(), end, env)
                sources |= self._call(name, match.start(), opening, close, env)
                index = close + 1
            else:
                root = name.split(".")[0]
                if root not in {"true", "false", "null", "undefined", "await", "new"}:
                    sources |= env.get(root, UNKNOWN)
                index = match.end()
        # Template interpolation is data even though ordinary quoted text is not.
        for template in re.finditer(r"`(?:\\[\s\S]|[^`\\])*`", self.source[start:end]):
            for interpolation in re.finditer(r"\$\{([^}]+)\}", template[0]):
                sources |= union(
                    env.get(name, UNKNOWN)
                    for name in re.findall(_IDENTIFIER, interpolation[1])
                )
        return sources

    def _call(
        self, name: str, start: int, opening: int, close: int, env: dict[str, Sources]
    ) -> Sources:
        raw = self.source[opening + 1 : close]
        parts = _split_top_level(raw)
        arguments = []
        cursor = opening + 1
        for part in parts:
            offset = self.source.find(part, cursor, close)
            arguments.append(
                (
                    offset,
                    offset + len(part),
                    self._expression(offset, offset + len(part), env),
                )
            )
            cursor = offset + len(part)
        sources = union(value for _, _, value in arguments)
        site = self._site(start, close + 1)
        if name in self.functions and name not in self.shadowed:
            function = self.functions[name]
            bindings: dict[str, Sources] = {}
            valid = (
                len(arguments) == len(function.arguments)
                and "..." not in self.masked[opening:close]
            )
            for spec, (arg_start, arg_end, value) in zip(
                function.arguments, arguments, strict=False
            ):
                for key, local in spec:
                    if key is None:
                        bindings[local] = value
                    else:
                        expression = self.source[arg_start:arg_end].strip()
                        fields = (
                            _split_top_level(expression[1:-1])
                            if expression.startswith("{") and expression.endswith("}")
                            else ()
                        )
                        members = [
                            field
                            for field in fields
                            if re.match(rf"{re.escape(key)}\s*(?::|$)", field)
                        ]
                        if len(members) != 1:
                            valid = False
                            continue
                        member = members[0]
                        offset = self.source.find(member, arg_start, arg_end)
                        colon = member.find(":")
                        bindings[local] = self._expression(
                            offset + colon + 1 if colon >= 0 else offset,
                            offset + len(member),
                            env,
                        )
            if function.asynchronous and not re.search(
                r"\bawait\s*$", self.masked[max(0, start - 20) : start]
            ):
                valid = False
            if valid:
                self.summary.calls.append(Call(site, name, bindings))
                if name in self.summaries:
                    returned = substitute(self.summaries[name].returned, bindings)
                    if not returned & UNKNOWN:
                        return returned
                    reason = f"unresolved effects or return flow through {name}"
                else:
                    reason = f"recursive return flow through {name}"
            else:
                reason = f"unresolved argument binding or deferred call to {name}"
        else:
            root, separator, tail = name.partition(".")
            qualified = self.aliases.get(root, root) + (separator + tail)
            resolved = qualified.rsplit(".", 1)[-1]
            recognized = (
                self.tool is not None
                or name in {"eval", "Function"}
                or qualified.startswith(
                    ("node:child_process.", "child_process.", "node:vm.", "vm.")
                )
            )
            if (
                recognized
                and root not in self.shadowed
                and resolved
                in {
                    "eval",
                    "Function",
                    "runInContext",
                    "runInNewContext",
                    "runInThisContext",
                    "exec",
                    "execSync",
                    "execFile",
                    "execFileSync",
                    "spawn",
                    "spawnSync",
                }
            ):
                direct_name = re.search(
                    rf"{_IDENTIFIER}\s*$", self.masked[start:opening]
                )
                sink_start = (
                    start + direct_name.start() if self.tool and direct_name else start
                )
                self.summary.sinks.append(
                    (
                        replace(
                            self._site(sink_start, close + 1, sink=True),
                            captures={"sink_name": name},
                        ),
                        sources,
                    )
                )
                return sources
            if name in {"String", "Number", "Boolean"} and name not in self.shadowed:
                return sources
            sources |= env.get(name.split(".")[0], frozenset())
            reason = f"unresolved call to {name}"
        self.summary.issues.append((site, sources, reason))
        # Unsupported calls may mutate arguments; do not certify constant outputs.
        self.summary.returned |= sources | UNKNOWN
        for variable in env:
            env[variable] |= sources | UNKNOWN
        return sources | UNKNOWN
