"""Declared workspace expansion stays inside the scan boundary."""

import time
from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.errors import TargetError
from sentinel.orchestrator import run_scan
from sentinel.report.model import ScanContext, ScanTarget
from sentinel.static.engine import run_static_scan
from sentinel.static.semgrep_adapter import run_semgrep
from sentinel.static.traversal import collect_static_files
from sentinel.workspaces import discover_workspace
from tests.conftest import NOW


@pytest.mark.parametrize(
    "manifest,content",
    [
        (
            "pyproject.toml",
            '[tool.uv.workspace]\nmembers=["packages/*"]\nexclude=["packages/skip"]\n',
        ),
        ("package.json", '{"workspaces":["packages/*","!packages/skip"]}'),
        ("pnpm-workspace.yaml", 'packages:\n  - "packages/*"\n  - "!packages/skip"\n'),
    ],
)
def test_declared_members_and_exclusions(
    tmp_path: Path, manifest: str, content: str
) -> None:
    (tmp_path / manifest).write_text(content)
    for name in ("py", "ts", "skip", "nested/child"):
        directory = tmp_path / "packages" / name
        directory.mkdir(parents=True)
        (directory / "pyproject.toml").write_text('[project]\nname="member"\n')
        (directory / "package.json").write_text('{"name":"member"}')
    workspace = discover_workspace(tmp_path)
    assert workspace is not None
    assert workspace.members == (".", "packages/py", "packages/ts")
    assert any(issue.path == "packages/nested" for issue in workspace.issues)


def test_symlink_missing_and_escaping_members_are_not_read(tmp_path: Path) -> None:
    root, outside = tmp_path / "root", tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "package.json").write_text("deliberately invalid JSON")
    (root / "linked").symlink_to(outside, target_is_directory=True)
    (root / "package.json").write_text('{"workspaces":["linked","missing"]}')
    workspace = discover_workspace(root)
    assert workspace is not None and workspace.members == (".",)
    assert {issue.path for issue in workspace.issues} == {"linked", "missing"}
    (root / "package.json").write_text('{"workspaces":["../outside"]}')
    with pytest.raises(TargetError, match="boundary"):
        discover_workspace(root)


def test_no_workspace_does_not_expand_arbitrary_packages(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name":"single"}')
    assert discover_workspace(tmp_path) is None


@pytest.fixture
def mixed_workspace(tmp_path: Path) -> Path:
    (tmp_path / "package.json").write_text('{"workspaces":["packages/*"]}')
    (tmp_path / "sentinel.toml").write_text('[scanner]\nrules=["SENT-012"]\n')
    py, ts = tmp_path / "packages/py", tmp_path / "packages/ts"
    py.mkdir(parents=True)
    ts.mkdir(parents=True)
    (py / "package.json").write_text('{"name":"python-member"}')
    (py / "pyproject.toml").write_text(
        '[project]\nname="py-member"\ndependencies=["mcp"]\n'
    )
    (py / "server.py").write_text(
        "@mcp.tool()\ndef read(path):\n    return open(path)\n"
    )
    (ts / "package.json").write_text(
        '{"dependencies":{"@modelcontextprotocol/sdk":"^1"}}'
    )
    (ts / "server.ts").write_text(
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import fs from "node:fs/promises";\n'
        'const s = new McpServer({name:"test",version:"1"});\n'
        's.registerTool("read", {inputSchema:{path:z.string()}}, '
        "async ({path}) => fs.readFile(path));\n"
    )
    (ts / "sentinel.toml").write_text('[scanner]\nrules=["SENT-005"]\n')
    return tmp_path


def test_aggregate_scan_uses_root_configuration(mixed_workspace: Path) -> None:
    config = load_configuration(mixed_workspace, environ={}, static_only=True)
    result = run_static_scan(config, uuid4(), timestamp=NOW)
    assert {item.location.path for item in result.findings} == {
        "packages/py/server.py",
        "packages/ts/server.ts",
    }
    assert result.summary.selected_rule_ids == ("SENT-012",)
    assert any(w.code == "workspace_nested_configuration" for w in result.warnings)
    assert load_configuration(
        mixed_workspace / "packages/ts", environ={}, static_only=True
    ).scanner.scanner.rules == ("SENT-005",)


def test_missing_workspace_member_preserves_findings_and_returns_incomplete(
    mixed_workspace: Path,
) -> None:
    (mixed_workspace / "package.json").write_text(
        '{"workspaces":["packages/*","missing"]}'
    )
    config = load_configuration(
        mixed_workspace, environ={}, cli_overrides={"rules_only": True}
    )
    context = ScanContext(
        scan_id=uuid4(), started_at=NOW, target=ScanTarget(display_name="workspace")
    )
    outcome = run_scan(config, context, completed_at=NOW, allow_degraded=False)
    assert outcome.exit_code == 3 and not outcome.report.analysis_complete
    assert len(outcome.report.findings) == 2
    assert any(w.code == "workspace_member_incomplete" for w in outcome.report.warnings)


def test_workspace_dynamic_requires_one_package(mixed_workspace: Path) -> None:
    with pytest.raises(TargetError, match="one Python package"):
        load_configuration(mixed_workspace, environ={})


def test_aggregate_runs_existing_injection_rule_for_both_languages(
    mixed_workspace: Path,
) -> None:
    (mixed_workspace / "sentinel.toml").write_text('[scanner]\nrules=["SENT-002"]\n')
    (mixed_workspace / "packages/py/server.py").write_text(
        "import subprocess\n@mcp.tool()\ndef run(cmd):\n"
        "    return subprocess.run(cmd, shell=True)\n"
    )
    (mixed_workspace / "packages/ts/server.ts").write_text(
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import { execSync } from "node:child_process";\n'
        'const s = new McpServer({name:"test",version:"1"});\n'
        's.registerTool("run", {inputSchema:{cmd:z.string()}}, '
        "async ({cmd}) => execSync(cmd));\n"
    )
    config = load_configuration(mixed_workspace, environ={}, static_only=True)
    files = collect_static_files(
        mixed_workspace, config.scanner.scanner.ignore_paths, config.language
    )
    matches = run_semgrep(
        files, ("SENT-002",), mixed_workspace, deadline=time.monotonic() + 30
    )
    assert {match.path for match in matches["SENT-002"]} == {
        "packages/py/server.py",
        "packages/ts/server.ts",
    }
    result = run_static_scan(config, uuid4(), timestamp=NOW)
    assert {item.location.path for item in result.findings} == {
        "packages/py/server.py",
        "packages/ts/server.ts",
    }
