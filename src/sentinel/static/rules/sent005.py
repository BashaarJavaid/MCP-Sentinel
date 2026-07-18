"""SENT-005 hardcoded-secret candidate filtering and redaction."""

from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path

from pathspec import GitIgnoreSpec

from sentinel.finding import SourceRange
from sentinel.static.model import RuleRunState, StaticContext, StaticMatch

_KNOWN_SECRET = re.compile(
    r"(?:sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{20,})"
)
_CONTEXTUAL_SECRET = re.compile(
    r"(?i)(?:api[_-]?key|secret|token|password|credential)\s*[:=]\s*"
    r"(?P<quote>['\"]?)(?P<value>[A-Za-z0-9_./+=-]{20,})(?P=quote)"
)


def run(
    context: StaticContext,
    semgrep_candidates: list[StaticMatch],
    state: RuleRunState,
) -> None:
    candidate_paths = {item.path for item in semgrep_candidates}
    path_sources = {
        item.relative_path: item.source for item in context.files.python_files
    }
    for config_path in context.files.config_files:
        relative = config_path.relative_to(context.configuration.scan_root).as_posix()
        if relative in candidate_paths:
            path_sources[relative] = config_path.read_text(encoding="utf-8")

    seen: set[tuple[str, int, int]] = set()
    for path in sorted(candidate_paths):
        source = path_sources.get(path)
        if source is None:
            continue
        for line_number, line in enumerate(source.splitlines(), start=1):
            for match in _candidate_values(line):
                contextual = match.groupdict().get("value")
                value = match.group(0) if contextual is None else contextual
                if not _is_secret(value):
                    continue
                group = 0 if contextual is None else "value"
                start = match.start(group) + 1
                end = match.end(group) + 1
                key = (path, line_number, start)
                if key in seen:
                    continue
                seen.add(key)
                fingerprint = hashlib.sha256(value.encode("utf-8")).hexdigest()
                if _is_allowlisted(context, path, fingerprint):
                    state.exempt("configured_path_and_fingerprint")
                    continue
                if value.startswith("sk-test-") and _is_reserved_test_path(path):
                    state.exempt("reserved_test_token")
                    continue
                redacted = line.replace(value, "<redacted>")
                state.matches.append(
                    StaticMatch(
                        rule_id="SENT-005",
                        path=path,
                        range=SourceRange(
                            start_line=line_number,
                            start_column=start,
                            end_line=line_number,
                            end_column=end,
                        ),
                        snippet=redacted,
                        fingerprint=fingerprint,
                        match_kinds=("secret_signature",),
                    )
                )


def _candidate_values(line: str) -> tuple[re.Match[str], ...]:
    matches = [*_KNOWN_SECRET.finditer(line), *_CONTEXTUAL_SECRET.finditer(line)]
    return tuple(sorted(matches, key=lambda item: (item.start(), item.end())))


def _is_secret(value: str) -> bool:
    if _KNOWN_SECRET.fullmatch(value):
        return True
    if len(value) < 20:
        return False
    counts = {character: value.count(character) for character in set(value)}
    entropy = -sum(
        (count / len(value)) * math.log2(count / len(value))
        for count in counts.values()
    )
    return entropy >= 4.5


def _is_allowlisted(context: StaticContext, path: str, fingerprint: str) -> bool:
    entries = context.configuration.scanner.rules.sent005.allowlist
    for entry in entries:
        spec = GitIgnoreSpec.from_lines([entry.path])
        if spec.match_file(path) and entry.fingerprint == fingerprint:
            return True
    return False


def _is_reserved_test_path(path: str) -> bool:
    normalized = Path(path).as_posix()
    return normalized.startswith(("tests/fixtures/", "demo/"))
