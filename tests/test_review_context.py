"""Cross-file review context keeps a total source budget and exact references."""

from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.finding import FileLocation, SourceRange, StaticEvidence
from sentinel.llm.context import build_finding_context
from sentinel.static.engine import _deduplicate, _finding_from_match
from sentinel.static.model import StaticMatch
from tests.conftest import NOW


def match(path: str = "server.py", line: int = 1, **captures: str) -> StaticMatch:
    return StaticMatch(
        "SENT-014",
        path,
        SourceRange(start_line=line, start_column=1, end_line=line, end_column=2),
        "command(value)",
        captures=captures,
    )


def test_shared_sink_dedup_retains_every_caller_location() -> None:
    matches = _deduplicate(
        [
            match(flow_locations='[["first.py", 1], ["sink.py", 3]]'),
            match(flow_locations='[["second.py", 2], ["sink.py", 3]]'),
        ]
    )
    assert len(matches) == 1
    finding = _finding_from_match(matches[0], uuid4(), NOW)
    assert isinstance(finding.evidence, StaticEvidence)
    assert {
        (item.path, item.range.start_line) for item in finding.evidence.flow_locations
    } == {
        ("first.py", 1),
        ("second.py", 2),
        ("sink.py", 3),
    }


def test_base_context_deduplicates_overlapping_helper_lines(tmp_path: Path) -> None:
    source = (
        "def helper(value):\n    return value\n\n"
        "def run(value):\n    return helper(value)\n"
    )
    (tmp_path / "server.py").write_text(source, encoding="utf-8")
    context = build_finding_context(
        tmp_path, _finding_from_match(match(line=5), uuid4(), NOW)
    )
    lines = [
        (b.path, n) for b in context.blocks for n in range(b.start_line, b.end_line + 1)
    ]
    assert len(lines) == len(set(lines))
    assert context.contains("server.py", 5, 5)


def test_context_total_budget_omissions_and_symlinks(tmp_path: Path) -> None:
    import json

    (tmp_path / "server.py").write_text("value = 1\n" * 200, encoding="utf-8")
    (tmp_path / "helper.py").write_text("value = 2\n" * 200, encoding="utf-8")
    (tmp_path / "linked.py").symlink_to(tmp_path / "helper.py")
    anchors = (
        [("server.py", n) for n in range(1, 151)]
        + [("helper.py", n) for n in range(1, 151)]
        + [("linked.py", 1)]
    )
    finding = _finding_from_match(
        match(flow_locations=json.dumps(anchors)), uuid4(), NOW
    )
    context = build_finding_context(tmp_path, finding)
    lines = [
        (b.path, n) for b in context.blocks for n in range(b.start_line, b.end_line + 1)
    ]
    assert len(lines) == len(set(lines)) == 160
    assert context.omitted_flow_locations
    assert not context.contains("linked.py", 1, 1)
    assert (
        FileLocation(
            path="linked.py",
            range=SourceRange(start_line=1, start_column=1, end_line=1, end_column=2),
        )
        in context.omitted_flow_locations
    )
    assert all(
        context.contains(b.path, b.start_line, b.end_line) for b in context.blocks
    )


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_multiline_secret_redaction_preserves_lines(newline: str) -> None:
    from sentinel.llm.context import SECRET_PLACEHOLDER, sanitize_text

    source = (
        "api_token =" + newline + '    "sensitive-token-value"' + newline + "send()"
    )
    redacted = sanitize_text(source)
    assert "sensitive-token-value" not in redacted
    assert SECRET_PLACEHOLDER in redacted
    assert redacted.count(newline) == source.count(newline)
    assert redacted.splitlines()[-1] == "send()"
