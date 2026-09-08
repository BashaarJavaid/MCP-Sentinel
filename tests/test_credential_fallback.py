"""Caller credential absence must not select operator credentials across HTTP."""

from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.finding import StaticEvidence
from sentinel.static.engine import run_static_scan
from tests.conftest import NOW, make_target


@pytest.mark.parametrize(
    "selection",
    [
        "token = token || process.env.OPERATOR_TOKEN;",
        "token = token ?? process.env.OPERATOR_TOKEN;",
        "if (!token) token = process.env.OPERATOR_TOKEN;",
    ],
)
@pytest.mark.parametrize(
    ("guard", "expected"),
    [
        ("", 1),
        ("if (!token) throw new Error('missing');", 0),
        ("if (!token) return res.sendStatus(401);", 0),
        ("if (!other) throw new Error('missing');", 1),
        ("if (!token) res.sendStatus(401);", 1),
        ("if (!token) throw new Error('missing'); token = other;", 1),
    ],
)
def test_typescript_http_credential_selection(
    tmp_path: Path, guard: str, expected: int, selection: str
) -> None:
    root = tmp_path / "target"
    root.mkdir()
    (root / "package.json").write_text(
        '{"dependencies":{"@modelcontextprotocol/sdk":"1.0.0"}}',
        encoding="utf-8",
    )
    (root / "server.ts").write_text(
        'import express from "express";\nconst app = express();\n'
        'app.post("/data", async (req, res) => {\n'
        "  let token = req.headers.authorization;\n"
        "  const other = req.headers.other;\n"
        f"  {guard}\n"
        f"  {selection}\n"
        '  return fetch("https://api.example.com", '
        "{headers: {Authorization: token}});\n"
        "});\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    findings = run_static_scan(config, uuid4(), timestamp=NOW).findings
    assert len(findings) == expected


@pytest.mark.parametrize(
    ("setup", "parameters", "sink", "expected"),
    [
        ("", "req, res", "fetch", 1),
        ('import send from "node-fetch";', "req, res", "send", 1),
        ("express = unknown;", "req, res", "fetch", 0),
        ("app = unknown;", "req, res", "fetch", 0),
        ("const process = custom;", "req, res", "fetch", 0),
        ("", "req, res, process", "fetch", 0),
        ("const fetch = custom;", "req, res", "fetch", 0),
    ],
)
def test_typescript_http_source_and_sink_bindings(
    tmp_path: Path, setup: str, parameters: str, sink: str, expected: int
) -> None:
    root = tmp_path / "target"
    root.mkdir()
    (root / "package.json").write_text(
        '{"dependencies":{"@modelcontextprotocol/sdk":"1.0.0"}}',
        encoding="utf-8",
    )
    (root / "server.ts").write_text(
        'import express from "express"; let app = express();\n'
        + setup
        + f'\napp.post("/data", async ({parameters}) => {{\n'
        "const token = req.headers.authorization || process.env.OPERATOR_TOKEN;\n"
        f'return {sink}("https://api.example.com", '
        "{headers: {Authorization: token}});\n"
        "});\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    assert len(run_static_scan(config, uuid4(), timestamp=NOW).findings) == expected


def test_typescript_imported_http_handler(tmp_path: Path) -> None:
    root = tmp_path / "target"
    root.mkdir()
    (root / "package.json").write_text(
        '{"dependencies":{"@modelcontextprotocol/sdk":"1.0.0"}}',
        encoding="utf-8",
    )
    (root / "server.ts").write_text(
        'import express from "express"; import { handle } from "./barrel.js";\n'
        'const app = express(); app.post("/data", handle);\n',
        encoding="utf-8",
    )
    (root / "barrel.ts").write_text(
        'export { handler as handle } from "./handler.js";\n', encoding="utf-8"
    )
    (root / "handler.ts").write_text(
        "export async function handler(req, res) {\n"
        "const token = req.headers.authorization || process.env.OPERATOR_TOKEN;\n"
        'return fetch("https://api.example.com", {headers:{Authorization:token}});\n'
        "}\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    findings = run_static_scan(config, uuid4(), timestamp=NOW).findings
    assert len(findings) == 1


def test_typescript_tool_input_does_not_establish_http_authority(
    tmp_path: Path,
) -> None:
    root = tmp_path / "target"
    root.mkdir()
    (root / "package.json").write_text(
        '{"dependencies":{"@modelcontextprotocol/sdk":"1.0.0"}}',
        encoding="utf-8",
    )
    (root / "server.ts").write_text(
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'const server = new McpServer({name:"owner",version:"1"});\n'
        'server.registerTool("fetch", {inputSchema:{token:z.string()}}, '
        "async ({token}) => {\n"
        'return fetch("https://api.example.com", '
        "{headers:{Authorization:token || process.env.OPERATOR_TOKEN}});\n"
        "});\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    assert not run_static_scan(config, uuid4(), timestamp=NOW).findings


@pytest.mark.parametrize("client", ["Jira", "Confluence"])
@pytest.mark.parametrize(
    ("argument", "guard", "expected"),
    [
        ("token", "", 1),
        ("password", "", 1),
        ("url", "", 0),
        ("username", "", 0),
        ("token", 'if not token: raise ValueError("unauthenticated")', 0),
        ("token", 'if not other: raise ValueError("unauthenticated")', 1),
    ],
)
def test_service_client_credential_arguments(
    tmp_path: Path, client: str, argument: str, guard: str, expected: int
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from fastapi import FastAPI, Request\n"
        f"from atlassian import {client} as Service\n"
        "import os\napp = FastAPI()\n"
        "@app.get('/data')\ndef fetch(request: Request):\n"
        "    token = request.headers.get('Authorization')\n"
        "    other = request.headers.get('X-Other')\n"
        f"    {guard or 'pass'}\n"
        "    selected = token or os.getenv('OPERATOR_TOKEN')\n"
        f"    return Service({argument}=selected)\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    findings = run_static_scan(config, uuid4(), timestamp=NOW).findings
    assert len(findings) == expected


@pytest.mark.parametrize("replacement", ["local_module", "assignment", "parameter"])
def test_service_client_binding_must_be_external(
    tmp_path: Path, replacement: str
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    if replacement == "local_module":
        (root / "atlassian.py").write_text(
            "def Jira(**kwargs): return kwargs\n", encoding="utf-8"
        )
    (root / "server.py").write_text(
        "from fastapi import FastAPI, Request\nfrom atlassian import Jira\n"
        "import os\napp = FastAPI()\n"
        + ("Jira = custom\n" if replacement == "assignment" else "")
        + "@app.get('/data')\ndef fetch(request: Request"
        + (", Jira=None" if replacement == "parameter" else "")
        + "):\n"
        "    token = request.headers.get('Authorization') or os.getenv('OPERATOR')\n"
        "    return Jira(token=token)\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    assert not run_static_scan(config, uuid4(), timestamp=NOW).findings


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ('token = token or os.environ["OPERATOR_TOKEN"]', 1),
        ('if not token: token = os.getenv("OPERATOR_TOKEN")', 1),
        (
            "if not token: raise HTTPException(401)\n"
            '    token = token or os.environ["OPERATOR_TOKEN"]',
            0,
        ),
        (
            "if not other: raise HTTPException(401)\n"
            '    token = token or os.environ["OPERATOR_TOKEN"]',
            1,
        ),
        (
            "if not token: raise HTTPException(401)\n"
            "    token = other\n"
            '    token = token or os.environ["OPERATOR_TOKEN"]',
            1,
        ),
        ('token = token or ""', 0),
        ('operator = os.environ["OPERATOR_TOKEN"]', 0),
    ],
)
def test_http_credential_selection(tmp_path: Path, body: str, expected: int) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from fastapi import FastAPI, Request, HTTPException\n"
        "import os\nimport requests\napp = FastAPI()\n"
        '@app.get("/data")\nasync def fetch(request: Request):\n'
        '    token = request.headers.get("Authorization")\n'
        '    other = request.headers.get("X-Other-Token")\n    ' + body + "\n"
        '    return requests.get("https://api.example.com/", '
        'headers={"Authorization": token})\n',
        encoding="utf-8",
    )
    configuration = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    findings = run_static_scan(configuration, uuid4(), timestamp=NOW).findings
    assert len(findings) == expected


def test_stdio_owner_credentials_do_not_establish_http_crossing(tmp_path: Path) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from mcp.server.fastmcp import FastMCP\nimport os\nimport requests\n"
        'mcp=FastMCP("owner")\n@mcp.tool()\ndef fetch(token: str = ""):\n'
        '    token = token or os.environ["OPERATOR_TOKEN"]\n'
        '    return requests.get("https://api.example.com/", '
        'headers={"Authorization": token})\n',
        encoding="utf-8",
    )
    configuration = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    assert not run_static_scan(configuration, uuid4(), timestamp=NOW).findings


@pytest.mark.parametrize("replace_token", [False, True])
def test_mutable_outbound_credentials(tmp_path: Path, replace_token: bool) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from fastapi import FastAPI, Request\nimport os\nimport requests\n"
        "app = FastAPI()\n@app.get('/data')\nasync def fetch(request: Request):\n"
        "    headers = {}\n"
        '    token = request.headers.get("Authorization")\n'
        '    headers["Authorization"] = token or os.environ["OPERATOR_TOKEN"]\n'
        + ('    headers["Authorization"] = token\n' if replace_token else "")
        + '    return requests.get("https://api.example.com/", '
        "headers=headers)\n",
        encoding="utf-8",
    )
    configuration = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    findings = run_static_scan(configuration, uuid4(), timestamp=NOW).findings
    assert len(findings) == (not replace_token)


@pytest.mark.parametrize(
    ("setup", "guard", "expected"),
    [
        ("", "", 1),
        ("", '    if not token: raise ValueError("missing token")\n', 0),
        ("get_http_request = unknown\n", "", 0),
    ],
)
def test_sdk_http_request_credentials(
    tmp_path: Path, setup: str, guard: str, expected: int
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from mcp.server.fastmcp import FastMCP\n"
        "from fastmcp.server.dependencies import get_http_request\n"
        "import os\nimport requests\n"
        + setup
        + 'mcp=FastMCP("test")\n@mcp.tool()\ndef fetch():\n'
        "    request=get_http_request()\n"
        '    token=request.headers.get("Authorization")\n'
        + guard
        + "    token=token or "
        'os.getenv("OPERATOR_TOKEN")\n'
        '    return requests.get("https://api.example.com/", '
        'headers={"Authorization": token})\n',
        encoding="utf-8",
    )
    configuration = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    assert (
        len(run_static_scan(configuration, uuid4(), timestamp=NOW).findings) == expected
    )


def test_local_module_cannot_impersonate_sdk_http_getter(tmp_path: Path) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    package = root / "fastmcp" / "server"
    package.mkdir(parents=True)
    (package / "dependencies.py").write_text(
        "def get_http_request(): return custom\n", encoding="utf-8"
    )
    (root / "server.py").write_text(
        "from mcp.server.fastmcp import FastMCP\n"
        "from fastmcp.server.dependencies import get_http_request\n"
        'import os\nimport requests\nmcp=FastMCP("test")\n'
        "@mcp.tool()\ndef fetch():\n"
        '    token=get_http_request().headers.get("Authorization") or '
        'os.getenv("OPERATOR_TOKEN")\n'
        '    return requests.get("https://api.example.com/", '
        'headers={"Authorization": token})\n',
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    assert not run_static_scan(config, uuid4(), timestamp=NOW).findings


@pytest.mark.parametrize("helper", [False, True])
@pytest.mark.parametrize(
    ("branch", "expected"),
    [
        ("if token: return Service(token=token)", 1),
        ("if not token: raise ValueError('missing')", 0),
        (
            "if not other: raise ValueError('missing')\n"
            "    if token: return Service(token=token)",
            1,
        ),
    ],
)
def test_absent_http_credential_selects_separate_operator_client(
    tmp_path: Path, helper: bool, branch: str, expected: int
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from fastapi import FastAPI, Request\nfrom atlassian import Jira as Service\n"
        "import os\napp=FastAPI()\n"
        "def operator_client():\n    return Service(token=os.getenv('OWNER'))\n"
        "@app.get('/data')\ndef fetch(request: Request):\n"
        "    token=request.headers.get('Authorization')\n"
        "    other=request.headers.get('X-Other')\n    " + branch + "\n"
        "    return "
        + ("operator_client()" if helper else "Service(token=os.getenv('OWNER'))")
        + "\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    assert len(run_static_scan(config, uuid4(), timestamp=NOW).findings) == expected


@pytest.mark.parametrize("refuse_http", [False, True])
def test_sdk_auth_mode_fallback_preserves_successful_http_context(
    tmp_path: Path, refuse_http: bool
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from mcp.server.fastmcp import FastMCP\n"
        "from fastmcp.server.dependencies import get_http_request\n"
        "from atlassian import Jira as Service\nimport os\nmcp=FastMCP('test')\n"
        "def operator_client():\n    return Service(token=os.getenv('OWNER'))\n"
        "@mcp.tool()\ndef fetch():\n"
        "    in_http=False\n    try:\n"
        "        request=get_http_request()\n        in_http=True\n"
        "        mode=request.headers.get('X-Auth-Mode')\n"
        "        token=request.headers.get('Authorization')\n"
        "        if mode == 'pat' and token:\n            return Service(token=token)\n"
        "    except RuntimeError:\n        pass\n"
        + (
            "    if in_http: raise ValueError('refusing HTTP fallback')\n"
            if refuse_http
            else ""
        )
        + "    return operator_client()\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    assert len(run_static_scan(config, uuid4(), timestamp=NOW).findings) == (
        not refuse_http
    )


@pytest.mark.parametrize(
    ("default", "guard", "conditional"),
    [
        ("", "if not opted_in('ALLOW_FALLBACK'): raise ValueError('refuse')", True),
        (
            "true",
            "if not opted_in('ALLOW_FALLBACK'): raise ValueError('refuse')",
            False,
        ),
        ("", "if opted_in('ALLOW_FALLBACK'): pass", False),
        ("", "opted_in('ALLOW_FALLBACK')", False),
        (
            "",
            "opted_in('UNRELATED')\n"
            "    if not opted_in('ALLOW_FALLBACK'): raise ValueError('refuse')",
            True,
        ),
        (
            "",
            "opted_in = lambda name: True\n"
            "    if not opted_in('ALLOW_FALLBACK'): raise ValueError('refuse')",
            False,
        ),
        ("", "if not opted_in('ALLOW_FALLBACK'): return operator_client()", False),
        (
            "",
            "def optional_config():\n"
            "        if opted_in('EXTRA'): return {}\n"
            "        return None\n"
            "    optional_config()",
            False,
        ),
    ],
)
def test_operator_fallback_reports_enforced_nondefault_configuration(
    tmp_path: Path, default: str, guard: str, conditional: bool
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from fastapi import FastAPI, Request\nfrom atlassian import Jira as Service\n"
        "import os\napp=FastAPI()\n"
        "def opted_in(name):\n"
        f"    return os.getenv(name, {default!r}).lower() in ('true', '1', 'yes')\n"
        "def operator_client():\n    return Service(token=os.getenv('OWNER'))\n"
        "@app.get('/data')\ndef fetch(request: Request):\n"
        "    token=request.headers.get('Authorization')\n"
        "    if token: return Service(token=token)\n    " + guard + "\n"
        "    return operator_client()\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    findings = run_static_scan(config, uuid4(), timestamp=NOW).findings
    assert len(findings) == 1
    assert ("declared default" in findings[0].description) is conditional
    if conditional:
        assert "ALLOW_FALLBACK" in findings[0].description


@pytest.mark.parametrize(
    ("guard", "expected"),
    [
        ("if not config: raise ValueError('missing config')", 0),
        ("if config is None: raise ValueError('missing config')", 0),
        ("config is None", 1),
        ("if not request.headers.get('Other'): raise ValueError('unrelated')", 1),
    ],
)
def test_optional_config_refusal_prevents_operator_default(
    tmp_path: Path, guard: str, expected: int
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from dataclasses import dataclass\nfrom fastapi import FastAPI, Request\n"
        "from atlassian import Jira\nimport os\napp=FastAPI()\n"
        "@dataclass\nclass Config:\n    token: str\n"
        "def optional_config(request):\n"
        "    if request.headers.get('Enabled'):\n"
        "        return Config('explicit-credential')\n"
        "    return None\n"
        "def client(config, request):\n"
        "    config = config or Config(request.headers.get('Authorization') "
        "or os.getenv('OWNER'))\n"
        "    return Jira(token=config.token)\n"
        "@app.get('/data')\ndef fetch(request: Request):\n"
        "    config = optional_config(request)\n    " + guard + "\n"
        "    return client(config, request)\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    assert len(run_static_scan(config, uuid4(), timestamp=NOW).findings) == expected


@pytest.mark.parametrize(
    ("constructor", "context"),
    [
        ("httpx.AsyncClient", "async with"),
        ("httpx.Client", "with"),
        ("requests.Session", "with"),
        ("aiohttp.ClientSession", "async with"),
    ],
)
@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ("pass", 2),
        ("client.get = unknown", 0),
        ("unknown(client)", 0),
        ("client = unknown", 0),
    ],
)
def test_http_client_identity_is_shared_by_url_and_credential_flows(
    tmp_path: Path, constructor: str, context: str, change: str, expected: int
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from fastapi import FastAPI, Request\n"
        "import os, httpx, requests, aiohttp\napp = FastAPI()\n"
        "@app.get('/data')\nasync def fetch(request: Request):\n"
        "    token = request.headers.get('Authorization') or os.getenv('TOKEN')\n"
        f"    {context} {constructor}() as client:\n"
        f"        {change}\n"
        "        return client.get(request.query_params.get('url'), "
        "params={'access_token': token})\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root,
        environ={},
        static_only=True,
        cli_overrides={"rules": ["SENT-015", "SENT-016"]},
    )
    findings = run_static_scan(config, uuid4(), timestamp=NOW).findings
    assert len(findings) == expected
    if expected:
        assert {finding.rule_id for finding in findings} == {"SENT-015", "SENT-016"}


@pytest.mark.parametrize("rule", ["SENT-012", "SENT-014", "SENT-015", "SENT-016"])
@pytest.mark.parametrize("method", ["get", "unknown_method"])
def test_python_client_receiver_is_evaluated_once_per_call(
    monkeypatch: pytest.MonkeyPatch, rule: str, method: str
) -> None:
    import time

    from sentinel.static.discovery import Symbol
    from sentinel.static.model import RuleRunState
    from sentinel.static.path_flow import PathFlow, Value
    from sentinel.static.rules.sent012 import analyze
    from sentinel.static.rules.sent014 import OptionFlow
    from sentinel.static.rules.sent015 import URLFlow
    from sentinel.static.rules.sent016 import CredentialFlow
    from tests.test_python_discovery import program

    flow_types: dict[str, type[PathFlow]] = {
        "SENT-012": PathFlow,
        "SENT-014": OptionFlow,
        "SENT-015": URLFlow,
        "SENT-016": CredentialFlow,
    }
    flow_type = flow_types[rule]
    original = flow_type.function
    calls = []

    def traced(self: PathFlow, symbol: Symbol, bindings: dict[str, Value]) -> Value:
        if symbol.name == "client_factory":
            calls.append(symbol)
        return original(self, symbol, bindings)

    monkeypatch.setattr(flow_type, "function", traced)
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "import httpx, subprocess\nmcp = FastMCP('test')\n"
            "def client_factory(): return httpx.Client()\n"
            "@mcp.tool()\ndef fetch(url: str, other: str):\n"
            "    subprocess.run(['git', '--version'])\n"
            f"    client_factory().{method}(url)\n"
            f"    client_factory().{method}(other)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state, flow=flow_type(index, state, time.monotonic() + 20))
    assert len(calls) == 2


@pytest.mark.parametrize("request_call", ["requests.get", "httpx.Client().get"])
def test_request_arguments_run_before_credential_keyword_values(
    tmp_path: Path, request_call: str
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from fastapi import FastAPI, Request\n"
        "import os, httpx, requests\napp = FastAPI()\n"
        "def prepare(params):\n"
        "    params['access_token'] = 'fixed'\n"
        "    return 'https://api.example.com'\n"
        "@app.get('/data')\ndef fetch(request: Request):\n"
        "    token = request.headers.get('Authorization') or os.getenv('TOKEN')\n"
        "    params = {'access_token': token}\n"
        f"    return {request_call}(prepare(params), params=params)\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    assert not run_static_scan(config, uuid4(), timestamp=NOW).findings


@pytest.mark.parametrize(
    ("setup", "read", "expected"),
    [
        ("token.set(request.headers.get('Authorization'))", "token.get()", 1),
        ("token.set('explicit')", "token.get()", 0),
        ("token.set(None)", "token.get('explicit')", 1),
        ("pass", "token.get('explicit')", 0),
        ("token.set('explicit'); token.set(None)", "token.get()", 1),
        ("saved = token.set('explicit'); token.reset(saved)", "token.get()", 1),
        (
            "token.set('explicit'); saved = token.set(None); token.reset(saved)",
            "token.get()",
            0,
        ),
        ("other.set('explicit')", "token.get()", 1),
        ("alias = token; alias.set('explicit')", "token.get()", 0),
        ("if request.headers.get('Other'): token.set('explicit')", "token.get()", 1),
        ("set_token('explicit')", "token.get()", 0),
        ("token.set('explicit')", "read_token()", 0),
    ],
)
def test_context_variable_credential_state(
    tmp_path: Path, setup: str, read: str, expected: int
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from contextvars import ContextVar\n"
        "from fastapi import FastAPI, Request\n"
        "import os, requests\napp = FastAPI()\n"
        "token = ContextVar('token', default=None)\n"
        "other = ContextVar('token', default=None)\n"
        "def set_token(value): return token.set(value)\n"
        "def read_token(): return token.get()\n"
        "@app.get('/data')\ndef fetch(request: Request):\n"
        "    if request.headers.get('Authorization'): return\n"
        f"    {setup}\n"
        f"    credential = {read} or os.getenv('OWNER')\n"
        "    return requests.get('https://api.example.com', "
        "params={'access_token': credential})\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    assert len(run_static_scan(config, uuid4(), timestamp=NOW).findings) == expected


@pytest.mark.parametrize(
    "operation",
    [
        "token.get()",
        "saved = token.set('explicit'); other.reset(saved)",
        "saved = token.set('explicit'); token.reset(saved); token.reset(saved)",
        "saved = token.set('explicit')\n"
        "    if condition: token.reset(saved)\n"
        "    token.reset(saved)",
        "unknown(token); token.get('explicit')",
        "saved = token.set('explicit'); unknown(saved); token.reset(saved)",
        "token.get = unknown; token.get('explicit')",
    ],
)
def test_unresolved_context_operations_cannot_establish_state(operation: str) -> None:
    from sentinel.static.model import RuleRunState
    from sentinel.static.path_flow import PathFlow, Value
    from tests.test_python_discovery import program

    index = program(
        {
            "server.py": "from contextvars import ContextVar\n"
            "token = ContextVar('token')\nother = ContextVar('token')\n"
            f"def fetch(condition):\n    {operation}\n"
        }
    )
    handler = index.resolve(index.files[0], "fetch")
    assert handler is not None
    state = RuleRunState()
    flow = PathFlow(index, state, float("inf"))
    flow.function(handler, {"condition": Value(sources=frozenset({"condition"}))})
    assert any(
        "unresolved ContextVar operation" in item.message for item in state.warnings
    )


def test_context_state_does_not_leak_between_handler_entries() -> None:
    from sentinel.static.model import RuleRunState
    from sentinel.static.path_flow import PathFlow
    from tests.test_python_discovery import program

    index = program(
        {
            "server.py": "from contextvars import ContextVar\n"
            "token = ContextVar('token', default='default')\n"
            "def first(): token.set('previous-request')\n"
            "def second(): return token.get()\n"
        }
    )
    first = index.resolve(index.files[0], "first")
    second = index.resolve(index.files[0], "second")
    assert first is not None and second is not None
    flow = PathFlow(index, RuleRunState(), float("inf"))
    flow.function(first, {})
    assert flow.function(second, {}).key == "'default'"


@pytest.mark.parametrize("reject_missing", [False, True])
@pytest.mark.parametrize("attach", [False, True])
def test_base_http_context_token_requires_attached_enforced_authentication(
    tmp_path: Path, reject_missing: bool, attach: bool
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from fastmcp import FastMCP\n"
        "from starlette.middleware import Middleware\n"
        "from starlette.middleware.base import BaseHTTPMiddleware\n"
        "from contextvars import ContextVar\nimport requests, os\n"
        "token = ContextVar('token', default=None)\n"
        "class Guard(BaseHTTPMiddleware):\n"
        "    async def dispatch(self, request, call_next):\n"
        "        credential = request.headers.get('Authorization')\n"
        + ("        if not credential: return None\n" if reject_missing else "")
        + "        token.set(credential)\n"
        "        return await call_next(request)\n"
        "class App(FastMCP):\n"
        "    def http_app(self, **kwargs):\n"
        "        return super().http_app(middleware=[Middleware(Guard)], **kwargs)\n"
        + ("mcp = App('test')\n" if attach else "mcp = FastMCP('test')\n")
        + "@mcp.tool()\ndef accounts():\n"
        "    credential = token.get() or os.getenv('OPERATOR_TOKEN')\n"
        "    return requests.get('https://api.example.com', "
        "params={'access_token': credential})\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    findings = run_static_scan(config, uuid4(), timestamp=NOW).findings
    assert len(findings) == (1 if attach and not reject_missing else 0)


@pytest.mark.parametrize("detached", [False, True])
@pytest.mark.parametrize("reject_missing", [False, True])
@pytest.mark.parametrize("transport", ["stdio", "streamable-http", "sse"])
@pytest.mark.parametrize(
    "mutation",
    [
        "",
        "mcp.__class__=unknown",
        "mcp._token_verifier=unknown",
        "mcp.settings.auth=unknown",
        "unknown(mcp)",
        "mcp.{provider}=lambda: unknown",
        "FastMCP.{provider}=lambda self: unknown",
        "def unused(): unknown(Guard)",
        "def change(): unknown(Guard)\n    change()",
    ],
)
def test_sdk_source_provider_wrapper_attaches_to_the_selected_launch(
    tmp_path: Path, reject_missing: bool, transport: str, mutation: str, detached: bool
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    provider = "sse_app" if transport == "sse" else "streamable_http_app"
    (root / "server.py").write_text(
        "from mcp.server.fastmcp import FastMCP\n"
        "from starlette.middleware.base import BaseHTTPMiddleware\n"
        "from contextvars import ContextVar\nimport requests, os\n"
        "token=ContextVar('token', default=None)\n"
        "class Guard(BaseHTTPMiddleware):\n"
        "    async def dispatch(self, request, call_next):\n"
        "        credential=request.headers.get('Authorization')\n"
        + ("        if not credential: return None\n" if reject_missing else "")
        + "        token.set(credential)\n"
        "        return await call_next(request)\n"
        "mcp=FastMCP('test')\n"
        "def setup(server):\n"
        f"    original=server.{provider}\n"
        "    def wrapped(*args, **kwargs):\n"
        "        app=original(*args, **kwargs)\n"
        "        app.add_middleware(Guard)\n"
        + (
            "        return original(*args, **kwargs)\n"
            if detached
            else "        return app\n"
        )
        + f"    server.{provider}=wrapped\n"
        "def main():\n    setup(mcp)\n"
        + ("    " + mutation.format(provider=provider) + "\n" if mutation else "")
        + f"    mcp.run(transport={transport!r})\n"
        "@mcp.tool()\ndef accounts():\n"
        "    credential=token.get() or os.getenv('OPERATOR_TOKEN')\n"
        "    return requests.get('https://api.example.com', "
        "params={'access_token': credential})\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    findings = run_static_scan(config, uuid4(), timestamp=NOW).findings
    assert len(findings) == (
        transport != "stdio"
        and (detached or not reject_missing)
        and (
            not mutation
            or mutation.startswith("def unused")
            or (detached and mutation.startswith("def change"))
        )
    )


@pytest.mark.parametrize("transport", ["stdio", "streamable-http", "sse"])
@pytest.mark.parametrize("configured_auth", [False, True])
def test_sdk_unset_request_context_can_select_operator_credentials(
    tmp_path: Path, transport: str, configured_auth: bool
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "import os, requests\nfrom mcp.server.fastmcp import FastMCP\n"
        "from contextvars import ContextVar\ntoken=ContextVar('token',default=None)\n"
        + (
            "mcp=FastMCP('test',auth=unknown)\n"
            if configured_auth
            else "mcp=FastMCP('test')\n"
        )
        + "def main():\n"
        + f"    mcp.run(transport={transport!r})\n"
        "@mcp.tool()\ndef accounts():\n"
        "    selected=token.get() or os.getenv('OPERATOR_TOKEN')\n"
        "    return requests.get('https://api.example.com',params={'access_token':selected})\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    report = run_static_scan(config, uuid4(), timestamp=NOW)
    assert len(report.findings) == (transport != "stdio" and not configured_auth)
    if configured_auth:
        assert any(
            "SDK authentication configuration" in warning.message
            for warning in report.warnings
        )


def test_sdk_branch_evidence_survives_finding_merge(tmp_path: Path) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "import os, requests\nfrom mcp.server.fastmcp import FastMCP\n"
        "from contextvars import ContextVar\ntoken=ContextVar('token',default=None)\n"
        "mcp=FastMCP('test')\n"
        "def setup(server):\n"
        "    if server.settings.json_response: pass\n    else: pass\n"
        "def main():\n"
        "    mcp.settings.json_response=bool(os.getenv('JSON_RESPONSE'))\n"
        "    setup(mcp)\n    mcp.run(transport='streamable-http')\n"
        "@mcp.tool()\ndef accounts():\n"
        "    selected=token.get() or os.getenv('OPERATOR_TOKEN')\n"
        "    return requests.get('https://api.example.com',params={'access_token':selected})\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    findings = run_static_scan(config, uuid4(), timestamp=NOW).findings
    assert len(findings) == 1
    assert "json_response=True" in findings[0].description
    assert "json_response=False" in findings[0].description
    assert isinstance(findings[0].evidence, StaticEvidence)
    assert any(
        location.range.start_line == 7
        for location in findings[0].evidence.flow_locations
    )


@pytest.mark.parametrize(
    ("guard", "protected"),
    [
        ("", False),
        ("if (!token) throw Error('missing');", True),
        ("if (!req.headers.other) throw Error('missing');", False),
        ("if (!token) res.sendStatus(401);", False),
        ("if (!token) throw Error('missing'); token=req.headers.other;", False),
    ],
)
@pytest.mark.parametrize("replaced", [False, True])
def test_typescript_factory_http_callback(
    tmp_path: Path, guard: str, protected: bool, replaced: bool
) -> None:
    root = tmp_path / "target"
    root.mkdir()
    (root / "package.json").write_text(
        '{"dependencies":{"express":"4.0.0","@modelcontextprotocol/sdk":"1.0.0"}}',
        encoding="utf-8",
    )
    (root / "server.ts").write_text(
        'import express from "express";\n'
        'import {attach} from "./routes.js";\n'
        "export function createApp() {\n"
        " const app=express();\n"
        + (" app.get = replacement;\n" if replaced else "")
        + " attach(app);\n return app;\n}\n",
        encoding="utf-8",
    )
    (root / "routes.ts").write_text(
        "export function attach(app) {\n"
        ' app.get("/accounts", async (req, res) => {\n'
        "  let token=req.headers.authorization;\n"
        + guard
        + "\n  token=token || process.env.OPERATOR_TOKEN;\n"
        '  return fetch("https://api.example.com",{headers:{Authorization:token}});\n'
        " });\n}\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    report = run_static_scan(config, uuid4(), timestamp=NOW)
    assert len(report.findings) == (not protected and not replaced)


@pytest.mark.parametrize("factory", [False, True])
@pytest.mark.parametrize("attachment", ["route", "use"])
@pytest.mark.parametrize(
    ("guard", "expected"),
    [
        ("", 1),
        ("if (!req.headers.authorization) return res.sendStatus(401);", 0),
        ("if (!req.headers.other) return res.sendStatus(401);", 1),
        ("if (!req.headers.authorization) res.sendStatus(401);", 1),
        ("return res.sendStatus(401);", 0),
        ("next = () => {};", 0),
    ],
)
def test_typescript_attached_http_middleware(
    tmp_path: Path, factory: bool, attachment: str, guard: str, expected: int
) -> None:
    root = tmp_path / "target"
    root.mkdir()
    (root / "package.json").write_text(
        '{"dependencies":{"express":"4.0.0","@modelcontextprotocol/sdk":"1.0.0"}}',
        encoding="utf-8",
    )
    registration = (
        'app.get("/accounts", auth, handler);'
        if attachment == "route"
        else 'app.use(auth); app.get("/accounts", handler);'
    )
    (root / "server.ts").write_text(
        'import express from "express";\n'
        'import {auth, handler} from "./routes.js";\n'
        + ("export function createApp() {\n" if factory else "")
        + " const app=express();\n"
        + registration
        + ("\n return app;\n}\n" if factory else "\n"),
        encoding="utf-8",
    )
    (root / "routes.ts").write_text(
        "function forward(next) { next(); }\n"
        "export function auth(req, res, next) {\n" + guard + "\n forward(next);\n}\n"
        "export async function handler(req, res) {\n"
        " const token=req.headers.authorization || process.env.OPERATOR_TOKEN;\n"
        ' return fetch("https://api.example.com",{headers:{Authorization:token}});\n'
        "}\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    report = run_static_scan(config, uuid4(), timestamp=NOW)
    assert len(report.findings) == expected
    assert report.summary.coverage is not None
    routes = [
        surface
        for surface in report.summary.coverage.surfaces
        if surface.kind == "http_route"
    ]
    assert len(routes) == 1
    assert routes[0].status == "recognized"
    assert routes[0].handler is not None and routes[0].handler.path == "routes.ts"
    assert "SENT-016" in routes[0].examined_rule_ids


@pytest.mark.parametrize(
    ("registration", "expected"),
    [
        ('app.use("/accounts", auth); app.get("/accounts", handler);', 0),
        ('if (true) app.get("/accounts", handler);', 1),
        ('if (true) app.use(auth); app.get("/accounts", handler);', 0),
        ('if (enabled) app.use(auth); app.get("/accounts", handler);', 1),
        ('app.use("/other", auth); app.get("/accounts", handler);', 1),
        ('app.use("/account", auth); app.get("/accounts", handler);', 1),
        ('app.get("/accounts", handler); app.use(auth);', 1),
        ('app.use(process.env.PREFIX, auth); app.get("/accounts", handler);', 1),
        ('app.use("/:id", auth); app.get("/accounts", handler);', 1),
        ('app.use(auth); app.get("/accounts", mutate, handler);', 1),
        ('app.use(auth); app.get("/accounts", unknown, handler);', 1),
        ('app.get("/accounts", auth, unknown, handler);', 1),
        ('const other=express(); other.use(auth); app.get("/accounts", handler);', 1),
        ('app.use([auth]); app.get("/accounts", handler);', 0),
        ('app.get("/accounts", [auth, handler]);', 0),
        (
            'app.use(auth); app.get("/accounts", handler); app.get("/other", handler);',
            0,
        ),
        (
            'app.get("/accounts", handler); app.use(auth); app.get("/other", handler);',
            1,
        ),
    ],
)
def test_typescript_http_middleware_scope(
    tmp_path: Path, registration: str, expected: int
) -> None:
    root = tmp_path / "target"
    root.mkdir()
    (root / "package.json").write_text(
        '{"dependencies":{"express":"4.0.0","@modelcontextprotocol/sdk":"1.0.0"}}',
        encoding="utf-8",
    )
    (root / "server.ts").write_text(
        'import express from "express";\n'
        "const app=express();\n"
        "function auth(req,res,next) {\n"
        " if (!req.headers.authorization) return res.sendStatus(401);\n"
        " next();\n}\n"
        "function mutate(request,response,next) {\n"
        " request.headers.authorization=request.headers.other; next();\n}\n"
        "function handler(request,response) {\n"
        " const token=request.headers.authorization || process.env.OPERATOR_TOKEN;\n"
        ' return fetch("https://api.example.com",{headers:{Authorization:token}});\n'
        "}\n" + registration,
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    report = run_static_scan(config, uuid4(), timestamp=NOW)
    assert len(report.findings) == expected


def test_typescript_repeated_http_middleware(tmp_path: Path) -> None:
    root = tmp_path / "target"
    root.mkdir()
    (root / "package.json").write_text(
        '{"dependencies":{"express":"4.0.0","@modelcontextprotocol/sdk":"1.0.0"}}',
        encoding="utf-8",
    )
    (root / "server.ts").write_text(
        'import express from "express";\n'
        "const app=express();\n"
        "function pass(req,res,next) { next(); }\n"
        'app.get("/accounts", pass, pass, (req,res)=> {\n'
        " const token=req.headers.authorization || process.env.OPERATOR_TOKEN;\n"
        ' return fetch("https://api.example.com",{headers:{Authorization:token}});\n'
        "});\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    report = run_static_scan(config, uuid4(), timestamp=NOW)
    assert len(report.findings) == 1


@pytest.mark.parametrize("protected", [False, True])
def test_typescript_mixed_mcp_http_factory(tmp_path: Path, protected: bool) -> None:
    root = tmp_path / "target"
    root.mkdir()
    (root / "package.json").write_text(
        '{"dependencies":{"express":"4.0.0","@modelcontextprotocol/sdk":"1.0.0"}}',
        encoding="utf-8",
    )
    (root / "server.ts").write_text(
        'import express from "express";\n'
        'import {McpServer} from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        "export function createServer() {\n"
        ' const server=new McpServer({name:"sample",version:"1"});\n'
        ' server.registerTool("ping",{inputSchema:{}},()=>"pong");\n'
        " const app=express();\n"
        ' app.get("/accounts", (req,res)=>{\n'
        + (
            " if (!req.headers.authorization) return res.sendStatus(401);\n"
            if protected
            else ""
        )
        + " const token=req.headers.authorization || process.env.OPERATOR_TOKEN;\n"
        ' return fetch("https://api.example.com",{headers:{Authorization:token}});\n'
        " }); return app;\n}\n",
        encoding="utf-8",
    )
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    report = run_static_scan(config, uuid4(), timestamp=NOW)
    assert len(report.findings) == (not protected)
