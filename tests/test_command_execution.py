"""Shell execution follows registered cross-file dispatch and command mutations."""

from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.finding import FileLocation
from sentinel.static.engine import run_static_scan
from tests.conftest import NOW


@pytest.mark.parametrize(
    ("command", "sink", "expected"),
    [
        (
            'let command = "kubectl get "; command += input.resource;',
            "execSync(command)",
            1,
        ),
        (
            'let command = "kubectl get "; command += input.resource; '
            'command = "true";',
            "execSync(command)",
            0,
        ),
        ('const command = "kubectl";', "execFileSync(command, [input.resource])", 0),
        (
            'let command = "kubectl get "; command += input.resource;',
            "execFileSync(command, [], {shell: true})",
            1,
        ),
        ("const command = input.resource;", "fake(command)", 0),
    ],
)
def test_cross_file_low_level_shell_dispatch(
    tmp_path: Path, command: str, sink: str, expected: int
) -> None:
    (tmp_path / "package.json").write_text(
        '{"dependencies":{"@modelcontextprotocol/sdk":"1.0.0"}}',
        encoding="utf-8",
    )
    (tmp_path / "server.ts").write_text(
        'import { Server } from "@modelcontextprotocol/sdk/server/index.js";\n'
        'import { CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";\n'
        'import { run } from "./commands.js";\n'
        'const server = new Server({name:"test", version:"1"});\n'
        "server.setRequestHandler(CallToolRequestSchema, async (request) => {\n"
        "const {name, arguments: input = {}} = request.params;\n"
        'if (name === "get") return await run({}, input as {resource:string});\n'
        "});\n",
        encoding="utf-8",
    )
    (tmp_path / "commands.ts").write_text(
        'import { execSync, execFileSync } from "node:child_process";\n'
        "const fake = unknown;\n"
        "export async function run(manager, input) {\n"
        + command
        + "\nreturn "
        + sink
        + ";\n}\n",
        encoding="utf-8",
    )
    configuration = load_configuration(
        tmp_path, environ={}, static_only=True, cli_overrides={"rules": ["SENT-002"]}
    )
    result = run_static_scan(configuration, uuid4(), timestamp=NOW)
    assert not result.incomplete
    assert len(result.findings) == expected
    for finding in result.findings:
        assert isinstance(finding.location, FileLocation)
        assert finding.location.path == "commands.ts"
