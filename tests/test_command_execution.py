"""Shell execution follows registered cross-file dispatch and command mutations."""

from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.finding import FileLocation
from sentinel.static.engine import run_static_scan
from tests.conftest import NOW


@pytest.mark.parametrize("api", ["check_call", "check_output"])
@pytest.mark.parametrize("helper", [False, True])
@pytest.mark.parametrize(
    ("case", "expected"),
    [("caller", 1), ("fixed", 0), ("shadowed", 0), ("no-shell", 0)],
)
def test_python_checked_shell_calls(
    tmp_path: Path, api: str, helper: bool, case: str, expected: int
) -> None:
    (tmp_path / "requirements.txt").write_text("mcp==1.29.0\n")
    body = (
        ("    execute=unknown\n" if case == "shadowed" else "")
        + "    return execute("
        + ('"fixed"' if case == "fixed" else "command")
        + f", shell={case != 'no-shell'})\n"
    )
    source = (
        f"from subprocess import {api} as execute\n"
        "from mcp.server.fastmcp import FastMCP\n"
        'mcp=FastMCP("test")\n'
        + ("def helper(command):\n" + body if helper else "")
        + "@mcp.tool()\ndef run(command: str):\n"
        + ("    return helper(command)\n" if helper else body)
    )
    (tmp_path / "server.py").write_text(source)
    config = load_configuration(
        tmp_path, environ={}, static_only=True, cli_overrides={"rules": ["SENT-002"]}
    )
    result = run_static_scan(config, uuid4(), timestamp=NOW)
    assert not result.incomplete
    assert len(result.findings) == expected


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


@pytest.mark.parametrize(
    "imports,factory,target",
    [
        (
            'import {promisify as promise} from "node:util"; '
            'import {exec as command, execFile} from "node:child_process";',
            "promise",
            "command",
        ),
        (
            'import * as utility from "util"; import * as child from "child_process";',
            "utility.promisify",
            "child.exec",
        ),
        (
            'import utility from "node:util"; import child from "node:child_process";',
            "utility.promisify",
            "child.exec",
        ),
        (
            'import {promisify} from "util"; import {exec} from "child_process"; '
            "const promise=promisify; const command=exec;",
            "promise",
            "command",
        ),
    ],
)
@pytest.mark.parametrize(
    "case",
    [
        "tainted",
        "literal",
        "argv",
        "wrapper-alias",
        "escape",
        "field-mutation",
        "field-invocation",
        "custom",
        "reflect",
        "target-escape",
        "factory-rebound",
        "branch",
    ],
)
def test_promisified_shell_identity(
    tmp_path: Path, imports: str, factory: str, target: str, case: str
) -> None:
    import time

    from sentinel.static.model import RuleRunState, TypeScriptSourceFile
    from sentinel.static.typescript_discovery import TypeScriptProgram
    from sentinel.static.typescript_execution import ShellFlow
    from sentinel.static.typescript_path_flow import analyze

    original = (
        target
        if case != "argv"
        else target.rsplit(".", 1)[0] + ".execFile"
        if "." in target
        else "execFile"
    )
    if case == "argv" and "execFile" not in imports and "." not in target:
        imports += 'import {execFile} from "child_process";'
    mutation = {
        "custom": f"{target}[{factory}.custom] = unknown;",
        "reflect": f"Object.defineProperty({target}, "
        'Symbol.for("nodejs.util.promisify.custom"), {value: unknown});',
        "target-escape": f"unknown({target});",
        "factory-rebound": f"{factory} = unknown;",
    }.get(case, "")
    local = {
        "escape": "unknown(wrapped);",
        "field-mutation": "const box={fn:wrapped}; box.fn.extra = unknown;",
        "field-invocation": "const box={fn:wrapped}; wrapped.extra = unknown;",
        "branch": "if (input.flag) wrapped = unknown;",
        "wrapper-alias": "const alternate = wrapped;",
    }.get(case, "")
    invocation = (
        "alternate(input.command)"
        if case == "wrapper-alias"
        else "box.fn(input.command)"
        if case == "field-invocation"
        else 'wrapped("literal")'
        if case == "literal"
        else 'wrapped("git", [input.command])'
        if case == "argv"
        else "wrapped(input.command)"
    )
    sources = {
        "server.ts": "import {McpServer} from "
        '"@modelcontextprotocol/sdk/server/mcp.js"; '
        'import {run} from "./logic.js"; '
        'const server=new McpServer({name:"test",version:"1"}); '
        'server.tool("run", {}, async (input)=>run(input));',
        "logic.ts": imports
        + mutation
        + f" export async function run(input) {{ let wrapped={factory}({original}); "
        + f"{local} return await {invocation}; }}",
    }
    files = tuple(
        TypeScriptSourceFile(tmp_path / name, name, source)
        for name, source in sources.items()
    )
    program = TypeScriptProgram(files, deadline=time.monotonic() + 20)
    state = RuleRunState()
    flow = ShellFlow(program, state)
    analyze(program, state, flow=flow)
    assert len(state.matches) == (1 if case in {"tainted", "wrapper-alias"} else 0)
    if case in {"tainted", "wrapper-alias", "literal", "argv"}:
        assert any("promisified" in s.node for s in flow.callables.values())
        assert all(w.code == "static_binding_unresolved" for w in state.warnings)
    else:
        assert any(w.code == "static_flow_unresolved" for w in state.warnings)
    for match in state.matches:
        assert match.path == "logic.ts" and match.range.start_line == 1


@pytest.mark.parametrize("fixed", [False, True])
def test_promisified_registered_barrel_callback(tmp_path: Path, fixed: bool) -> None:
    import time

    from sentinel.static.model import RuleRunState, TypeScriptSourceFile
    from sentinel.static.rules.sent014 import TypeScriptOptionFlow
    from sentinel.static.rules.sent015 import TypeScriptURLFlow
    from sentinel.static.rules.sent016 import TypeScriptCredentialFlow
    from sentinel.static.typescript_discovery import TypeScriptProgram
    from sentinel.static.typescript_execution import ShellFlow
    from sentinel.static.typescript_path_flow import TypeScriptPathFlow, analyze

    sources = {
        "server.ts": "import {McpServer} from "
        '"@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import {register} from "./registration.js";\n'
        "export async function build() {\n"
        'const server=new McpServer({name:"test",version:"1"});\n'
        "await register(server); return server; }\n",
        "registration.ts": 'import {Boundary} from "./barrel.js";\n'
        'import {perform} from "./logic.js";\n'
        "export async function register(server) {\n"
        "await Boundary.forward(async () => {\n"
        'server.tool("operation", {}, async (input) =>\n'
        "Boundary.forward(async () => perform(input)));\n"
        "}); }\n",
        "barrel.ts": 'export * from "./internal.js";\n'
        'export * from "./unrelated.js";\n',
        "internal.ts": 'export * from "./boundary.js";\n',
        "unrelated.ts": 'export const other = "value";\n',
        "boundary.ts": "export class Boundary {\n"
        "public static async forward(fn) {\n"
        "try { return await fn(); } catch(error) { throw error; }\n"
        "} }\n",
        "logic.ts": 'import {promisify} from "node:util";\n'
        'import {exec, execFile} from "node:child_process";\n'
        + (
            "const operation=promisify(execFile);\n"
            if fixed
            else "const operation=promisify(exec);\n"
        )
        + "export async function perform(input) {\n"
        + (
            'return await operation("git", [input.branch]);\n'
            if fixed
            else 'return await operation("git init -b " + input.branch);\n'
        )
        + "}\n",
    }
    files = tuple(
        TypeScriptSourceFile(tmp_path / name, name, source)
        for name, source in sources.items()
    )
    program = TypeScriptProgram(files, deadline=time.monotonic() + 30)
    assert len(program.tools()) == 1
    for kind in (
        ShellFlow,
        TypeScriptPathFlow,
        TypeScriptOptionFlow,
        TypeScriptURLFlow,
        TypeScriptCredentialFlow,
    ):
        state = RuleRunState()
        flow = kind(program, state)
        analyze(program, state, flow=flow)
        assert any("promisified" in s.node for s in flow.callables.values()), (
            kind.__name__,
            [w.message for w in state.warnings],
        )
        assert not any("promisif" in w.message for w in state.warnings)
        if kind is ShellFlow:
            assert len(state.matches) == (0 if fixed else 1)
            if state.matches:
                assert state.matches[0].path == "logic.ts"
                assert state.matches[0].range.start_line == 5
