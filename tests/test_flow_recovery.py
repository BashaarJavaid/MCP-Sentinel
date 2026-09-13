"""Synthetic startup, import and checked-return regressions; no target execution."""

import time
from pathlib import Path

import pytest

from sentinel.static.model import RuleRunState, TypeScriptSourceFile
from sentinel.static.rules.sent012 import analyze as python_paths
from sentinel.static.rules.sent015 import URLFlow
from sentinel.static.typescript_discovery import TypeScriptProgram
from sentinel.static.typescript_path_flow import analyze as typescript_paths
from tests.test_python_discovery import program


def ts_scan(tmp_path: Path, sources: dict[str, str]) -> RuleRunState:
    files = []
    for name, source in sources.items():
        path = tmp_path / name
        path.write_text(source)
        files.append(TypeScriptSourceFile(path, name, source))
    state = RuleRunState()
    typescript_paths(
        TypeScriptProgram(tuple(files), deadline=time.monotonic() + 20), state
    )
    return state


def test_imported_class_constructed_by_actual_startup(tmp_path: Path) -> None:
    state = ts_scan(
        tmp_path,
        {
            "entry.ts": "import {Application} from './app';\n"
            "async function main() { const app = new Application(); app.start(); }\n"
            "main().catch(console.error);\n",
            "app.ts": "import {Server} from '@modelcontextprotocol/s"
            "dk/server/index.js';\n"
            "import {CallToolRequestSchema} from '@modelco"
            "ntextprotocol/sdk/types.js';\n"
            "import fs from 'node:fs';\n"
            "export class Application { server; constructor() {\n"
            "this.server = new Server({name:'unit',version:'1'}); this.register(); }\n"
            "register() { this.server.setRequestHandler(Ca"
            "llToolRequestSchema, request =>\n"
            "fs.readFileSync(request.params.arguments.path)); } start() {} }\n",
        },
    )
    assert len(state.matches) == 1


def test_checked_record_preserves_lexical_component_boundary(tmp_path: Path) -> None:
    state = ts_scan(
        tmp_path,
        {
            "server.ts": """
import {McpServer} from '@modelcontextprotocol/sdk/server/mcp.js';
import fs from 'node:fs'; import path from 'node:path';
const server = new McpServer({name:'unit',version:'1'});
function check(input, root) {
  try {
    const output = path.resolve(root, input);
    const prefix = path.resolve(root) + path.sep;
    if (!output.startsWith(prefix) && output !== path.resolve(root))
      return {safe:false, output};
    return {safe:true, output};
  } catch { return {safe:false, output:''}; }
}
server.registerTool('write', {}, ({input}) => {
  const checked = check(input, '/srv/unit');
  if (!checked.safe) return;
  fs.writeFileSync(checked.output, 'data');
});
"""
        },
    )
    assert len(state.matches) == 1
    assert state.matches[0].captures.get("containment_gap") == "physical"


def test_function_local_pathlib_import_reaches_actual_write() -> None:
    state = RuleRunState()
    python_paths(
        program(
            {
                "server.py": """
@mcp.tool()
def export(output):
    from pathlib import Path
    destination = Path(output) / 'bundle' / 'manifest.json'
    destination.write_text('data')
"""
            }
        ),
        state,
    )
    assert len(state.matches) == 1


def test_available_optional_httpx_import_reaches_actual_request() -> None:
    index = program(
        {
            "server.py": """
try:
    import httpx
except ImportError:
    httpx = None
@mcp.tool()
async def fetch(url):
    if httpx is None:
        return 'unavailable'
    async with httpx.AsyncClient() as client:
        return await client.get(url)
"""
        }
    )
    state = RuleRunState()
    python_paths(index, state, flow=URLFlow(index, state, time.monotonic() + 20))
    assert len(state.matches) == 1


@pytest.mark.parametrize(
    "edit",
    [
        "",
        "Path = replacement",
        "unknown(Path)",
        "Path = None",
    ],
)
def test_local_import_identity_requires_intact_value(edit: str) -> None:
    state = RuleRunState()
    python_paths(
        program(
            {
                "server.py": f"""
@mcp.tool()
def export(output):
    from pathlib import Path
    {edit}
    Path(output).write_text('data')
"""
            }
        ),
        state,
    )
    assert len(state.matches) == (0 if edit else 1)


@pytest.mark.parametrize(
    "body, expected",
    [
        ("if httpx is None: return", 1),
        ("if httpx is not None:\n        return\n", 0),
        ("pass", 0),
        ("if httpx is None: pass", 0),
        ("if httpx is None: return\n    httpx = replacement", 0),
        ("if httpx is None: return\n    httpx.AsyncClient = replacement", 0),
        ("if httpx is None: return\n    unknown(httpx)", 0),
    ],
)
def test_optional_import_requires_available_unmodified_branch(
    body: str, expected: int
) -> None:
    index = program(
        {
            "server.py": f"""
try:
    import httpx
except ImportError:
    httpx = None
@mcp.tool()
async def fetch(url):
    {body}
    async with httpx.AsyncClient() as client:
        return await client.get(url)
"""
        }
    )
    state = RuleRunState()
    python_paths(index, state, flow=URLFlow(index, state, time.monotonic() + 20))
    assert len(state.matches) == expected


@pytest.mark.parametrize(
    "destination, expected",
    [
        ("checked", 0),
        ("Path(output)", 1),
        ("Path(other)", 1),
    ],
)
def test_home_guard_does_not_protect_reconstructed_original(
    destination: str, expected: int
) -> None:
    state = RuleRunState()
    python_paths(
        program(
            {
                "server.py": f"""
@mcp.tool()
def export(output, other):
    from pathlib import Path
    checked = Path(output).resolve()
    home = Path.home().resolve()
    try:
        checked.relative_to(home)
    except ValueError:
        return
    destination = {destination}
    destination.write_text('data')
"""
            }
        ),
        state,
    )
    assert len(state.matches) == expected


@pytest.mark.parametrize(
    "startup, expected, module_tail",
    [
        ("main().catch(console.error);", 1, ""),
        ("", 0, ""),
        ("Application.prototype.register = () => {}; main();", 0, ""),
        ("unknown(Application); main();", 0, ""),
        ("main();", 0, "unknown(Application);"),
        ("main();", 0, "Application.prototype.register = () => {};"),
    ],
)
def test_imported_constructor_requires_actual_intact_startup(
    tmp_path: Path, startup: str, expected: int, module_tail: str
) -> None:
    state = ts_scan(
        tmp_path,
        {
            "entry.ts": "import {Application} from './app';\n"
            "async function main() { new Application(); }\n" + startup,
            "app.ts": "import {Server} from '@modelcontextprotocol/s"
            "dk/server/index.js';\n"
            "import {CallToolRequestSchema} from '@modelco"
            "ntextprotocol/sdk/types.js';\n"
            "import fs from 'node:fs';\n"
            "export class Application { server; constructor() {\n"
            "this.server = new Server({name:'unit',version:'1'}); this.register(); }\n"
            "register() { this.server.setRequestHandler(Ca"
            "llToolRequestSchema, request =>\n"
            "fs.readFileSync(request.params.arguments.path)); } }\n" + module_tail,
        },
    )
    assert len(state.matches) == expected


@pytest.mark.parametrize(
    "guard, caller, qualified",
    [
        (
            "!output.startsWith(prefix) && output !== path.resolve(root)",
            "if (!checked.safe) return;",
            True,
        ),
        ("!output.startsWith(path.resolve(root))", "if (!checked.safe) return;", False),
        ("!output.startsWith(prefix) && output !== path.resolve(root)", "", False),
        (
            "!output.startsWith(prefix) && output !== path.resolve(root)",
            "checked.safe = true; if (!checked.safe) return;",
            False,
        ),
        (
            "!output.startsWith(prefix) && output !== path.resolve(root)",
            "unknown(checked); if (!checked.safe) return;",
            False,
        ),
        (
            "!output.startsWith(prefix) && output !== path.resolve(root)",
            "if (!checked.safe) return; checked.output = other;",
            False,
        ),
    ],
)
def test_compound_record_guard_is_checked_and_unmodified(
    tmp_path: Path, guard: str, caller: str, qualified: bool
) -> None:
    state = ts_scan(
        tmp_path,
        {
            "server.ts": f"""
import {{McpServer}} from '@modelcontextprotocol/sdk/server/mcp.js';
import fs from 'node:fs'; import path from 'node:path';
const server = new McpServer({{name:'unit',version:'1'}});
function check(input, root) {{
  try {{
    const output = path.resolve(root, input);
    const prefix = path.resolve(root) + path.sep;
    if ({guard}) return {{safe:false, output}};
    return {{safe:true, output}};
  }} catch {{ return {{safe:false, output:''}}; }}
}}
server.registerTool('write', {{}}, ({{input, other}}) => {{
  const checked = check(input, '/srv/unit');
  {caller}
  fs.writeFileSync(checked.output, 'data');
}});
"""
        },
    )
    assert len(state.matches) == 1
    assert (state.matches[0].captures.get("containment_gap") == "physical") is qualified


@pytest.mark.parametrize("guarded", [False, True])
def test_startup_dictionary_forwarding_and_checked_read(
    tmp_path: Path, guarded: bool
) -> None:
    state = ts_scan(
        tmp_path,
        {
            "entry.ts": "import {Application} from './app';\n"
            "async function main() { const app = new Application(); } main();\n",
            "app.ts": "import {Server} from '@modelcontextprotocol/s"
            "dk/server/index.js';\n"
            "import {CallToolRequestSchema} from '@modelco"
            "ntextprotocol/sdk/types.js';\n"
            "import {Handler} from './handler';\n"
            "export class Application { server; handler; constructor() {\n"
            "this.server = new Server({name:'unit',version"
            ":'1'}); this.handler = new Handler();\n"
            "this.server.setRequestHandler(CallToolRequestSchema, request =>\n"
            "this.handler.call(request.params.name, reques"
            "t.params.arguments ?? {})); } }\n",
            "handler.ts": "import {operations} from './read';\n"
            "export class Handler { call(name, args) { switch(name) {\n"
            "case 'read': return operations.read(args); de"
            "fault: throw new Error(); } } }\n",
            "read.ts": "import fs from 'node:fs/promises'; import pat"
            "h from 'node:path';\n"
            "async function check(input) { const output = await fs.realpath(input); "
            "const roots = [path.resolve('/srv/unit')]; "
            "if (!roots.some(root => output === root || ou"
            "tput.startsWith(root + path.sep))) throw new "
            "Error(); "
            "return output; }\n"
            "async function read(args) { const {path: input} = args; "
            + (
                "const output = await check(input); "
                if guarded
                else "const output = input; "
            )
            + "return await Promise.race([fs.readFile(output"
            ", 'utf8'), new Promise((_, reject) => setTime"
            "out(reject, 30000))]); }\n"
            "export const operations = {read};\n",
        },
    )
    assert len(state.matches) == (0 if guarded else 1)


@pytest.mark.parametrize(
    "checked, caught, qualified",
    [
        ("url", "return", True),
        ("other", "return", False),
        ("url", "pass", False),
    ],
)
def test_optional_client_retains_literal_guard_and_dns_limit(
    checked: str, caught: str, qualified: bool
) -> None:
    index = program(
        {
            "server.py": f"""
import ipaddress
from urllib.parse import urlsplit
try:
    import httpx
except ImportError:
    httpx = None
def blocked(ip):
    return (ip.is_private or ip.is_loopback or ip.is_link_local or
            ip.is_reserved or ip.is_multicast or ip.is_unspecified)
async def check(url):
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https'): raise ValueError()
    try:
        address = ipaddress.ip_address(parsed.hostname)
    except ValueError:
        address = None
    if address is not None:
        if blocked(address): raise ValueError()
        return
    try:
        await resolver(parsed.hostname)
    except OSError:
        return
@mcp.tool()
async def fetch(url, other):
    if httpx is None: return
    try:
        await check({checked})
    except ValueError:
        {caught}
    async with httpx.AsyncClient(follow_redirects=False) as client:
        return await client.get(url)
"""
        }
    )
    state = RuleRunState()
    python_paths(index, state, flow=URLFlow(index, state, time.monotonic() + 20))
    assert len(state.matches) == 1
    assert (
        state.matches[0].captures.get("url_guard_scope") == "literal-ipv4"
    ) is qualified


@pytest.mark.parametrize("fallback", ["path.resolve(input)", "input"])
def test_infinite_canonicalization_loop_keeps_all_return_alternatives(
    tmp_path: Path, fallback: str
) -> None:
    state = ts_scan(
        tmp_path,
        {
            "server.ts": f"""
import {{McpServer}} from '@modelcontextprotocol/sdk/server/mcp.js';
import fs from 'node:fs'; import path from 'node:path';
const server = new McpServer({{name:'unit',version:'1'}});
function canonical(input) {{
  let current = path.resolve(input);
  const suffix = [];
  for (;;) {{
    try {{
      const real = fs.realpathSync(current);
      return suffix.length ? path.join(real, ...suffix.reverse()) : real;
    }} catch {{
      const parent = path.dirname(current);
      if (parent === current) return {fallback};
      suffix.push(path.basename(current));
      current = parent;
    }}
  }}
}}
server.registerTool('read', {{}}, ({{input}}) => {{
  const output = canonical(input);
  const root = path.resolve('/srv/unit');
  if (!(output === root || output.startsWith(root + path.sep))) throw new Error();
  return fs.readFileSync(output);
}});
"""
        },
    )
    assert len(state.matches) == 1
    assert (state.matches[0].captures.get("containment_gap") == "physical") is (
        fallback == "path.resolve(input)"
    )


@pytest.mark.parametrize("available", [False, True])
def test_optional_global_availability_reaches_included_helpers(available: bool) -> None:
    index = program(
        {
            "server.py": f"""
try:
    import httpx
except ImportError:
    httpx = None
async def request(client, url):
    return await client.get(url)
async def load(url):
    async with httpx.AsyncClient() as client:
        return await request(client, url)
@mcp.tool()
async def fetch(url):
    {"if httpx is None: return" if available else "pass"}
    return await load(url)
"""
        }
    )
    state = RuleRunState()
    python_paths(index, state, flow=URLFlow(index, state, time.monotonic() + 20))
    assert len(state.matches) == int(available)


@pytest.mark.parametrize(
    "setup, constructor, expected",
    [
        ("import pathlib as paths", "paths.Path", 1),
        ("import pathlib as paths\n    Local = paths.Path", "Local", 1),
        ("import pathlib as paths\n    paths.Path = replacement", "paths.Path", 0),
        ("import pathlib as paths\n    unknown(paths.Path)", "paths.Path", 0),
        (
            "import pathlib as paths\n    paths.Path = replacement\n"
            "    from pathlib import Path",
            "Path",
            0,
        ),
        (
            "from pathlib import Path\n    unknown(Path)\n"
            "    from pathlib import Path as Local",
            "Local",
            0,
        ),
    ],
)
def test_local_import_aliases_retain_namespace_mutations(
    setup: str, constructor: str, expected: int
) -> None:
    state = RuleRunState()
    python_paths(
        program(
            {
                "server.py": f"""
@mcp.tool()
def export(output):
    {setup}
    {constructor}(output).write_text('data')
"""
            }
        ),
        state,
    )
    assert len(state.matches) == expected


@pytest.mark.parametrize(
    "fallback, mutate, qualified",
    [
        ("[path.resolve('/srv/unit')]", "", True),
        ("[]", "", False),
        ("[path.resolve('/srv/unit')]", "unknown(roots);", False),
        ("[path.resolve('/srv/unit')]", "const alias = roots; unknown(alias);", False),
        ("[path.resolve('/srv/unit')]", "roots.length = 0;", False),
        ("[path.resolve('/srv/unit')]", "roots = roots.map(root => root);", True),
        ("[path.resolve('/srv/unit')]", "roots = roots.filter(() => false);", False),
        ("[path.resolve('/srv/unit')]", "roots = roots.flatMap(() => []);", False),
        ("[path.resolve('/srv/unit')]", "roots = roots.find(() => true);", False),
    ],
)
def test_operator_root_fallback_requires_nonempty_collection(
    tmp_path: Path, fallback: str, mutate: str, qualified: bool
) -> None:
    state = ts_scan(
        tmp_path,
        {
            "server.ts": f"""
import {{McpServer}} from '@modelcontextprotocol/sdk/server/mcp.js';
import fs from 'node:fs'; import path from 'node:path';
const server = new McpServer({{name:'unit',version:'1'}});
function configured() {{
  const value = process.env.UNIT_ROOTS;
  if (value && value.trim()) return value.split(path.delimiter)
    .filter(Boolean).map(root => path.resolve(root));
  return [];
}}
function rootsForRead() {{
  const optional = configured();
  if (optional.length) return optional;
  return {fallback};
}}
server.registerTool('read', {{}}, ({{input}}) => {{
  const output = path.resolve(input);
  let roots = rootsForRead().map(root => path.resolve(root));
  {mutate}
  if (roots.length > 0 && !roots.some(root => output === root ||
      output.startsWith(root + path.sep))) throw new Error();
  return fs.readFileSync(output);
}});
"""
        },
    )
    assert len(state.matches) == 1
    assert (state.matches[0].captures.get("containment_gap") == "physical") is qualified


@pytest.mark.parametrize(
    "checked, catch, change, qualified",
    [
        ("output", "return", "", True),
        ("other", "return", "", False),
        ("output", "pass", "", False),
        ("output", "return", "output = other", False),
        ("output", "return", "output = unknown(output)", False),
        ("output", "return", "os.chdir(other)", True),
    ],
)
def test_manifest_reconstruction_keeps_only_initial_copy_evidence(
    checked: str, catch: str, change: str, qualified: bool
) -> None:
    from uuid import uuid4

    from sentinel.static.engine import _finding_from_match
    from tests.conftest import NOW

    state = RuleRunState()
    python_paths(
        program(
            {
                "server.py": f"""
import os
@mcp.tool()
def export(output, other):
    from pathlib import Path
    checked = Path({checked}).resolve()
    home = Path.home().resolve()
    try:
        checked.relative_to(home)
    except ValueError:
        {catch}
    {change}
    destination = Path(output) / 'bundle' / 'manifest.json'
    destination.write_text('data')
"""
            }
        ),
        state,
    )
    assert len(state.matches) == 1
    assert (
        state.matches[0].captures.get("containment_gap") == "resolved-copy"
    ) is qualified
    finding = _finding_from_match(state.matches[0], uuid4(), NOW)
    assert (
        "equivalence and containment at filesystem use are not established"
        in finding.description
    ) is qualified


@pytest.mark.parametrize(
    "effect",
    [
        "unknown();",
        "fs.realpathSync = replacement;",
        "break;",
    ],
)
def test_path_loop_summary_rejects_unproven_effects(
    tmp_path: Path, effect: str
) -> None:
    state = ts_scan(
        tmp_path,
        {
            "server.ts": f"""
import {{McpServer}} from '@modelcontextprotocol/sdk/server/mcp.js';
import fs from 'node:fs';
const server = new McpServer({{name:'unit',version:'1'}});
function canonical(input) {{
  for (;;) {{
    try {{ return fs.realpathSync(input); }} catch {{ {effect} }}
  }}
}}
server.registerTool('read', {{}}, ({{input}}) => fs.readFileSync(canonical(input)));
"""
        },
    )
    assert any(
        "unsupported control flow" in warning.message for warning in state.warnings
    )
    assert not any(
        "unbounded loop state widened" in warning.message for warning in state.warnings
    )
