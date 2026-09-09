"""Resolve original TypeScript source, including imports and typed handlers."""

import time
from pathlib import Path

import pytest

from sentinel.static.model import TypeScriptSourceFile
from sentinel.static.typescript_discovery import TypeScriptProgram


@pytest.mark.parametrize("invoke", [False, True])
def test_http_discovery_distinguishes_registered_and_called_tool(
    tmp_path: Path, invoke: bool
) -> None:
    from sentinel.static.http_discovery import typescript_handlers

    source = (
        'import express from "express";\n'
        'import {McpServer} from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        "export function create() {\n"
        " const app=express();\n"
        ' const server=new McpServer({name:"test",version:"1"});\n'
        ' function attach() { app.post("/startup", (req,res)=>req.body); }\n'
        ' function tool() { app.post("/called", (req,res)=>req.body); }\n'
        " attach();\n"
        ' server.registerTool("tool", {inputSchema:{}}, tool);\n'
        + (" tool();\n" if invoke else "")
        + " return app;\n}\n"
    )
    path = tmp_path / "server.ts"
    path.write_text(source, encoding="utf-8")
    file = TypeScriptSourceFile(path, path.name, source)
    program = TypeScriptProgram((file,), deadline=time.monotonic() + 15)
    routes = typescript_handlers(program)
    assert {route.name for route in routes} == (
        {"/startup", "/called"} if invoke else {"/startup"}
    )
    assert all(route.handler is not None for route in routes)
    assert [tool.name for tool in program.tools()] == ["tool"]


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


def test_factory_reads_metadata_after_configuration_helper(tmp_path: Path) -> None:
    source = (
        'import {McpServer} from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import {z} from "zod";\n'
        "function configure(config) {\n"
        " config.inputSchema={path:z.string()};\n"
        ' config.description="List a directory";\n}\n'
        "export function create() {\n"
        ' const server=new McpServer({name:"test",version:"1"});\n'
        " const config={}; configure(config);\n"
        ' server.registerTool("list",config,(args)=>args.path);\n'
        " return server;\n}\n"
    )
    path = tmp_path / "server.ts"
    path.write_text(source)
    file = TypeScriptSourceFile(path, path.name, source)
    program = TypeScriptProgram((file,), deadline=time.monotonic() + 15)
    tools = program.tools()
    assert len(tools) == 1 and tools[0].name == "list"
    assert program.literal(tools[0].description) == "List a directory"
    schema = tools[0].schema
    assert schema is not None
    assert program.text(schema.file, schema.node) == "{path:z.string()}"
