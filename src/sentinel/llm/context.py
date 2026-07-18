"""Evidence-centered, line-preserving context construction and sanitization."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path

from sentinel.errors import InfrastructureError
from sentinel.finding import ContractModel, FileLocation, Finding, NonEmptyString

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

    def contains(self, path: str, start_line: int, end_line: int) -> bool:
        return any(
            block.path == path
            and block.start_line <= start_line <= end_line <= block.end_line
            for block in self.blocks
        )


def build_finding_context(root: Path, finding: Finding) -> FindingContext:
    if not isinstance(finding.location, FileLocation):
        evidence_text = sanitize_text(
            json.dumps(
                finding.evidence.model_dump(mode="json"),
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
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=finding.location.path)
    except (OSError, UnicodeDecodeError, SyntaxError) as error:
        raise InfrastructureError(
            f"cannot construct GPT context for {finding.location.path}: {error}"
        ) from error
    lines = source.splitlines()
    target_line = finding.location.range.start_line
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
    finding: Finding, blocks: tuple[ContextBlock, ...]
) -> FindingContext:
    payload = [block.model_dump(mode="json") for block in blocks]
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return FindingContext(
        finding_id=str(finding.finding_id), blocks=blocks, context_hash=digest
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
