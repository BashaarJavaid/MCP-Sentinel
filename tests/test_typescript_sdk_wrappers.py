"""Source-bound SDK forwarding, including replaced and escaped methods."""

import time
from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.static.engine import _deduplicate, _finding_from_match
from sentinel.static.model import RuleRunState, TypeScriptSourceFile
from sentinel.static.rules.sent015 import TypeScriptURLFlow
from sentinel.static.typescript_discovery import TypeScriptProgram
from sentinel.static.typescript_path_flow import analyze
from tests.conftest import NOW


def source_flow(tmp_path: Path, source: str) -> RuleRunState:
    path = tmp_path / "unit.ts"
    path.write_text(source)
    program = TypeScriptProgram(
        (TypeScriptSourceFile(path, path.name, source),),
        deadline=time.monotonic() + 30,
    )
    state = RuleRunState()
    analyze(program, state, flow=TypeScriptURLFlow(program, state))
    return state


@pytest.mark.parametrize(
    ("patch", "startup", "expected"),
    [
        ("", "new App();", 1),
        (
            "const saved = Server.prototype.setRequestHandler;"
            "Server.prototype.setRequestHandler = function(schema, handler) {"
            " return saved.call(this, schema, handler); };",
            "new App();",
            1,
        ),
        (
            "const saved = Server.prototype.setRequestHandler;"
            "Server.prototype.setRequestHandler = function(schema, handler) {"
            " try { return saved.call(this, schema, handler); }"
            " catch (error) { throw error; } };",
            "new App();",
            1,
        ),
        (
            "const saved = Server.prototype.setRequestHandler;"
            "Server.prototype.setRequestHandler = function(schema, handler) {"
            " try { return saved.call(this, schema, handler); }"
            " catch (error) { if (error.message.includes('shape')) {"
            " Object.defineProperty(schema, 'shape', {value: {}});"
            " return saved.call(this, schema, handler); } throw error; } };",
            "new App();",
            2,  # Both source branches; the canonical report merges the sink.
        ),
        (
            "Server.prototype.setRequestHandler = function(schema, handler) {};",
            "new App();",
            0,
        ),
        (
            "const saved = Server.prototype.setRequestHandler;"
            "Server.prototype.setRequestHandler = function(schema, handler) {"
            " return saved.call({}, schema, handler); };",
            "new App();",
            0,
        ),
        (
            "const saved = Server.prototype.setRequestHandler;"
            "Server.prototype.setRequestHandler = function(schema, handler) {"
            " return saved.call(this, schema, () => 'replacement'); };",
            "new App();",
            0,
        ),
        (
            "const saved = Server.prototype.setRequestHandler;"
            "saved.call = unknown;"
            "Server.prototype.setRequestHandler = function(schema, handler) {"
            " return saved.call(this, schema, handler); };",
            "new App();",
            0,
        ),
        ("unknown(Server.prototype);", "new App();", 0),
        ("unknown(Server);", "new App();", 0),
        (
            'import {Server as Alias} from "@modelcontextprotocol/sdk/server/index.js";'
            "unknown(Alias);",
            "new App();",
            0,
        ),
        (
            "const saved = Server.prototype.setRequestHandler; unknown(saved);"
            "Server.prototype.setRequestHandler = function(schema, handler) {"
            " return saved.call(this, schema, handler); };",
            "new App();",
            0,
        ),
        (
            "Server.prototype.setRequestHandler = function() {};"
            "const alias = Server.prototype; unknown(alias);",
            "new App();",
            0,
        ),
        ("", "const app = new App(); unknown(app.server); app.install();", 1),
        (
            "",
            "const app = new App(); app.server.setRequestHandler = unknown;"
            "app.install();",
            1,
        ),
        ("", "", 0),
    ],
)
def test_module_class_sdk_registration_and_forwarding(
    tmp_path: Path, patch: str, startup: str, expected: int
) -> None:
    source = (
        'import {Server} from "@modelcontextprotocol/sdk/server/index.js";\n'
        'import {CallToolRequestSchema} from "@modelcontextprotocol/sdk/types.js";\n'
        'import lighthouse from "lighthouse";\n' + patch + "\nclass App {\n"
        " constructor() { this.server = new Server({name:'unit',version:'1'});"
        " this.install(); }\n"
        " install() { this.server.setRequestHandler(CallToolRequestSchema,"
        " request => this.audit(request.params.arguments.url)); }\n"
        " audit(url) { return lighthouse(url); }\n"
        "}\n" + startup
    )
    state = source_flow(tmp_path, source)
    assert len(state.matches) == expected
    if expected:
        assert len(_deduplicate(state.matches)) == 1
        assert state.matches[0].rule_id == "SENT-015"
        assert "lighthouse(url)" in state.matches[0].snippet
        assert state.matches[0].captures["flow_locations"]


def test_module_class_constructor_callbacks_keep_registered_handler(
    tmp_path: Path,
) -> None:
    state = source_flow(
        tmp_path,
        """
import {Server} from '@modelcontextprotocol/sdk/server/index.js';
import {CallToolRequestSchema} from '@modelcontextprotocol/sdk/types.js';
import lighthouse from 'lighthouse';
class App {
 private server: Server;
 constructor() {
  this.server = new Server({name: 'unit', version: '1'});
  this.install();
  this.server.onerror = error => console.error(error);
  process.on('SIGINT', async () => {
   await this.server.close();
   process.exit(0);
  });
 }
 private install() {
  this.server.setRequestHandler(CallToolRequestSchema,
   request => lighthouse(request.params.arguments.url));
 }
 async run() { await this.server.connect(transport); }
}
const app = new App();
app.run().catch(console.error);
""",
    )
    assert len(_deduplicate(state.matches)) == 1


@pytest.mark.parametrize(
    ("guard", "before", "after", "expected"),
    [
        ("", "", "", None),
        ("check(url);", "", "", "linklocal-ipv4"),
        ("check('https://example.org');", "", "", None),
        ("", "", "check(url);", None),
        ("try { check(url); } catch {}", "", "", None),
        ("check(url);", "denied.pop();", "", None),
        ("check(url);", "unknown(denied);", "", None),
        ("check(url);", "denied[1].prefix = '192.168.';", "", None),
        ("check(url);", "denied[1].mask = () => false;", "", None),
        ("check(url);", "denied[1].mask = unknown;", "", None),
        ("check(url);", "net.isIP = () => 0;", "", None),
    ],
)
def test_lighthouse_linklocal_guard_remains_narrow(
    tmp_path: Path, guard: str, before: str, after: str, expected: str | None
) -> None:
    source = (
        """
import {Server} from "@modelcontextprotocol/sdk/server/index.js";
import {CallToolRequestSchema} from "@modelcontextprotocol/sdk/types.js";
import lighthouse from "lighthouse";
import net from "node:net";
const denied = [{prefix: '10.', mask: null}, {prefix: '169.254.', mask: null}];
function deniedIP(ip) {
 for (const item of denied) {
  if (ip.startsWith(item.prefix)) {
   if (item.mask === null || item.mask(ip)) return true;
  }
 }
 return false;
}
function check(input) {
 const parsed = new URL(input);
 if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') throw Error();
 if (net.isIP(parsed.hostname)) {
  if (parsed.hostname.startsWith('127.')) return;
  if (deniedIP(parsed.hostname)) throw Error();
  return;
 }
 // Hostnames remain unresolved; this is not a broad SSRF protection claim.
}
const server = new Server({name:'unit',version:'1'});
server.setRequestHandler(CallToolRequestSchema, request => {
 const url = request.params.arguments.url;
 BEFORE
 GUARD
 const result = lighthouse(url);
 AFTER
 return result;
});
""".replace("GUARD", guard)
        .replace("BEFORE", before)
        .replace("AFTER", after)
    )
    state = source_flow(tmp_path, source)
    assert state.matches
    assert all(m.captures.get("url_guard_scope") == expected for m in state.matches)
    if expected:
        finding = _finding_from_match(_deduplicate(state.matches)[0], uuid4(), NOW)
        assert "initial literal link-local bypass" in finding.description
        assert (
            "DNS, redirects and IPv6 protection remain unestablished"
            in finding.description
        )


@pytest.mark.parametrize(
    ("prefixes", "body", "qualified"),
    [
        ("['10.', '169.254.']", "", True),
        ("['10.', '169.254.']", "break;", False),
        ("['10.', '169.254.']", "continue;", False),
        ("['10.', '169.254.']", "return false;", False),
        ("['10.', '169.254.']", "prefixes.pop();", False),
        ("['10.', '169.254.']", "unknown(prefixes);", False),
        ("unknown()", "", False),
        ("[" + "'10.'," * 31 + "'169.254.']", "", True),
        ("[" + "'10.'," * 32 + "'169.254.']", "", False),
    ],
)
def test_url_policy_loop_requires_complete_bounded_flow(
    tmp_path: Path, prefixes: str, body: str, qualified: bool
) -> None:
    state = source_flow(
        tmp_path,
        """
import {Server} from '@modelcontextprotocol/sdk/server/index.js';
import {CallToolRequestSchema} from '@modelcontextprotocol/sdk/types.js';
import lighthouse from 'lighthouse';
const prefixes = PREFIXES;
function denied(host) {
 for (const prefix of prefixes) {
  BODY
  if (host.startsWith(prefix)) return true;
 }
 return false;
}
const server = new Server({name:'unit',version:'1'});
server.setRequestHandler(CallToolRequestSchema, request => {
 const url = request.params.arguments.url;
 if (denied(new URL(url).hostname)) throw Error();
 return lighthouse(url);
});
""".replace("PREFIXES", prefixes).replace("BODY", body),
    )
    assert state.matches
    assert all(
        (m.captures.get("url_guard_scope") == "linklocal-ipv4") == qualified
        for m in state.matches
    )
