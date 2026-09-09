"""Resolve original TypeScript source, including imports and typed handlers."""

import time
from pathlib import Path

from sentinel.static.model import TypeScriptSourceFile
from sentinel.static.typescript_discovery import TypeScriptProgram


def test_imported_reexported_handler_and_schema(tmp_path: Path) -> None:
    sources = {
        "server.ts": 'import { load, schema } from "./barrel.js";\n'
        "const handler = load;\n"
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'const server = new McpServer({name:"test",version:"1"});\n'
        'server.registerTool("read", { inputSchema: schema }, handler);\n',
        "barrel.ts": 'export { read as load, schema } from "./handler.js";\n',
        "handler.ts": 'import fs from "node:fs/promises";\n'
        "export const schema = z.object({path: z.string()});\n"
        "export async function read(value: string): Promise<{text: string}> {\n"
        'return {text: await fs.readFile(value, "utf8")};\n}\n',
    }
    files = []
    for name, source in sources.items():
        path = tmp_path / name
        path.write_text(source)
        files.append(TypeScriptSourceFile(path, name, source))
    program = TypeScriptProgram(tuple(files), deadline=time.monotonic() + 15)
    handler = program.resolve(files[0], "handler")
    assert handler is not None and handler.file.relative_path == "handler.ts"
    assert handler.function is not None
    assert program.text(handler.file, handler.function["fbody"]).startswith("{")
    assert "fs.readFile" in program.text(handler.file, handler.function["fbody"])
    schema = program.resolve(files[0], "schema")
    assert schema is not None and "z.object" in program.text(schema.file, schema.node)
    fs = program.resolve(files[2], "fs.readFile")
    assert fs is not None and fs.external == "node:fs/promises.readFile"
    tools = program.tools()
    assert len(tools) == 1 and tools[0].name == "read"
    assert tools[0].handler == handler and tools[0].schema == schema
    assert tools[0].registration.file == files[0]


def test_ambiguous_rebound_private_and_escaping_bindings(tmp_path: Path) -> None:
    sources = {
        "server.ts": 'import { read, hidden } from "./helper";\n'
        'import { other } from "../outside";\n'
        "let alias = read; alias = replacement;\n",
        "helper.ts": "export function read(p: string) { return p; }\n"
        "function hidden(p: string) { return p; }\n",
        "helper/index.ts": "export function read(p: string) { return p; }\n",
    }
    files = []
    for name, source in sources.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source)
        files.append(TypeScriptSourceFile(path, name, source))
    program = TypeScriptProgram(tuple(files), deadline=time.monotonic() + 15)
    assert program.resolve(files[0], "read") is None
    assert program.resolve(files[0], "hidden") is None
    assert program.resolve(files[0], "alias") is None
    assert program.resolve(files[0], "other") is None
    assert program.warnings


def test_object_handler_method_uses_original_function_node(tmp_path: Path) -> None:
    source = (
        'import { MCPServer } from "@mastra/mcp";\n'
        'const tool = {description:"Read a document", '
        "parameters:z.object({path:z.string()}),\n"
        "execute: async (args: Input) => { return fs.readFile(args.path); }};\n"
        "const server = new MCPServer({tools:{read:tool}});\n"
    )
    path = tmp_path / "server.ts"
    path.write_text(source)
    file = TypeScriptSourceFile(path, path.name, source)
    program = TypeScriptProgram((file,), deadline=time.monotonic() + 15)
    tools = program.tools()
    assert len(tools) == 1 and tools[0].name == "read"
    assert tools[0].handler is not None and tools[0].handler.function is not None
    assert tools[0].schema is not None


def test_typed_destructuring_keeps_runtime_member_identity(tmp_path: Path) -> None:
    from sentinel.static.model import RuleRunState
    from sentinel.static.path_flow import Value
    from sentinel.static.typescript_path_flow import TypeScriptPathFlow

    source = "function run({ref, other: alias}: {ref: string, alias: string}) {}"
    path = tmp_path / "typed.ts"
    path.write_text(source, encoding="utf-8")
    file = TypeScriptSourceFile(path, path.name, source)
    program = TypeScriptProgram((file,), deadline=time.monotonic() + 15)
    handler = program.resolve(file, "run")
    assert handler is not None and handler.function is not None
    flow = TypeScriptPathFlow(program, RuleRunState())
    argument = Value(sources=frozenset({"caller"}), key="argument")
    env: dict[str, Value] = {}
    flow.pattern(handler.function["fparams"][1][0]["ParamPattern"], argument, env)
    assert set(env) == {"ref", "alias"}
    assert env["ref"] == flow.member(argument, "ref", env)
    assert env["alias"] == flow.member(argument, "other", env)
    assert env["ref"].key != env["alias"].key
