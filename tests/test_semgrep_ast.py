"""The installed parser preserves locations without executing TypeScript."""

import time
from pathlib import Path

import pytest

from sentinel.errors import TargetError
from sentinel.static.model import TypeScriptSourceFile
from sentinel.static.semgrep_ast import parse_typescript, source_range


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_semgrep_ast_preserves_typed_callback_and_unicode_source(
    tmp_path: Path,
    newline: str,
) -> None:
    source = (
        "// π is a comment, not syntax\n"
        'import fs from "node:fs/promises";\n'
        "export async function read(path: string): Promise<{ value: string }> {\n"
        '  return { value: await fs.readFile(path, "utf8") };\n'
        "}\n"
        'throw new Error("must never execute");\n'
    )
    path = tmp_path / "server.ts"
    path.write_bytes(source.replace("\n", newline).encode("utf-8"))
    file = TypeScriptSourceFile(path, "server.ts", source)
    tree = parse_typescript(file, deadline=time.monotonic() + 15)
    assert "Pr" in tree
    function = tree["Pr"][1]
    location = source_range(function, file)
    assert (location.start_line, location.end_line) == (3, 5)
    assert source.splitlines()[location.start_line - 1].startswith("export async")
    assert path.read_text(encoding="utf-8") == source


def test_semgrep_ast_rejects_parse_failure(tmp_path: Path) -> None:
    path = tmp_path / "broken.ts"
    path.write_text("function broken(")
    with pytest.raises(TargetError, match="parse"):
        parse_typescript(
            TypeScriptSourceFile(path, "broken.ts", path.read_text()),
            deadline=time.monotonic() + 15,
        )


@pytest.mark.parametrize("remaining", [15.0, 240.0])
def test_typescript_parser_uses_remaining_shared_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, remaining: float
) -> None:
    import subprocess
    from typing import Any

    from sentinel.static import semgrep_ast

    monkeypatch.setattr(time, "monotonic", lambda: 1000.0)
    monkeypatch.setattr(semgrep_ast, "_verify_semgrep_version", lambda: None)
    observed: list[float] = []

    def parse(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        observed.append(kwargs["timeout"])
        return subprocess.CompletedProcess([], 0, '{"Pr": []}', "")

    monkeypatch.setattr(subprocess, "run", parse)
    file = TypeScriptSourceFile(tmp_path / "source.ts", "source.ts", "const x = 1;")
    assert parse_typescript(file, deadline=1000.0 + remaining) == {"Pr": []}
    assert observed == [remaining]
