"""Auditable inline suppression parsing for included source files."""

from __future__ import annotations

import io
import re
import tokenize
from collections.abc import Iterable
from dataclasses import dataclass

from pydantic import ValidationError

from sentinel.errors import ConfigurationError
from sentinel.finding import FileLocation, Finding, FindingStatus, InlineSuppression
from sentinel.report.model import ReportWarning
from sentinel.static.model import StaticFileSet

_DIRECTIVE = re.compile(
    r"sentinel\s*:\s*ignore\s*\[\s*(SENT-\d{3})\s*\]\s+reason\s*=\s*(.*)"
)
_PREFIX = re.compile(r"sentinel\s*:", re.IGNORECASE)
_STATIC_RULES = frozenset(f"SENT-{number:03d}" for number in range(1, 8))


@dataclass(frozen=True)
class _Directive:
    path: str
    directive_line: int
    binding_line: int
    rule_id: str
    reason: str


def apply_inline_suppressions(
    files: StaticFileSet, findings: tuple[Finding, ...]
) -> tuple[tuple[Finding, ...], tuple[ReportWarning, ...]]:
    directives: list[_Directive] = []
    for python_file in files.python_files:
        directives.extend(
            _python_directives(python_file.relative_path, python_file.source)
        )
    for typescript_file in files.typescript_files:
        directives.extend(
            _typescript_directives(
                typescript_file.relative_path, typescript_file.source
            )
        )

    by_binding: dict[tuple[str, int, str], _Directive] = {}
    for directive in directives:
        key = (directive.path, directive.binding_line, directive.rule_id)
        if key in by_binding:
            raise ConfigurationError(
                f"duplicate inline suppression binding at {directive.path}:"
                f"{directive.binding_line} for {directive.rule_id}"
            )
        by_binding[key] = directive

    used: set[tuple[str, int, str]] = set()
    updated: list[Finding] = []
    for finding in findings:
        location = finding.location
        if not isinstance(location, FileLocation):
            updated.append(finding)
            continue
        key = (location.path, location.range.start_line, finding.rule_id)
        matched_directive = by_binding.get(key)
        if matched_directive is None:
            updated.append(finding)
            continue
        used.add(key)
        suppression = InlineSuppression(
            reason=matched_directive.reason,
            path=matched_directive.path,
            line=matched_directive.directive_line,
        )
        updated.append(
            finding.model_copy(
                update={
                    "status": FindingStatus.SUPPRESSED,
                    "suppression": suppression,
                }
            )
        )

    warnings = tuple(
        ReportWarning(
            code="inline_suppression_unused",
            message=(
                f"Unused inline suppression at {item.path}:{item.directive_line} "
                f"for {item.rule_id}: {item.reason}"
            ),
        )
        for item in directives
        if (item.path, item.binding_line, item.rule_id) not in used
    )
    return tuple(updated), warnings


def _python_directives(path: str, source: str) -> tuple[_Directive, ...]:
    comments = (
        (token.start[0], token.start[1], token.string[1:])
        for token in tokenize.generate_tokens(io.StringIO(source).readline)
        if token.type == tokenize.COMMENT
    )
    return _parse_comments(path, source, comments)


def _typescript_directives(path: str, source: str) -> tuple[_Directive, ...]:
    comments: list[tuple[int, int, str]] = []
    line = 1
    column = 0
    index = 0
    state = "code"
    while index < len(source):
        character = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""
        if character == "\n":
            line += 1
            column = 0
            index += 1
            continue
        if state == "block":
            if character == "*" and following == "/":
                state = "code"
                index += 2
                column += 2
            else:
                index += 1
                column += 1
            continue
        if state in {"single", "double", "template"}:
            delimiter = {"single": "'", "double": '"', "template": "`"}[state]
            if character == "\\":
                index += 2
                column += 2
            elif character == delimiter:
                state = "code"
                index += 1
                column += 1
            else:
                index += 1
                column += 1
            continue
        if character == "/" and following == "*":
            state = "block"
            index += 2
            column += 2
        elif character == "/" and following == "/":
            end = source.find("\n", index)
            if end == -1:
                end = len(source)
            comments.append((line, column, source[index + 2 : end]))
            column += end - index
            index = end
        elif character in {"'", '"', "`"}:
            state = {"'": "single", '"': "double", "`": "template"}[character]
            index += 1
            column += 1
        else:
            index += 1
            column += 1
    return _parse_comments(path, source, comments)


def _parse_comments(
    path: str,
    source: str,
    comments: Iterable[tuple[int, int, str]],
) -> tuple[_Directive, ...]:
    lines = source.splitlines()
    directives: list[_Directive] = []
    for line, column, body in comments:
        text = body.strip()
        if _PREFIX.match(text) is None:
            continue
        match = _DIRECTIVE.fullmatch(text)
        if match is None:
            raise ConfigurationError(f"malformed inline suppression at {path}:{line}")
        rule_id, reason = match.groups()
        if rule_id not in _STATIC_RULES:
            raise ConfigurationError(
                f"unsupported inline suppression rule {rule_id} at {path}:{line}"
            )
        reason = reason.strip()
        try:
            InlineSuppression(reason=reason, path=path, line=line)
        except ValidationError as error:
            raise ConfigurationError(
                f"invalid inline suppression reason at {path}:{line}: "
                f"{error.errors()[0]['msg']}"
            ) from error
        standalone = not lines[line - 1][:column].strip()
        directives.append(
            _Directive(path, line, line + 1 if standalone else line, rule_id, reason)
        )
    return tuple(directives)
