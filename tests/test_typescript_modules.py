"""Declared module resolution cannot substitute unrelated or excluded source."""

import json
from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.static.engine import run_static_scan
from sentinel.static.typescript_modules import TypeScriptModules
from tests.conftest import NOW


@pytest.mark.parametrize("specifier", ["@local/io", "@local/io/read", "@helpers/io"])
def test_exported_and_aliased_workspace_handler(tmp_path: Path, specifier: str) -> None:
    sources = {
        "package.json": '{"workspaces":["packages/*"]}',
        "sentinel.toml": '[scanner]\nrules=["SENT-012"]\n',
        "packages/server/package.json": '{"name":"server","dependencies":'
        '{"@modelcontextprotocol/sdk":"^1"}}',
        "packages/server/tsconfig.json": '{// source aliases\n"compilerOptions":'
        '{"paths":{"@helpers/*":["../lib/src/*"]},},}',
        "packages/server/index.ts": f'import {{ read }} from "{specifier}";\n'
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'const server = new McpServer({name:"test",version:"1"});\n'
        'server.registerTool("read",{inputSchema:{path:z.string()}}, read);\n',
        "packages/lib/package.json": json.dumps(
            {
                "name": "@local/io",
                "exports": {
                    ".": {"types": "./types.d.ts", "import": "./src/io.js"},
                    "./*": "./src/*.js",
                },
            }
        ),
        "packages/lib/src/io.ts": 'import {readFile} from "node:fs/promises";\n'
        'export async function read({path}) { return readFile(path, "utf8"); }\n',
        "packages/lib/src/read.ts": 'export {read} from "./io.js";\n',
    }
    for name, text in sources.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    config = load_configuration(tmp_path, environ={}, static_only=True)
    result = run_static_scan(config, uuid4(), timestamp=NOW)
    assert len(result.findings) == 1
    assert result.findings[0].location.path == "packages/lib/src/io.ts"
    assert result.summary.coverage is not None
    surface = next(
        item for item in result.summary.coverage.surfaces if item.name == "read"
    )
    assert surface.handler is not None
    assert surface.handler.path == "packages/lib/src/io.ts"


def test_private_ambiguous_and_escaping_exports(tmp_path: Path) -> None:
    files = []
    for member, name, exports in (
        ("a", "same", "./index.ts"),
        ("b", "same", "./index.ts"),
        ("escape", "escape", "./../a/index.ts"),
        ("private", "private", {".": "./index.ts"}),
    ):
        path = tmp_path / member / "package.json"
        path.parent.mkdir()
        path.write_text(json.dumps({"name": name, "exports": exports}))
        files.append(path)
    modules = TypeScriptModules(tmp_path, tuple(files), ("a", "b", "escape", "private"))
    for name in ("same", "escape", "private/secret"):
        assert modules.resolve("server.ts", name) == (True, ())
    assert modules.resolve("server.ts", "node:fs") == (False, ())
    assert modules.resolve("server.ts", "../escape") == (True, ())


def test_inherited_alias_origins_cycles_and_escapes(tmp_path: Path) -> None:
    values = {
        "config/tsconfig.base.json": {
            "compilerOptions": {"paths": {"@src/*": ["../shared/*"]}}
        },
        "app/tsconfig.json": {"extends": "../config/tsconfig.base.json"},
        "bad/tsconfig.json": {
            "compilerOptions": {"paths": {"escape": ["../../outside", "./local"]}}
        },
        "cycle/tsconfig.json": {"extends": "./tsconfig.json"},
    }
    paths = []
    for name, value in values.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))
        paths.append(path)
    modules = TypeScriptModules(tmp_path, tuple(paths), (".",))
    assert modules.resolve("app/server.ts", "@src/io") == (True, ("shared/io",))
    assert modules.resolve("bad/server.ts", "escape") == (True, ())
    assert modules.resolve("cycle/server.ts", "anything") == (True, ())


def test_conditional_missing_source_does_not_certify_another_target(
    tmp_path: Path,
) -> None:
    sources = {
        "package.json": '{"name":"local", "dependencies":'
        '{"@modelcontextprotocol/sdk":"^1"},'
        '"exports":{"import":"./guard.ts","default":"./missing.ts"}}',
        "sentinel.toml": '[scanner]\nrules=["SENT-012"]\n',
        "server.ts": 'import {read} from "local";\n'
        'import {McpServer} from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'const server = new McpServer({name:"s",version:"1"});\n'
        'server.registerTool("read",{inputSchema:{}},read);',
        "guard.ts": 'export function read() { return "safe"; }',
    }
    for name, value in sources.items():
        (tmp_path / name).write_text(value)
    config = load_configuration(tmp_path, environ={}, static_only=True)
    result = run_static_scan(config, uuid4(), timestamp=NOW)
    assert any(w.code == "static_binding_unresolved" for w in result.warnings)
    assert result.summary.coverage is not None
    surface = next(
        item for item in result.summary.coverage.surfaces if item.name == "read"
    )
    assert surface.status == "unresolved" and surface.handler is None


def test_unavailable_parent_is_disclosed_without_discarding_direct_imports(
    tmp_path: Path,
) -> None:
    config = tmp_path / "tsconfig.json"
    config.write_text(
        json.dumps(
            {
                "extends": "../../outside.json",
                "compilerOptions": {
                    "paths": {"@local/*": ["./src/*"]},
                },
            }
        )
    )
    modules = TypeScriptModules(tmp_path, (config,), (".",))
    assert modules.resolve("server.ts", "@local/io") == (True, ("src/io",))
    assert modules.resolve("server.ts", "node:fs") == (False, ())
    assert len(modules.warnings) == 1
    assert "not applied" in modules.warnings[0].message
    assert "../../outside.json" in modules.warnings[0].message
