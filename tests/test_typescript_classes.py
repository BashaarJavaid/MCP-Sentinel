"""Included class methods must retain the actual receiver and caller value."""

import time
from pathlib import Path
from typing import Any

import pytest

from sentinel.static.model import RuleRunState, TypeScriptSourceFile
from sentinel.static.path_flow import Value
from sentinel.static.rules.sent014 import TypeScriptOptionFlow
from sentinel.static.rules.sent015 import TypeScriptURLFlow
from sentinel.static.rules.sent016 import TypeScriptCredentialFlow
from sentinel.static.typescript_discovery import TypeScriptProgram, name_of
from sentinel.static.typescript_path_flow import TypeScriptPathFlow, analyze


@pytest.mark.parametrize(
    ("body", "call", "expected"),
    [
        (
            "write(p) { return fs.writeFileSync(p, 'data'); }",
            "writer.write(args.path)",
            1,
        ),
        (
            "output = ''; constructor() {} "
            "write(p) { this.output = p; return this.save(); } "
            "save() { return fs.writeFileSync(this.output, 'data'); }",
            "writer.write(args.path)",
            1,
        ),
        (
            "static write(p) { return fs.writeFileSync(p, 'data'); }",
            "Writer.write(args.path)",
            1,
        ),
        (
            "write(p) { return fs.writeFileSync('/srv/fixed', 'data'); }",
            "writer.write(args.path)",
            0,
        ),
        (
            "write(p) { return fs.writeFileSync(p, 'data'); }",
            "(writer.write = unknown, writer.write(args.path))",
            0,
        ),
        (
            "write(p) { return fs.writeFileSync(p, 'data'); }",
            "(unknown(writer), writer.write(args.path))",
            0,
        ),
        (
            "constructor(p) { this.output = p; } "
            "save() { return fs.writeFileSync(this.output, 'data'); }",
            "new Writer(args.path).save()",
            1,
        ),
        (
            "set(p) { this.output = p; } "
            "save() { return fs.writeFileSync(this.output, 'data'); }",
            "(writer.set(args.path), writer.save())",
            1,
        ),
        (
            "output = '/fixed'; set(p) { this.output = p; } "
            "save() { return fs.writeFileSync(this.output, 'data'); }",
            "(writer.set(args.path), new Writer().save())",
            0,
        ),
        (
            "output = '/fixed'; write(p) { "
            "if (unknown()) this.output = p; return this.save(); } "
            "save() { return fs.writeFileSync(this.output, 'data'); }",
            "writer.write(args.path)",
            1,
        ),
        (
            "static write(p) { return this.save(p); } "
            "static save(p) { return fs.writeFileSync(p, 'data'); }",
            "Writer.write(args.path)",
            1,
        ),
        (
            "write(p) { return fs.writeFileSync(p, 'data'); }",
            "(unknown(Writer), new Writer().write(args.path))",
            0,
        ),
        (
            "write(p) { return fs.writeFileSync(p, 'data'); }",
            "(writer['write'] = unknown, writer.write(args.path))",
            0,
        ),
        (
            "write(p) { return fs.writeFileSync(p, 'data'); }",
            "(delete writer.write, writer.write(args.path))",
            0,
        ),
        (
            "constructor() { return unknown(); } "
            "write(p) { return fs.writeFileSync(p, 'data'); }",
            "writer.write(args.path)",
            0,
        ),
        (
            "constructor() { unknown(this); } "
            "write(p) { return fs.writeFileSync(p, 'data'); }",
            "writer.write(args.path)",
            0,
        ),
        (
            "output = ''; write(p) { this.output += p; return this.save(); } "
            "save() { return fs.writeFileSync(this.output, 'data'); }",
            "writer.write(args.path)",
            1,
        ),
        (
            "write(p) { const f = () => this.save(p); return f(); } "
            "save(p) { return fs.writeFileSync(p, 'data'); }",
            "writer.write(args.path)",
            1,
        ),
        (
            "write(p) { const f = function() { return this.save(p); }; return f(); } "
            "save(p) { return fs.writeFileSync(p, 'data'); }",
            "writer.write(args.path)",
            0,
        ),
        (
            "write(p) { return [p].map(p => this.save(p)); } "
            "save(p) { return fs.writeFileSync(p, 'data'); }",
            "writer.write(args.path)",
            1,
        ),
        (
            "write(p) { return [p].map(function(p) { return this.save(p); }); } "
            "save(p) { return fs.writeFileSync(p, 'data'); }",
            "writer.write(args.path)",
            0,
        ),
        (
            "constructor(p) { fs.writeFileSync(p, 'data'); } save() { return 'done'; }",
            "new Writer(args.path).save()",
            1,
        ),
    ],
)
def test_imported_class_receiver_and_replacement(
    tmp_path: Path, body: str, call: str, expected: int
) -> None:
    sources = {
        "writer.ts": 'import fs from "node:fs";\nexport class Writer { '
        + body
        + " }\n",
        "server.ts": "import {McpServer} from "
        '"@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import {Writer} from "./writer";\nconst writer = new Writer();\n'
        'const mcp = new McpServer({name:"test",version:"1"});\n'
        'mcp.registerTool("write", {inputSchema:{path:z.string()}}, '
        + "args => "
        + call
        + ");\n",
    }
    files = []
    for name, source in sources.items():
        path = tmp_path / name
        path.write_text(source, encoding="utf-8")
        files.append(TypeScriptSourceFile(path, name, source))
    program = TypeScriptProgram(tuple(files), deadline=time.monotonic() + 20)
    state = RuleRunState()
    analyze(program, state)
    assert len(state.matches) == expected
    if expected:
        assert state.matches[0].path == "writer.ts"
        assert "server.ts" in state.matches[0].captures["flow_locations"]


@pytest.mark.parametrize(
    "flow_type",
    [
        TypeScriptPathFlow,
        TypeScriptOptionFlow,
        TypeScriptURLFlow,
        TypeScriptCredentialFlow,
    ],
)
@pytest.mark.parametrize(
    ("expression", "count"),
    [
        ("new Writer().write(args.value)", 1),
        ("['http:', 'https:'].includes(new Writer().write(args.value))", 1),
        ("false && new Writer().write(args.value)", 0),
        ("true || new Writer().write(args.value)", 0),
    ],
)
def test_rule_delegation_does_not_repeat_callee_or_argument_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    flow_type: type[TypeScriptPathFlow],
    expression: str,
    count: int,
) -> None:
    source = (
        'import {McpServer} from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        "class Writer { constructor() { observe(); } write(value) { return value; } }\n"
        'const mcp = new McpServer({name:"test",version:"1"});\n'
        'mcp.registerTool("test", {inputSchema:{value:z.string()}}, '
        f"args => {expression});\n"
    )
    path = tmp_path / "server.ts"
    path.write_text(source, encoding="utf-8")
    program = TypeScriptProgram(
        (TypeScriptSourceFile(path, "server.ts", source),),
        deadline=time.monotonic() + 20,
    )
    state = RuleRunState()
    flow = flow_type(program, state)
    observed = []
    original = flow.call

    def call(
        file: TypeScriptSourceFile, node: dict[str, Any], env: dict[str, Value]
    ) -> Value:
        if name_of(node["Call"][0]) == "observe":
            observed.append(node)
        return original(file, node, env)

    monkeypatch.setattr(flow, "call", call)
    analyze(program, state, flow=flow)
    assert len(observed) == count
