"""Outbound requests require enforced checks on the actual caller URL."""

import time
from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.static.engine import run_static_scan
from sentinel.static.model import RuleRunState, TypeScriptSourceFile
from sentinel.static.typescript_discovery import TypeScriptProgram
from sentinel.static.typescript_path_flow import analyze
from tests.conftest import NOW, make_target


def scan(root: Path, source: str) -> tuple:
    make_target(root, target_yaml="")
    (root / "server.py").write_text(source, encoding="utf-8")
    configuration = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-015"]}
    )
    return run_static_scan(configuration, uuid4(), timestamp=NOW).findings


PREFIX = """from mcp.server.fastmcp import FastMCP
import requests
import httpx
from urllib.parse import urlparse
mcp = FastMCP("test")
"""

CHECK = """parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        raise ValueError()
    if parsed.hostname not in ("images.example.com",):
        raise ValueError()
"""


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("return requests.get(url)", 1),
        ("return httpx.get(url=url)", 1),
        ('return requests.get("https://images.example.com/fixed")', 0),
        ('return requests.get("https://images.example.com/" + url)', 0),
        ('return requests.get("https://images.example.com" + url)', 1),
        ('return requests.get("http://127.0.0.1/" + url)', 1),
        ('return requests.get(f"https://images.example.com/{url}")', 0),
        ('return requests.get(f"https://{url}/image")', 1),
        (CHECK + "    return requests.get(url)", 0),
        (
            CHECK.replace("urlparse(url)", "urlparse(other)")
            + "    return requests.get(url)",
            1,
        ),
        (CHECK + "    url = other\n    return requests.get(url)", 1),
        (
            CHECK.replace('("https", "http")', '("https", "file")')
            + "    return requests.get(url)",
            1,
        ),
        (
            CHECK.replace('("images.example.com",)', '("localhost",)')
            + "    return requests.get(url)",
            1,
        ),
        (
            CHECK.replace('("images.example.com",)', '("127.0.0.1",)')
            + "    return requests.get(url)",
            1,
        ),
        (
            CHECK.replace('("images.example.com",)', '("10.0.0.1",)')
            + "    return requests.get(url)",
            1,
        ),
        (
            CHECK.replace('("images.example.com",)', '("::1",)')
            + "    return requests.get(url)",
            1,
        ),
        (
            CHECK.replace('("images.example.com",)', '("169.254.169.254",)')
            + "    return requests.get(url)",
            1,
        ),
        (
            CHECK.replace('("images.example.com",)', '("8.8.8.8",)')
            + "    return requests.get(url)",
            0,
        ),
        (
            "parsed = urlparse(url)\n    parsed.scheme in ('https',)\n "
            "   parsed.hostname in ('images.example.com',)\n    return"
            " requests.get(url)",
            1,
        ),
    ],
)
def test_python_request_boundary(tmp_path: Path, body: str, expected: int) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX + "@mcp.tool()\ndef fetch(url: str, other: str):\n    " + body + "\n",
    )
    assert len(findings) == expected


@pytest.mark.parametrize("checked", ["url", "other"])
@pytest.mark.parametrize("client", ["httpx.Client", "requests.Session"])
def test_imported_enforced_guard(tmp_path: Path, checked: str, client: str) -> None:
    root = tmp_path / "target"
    root.mkdir()
    (root / "guard.py").write_text(
        "from urllib.parse import urlparse\ndef validate(url):\n    " + CHECK,
        encoding="utf-8",
    )
    findings = scan(
        root,
        PREFIX
        + "from guard import validate\n@mcp.tool()\ndef fetch(url:str, other:str):\n"
        f"    validate({checked})\n    with {client}() as client:\n"
        "        return client.get(url)\n",
    )
    assert len(findings) == (checked != "url")


def test_caught_guard_does_not_protect_request(tmp_path: Path) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX
        + "def validate(url):\n    "
        + CHECK
        + "\n@mcp.tool()\ndef fetch(url:str):\n"
        "    try:\n        validate(url)\n    except ValueError:\n        pass\n"
        "    return requests.get(url)\n",
    )
    assert len(findings) == 1


@pytest.mark.parametrize(
    ("check", "expected"),
    [
        ("if blocked(ip): raise ValueError()", 0),
        ("blocked(ip)", 1),
        (
            "if blocked(ipaddress.ip_address(urlparse(other).hostname"
            ")): raise ValueError()",
            1,
        ),
        ("if blocked(ip): raise ValueError()\n    url = other", 1),
        ("if not ip.is_global or ip.is_multicast: raise ValueError()", 0),
        ("if ip.is_multicast: raise ValueError()", 1),
    ],
)
def test_literal_address_predicates(tmp_path: Path, check: str, expected: int) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX + "import ipaddress\n"
        "def blocked(ip):\n"
        "    return ip.is_private or ip.is_loopback or ip.is_link"
        "_local or ip.is_reserved or ip.is_multicast or ip.is_uns"
        "pecified\n"
        "@mcp.tool()\ndef fetch(url:str, other:str):\n"
        "    parsed = urlparse(url)\n"
        "    if parsed.scheme not in ('http', 'https'): raise ValueError()\n"
        "    ip = ipaddress.ip_address(parsed.hostname)\n    " + check + "\n"
        "    return requests.get(url)\n",
    )
    assert len(findings) == expected


@pytest.mark.parametrize(
    "use", ["if not allowed(url): raise ValueError()", "allowed(url)"]
)
def test_returned_boolean_is_enforced(tmp_path: Path, use: str) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX + "def allowed(url):\n    parsed = urlparse(url)\n"
        "    return parsed.scheme in ('https',) and parsed.hostna"
        "me in ('images.example.com',)\n"
        "@mcp.tool()\ndef fetch(url:str):\n    "
        + use
        + "\n    return requests.get(url)\n",
    )
    assert len(findings) == (use == "allowed(url)")


@pytest.mark.parametrize("mutation", ["", "ips.clear()", "ips = []"])
def test_literal_ip_validation_loop(tmp_path: Path, mutation: str) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX + "import ipaddress\nimport socket\n"
        "def blocked(ip):\n"
        "    mapped = getattr(ip, 'ipv4_mapped', None)\n"
        "    if mapped is not None: ip = mapped\n"
        "    return ip.is_private or ip.is_loopback or ip.is_link"
        "_local or ip.is_reserved or ip.is_multicast or ip.is_uns"
        "pecified\n"
        "def validate(url):\n"
        "    parsed = urlparse(url.strip())\n"
        "    scheme = (parsed.scheme or '').lower()\n"
        "    if scheme not in ('https', 'http'): raise ValueError()\n"
        "    try:\n        ips = [ipaddress.ip_address(parsed.hostname)]\n"
        "    except ValueError:\n        ips = []\n"
        f"    {mutation or 'pass'}\n"
        "    for ip in ips:\n        if blocked(ip): raise ValueError()\n"
        "@mcp.tool()\ndef fetch(url:str):\n"
        "    validate(url)\n    return requests.get(url)\n",
    )
    assert len(findings) == bool(mutation)


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("return fetch(url);", 1),
        ("return axios.get(url);", 1),
        ("return http.get(url);", 1),
        ('return fetch("https://images.example.com/fixed");', 0),
        ('return fetch("https://images.example.com/" + url);', 0),
        ('return fetch("https://images.example.com" + url);', 1),
        ('return fetch("http://127.0.0.1/" + url);', 1),
        (
            'const u = new URL(url); if (u.protocol !== "https:" || u'
            '.hostname !== "images.example.com") throw new Error(); r'
            "eturn fetch(url);",
            0,
        ),
        (
            'const u = new URL(url); if (u.protocol !== "https:") thr'
            "ow new Error(); return fetch(url);",
            1,
        ),
        (
            'const u = new URL(other); if (u.protocol !== "https:" ||'
            ' u.hostname !== "images.example.com") throw new Error();'
            " return fetch(url);",
            1,
        ),
        (
            'const u = new URL(url); if (u.protocol !== "https:" || u'
            '.hostname !== "images.example.com") throw new Error(); u'
            "rl = other; return fetch(url);",
            1,
        ),
        (
            'const u = new URL(url); u.protocol === "https:" && u.hos'
            'tname === "images.example.com"; return fetch(url);',
            1,
        ),
        (
            'const u = new URL(url); if (u.protocol !== "file:" || u.'
            'hostname !== "images.example.com") throw new Error(); re'
            "turn fetch(url);",
            1,
        ),
        (
            'const u = new URL(url); if (u.protocol !== "https:" || u'
            '.hostname !== "127.0.0.1") throw new Error(); return fet'
            "ch(url);",
            1,
        ),
        (
            'const u = new URL(url); if (u.protocol !== "https:" || u'
            '.hostname !== "[::1]") throw new Error(); return fetch(u'
            "rl);",
            1,
        ),
        (
            'const u = new URL(url); if (!["https:", "http:"].include'
            's(u.protocol) || !["images.example.com"].includes(u.host'
            "name)) throw new Error(); return fetch(url);",
            0,
        ),
    ],
)
def test_typescript_request_boundary(tmp_path: Path, body: str, expected: int) -> None:
    from sentinel.static.rules.sent015 import TypeScriptURLFlow

    source = (
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'import axios from "axios"; import http from "node:http";\n'
        'const server = new McpServer({name:"test", version:"1"});\n'
        "async function fetchImage({url, other}: {url: string; other: string}) { "
        + body
        + " }\n"
        'server.registerTool("fetch", {inputSchema: {url: z.strin'
        "g(), other: z.string()}}, fetchImage);\n"
    )
    path = tmp_path / "server.ts"
    path.write_text(source, encoding="utf-8")
    program = TypeScriptProgram(
        (TypeScriptSourceFile(path, path.name, source),), deadline=time.monotonic() + 20
    )
    state = RuleRunState()
    analyze(program, state, flow=TypeScriptURLFlow(program, state))
    assert len(state.matches) == expected


@pytest.mark.parametrize(
    ("validation", "expected"),
    [
        ("error = validate(url)\n    if error: raise ValueError(error)", 0),
        ("validate(url)", 1),
        ("error = validate(other)\n    if error: raise ValueError(error)", 1),
        (
            "error = validate(url)\n    if error: raise ValueError(error)\n"
            "    url = other",
            1,
        ),
    ],
)
def test_returned_validation_error_requires_enforcement(
    tmp_path: Path, validation: str, expected: int
) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX + "import ipaddress\n"
        "def check_ip(host):\n"
        "    try:\n        ip = ipaddress.ip_address(host)\n"
        "    except ValueError:\n        return None\n"
        "    if not ip.is_global: return 'Blocked address'\n"
        "    return None\n"
        "def validate(url):\n    parsed = urlparse(url)\n"
        "    if parsed.scheme not in ('https', 'http'): return 'Blocked scheme'\n"
        "    error = check_ip(parsed.hostname)\n"
        "    if error: return error\n    return None\n"
        "@mcp.tool()\ndef fetch(url:str, other:str):\n    "
        + validation
        + "\n    return requests.get(url)\n",
    )
    assert len(findings) == expected
