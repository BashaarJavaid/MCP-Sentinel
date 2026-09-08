"""Caller references must not become Git options through their argument position."""

import time
from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.static.engine import run_static_scan
from sentinel.static.model import RuleRunState, TypeScriptSourceFile
from sentinel.static.rules.sent014 import TypeScriptOptionFlow
from sentinel.static.typescript_discovery import TypeScriptProgram
from sentinel.static.typescript_path_flow import analyze
from tests.conftest import NOW, make_target


def test_no_command_sinks_does_not_interpret_service_construction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sentinel.static.path_flow import PathFlow

    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from mcp.server.fastmcp import FastMCP\n"
        "mcp = FastMCP('test')\n"
        "@mcp.tool()\ndef fetch(value: str):\n"
        "    return Service(value).fetch()\n",
        encoding="utf-8",
    )

    def unexpected(*args: object, **kwargs: object) -> None:
        pytest.fail("command analysis interpreted an input with no supported sinks")

    monkeypatch.setattr(PathFlow, "function", unexpected)
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-014"]}
    )
    result = run_static_scan(config, uuid4(), timestamp=NOW)
    assert not result.incomplete
    assert not result.findings


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (
            'state = {"ref": ref}\n'
            '    if ref.startswith("-"): raise ValueError()\n'
            '    return repo.git.diff(state["ref"])',
            0,
        ),
        (
            'state = {"ref": ref}\n'
            '    if ref.startswith("-"): raise ValueError()\n'
            '    state["ref"] = other\n'
            '    return repo.git.diff(state["ref"])',
            1,
        ),
        ("return repo.git.diff(ref)", 1),
        ('return repo.git.checkout(ref, "--")', 1),
        ("return repo.git.show(ref)", 1),
        ('return repo.git.diff("--", ref)', 0),
        ('return repo.git.diff("--end-of-options", ref)', 0),
        (
            'if ref.startswith("-"): raise ValueError()\n    return repo.git.diff(ref)',
            0,
        ),
        ('ref.startswith("-")\n    return repo.git.diff(ref)', 1),
        (
            'if other.startswith("-"): raise ValueError()\n    '
            "return repo.git.diff(ref)",
            1,
        ),
        (
            'if ref.startswith("-"): raise ValueError()\n    ref = '
            "other\n    return repo.git.diff(ref)",
            1,
        ),
        ('return repo.git.diff(f"--unified={ref}")', 0),
        ('return repo.git.diff("HEAD")', 0),
        ("return repo.commit(ref)", 0),
    ],
)
def test_python_git_reference_option_position(
    tmp_path: Path, body: str, expected: int
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        'from mcp.server.fastmcp import FastMCP\nimport git\nmcp=FastMCP("test")\n'
        '@mcp.tool()\ndef diff(ref:str, other:str=""):\n'
        '    repo=git.Repo("/workspace")\n    ' + body + "\n",
        encoding="utf-8",
    )
    configuration = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-014"]}
    )
    result = run_static_scan(configuration, uuid4(), timestamp=NOW)
    assert len(result.findings) == expected
    assert all(f.rule_id == "SENT-014" for f in result.findings)


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ('return cp.execFileSync("git", ["show", ref]);', 1),
        ('return cp.spawnSync("git", ["diff", "--", ref]);', 0),
        ('return cp.spawnSync("git", ["diff", ref, "--"]);', 1),
        (
            'if (ref.startsWith("-")) throw new Error(); return '
            'cp.execFileSync("git", ["show", ref]);',
            0,
        ),
        ('ref.startsWith("-"); return cp.execFileSync("git", ["show", ref]);', 1),
        (
            'if (other.startsWith("-")) throw new Error(); return '
            'cp.execFileSync("git", ["show", ref]);',
            1,
        ),
        (
            'if (ref.startsWith("-")) throw new Error(); ref = '
            'other; return cp.execFileSync("git", ["show", ref]);',
            1,
        ),
        (
            "const args = {ref, other}; "
            'if (args.ref.startsWith("-")) throw new Error(); '
            'return cp.execFileSync("git", ["show", args.ref]);',
            0,
        ),
        (
            "const args = {ref, other}; "
            'if (args.other.startsWith("-")) throw new Error(); '
            'return cp.execFileSync("git", ["show", args.ref]);',
            1,
        ),
        (
            "const args = {ref, other}; "
            'if (args.ref.startsWith("-")) throw new Error(); '
            'args.ref = other; return cp.execFileSync("git", ["show", args.ref]);',
            1,
        ),
        ("const repo = simpleGit(); return repo.diff([ref]);", 1),
        ('const repo = simpleGit(); return repo.diff(["--", ref]);', 0),
    ],
)
def test_typescript_git_option_positions(
    tmp_path: Path, body: str, expected: int
) -> None:
    source = (
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import cp from "node:child_process"; import '
        '{simpleGit} from "simple-git";\n'
        'const server = new McpServer({name:"test", version:"1"});\n'
        f"function run({{ref, other}}: {{ref: string, other: string}}) {{ {body} }}\n"
        'server.registerTool("run", {inputSchema: '
        "{ref:z.string(),other:z.string()}}, run);\n"
    )
    path = tmp_path / "server.ts"
    path.write_text(source, encoding="utf-8")
    program = TypeScriptProgram(
        (TypeScriptSourceFile(path, path.name, source),), deadline=time.monotonic() + 15
    )
    state = RuleRunState()
    analyze(program, state, flow=TypeScriptOptionFlow(program, state))
    assert len(state.matches) == expected
    assert all(m.rule_id == "SENT-014" for m in state.matches)


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ('args = ["git", "show", ref]\n    return subprocess.run(args)', 1),
        ('args = ["git", "show", "--", ref]\n    return subprocess.run(args)', 0),
        ('args = ["git", "show", ref, "--"]\n    return subprocess.run(args)', 1),
        (
            'args = ["git", "show"]\n    args.append(ref)\n    return '
            "subprocess.run(args)",
            1,
        ),
        (
            'args = ["git", "show"]\n    args.extend(["--", ref])\n   '
            " return subprocess.run(args)",
            0,
        ),
        (
            'args = ["git", "show", "--"]\n    args.insert(2, ref)\n  '
            "  return subprocess.run(args)",
            1,
        ),
        (
            'args = ["dbt", "run", "--select"]\n    tokens = '
            "ref.split()\n    args.extend(tokens)\n    return "
            "subprocess.Popen(args=args)",
            1,
        ),
        (
            'args = ["dbt", "run", "--select"]\n    tokens = '
            'ref.split()\n    if any(t.startswith("-") for t in '
            "tokens): raise ValueError()\n    args.extend(tokens)\n   "
            " return subprocess.Popen(args=args)",
            0,
        ),
        (
            'args = ["dbt", "run", "--select"]\n    tokens = '
            'ref.split()\n    any(t.startswith("-") for t in '
            "tokens)\n    args.extend(tokens)\n    return "
            "subprocess.Popen(args=args)",
            1,
        ),
        (
            'args = ["dbt", "run", "--select"]\n    tokens = '
            'ref.split()\n    if any(t.startswith("-") for t in '
            "other.split()): raise ValueError()\n    "
            "args.extend(tokens)\n    return "
            "subprocess.Popen(args=args)",
            1,
        ),
        (
            'args = ["git", "show"]\n    if ref.startswith("-"): '
            "raise ValueError()\n    args.append(ref)\n    return "
            "subprocess.run(args)",
            0,
        ),
        (
            'args = ["git", "show"]\n    if ref.startswith("-"): '
            "raise ValueError()\n    ref = other\n    "
            "args.append(ref)\n    return subprocess.run(args)",
            1,
        ),
        (
            'args = ["git", "show", "--"]\n    copy = args.copy()\n    '
            "copy.insert(2, ref)\n    return subprocess.run(args)",
            0,
        ),
        (
            'args = ["git", "show", "--"]\n    alias = args\n    '
            "alias.insert(2, ref)\n    return subprocess.run(args)",
            1,
        ),
        (
            'args = ["git", "show", "--"]\n    separate = ["git", '
            '"show", "--"]\n    '
            "separate.insert(2, ref)\n    return subprocess.run(args)",
            0,
        ),
        ("command = repo.git\n    return command.show(ref)", 1),
        ('return repo.git.unknown_command("--", ref)', 1),
    ],
)
def test_python_mutable_argv(tmp_path: Path, body: str, expected: int) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from mcp.server.fastmcp import FastMCP\nimport subprocess\nimport git\n"
        'mcp=FastMCP("test")\n@mcp.tool()\ndef run(ref:str, other:str=""):\n'
        '    repo = git.Repo("/workspace")\n    ' + body + "\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-014"]}
    )
    result = run_static_scan(config, uuid4(), timestamp=NOW)
    assert len(result.findings) == expected


def test_conditional_command_list_keeps_first_untrusted_argument(
    tmp_path: Path,
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "import subprocess\nfrom mcp.server.fastmcp import FastMCP\n"
        'mcp=FastMCP("test")\n@mcp.tool()\ndef run(ref:str, choose:bool):\n'
        '    args = ["git", "show"]\n'
        "    if choose: args.append(ref)\n"
        "    return subprocess.run(args)\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-014"]}
    )
    assert len(run_static_scan(config, uuid4(), timestamp=NOW).findings) == 1


@pytest.mark.parametrize(
    "guard",
    [
        'if any(t.startswith("-") for t in tokens): raise ValueError()',
        'if any(t.startswith("-") for t in tokens): return "invalid"',
    ],
)
def test_guarded_tokens_stay_protected_through_list_concatenation(
    tmp_path: Path, guard: str
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "import subprocess\nfrom mcp.server.fastmcp import FastMCP\n"
        'mcp=FastMCP("test")\n@mcp.tool()\ndef run(ref:str):\n'
        "    tokens = ref.split()\n    " + guard + "\n"
        '    args = ["dbt", "run"]\n'
        '    args.extend(["--select"] + tokens)\n'
        "    return subprocess.run(args)\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-014"]}
    )
    assert not run_static_scan(config, uuid4(), timestamp=NOW).findings


@pytest.mark.parametrize("tail", ["full[1:]", "full[1:] if len(full) > 1 else []"])
def test_optional_safe_selector_keeps_command_prefix_and_copy(
    tmp_path: Path, tail: str
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "import subprocess\nfrom mcp.server.fastmcp import FastMCP\n"
        'mcp=FastMCP("test")\n@mcp.tool()\ndef run(ref:str):\n'
        '    command = ["run"]\n'
        "    if ref:\n"
        "        tokens = ref.split()\n"
        '        if any(t.startswith("-") for t in tokens): raise ValueError()\n'
        '        command.extend(["--select"] + tokens)\n'
        "    full = command.copy()\n"
        "    if len(full) > 0:\n"
        f"        rest = {tail}\n"
        '        full = [full[0], "--quiet", *rest]\n'
        '    return subprocess.run(["dbt", *full])\n',
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-014"]}
    )
    assert not run_static_scan(config, uuid4(), timestamp=NOW).findings


@pytest.mark.parametrize(
    ("rule_id", "sink", "impact", "severity", "category"),
    [
        ("SENT-014", "    return repo.git.show(ref)", "Critical", "High", "ASI05:2026"),
        ("SENT-015", "    return requests.get(ref)", "High", "Medium", "ASI02:2026"),
        (
            "SENT-016",
            '    return requests.get("https://api.example.com/", '
            'headers={"Authorization": token})',
            "High",
            "Medium",
            "ASI03:2026",
        ),
    ],
)
def test_flow_rule_cli_selection_suppression_baseline_and_severity(
    tmp_path: Path,
    rule_id: str,
    sink: str,
    impact: str,
    severity: str,
    category: str,
) -> None:
    import json

    from typer.testing import CliRunner

    from sentinel.cli import app

    root = make_target(tmp_path / "target", target_yaml="")
    source = root / "server.py"
    entry = (
        '@api.get("/data")\ndef run(request: Request):\n'
        '    token=request.headers.get("Authorization") or '
        'os.getenv("OPERATOR_TOKEN")\n'
        if rule_id == "SENT-016"
        else "@mcp.tool()\ndef run(ref:str):\n"
    )
    source.write_text(
        "from mcp.server.fastmcp import FastMCP\nimport git\nimport requests\n"
        "from fastapi import FastAPI, Request\nimport os\napi=FastAPI()\n"
        'mcp=FastMCP("test")\n'
        + entry
        + '    repo=git.Repo("/workspace")\n'
        + sink
        + "\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    args = [
        "scan",
        str(root),
        "--rules-only",
        "--json",
        "--rules",
        rule_id,
        "--fail-on",
        severity.lower(),
    ]
    baseline = tmp_path / "baseline.json"
    result = runner.invoke(app, [*args, "--output", str(baseline)])
    assert result.exit_code == 1, result.output
    finding = json.loads(baseline.read_text())["findings"][0]
    assert finding["impact"] == impact and finding["severity"] == severity
    assert finding["owasp_category"]["id"] == category
    assert finding["evidence"]["flow_locations"]
    assert runner.invoke(app, [*args, "--baseline", str(baseline)]).exit_code == 0
    assert runner.invoke(app, [*args, "--fail-on", "critical"]).exit_code == 0
    default = runner.invoke(app, ["scan", str(root), "--rules-only", "--json"])
    assert any(f["rule_id"] == rule_id for f in json.loads(default.stdout)["findings"])
    source.write_text(
        source.read_text().replace(
            sink, sink + f"  # sentinel: ignore[{rule_id}] reason=audited fixture"
        ),
        encoding="utf-8",
    )
    suppressed = runner.invoke(app, args)
    assert suppressed.exit_code == 0, suppressed.output
    finding = json.loads(suppressed.stdout)["findings"][0]
    assert finding["status"] == "suppressed"
    assert finding["suppression"]["reason"] == "audited fixture"


@pytest.mark.parametrize(
    ("prepare", "serialize", "expected"),
    [
        ('payload = {"name": value}', "json.dumps(payload)", 0),
        ("payload = [value]", "json.dumps(payload)", 0),
        ("payload = value", "json.dumps(payload)", 1),
        ('payload = {"name": value}\n    payload = value', "json.dumps(payload)", 1),
        ('payload = {"name": value}', "json.dumps(payload, cls=CustomEncoder)", 1),
    ],
)
def test_json_container_is_one_fixed_prefix_option_value(
    tmp_path: Path, prepare: str, serialize: str, expected: int
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from mcp.server.fastmcp import FastMCP\nimport subprocess\nimport json\n"
        'mcp=FastMCP("test")\n@mcp.tool()\ndef run(value):\n    '
        + prepare
        + "\n    encoded = "
        + serialize
        + "\n"
        '    return subprocess.run(["dbt", "run-operation", "fixed_macro", '
        '"--args", encoded])\n',
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-014"]}
    )
    assert len(run_static_scan(config, uuid4(), timestamp=NOW).findings) == expected


@pytest.mark.parametrize("decorator", ["", "@replace_guard\n"])
def test_decorated_helper_does_not_establish_option_rejection(
    tmp_path: Path, decorator: str
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from mcp.server.fastmcp import FastMCP\nimport git\n"
        "def replace_guard(fn): return lambda value: value\n"
        + decorator
        + 'def guard(ref):\n    if ref.startswith("-"): raise ValueError()\n'
        'mcp=FastMCP("test")\n@mcp.tool()\ndef diff(ref: str):\n'
        '    guard(ref)\n    return git.Repo("/workspace").git.diff(ref)\n',
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-014"]}
    )
    assert len(run_static_scan(config, uuid4(), timestamp=NOW).findings) == bool(
        decorator
    )
