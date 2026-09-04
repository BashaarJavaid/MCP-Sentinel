"""Inline suppression parser and application tests."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from sentinel.errors import ConfigurationError
from sentinel.finding import FileLocation, Finding, FindingStatus, SourceRange
from sentinel.static.model import ParsedPythonFile, StaticFileSet, TypeScriptSourceFile
from sentinel.static.suppression import apply_inline_suppressions


def _files(source: str, *, typescript: bool = False) -> StaticFileSet:
    python_files: tuple[ParsedPythonFile, ...]
    typescript_files: tuple[TypeScriptSourceFile, ...]
    if typescript:
        python_files = ()
        typescript_files = (
            TypeScriptSourceFile(Path("server.ts"), "server.ts", source),
        )
    else:
        python_files = (
            ParsedPythonFile(Path("server.py"), "server.py", source, ast.parse(source)),
        )
        typescript_files = ()
    return StaticFileSet(
        python_files=python_files,
        typescript_files=typescript_files,
        config_files=(),
        scanned_file_count=1,
        ignored_file_count=0,
        warnings=(),
    )


def _at(sample: Finding, path: str, line: int) -> Finding:
    source_range = SourceRange(
        start_line=line, start_column=1, end_line=line, end_column=2
    )
    return sample.model_copy(
        update={"location": FileLocation(path=path, range=source_range)}
    )


def test_python_preceding_and_trailing_suppressions(sample_finding: Finding) -> None:
    source = """\
# sentinel: ignore[SENT-002] reason=accepted parser boundary
x = 1
y = 2  # sentinel: ignore[SENT-002] reason=legacy compatibility
"""
    findings = (
        _at(sample_finding, "server.py", 2),
        _at(sample_finding, "server.py", 3),
    )
    updated, warnings = apply_inline_suppressions(_files(source), findings)
    assert warnings == ()
    assert all(item.status is FindingStatus.SUPPRESSED for item in updated)
    assert [item.suppression.line for item in updated if item.suppression] == [1, 3]
    assert all(item.review.mode == "not_reviewed" for item in updated)


def test_typescript_ignores_strings_templates_and_blocks(
    sample_finding: Finding,
) -> None:
    source = """\
const a = '// sentinel: ignore[SENT-002] reason=no';
const b = `// sentinel: ignore[SENT-002] reason=no`;
/* // sentinel: ignore[SENT-002] reason=no */
danger(); // sentinel: ignore[SENT-002] reason=audited exception
"""
    finding = _at(sample_finding, "server.ts", 4)
    updated, warnings = apply_inline_suppressions(
        _files(source, typescript=True), (finding,)
    )
    assert warnings == ()
    assert updated[0].suppression is not None
    assert updated[0].suppression.reason == "audited exception"


def test_valid_unused_suppression_warns(sample_finding: Finding) -> None:
    source = "# sentinel: ignore[SENT-005] reason=rotated test credential\nx = 1\n"
    _, warnings = apply_inline_suppressions(
        _files(source), (_at(sample_finding, "server.py", 2),)
    )
    assert len(warnings) == 1
    assert warnings[0].code == "inline_suppression_unused"
    assert "server.py:1" in warnings[0].message


@pytest.mark.parametrize(
    "directive, message",
    (
        ("# Sentinel: ignore[SENT-002] reason=x\n", "malformed"),
        ("# sentinel: ignore[SENT-008] reason=x\n", "unsupported"),
        ("# sentinel: ignore[SENT-002] reason=\n", "reason"),
        ("# sentinel: ignore[sent-002] reason=x\n", "malformed"),
    ),
)
def test_invalid_directives_fail(
    sample_finding: Finding, directive: str, message: str
) -> None:
    with pytest.raises(ConfigurationError, match=message):
        apply_inline_suppressions(_files(directive), (sample_finding,))


def test_duplicate_binding_fails(sample_finding: Finding) -> None:
    source = """\
# sentinel: ignore[SENT-002] reason=first
x = 1  # sentinel: ignore[SENT-002] reason=second
"""
    with pytest.raises(ConfigurationError, match="duplicate"):
        apply_inline_suppressions(
            _files(source), (_at(sample_finding, "server.py", 2),)
        )
