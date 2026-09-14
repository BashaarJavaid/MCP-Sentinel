"""Concurrent rule traversal preserves source evidence and owned-process cleanup."""

import dataclasses
import os
import subprocess
import time
from pathlib import Path
from typing import Any

import pytest

from sentinel.config import load_configuration
from sentinel.errors import InfrastructureError
from sentinel.static import engine, workers
from sentinel.static.model import RuleRunState, StaticContext, StaticScanResult
from sentinel.static.traversal import collect_static_files
from tests.conftest import NOW, SCAN_ID, make_target


@pytest.mark.parametrize(
    ("language", "parameter_property"),
    [
        ("python", False),
        ("typescript", False),
        ("mixed", False),
        ("typescript", True),
        ("mixed", True),
    ],
)
def test_parallel_native_result_matches_serial_and_never_imports_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    language: str,
    parameter_property: bool,
) -> None:
    root = make_target(tmp_path / "target")
    if language in {"python", "mixed"}:
        (root / "server.py").write_text(
            "from mcp.server.fastmcp import FastMCP\n"
            "from helpers import read_file\nimport subprocess, requests\n"
            'mcp=FastMCP("test")\n@mcp.tool()\n'
            "def inspect(path: str, url: str, ref: str):\n"
            "    read_file(path)\n"
            '    subprocess.run(["git", "show", ref])\n'
            "    return requests.get(url)\n"
        )
        (root / "helpers.py").write_text(
            "def read_file(path): return open(path).read()\n"
        )
    if language in {"typescript", "mixed"}:
        if language == "typescript":
            (root / "pyproject.toml").unlink()
            (root / "server.py").unlink()
        (root / "package.json").write_text(
            '{"dependencies":{"@modelcontextprotocol/sdk":"^1"}'
            + (',"workspaces":["."]' if language == "mixed" else "")
            + "}"
        )
        source = (
            "// π: original UTF-8 source\r\n"
            'import {McpServer} from "@modelcontextprotocol/sdk/server/mcp.js";\r\n'
            'import fs from "node:fs/promises";\r\n'
            'import {spawnSync} from "node:child_process";\r\n'
            'const server=new McpServer({name:"test",version:"1"});\r\n'
            "class Reader { inspect(args) { fs.readFile(args.path);\r\n"
            'spawnSync("git",["show",args.ref]); return fetch(args.url); }}\r\n'
            "const reader=new Reader();\r\n"
            'server.registerTool("inspect", {inputSchema:{}}, '
            "(args)=>reader.inspect(args));\r\n"
        )
        if parameter_property:
            source = (
                source.replace(
                    "class Reader { inspect(args)",
                    "class Reader { constructor(private args: any) {} inspect()",
                )
                .replace("args.path", "this.args.path")
                .replace("args.ref", "this.args.ref")
                .replace("args.url", "this.args.url")
                .replace(
                    "(args)=>reader.inspect(args)", "(args)=>new Reader(args).inspect()"
                )
            )
        (root / "server.ts").write_bytes(source.encode())
    marker = tmp_path / "target-imported"
    (root / "sentinel.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n"
    )
    configuration = load_configuration(
        root,
        environ={},
        cli_overrides={"rules_only": True, "rules": sorted(workers.FLOW_RULES)},
    )
    monkeypatch.setattr(workers, "MIN_SOURCE_SIZE", 0)
    monkeypatch.setattr(os, "cpu_count", lambda: 4)
    monkeypatch.setattr(engine, "run_flow_rules", lambda *_: {})
    from sentinel.static.typescript_discovery import TypeScriptProgram

    cached_tools = TypeScriptProgram.tools
    monkeypatch.setattr(TypeScriptProgram, "tools", TypeScriptProgram._discover_tools)
    serial = engine.run_static_scan(configuration, SCAN_ID, timestamp=NOW)
    monkeypatch.setattr(TypeScriptProgram, "tools", cached_tools)
    produced = []
    discover = TypeScriptProgram._discover_tools

    def producer(program: TypeScriptProgram) -> Any:
        produced.append(program)
        return discover(program)

    monkeypatch.setattr(TypeScriptProgram, "_discover_tools", producer)
    script = tmp_path / "trusted_reuse_worker.py"
    script.write_text(
        "import sys\nfrom pathlib import Path\n"
        f"sys.path.insert(0, {str(workers.WORKER.parents[2])!r})\n"
        "from sentinel.static import workers, engine\n"
        "from sentinel.static.typescript_discovery import TypeScriptProgram\n"
        "def duplicate(self):\n"
        " raise AssertionError('worker repeated tool discovery')\n"
        "TypeScriptProgram._discover_tools=duplicate\n"
        "rule=sys.argv[3]\noriginal=engine._AST_DETECTORS[rule]\n"
        "def detect(context,state):\n"
        f" Path({str(tmp_path)!r}, rule+'.started').touch()\n"
        " original(context,state)\n"
        "engine._AST_DETECTORS[rule]=detect\nworkers._worker()\n"
    )
    monkeypatch.setattr(workers, "WORKER", script)
    observed = {}

    def parallel(
        context: StaticContext, selected: tuple[str, ...]
    ) -> dict[str, RuleRunState]:
        states = workers.run_flow_rules(context, selected)
        observed.update(states)
        return states

    monkeypatch.setattr(engine, "run_flow_rules", parallel)
    monkeypatch.chdir(root)
    monkeypatch.setenv("PYTHONPATH", str(root))
    concurrent = engine.run_static_scan(configuration, SCAN_ID, timestamp=NOW)
    assert set(observed) == workers.FLOW_RULES
    assert {finding.rule_id for finding in concurrent.findings} >= {
        "SENT-012",
        "SENT-014",
        "SENT-015",
    }

    def stable(result: StaticScanResult) -> tuple[Any, ...]:
        return (
            [finding.model_dump(exclude={"finding_id"}) for finding in result.findings],
            result.summary.model_copy(update={"duration_ms": 0}),
            result.warnings,
            result.incomplete,
        )

    assert stable(concurrent) == stable(serial)
    assert not marker.exists()
    assert len(produced) == (0 if language == "python" else 1)
    assert all((tmp_path / (rule + ".started")).exists() for rule in workers.FLOW_RULES)


@pytest.mark.parametrize(
    "failure", ["timeout", "crash", "invalid", "invalid_state", "startup", "interrupt"]
)
def test_worker_failure_reaps_every_started_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    root = make_target(tmp_path / "target")
    configuration = load_configuration(
        root, environ={}, cli_overrides={"rules_only": True}
    )
    files = collect_static_files(root, (), configuration.language)
    context = StaticContext(configuration, files, time.monotonic() + 3)
    script = tmp_path / "trusted_worker.py"
    script.write_text(
        "import sys,time\n"
        + (
            "sys.exit(7)\n"
            if failure == "crash"
            else "from pathlib import Path\nPath(sys.argv[2]).write_bytes(b'invalid')\n"
            if failure == "invalid"
            else "import pickle\nfrom pathlib import Path\n"
            "Path(sys.argv[2]).write_bytes(pickle.dumps(None))\n"
            if failure == "invalid_state"
            else "time.sleep(30)\n"
        )
    )
    monkeypatch.setattr(workers, "MIN_SOURCE_SIZE", 0)
    monkeypatch.setattr(os, "cpu_count", lambda: 4)
    monkeypatch.setattr(workers, "WORKER", script)
    started: list[subprocess.Popen[bytes]] = []
    original = subprocess.Popen

    def launch(*args: Any, **kwargs: Any) -> subprocess.Popen[bytes]:
        if started and failure == "startup":
            raise OSError("worker startup failed")
        if started and failure == "interrupt":
            raise KeyboardInterrupt
        process = original(*args, **kwargs)
        started.append(process)
        return process

    monkeypatch.setattr(subprocess, "Popen", launch)
    expected = KeyboardInterrupt if failure == "interrupt" else InfrastructureError
    with pytest.raises(expected):
        workers.run_flow_rules(context, tuple(sorted(workers.FLOW_RULES)))
    assert started and all(process.poll() is not None for process in started)
    with pytest.raises(InfrastructureError, match="timeout"):
        workers.run_flow_rules(
            dataclasses.replace(context, deadline=0), tuple(sorted(workers.FLOW_RULES))
        )


def test_worker_snapshot_failure_is_an_infrastructure_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = make_target(tmp_path / "target")
    configuration = load_configuration(
        root, environ={}, cli_overrides={"rules_only": True}
    )
    context = StaticContext(
        configuration,
        collect_static_files(root, (), configuration.language),
        time.monotonic() + 3,
    )
    original = Path.write_bytes

    def write(path: Path, data: bytes) -> int:
        if path.name == "input.pickle":
            raise OSError("snapshot write failed")
        return original(path, data)

    monkeypatch.setattr(workers, "MIN_SOURCE_SIZE", 0)
    monkeypatch.setattr(os, "cpu_count", lambda: 4)
    monkeypatch.setattr(Path, "write_bytes", write)
    with pytest.raises(InfrastructureError, match="communication failed"):
        workers.run_flow_rules(context, tuple(sorted(workers.FLOW_RULES)))
