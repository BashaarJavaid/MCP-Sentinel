"""Caller credential absence must not select operator credentials across HTTP."""

from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
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
