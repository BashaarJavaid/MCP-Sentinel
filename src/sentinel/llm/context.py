"""Evidence-centered, line-preserving context construction and sanitization."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path

from sentinel.config import resolve_within_root
from sentinel.errors import ConfigurationError, InfrastructureError, TargetError
from sentinel.finding import (
    ContractModel,
    DynamicEvidence,
    FileLocation,
    Finding,
    NonEmptyString,
    StaticEvidence,
    proof_identity,
    runtime_evidence,
)

SECRET_PLACEHOLDER = "<SENTINEL_SECRET:REDACTED>"
PATH_PLACEHOLDER = "<SENTINEL_ABSOLUTE_PATH:REDACTED>"
_SECRET_PATTERNS = (
    re.compile(r"\b(?:ghp_|github_pat_|sk-|xox[baprs]-)[A-Za-z0-9_-]{12,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(
        r"(?i)(?:api[_-]?key|secret|token|password)\s*[:=]\s*"
        r"(?:[\"'][^\"'\r\n]{8,}[\"']|[^\s,;]{8,})"
    ),
)
_POSIX_ABSOLUTE = re.compile(
    r"(?<![A-Za-z0-9_.-])/(?:Users|home|var|tmp|private|opt|etc)/[^\s\"'`,;]+"
)
_WINDOWS_ABSOLUTE = re.compile(r"(?i)\b[A-Z]:\\(?:[^\\\s\"']+\\)*[^\\\s\"']+")


class ContextBlock(ContractModel):
    path: NonEmptyString
    start_line: int
    end_line: int
    text: str
    role: str


class FindingContext(ContractModel):
    finding_id: str
    blocks: tuple[ContextBlock, ...]
    context_hash: NonEmptyString
    omitted_flow_locations: tuple[FileLocation, ...] = ()

    def contains(self, path: str, start_line: int, end_line: int) -> bool:
        return any(
            block.path == path
            and block.start_line <= start_line <= end_line <= block.end_line
            for block in self.blocks
        )


def build_finding_context(root: Path, finding: Finding) -> FindingContext:
    context = _base_finding_context(root, finding)
    if not isinstance(finding.evidence, StaticEvidence) or not isinstance(
        finding.location, FileLocation
    ):
        return context
    locations = finding.evidence.flow_locations
    if all(
        context.contains(item.path, item.range.start_line, item.range.end_line)
        for item in locations
    ):
        return context
    anchors = tuple(
        dict.fromkeys(
            (item.path, item.range.start_line)
            for item in (finding.location, *locations)
        )
    )
    sources: dict[str, list[str]] = {}
    selected: dict[str, set[int]] = {}
    for path, line in anchors[:160]:
        if path not in sources:
            try:
                sources[path] = _read_source(root, path).splitlines()
            except InfrastructureError:
                continue
        if 1 <= line <= len(sources[path]):
            selected.setdefault(path, set()).add(line)
    remaining = 160 - sum(map(len, selected.values()))
    for distance in range(1, 41):
        for path, line in anchors[:160]:
            if path not in selected:
                continue
            for nearby in (line - distance, line + distance):
                if (
                    remaining
                    and 1 <= nearby <= len(sources[path])
                    and nearby not in selected[path]
                ):
                    selected[path].add(nearby)
                    remaining -= 1
        if remaining == 0:
            break
    blocks = []
    for path, numbers in selected.items():
        ordered = sorted(numbers)
        start = end = ordered[0]
        for line in (*ordered[1:], -1):
            if line == end + 1:
                end = line
                continue
            role = (
                "primary"
                if path == finding.location.path
                and start <= finding.location.range.start_line <= end
                else "resolved_flow"
            )
            blocks.append(_block(path, sources[path], start, end, role))
            start = end = line
    omitted = tuple(
        item
        for item in locations
        if not any(
            block.path == item.path
            and block.start_line
            <= item.range.start_line
            <= item.range.end_line
            <= block.end_line
            for block in blocks
        )
    )
    return _finish_context(finding, tuple(blocks), omitted=omitted)


def _read_source(root: Path, relative: str) -> str:
    from sentinel.static.traversal import MAX_STATIC_FILE_BYTES

    try:
        path = resolve_within_root(root, relative)
        if not path.is_file() or path.stat().st_size > MAX_STATIC_FILE_BYTES:
            raise InfrastructureError(
                f"GPT source is not a bounded regular file: {relative}"
            )
        return path.read_text(encoding="utf-8")
    except (ConfigurationError, TargetError, OSError, UnicodeDecodeError) as error:
        raise InfrastructureError(
            f"cannot construct GPT context for {relative}: {error}"
        ) from error


def _base_finding_context(root: Path, finding: Finding) -> FindingContext:
    if not isinstance(finding.location, FileLocation):
        evidence_text = sanitize_text(
            json.dumps(
                proof_identity(finding.evidence)
                if isinstance(finding.evidence, DynamicEvidence)
                and finding.evidence.proof is not None
                else finding.evidence.model_dump(mode="json", exclude={"proof"}),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        line_count = max(1, len(evidence_text.splitlines()))
        return _finish_context(
            finding,
            (
                ContextBlock(
                    path=".sentinel/dynamic-evidence.json",
                    start_line=1,
                    end_line=line_count,
                    text=evidence_text,
                    role="dynamic_evidence",
                ),
            ),
        )
    path = root / finding.location.path
    source = _read_source(root, finding.location.path)
    lines = source.splitlines()
    target_line = finding.location.range.start_line
    if path.suffix in {".ts", ".mts", ".cts"}:
        start, end = _centered_window(
            1, max(1, len(lines)), max(1, len(lines)), 80, focus=target_line
        )
        return _finish_context(
            finding,
            (_block(finding.location.path, lines, start, end, "primary"),),
        )
    try:
        tree = ast.parse(source, filename=finding.location.path)
    except SyntaxError as error:
        raise InfrastructureError(
            f"cannot construct GPT context for {finding.location.path}: {error}"
        ) from error
    units = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and node.lineno <= target_line <= (node.end_lineno or node.lineno)
    ]
    primary = min(
        units,
        key=lambda item: (item.end_lineno or item.lineno) - item.lineno,
        default=None,
    )
    if primary is None:
        start, end = _centered_window(target_line, target_line, len(lines), 80)
        calls: set[str] = set()
    else:
        start, end = _centered_window(
            primary.lineno,
            primary.end_lineno or primary.lineno,
            len(lines),
            80,
            focus=target_line,
        )
        calls = {
            call.func.id
            for call in ast.walk(primary)
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
        }
    blocks = [_block(finding.location.path, lines, start, end, "primary")]
    helpers = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in calls
        and not (node.lineno <= target_line <= (node.end_lineno or node.lineno))
    }
    for name in sorted(helpers)[:2]:
        helper = helpers[name]
        helper_start, helper_end = _centered_window(
            helper.lineno,
            helper.end_lineno or helper.lineno,
            len(lines),
            40,
        )
        blocks.append(
            _block(finding.location.path, lines, helper_start, helper_end, "helper")
        )
    if sum(block.end_line - block.start_line + 1 for block in blocks) > 160:
        raise InfrastructureError("GPT context exceeded the 160-line safety limit")
    return _finish_context(finding, tuple(blocks))


def sanitize_text(value: str) -> str:
    """Redact secrets and host paths without adding or removing lines."""

    sanitized = value
    for pattern in _SECRET_PATTERNS:
        sanitized = pattern.sub(SECRET_PLACEHOLDER, sanitized)
    sanitized = _POSIX_ABSOLUTE.sub(PATH_PLACEHOLDER, sanitized)
    sanitized = _WINDOWS_ABSOLUTE.sub(PATH_PLACEHOLDER, sanitized)
    if sanitized.count("\n") != value.count("\n"):
        raise InfrastructureError("unsafe GPT redaction changed line structure")
    verification = sanitized.replace(SECRET_PLACEHOLDER, "")
    if any(pattern.search(verification) for pattern in _SECRET_PATTERNS):
        raise InfrastructureError("unsafe GPT redaction left secret-like content")
    if _POSIX_ABSOLUTE.search(sanitized) or _WINDOWS_ABSOLUTE.search(sanitized):
        raise InfrastructureError("unsafe GPT redaction left an absolute path")
    return sanitized


def _block(
    path: str, lines: list[str], start: int, end: int, role: str
) -> ContextBlock:
    return ContextBlock(
        path=path,
        start_line=start,
        end_line=end,
        text=sanitize_text("\n".join(lines[start - 1 : end])),
        role=role,
    )


def _finish_context(
    finding: Finding,
    blocks: tuple[ContextBlock, ...],
    *,
    omitted: tuple[FileLocation, ...] = (),
) -> FindingContext:
    if isinstance(finding.location, FileLocation) and runtime_evidence(finding):
        text = sanitize_text(
            json.dumps(
                [proof_identity(item) for item in runtime_evidence(finding)],
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        blocks = (
            *blocks,
            ContextBlock(
                path=".sentinel/dynamic-evidence.json",
                start_line=1,
                end_line=len(text.splitlines()),
                text=text,
                role="dynamic_evidence",
            ),
        )
    payload = [block.model_dump(mode="json") for block in blocks]
    if omitted:
        payload.append(
            {
                "omitted_flow_locations": [
                    item.model_dump(mode="json") for item in omitted
                ]
            }
        )
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return FindingContext(
        finding_id=str(finding.finding_id),
        blocks=blocks,
        context_hash=digest,
        omitted_flow_locations=omitted,
    )


def _centered_window(
    unit_start: int,
    unit_end: int,
    line_count: int,
    limit: int,
    *,
    focus: int | None = None,
) -> tuple[int, int]:
    if unit_end - unit_start + 1 <= limit:
        return unit_start, unit_end
    center = focus if focus is not None else unit_start
    start = max(unit_start, center - limit // 2)
    end = min(unit_end, start + limit - 1)
    start = max(unit_start, end - limit + 1)
    return start, end
