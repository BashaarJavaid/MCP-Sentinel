"""Resolve original TypeScript source, including imports and typed handlers."""

import time
from pathlib import Path

import pytest

from sentinel.static.model import RuleRunState, TypeScriptSourceFile
from sentinel.static.typescript_discovery import TypeScriptProgram


@pytest.mark.parametrize("has_sources", [False, True])
@pytest.mark.parametrize("branch_count", [1, 2])
def test_unchanged_branch_values_keep_only_source_bound_protection(
    has_sources: bool, branch_count: int
) -> None:
    from dataclasses import replace

    from sentinel.static.path_flow import Value
    from sentinel.static.rules.sent015 import TypeScriptURLFlow

    flow = TypeScriptURLFlow(
        TypeScriptProgram((), deadline=time.monotonic() + 15), RuleRunState()
    )
    value = Value(
        key="input",
        sources=frozenset({"caller"}) if has_sources else frozenset(),
        locations=frozenset({("server.ts", 10)}),
        contained=True,
        checked_path_parent=True,
        option_safe=True,
        url_checks=frozenset({"scheme", "host"}),
        operator_credential=True,
        operator_opt_in=frozenset({"explicit-selection"}),
    )
    flow.url_parts[value.key] = ("original-url", "hostname")
    env: dict[str, Value] = {}
    flow.merge(
        env,
        [{"selected": value, "#guard:allowed": value} for _ in range(branch_count)],
    )
    assert env["selected"] == replace(
        value,
        contained=has_sources,
        checked_path_parent=has_sources,
        option_safe=has_sources,
        url_checks=value.url_checks if has_sources else frozenset(),
    )
    assert env["#guard:allowed"] == Value(contained=True)
    assert flow.url_parts[value.key] == ("original-url", "hostname")


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


def test_http_rule_entry_does_not_repeat_registered_mcp_callback(
    tmp_path: Path,
) -> None:
    from sentinel.static.model import RuleRunState
    from sentinel.static.typescript_path_flow import TypeScriptPathFlow, analyze

    source = (
        'import express from "express";\n'
        'import fs from "node:fs/promises";\n'
        'import {McpServer} from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        "export function create() {\n"
        " const app=express();\n"
        ' const server=new McpServer({name:"test",version:"1"});\n'
        ' server.registerTool("read", {inputSchema:{}}, '
        "(args)=>fs.readFile(args.path));\n"
        ' app.post("/health", (req,res)=>res.send("ok"));\n'
        " return app;\n}\n"
    )
    path = tmp_path / "server.ts"
    path.write_text(source, encoding="utf-8")
    file = TypeScriptSourceFile(path, path.name, source)
    program = TypeScriptProgram((file,), deadline=time.monotonic() + 15)
    factory = program.resolve(file, "create")
    assert factory is not None
    http_state = RuleRunState()
    TypeScriptPathFlow(program, http_state).http_initialize(factory)
    assert not http_state.matches
    tool_state = RuleRunState()
    analyze(program, tool_state)
    assert len(tool_state.matches) == 1


def test_reused_locations_stay_bound_to_original_node_and_source(
    tmp_path: Path,
) -> None:
    import copy

    from sentinel.errors import InfrastructureError
    from sentinel.static.semgrep_ast import tokens

    source = 'export function read() { return "π"; }\n'
    file = TypeScriptSourceFile(tmp_path / "server.ts", "server.ts", source)
    program = TypeScriptProgram((file,), deadline=time.monotonic() + 15)
    node = program.trees[file.relative_path]["Pr"][0]
    original = program.source_range(node, file)
    assert program.source_range(node, file) == original
    replaced = TypeScriptSourceFile(
        file.path, file.relative_path, source.replace("π", "x")
    )
    with pytest.raises(InfrastructureError, match="supplied source"):
        program.source_range(node, replaced)
    changed = copy.deepcopy(node)
    next(tokens(changed))["bytepos"] += 1
    with pytest.raises(InfrastructureError, match="supplied source"):
        program.source_range(changed, file)
    assert program.source_range(node, file) == original
    program.deadline = 0
    with pytest.raises(InfrastructureError, match="timeout"):
        program.source_range(node, file)


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


@pytest.mark.parametrize(
    ("schema", "expected"),
    [
        ("z.object({url:z.string().url()})", True),
        ("z.object({url:z.string().transform(x => 'fixed')})", False),
        ("fake.object({url:z.string()})", False),
    ],
)
def test_source_bound_zod_parse_retains_field_flow(
    tmp_path: Path, schema: str, expected: bool
) -> None:
    from sentinel.static.model import RuleRunState
    from sentinel.static.path_flow import Value
    from sentinel.static.typescript_path_flow import TypeScriptPathFlow

    sources = {
        "schema.ts": 'import {z} from "zod"; export const schema = ' + schema + ";",
        "server.ts": 'import {schema as input} from "./schema.js"; '
        "function run(args) { return input.parse(args).url; }",
    }
    files = []
    for name, source in sources.items():
        path = tmp_path / name
        path.write_text(source)
        files.append(TypeScriptSourceFile(path, name, source))
    program = TypeScriptProgram(tuple(files), deadline=time.monotonic() + 15)
    state = RuleRunState()
    flow = TypeScriptPathFlow(program, state)
    argument = Value(sources=frozenset({"caller"}), key="argument")
    handler = program.resolve(files[1], "run")
    assert handler is not None
    result = flow.function(handler, [argument])
    assert result.sources == argument.sources
    assert (result.key == flow.member(argument, "url", {}).key) == expected
    assert (
        any("input.parse" in warning.message for warning in state.warnings) != expected
    )


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


@pytest.mark.parametrize("computed_name", [False, True])
@pytest.mark.parametrize(
    "registration",
    [
        'registerTool(name,{inputSchema:schema,description:"Fetch"},handler)',
        'tool(name,"Fetch",schema,handler)',
        "tool(name,schema,handler)",
    ],
)
@pytest.mark.parametrize("safe", [False, True])
def test_factory_tool_overloads_preserve_closure_and_metadata(
    tmp_path: Path, computed_name: bool, registration: str, safe: bool
) -> None:
    from sentinel.static.model import RuleRunState
    from sentinel.static.rules.sent015 import TypeScriptURLFlow
    from sentinel.static.typescript_path_flow import analyze

    name = "process.env.TOOL_NAME" if computed_name else '"fetch"'
    destination = '"https://example.com/"' if safe else "url"
    source = (
        'import {McpServer} from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import {z} from "zod";\n'
        "function attach(server, requester) {\n"
        f" const name={name};\n"
        " const schema={url:z.string()};\n"
        " const handler=({url})=>requester(url);\n"
        f" server.{registration};\n"
        "}\n"
        "export function create() {\n"
        ' const server=new McpServer({name:"test",version:"1"});\n'
        f" const requester=(url)=>fetch({destination});\n"
        " attach(server,requester); return server;\n}\n"
    )
    path = tmp_path / "server.ts"
    file = TypeScriptSourceFile(path, path.name, source)
    program = TypeScriptProgram((file,), deadline=time.monotonic() + 20)
    bindings = program.tools()
    assert len(bindings) == 1
    assert bindings[0].name == (None if computed_name else "fetch")
    assert bindings[0].handler is not None
    assert bindings[0].schema is not None
    if '"Fetch"' in registration:
        assert program.literal(bindings[0].description) == "Fetch"
    state = RuleRunState()
    analyze(program, state, flow=TypeScriptURLFlow(program, state), entries=bindings)
    assert len(state.matches) == (0 if safe else 1)


@pytest.mark.parametrize(
    "metadata",
    [
        "",
        '"Fetch",',
        "{readOnlyHint:true},",
        '"Fetch",{readOnlyHint:true},',
        "unknownSchema,",
        '"Fetch",{url:z.string()},{readOnlyHint:true},',
    ],
)
def test_factory_legacy_ambiguous_arguments_stay_unresolved(
    tmp_path: Path, metadata: str
) -> None:
    from sentinel.static.model import RuleRunState
    from sentinel.static.rules.sent015 import TypeScriptURLFlow

    source = (
        'import {McpServer} from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import {z} from "zod";\n'
        "function attach(server) {\n"
        f' server.tool("fetch",{metadata}({{url}})=>fetch(url));\n'
        "}\n"
        "export function create() {\n"
        ' const server=new McpServer({name:"test",version:"1"});\n'
        " attach(server); return server;\n}\n"
    )
    file = TypeScriptSourceFile(tmp_path / "server.ts", "server.ts", source)
    program = TypeScriptProgram((file,), deadline=time.monotonic() + 20)
    assert not program.tools()
    factory = program.resolve(file, "create")
    assert factory is not None
    state = RuleRunState()
    TypeScriptURLFlow(program, state).function(factory, [])
    assert not state.matches
    assert any(
        "registration arguments" in warning.message
        or "ambiguous legacy tool metadata" in warning.message
        for warning in state.warnings
    )


@pytest.mark.parametrize(
    "method",
    [
        "execute: async (url)=>fetcher(url)",
        "async execute(url) { return fetcher(url); }",
    ],
)
@pytest.mark.parametrize("reverse", [False, True])
def test_object_service_allocations_keep_distinct_captured_fetchers(
    tmp_path: Path, method: str, reverse: bool
) -> None:
    declarations = [
        "const unsafe=service((url)=>fetch(url));",
        'const safe=service((url)=>fetch("https://example.com/"));',
    ]
    if reverse:
        declarations.reverse()
    state = _object_url_flow(
        tmp_path,
        f"function service(fetcher) {{ return {{{method}}}; }}\n"
        + "\n".join(declarations)
        + "\nunsafe.execute(url); safe.execute(url);",
    )
    assert len(state.matches) == 1


@pytest.mark.parametrize("access", [".execute", '["execute"]'])
@pytest.mark.parametrize(
    ("method", "expected"),
    [
        ("execute() { return fetch(this.url); }", 0),
        ("execute: ()=>fetch(this.url)", 1),
    ],
)
def test_object_method_receiver_and_arrow_lexical_this(
    tmp_path: Path, access: str, method: str, expected: int
) -> None:
    state = _object_url_flow(
        tmp_path,
        "const owner={url, make() { return {"
        f'url:"https://example.com/", {method}'
        "}; }};\n"
        f"const service=owner.make(); return service{access}();",
    )
    assert len(state.matches) == expected


@pytest.mark.parametrize(
    ("options", "change", "expected"),
    [
        ("", "", 1),
        ("undefined", "", 1),
        ("{fetcher:null}", "", 1),
        ('{fetcher:(url)=>fetch("https://example.com/")}', "", 0),
        ("{fetcher:(url)=>fetch(url)}", "", 1),
        ("{fetcher:false}", "", 0),
        ("unknownOptions", "", 0),
        ("{}", "options.fetcher=unknown;", 0),
        ("{}", "unknown(options);", 0),
        ("({} satisfies Options)", "", 1),
    ],
)
def test_default_service_fetcher_preserves_actual_dependency(
    tmp_path: Path, options: str, change: str, expected: int
) -> None:
    state = _object_url_flow(
        tmp_path,
        "function defaultFetch(value) { return fetch(value); }\n"
        "function service(options={}) {\n"
        f" {change}\n"
        " const fetcher=options.fetcher ?? defaultFetch;\n"
        " return {async execute(value) { return fetcher(value); }};\n"
        "}\n"
        f"const selected=service({options}); selected.execute(url);",
    )
    assert len(state.matches) == expected
    if "unknown" in options + change or options == "{fetcher:false}":
        assert any("unresolved call to fetcher" in w.message for w in state.warnings)


@pytest.mark.parametrize("safe", [False, True])
@pytest.mark.parametrize("dynamic", [False, True])
@pytest.mark.parametrize("optional", [False, True])
@pytest.mark.parametrize("before", [False, True])
def test_source_startup_binds_injected_runtime(
    tmp_path: Path, safe: bool, dynamic: bool, optional: bool, before: bool
) -> None:
    from sentinel.static.rules.sent015 import TypeScriptURLFlow
    from sentinel.static.typescript_path_flow import analyze

    destination = '"https://example.com/"' if safe else "url"
    sources = {
        "runtime.ts": (
            "export function runtime() { return {services:{fetchWeb:{"
            f"execute(url) {{return fetch({destination});}}"
            "}}}; }"
        ),
        "server.ts": (
            'import {McpServer} from "@modelcontextprotocol/sdk/server/mcp.js";\n'
            'import {z} from "zod";\n'
            + ('import {runtime} from "./runtime.js";\n' if not dynamic else "")
            + "function create(runtime) {\n"
            ' const server=new McpServer({name:"test",version:"1"});\n'
            ' server.tool("fetch",{url:z.string()},'
            "({url})=>runtime.services.fetchWeb.execute(url));\n"
            " return server;\n}\n"
            "async function start() {\n"
            + (' const {runtime}=await import("./runtime.js");\n' if dynamic else "")
            + (
                " const selected=flag ? runtime() : "
                "({services:{}} satisfies Runtime);\n"
                if optional
                else " const selected=runtime();\n"
            )
            + (
                " if (anotherFlag) selected.services.fetchWeb.execute("
                '"https://example.com/");\n'
                if before
                else ""
            )
            + " return create(selected);\n}\n"
            "start();\n"
        ),
    }
    files = tuple(
        TypeScriptSourceFile(tmp_path / name, name, source)
        for name, source in sources.items()
    )
    program = TypeScriptProgram(files, deadline=time.monotonic() + 20)
    state = RuleRunState()
    analyze(program, state, flow=TypeScriptURLFlow(program, state))
    assert len(state.matches) == (0 if safe else 1)
    assert not any(
        "unresolved call to runtime.services.fetchWeb.execute" in w.message
        for w in state.warnings
    )


def test_object_accessors_stay_unresolved(tmp_path: Path) -> None:
    state = _object_url_flow(
        tmp_path,
        "const service={get execute() { return (url)=>fetch(url); }};\n"
        "return service.execute(url);",
    )
    assert not state.matches
    assert any("object member" in w.message for w in state.warnings)


@pytest.mark.parametrize(
    ("call", "expected"),
    [
        ("return service.execute();", 1),
        ("const execute=service.execute; return execute();", 0),
        (
            'const other={url:"https://example.com/",execute:service.execute};'
            " return other.execute();",
            0,
        ),
        ("service.execute=(value)=>fetch(value); return service.execute(url);", 1),
        (
            'service.execute=()=>fetch("https://example.com/");'
            " return service.execute();",
            0,
        ),
        ("unknown(service); return service.execute();", 0),
    ],
)
def test_object_method_binding_replacement_and_escape(
    tmp_path: Path, call: str, expected: int
) -> None:
    state = _object_url_flow(
        tmp_path,
        "const service={url, execute(){return fetch(this.url);}};\n" + call,
    )
    assert len(state.matches) == expected


def _object_url_flow(tmp_path: Path, body: str) -> RuleRunState:
    from sentinel.static.rules.sent015 import TypeScriptURLFlow
    from sentinel.static.typescript_path_flow import analyze

    source = (
        'import {McpServer} from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import {z} from "zod";\n'
        'const server=new McpServer({name:"test",version:"1"});\n'
        'server.registerTool("fetch",{inputSchema:{url:z.string()}},'
        "async ({url})=>{\n" + body + "\n});\n"
    )
    file = TypeScriptSourceFile(tmp_path / "server.ts", "server.ts", source)
    program = TypeScriptProgram((file,), deadline=time.monotonic() + 20)
    state = RuleRunState()
    analyze(program, state, flow=TypeScriptURLFlow(program, state))
    return state
