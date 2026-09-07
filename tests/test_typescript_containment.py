"""Containment checks follow the actual TypeScript path and enforced branches."""

import time
from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.finding import FileLocation
from sentinel.static.engine import run_static_scan
from sentinel.static.model import RuleRunState, TypeScriptSourceFile
from sentinel.static.typescript_discovery import TypeScriptProgram
from sentinel.static.typescript_path_flow import analyze
from tests.conftest import NOW


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("return fs.readFile(input);", 1),
        ("const read = fs.readFile; return read(input);", 1),
        ("const files = fs; return files.readFile(input);", 1),
        ("const p = path.resolve(ROOT, input); return fs.readFile(p);", 1),
        (
            "const p = await fs.realpath(input); "
            "if (!p.startsWith(ROOT)) throw new Error(); return fs.readFile(p);",
            1,
        ),
        (
            "const p = await fs.realpath(input); const root = await fs.realpath(ROOT); "
            "const rel = path.relative(root, p); "
            'if (rel.startsWith("..") || path.isAbsolute(rel)) throw new Error(); '
            "return fs.readFile(p);",
            0,
        ),
        (
            "const p = await fs.realpath(input); const root = await fs.realpath(ROOT); "
            "const rel = path.relative(root, p); "
            'const outside = rel.startsWith("..") || path.isAbsolute(rel); '
            "if (outside) throw new Error(); return fs.readFile(p);",
            0,
        ),
        (
            "const p = await fs.realpath(input); const root = await fs.realpath(ROOT); "
            'const rel = path.relative(root, p); rel.startsWith(".."); '
            "path.isAbsolute(rel); return fs.readFile(p);",
            1,
        ),
        (
            'const p = await fs.realpath("/other"); '
            "const root = await fs.realpath(ROOT); const rel = path.relative(root, p); "
            'if (rel.startsWith("..") || path.isAbsolute(rel)) throw new Error(); '
            "return fs.readFile(input);",
            1,
        ),
        (
            "const p = await fs.realpath(input); const root = await fs.realpath(ROOT); "
            "const rel = path.relative(root, p); "
            'if (rel.startsWith("..") || path.isAbsolute(rel)) throw new Error(); '
            "return fs.readFile(input);",
            1,
        ),
    ],
)
def test_enforced_relevant_containment(
    tmp_path: Path, body: str, expected: int
) -> None:
    source = (
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import fs from "node:fs/promises"; import path from "node:path";\n'
        'const ROOT = "/workspace"; '
        'const server = new McpServer({name:"test", version:"1"});\n'
        f"async function read(input: string) {{ {body} }}\n"
        'server.registerTool("read", {inputSchema: {input: z.string()}}, read);\n'
        'throw new Error("never execute target source");\n'
    )
    file = tmp_path / "server.ts"
    file.write_text(source)
    program = TypeScriptProgram(
        (TypeScriptSourceFile(file, file.name, source),), deadline=time.monotonic() + 15
    )
    state = RuleRunState()
    analyze(program, state)
    assert len(state.matches) == expected
    for match in state.matches:
        assert match.rule_id == "SENT-012" and match.path == "server.ts"
        assert "read" in match.snippet or "writeFile" in match.snippet


@pytest.mark.parametrize(
    "body",
    [
        "return paths.map(async (p) => fs.readFile(p));",
        "for (const p of paths) { await fs.readFile(p); }",
        "try { const p = paths[0]; return await fs.readFile(p); } "
        'catch { return "missing"; }',
        'try { return "ok"; } finally { await fs.readFile(paths[0]); }',
    ],
)
def test_destructured_collection_callbacks_and_exception_paths(
    tmp_path: Path, body: str
) -> None:
    source = (
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import fs from "node:fs/promises";\n'
        'const server = new McpServer({name:"test",version:"1"});\n'
        'server.registerTool("read", {inputSchema: {paths: z.array(z.string())}}, '
        f"async ({{paths}}) => {{ {body} }});\n"
    )
    path = tmp_path / "server.ts"
    path.write_text(source)
    program = TypeScriptProgram(
        (TypeScriptSourceFile(path, path.name, source),), deadline=time.monotonic() + 15
    )
    state = RuleRunState()
    analyze(program, state)
    assert len(state.matches) == 1


def test_low_level_dispatch_follows_destructured_request(tmp_path: Path) -> None:
    source = (
        'import { Server } from "@modelcontextprotocol/sdk/server/index.js";\n'
        'import { CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";\n'
        'import fs from "node:fs/promises";\n'
        'const server = new Server({name:"test",version:"1"}, '
        "{capabilities:{tools:{}}});\n"
        "server.setRequestHandler(CallToolRequestSchema, async (request) => {\n"
        "const { name, arguments: args } = request.params;\n"
        'switch(name) { case "read": { const p = args.path; return fs.readFile(p); }\n'
        "default: throw new Error(); } });\n"
    )
    path = tmp_path / "server.ts"
    path.write_text(source)
    program = TypeScriptProgram(
        (TypeScriptSourceFile(path, path.name, source),), deadline=time.monotonic() + 15
    )
    state = RuleRunState()
    analyze(program, state)
    assert len(state.matches) == 1


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_scan_preserves_imported_handler_and_sink_locations(
    tmp_path: Path, newline: str
) -> None:
    (tmp_path / "package.json").write_text(
        '{"dependencies":{"@modelcontextprotocol/sdk":"^1"}}'
    )
    (tmp_path / "server.ts").write_text(
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import { read, schema } from "./handler.js";\n'
        'const server = new McpServer({name:"test",version:"1"});\n'
        'server.registerTool("read", {inputSchema:schema}, read);\n'
    )
    (tmp_path / "handler.ts").write_text(
        'import fs from "node:fs/promises"; import { z } from "zod";\n'
        "export const schema = {path:z.string()};\n"
        "export async function read({path}: {path:string}): Promise<string> {\n"
        'return fs.readFile(path, "utf8");\n}\n'
    )
    for path in tmp_path.glob("*.ts"):
        source = path.read_text(encoding="utf-8")
        source = "// π and 😀 preserve source coordinates\n" + source
        path.write_bytes(source.replace("\n", newline).encode("utf-8"))
    configuration = load_configuration(
        tmp_path, environ={}, static_only=True, cli_overrides={"rules": ("SENT-012",)}
    )
    result = run_static_scan(configuration, uuid4(), timestamp=NOW)
    assert len(result.findings) == 1
    assert isinstance(result.findings[0].location, FileLocation)
    assert result.findings[0].location.path == "handler.ts"
    assert result.findings[0].location.range.start_line == 5
    assert result.summary.coverage is not None
    surface = next(
        item for item in result.summary.coverage.surfaces if item.name == "read"
    )
    assert surface.location.path == "server.ts"
    assert surface.handler is not None and surface.handler.path == "handler.ts"
    assert surface.location.range.start_line == 5
    assert surface.handler.range.start_line == 4
    assert surface.status == "recognized" and surface.examined_rule_ids == ("SENT-012",)


@pytest.mark.parametrize("guarded", ["p", "unrelated"])
def test_imported_boolean_guard_tracks_argument_identity(
    tmp_path: Path, guarded: str
) -> None:
    sources = {
        "server.ts": "import { McpServer } "
        'from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import { isInside } from "./guard.js"; import fs from "node:fs/promises";\n'
        'const server = new McpServer({name:"test",version:"1"});\n'
        'server.registerTool("read", {inputSchema:{input:z.string()}}, '
        "async ({input}) => {\n"
        "const p = await fs.realpath(input); "
        'const root = await fs.realpath("/allowed");\n'
        'const unrelated = await fs.realpath("/allowed/fixed");\n'
        f"if (!isInside({guarded}, root)) throw new Error(); "
        "return fs.readFile(p); });\n",
        "guard.ts": 'import path from "node:path";\n'
        "export function isInside(value: string, root: string) {\n"
        "const rel = path.relative(root, value);\n"
        'return !rel.startsWith("..") && !path.isAbsolute(rel); }\n',
    }
    files = []
    for name, source in sources.items():
        path = tmp_path / name
        path.write_text(source)
        files.append(TypeScriptSourceFile(path, name, source))
    program = TypeScriptProgram(tuple(files), deadline=time.monotonic() + 15)
    state = RuleRunState()
    analyze(program, state)
    assert bool(state.matches) == (guarded == "unrelated")


def test_sdk_second_argument_is_injected_context(tmp_path: Path) -> None:
    source = (
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import fs from "node:fs/promises";\n'
        'const server = new McpServer({name:"test",version:"1"});\n'
        'server.registerTool("read", {inputSchema:{path:z.string()}}, '
        "async ({path}, ctx) => { fs.readFile(ctx.sessionId); "
        "return fs.readFile(path); });\n"
    )
    path = tmp_path / "server.ts"
    path.write_text(source, encoding="utf-8")
    state = RuleRunState()
    analyze(
        TypeScriptProgram(
            (TypeScriptSourceFile(path, path.name, source),),
            deadline=time.monotonic() + 15,
        ),
        state,
    )
    assert len(state.matches) == 1
    assert state.matches[0].snippet == "fs.readFile(path)"


@pytest.mark.parametrize(
    "check,expected",
    [
        ("p.startsWith(root + path.sep)", 0),
        ("p === root || p.startsWith(root + path.sep)", 0),
        ("p.startsWith(root)", 1),
        ('p.startsWith(root + "suffix")', 1),
        ("other.startsWith(root + path.sep)", 1),
    ],
)
def test_normalizing_helper_and_component_safe_prefix(
    tmp_path: Path, check: str, expected: int
) -> None:
    source = (
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import fs from "node:fs/promises"; import path from "node:path";\n'
        'const server = new McpServer({name:"test",version:"1"});\n'
        "function normalize(p: string) { return path.normalize(p); }\n"
        "function inside(p: string, root: string, other: string) { return "
        + check
        + "; }\n"
        'server.registerTool("read", {inputSchema:{input:z.string()}}, '
        "async ({input}) => {\n"
        "const p = await fs.realpath(input); "
        'const root = await fs.realpath("/allowed");\n'
        'const other = await fs.realpath("/allowed/fixed");\n'
        "if (!inside(normalize(p), normalize(root), other)) throw new Error();\n"
        "return fs.readFile(p); });\n"
    )
    path = tmp_path / "server.ts"
    path.write_text(source, encoding="utf-8")
    state = RuleRunState()
    analyze(
        TypeScriptProgram(
            (TypeScriptSourceFile(path, path.name, source),),
            deadline=time.monotonic() + 15,
        ),
        state,
    )
    assert len(state.matches) == expected


@pytest.mark.parametrize(
    ("method", "expected"),
    [("some", 0), ("every", 1), ("map", 1), ("filter", 1), ("find", 1)],
)
def test_collection_guard_requires_successful_member(
    tmp_path: Path, method: str, expected: int
) -> None:
    test_enforced_relevant_containment(
        tmp_path,
        "const p = await fs.realpath(input); "
        "const roots = [await fs.realpath(ROOT)]; "
        f"const allowed = roots.{method}(root => "
        "p === root || p.startsWith(root + path.sep)); "
        "if (!allowed) throw new Error(); return fs.readFile(p);",
        expected,
    )


@pytest.mark.parametrize("boundary", ["component", "bare", "unrelated", "discarded"])
def test_normalized_collection_helper_protects_exact_real_path(
    tmp_path: Path,
    boundary: str,
) -> None:
    predicate = "p === root || p.startsWith(root + path.sep)"
    if boundary == "bare":
        predicate = "p.startsWith(root)"
    checked = 'await fs.realpath("/other")' if boundary == "unrelated" else "p"
    check = f"within({checked}, roots)"
    enforcement = (
        check + ";" if boundary == "discarded" else f"if (!{check}) throw new Error();"
    )
    test_enforced_relevant_containment(
        tmp_path,
        "function within(value, dirs) { "
        "const p = path.resolve(path.normalize(value)); "
        "return dirs.some(dir => { const root = path.resolve(path.normalize(dir)); "
        f"return {predicate};" + " }); } "
        "const roots = [path.resolve(ROOT)]; "
        "const p = await fs.realpath(input); "
        + enforcement
        + " return fs.readFile(p);",
        0 if boundary == "component" else 1,
    )


@pytest.mark.parametrize("parent", ["checked", "unchecked", "unrelated", "replaced"])
def test_new_file_requires_lexical_and_real_parent_containment(
    tmp_path: Path,
    parent: str,
) -> None:
    checked = (
        'await fs.realpath("/other")'
        if parent == "unrelated"
        else "await fs.realpath(path.dirname(p))"
    )
    guard = (
        (
            "if (!parent.startsWith(root + path.sep) && parent !== root) "
            "throw new Error();"
        )
        if parent != "unchecked"
        else ""
    )
    test_enforced_relevant_containment(
        tmp_path,
        "const root = await fs.realpath(ROOT); "
        "let p = path.resolve(ROOT, input); "
        "if (!p.startsWith(root + path.sep) && p !== root) throw new Error(); "
        f"const parent = {checked}; "
        + guard
        + ("p = input;" if parent == "replaced" else "")
        + 'return fs.writeFile(p, "safe test content");',
        0 if parent == "checked" else 1,
    )


@pytest.mark.parametrize("root_branch", ["guarded", "unguarded"])
def test_root_directory_special_case_requires_the_matching_allowed_root(
    tmp_path: Path,
    root_branch: str,
) -> None:
    branch = (
        "if (root === path.sep) return p.startsWith(path.sep);"
        if root_branch == "guarded"
        else "return p.startsWith(path.sep);"
    )
    test_enforced_relevant_containment(
        tmp_path,
        "const p = await fs.realpath(input); const root = await fs.realpath(ROOT); "
        "const within = () => { "
        + branch
        + "return p === root || p.startsWith(root + path.sep); }; "
        "if (!within()) throw new Error(); return fs.readFile(p);",
        0 if root_branch == "guarded" else 1,
    )


def test_replaced_captured_root_cannot_exempt_path(tmp_path: Path) -> None:
    test_enforced_relevant_containment(
        tmp_path,
        "const p = await fs.realpath(input); let root = await fs.realpath(ROOT); "
        "function within() { return p === root || p.startsWith(root + path.sep); } "
        "root = p; if (!within()) throw new Error(); return fs.readFile(p);",
        1,
    )


def test_parent_guard_for_different_root_cannot_exempt_path(tmp_path: Path) -> None:
    test_enforced_relevant_containment(
        tmp_path,
        'const root = await fs.realpath(ROOT); '
        'const other = await fs.realpath("/else"); '
        "const p = path.resolve(ROOT, input); "
        "if (!p.startsWith(root + path.sep)) throw new Error(); "
        "const parent = await fs.realpath(path.dirname(p)); "
        "if (!parent.startsWith(other + path.sep)) throw new Error(); "
        'return fs.writeFile(p, "test");',
        1,
    )
