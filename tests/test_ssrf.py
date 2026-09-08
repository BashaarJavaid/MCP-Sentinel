"""Outbound requests require enforced checks on the actual caller URL."""

import time
from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.finding import Finding
from sentinel.static.engine import run_static_scan
from sentinel.static.model import RuleRunState, TypeScriptSourceFile
from sentinel.static.typescript_discovery import TypeScriptProgram
from sentinel.static.typescript_path_flow import analyze
from tests.conftest import NOW, make_target


def scan(root: Path, source: str) -> tuple[Finding, ...]:
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
    ("client", "operation"),
    [
        ("Jira", "myself()"),
        ("Confluence", "get('rest/api/user/current')"),
    ],
)
@pytest.mark.parametrize(
    ("guard", "change", "expected"),
    [
        ("", "pass", 1),
        (CHECK, "pass", 0),
        ("", "service.url = 'https://images.example.com'", 0),
        (CHECK, "service.url = other", 1),
        ("", "service = unknown", 0),
        ("", "unknown(service)", 0),
    ],
)
def test_atlassian_service_requests_use_current_base_url(
    tmp_path: Path, client: str, operation: str, guard: str, change: str, expected: int
) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX + f"from atlassian import {client} as Service\n"
        "@mcp.tool()\ndef fetch(url: str, other: str):\n"
        + ("    " + guard if guard else "")
        + f"    service = Service(url=url)\n    {change}\n"
        f"    return service.{operation}\n",
    )
    assert len(findings) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("service = Confluence(url=url)", 0),
        (
            "service = Confluence(url=url)\n    service.get = unknown\n"
            "    service.get('rest/api/user/current')",
            0,
        ),
        (
            "service = Confluence(url='https://images.example.com')\n"
            "    service.get(url)",
            0,
        ),
        (
            "service = Confluence(url='https://images.example.com')\n"
            "    service.get(url, absolute=True)",
            1,
        ),
        (
            "service = Confluence(url=url)\n"
            "    service.get('https://images.example.com', absolute=True)",
            0,
        ),
        (
            "service = Confluence(url='https://images.example.com')\n"
            "    service.get(url, absolute=other)",
            1,
        ),
        (
            "service = Confluence(url=url)\n"
            "    service.request('GET', path='rest/api/user/current')",
            1,
        ),
        ("service = Confluence(url=url)\n    service.unknown_method()", 0),
        (
            "service = Confluence(url=url, session=unknown)\n"
            "    service.get('rest/api/user/current')",
            0,
        ),
        (
            "service = Confluence(url=url, session=requests.Session())\n"
            "    service.get('rest/api/user/current')",
            1,
        ),
        (
            "service = Confluence(url=url)\n    service._session.request = unknown\n"
            "    service.get('rest/api/user/current')",
            0,
        ),
        (
            "service = Confluence(url=url)\n    service._session = unknown\n"
            "    service.get('rest/api/user/current')",
            0,
        ),
        (
            "Confluence = unknown\n"
            "    Confluence(url=url).get('rest/api/user/current')",
            0,
        ),
        ("service = Confluence(url=url)\n    service.get()", 0),
        (
            "service = Confluence(url=url)\n    service.request = unknown\n"
            "    service.get('rest/api/user/current')",
            0,
        ),
        (
            "service = Confluence(url=url)\n    service.url_joiner = unknown\n"
            "    service.get('rest/api/user/current')",
            0,
        ),
        (
            "service = Confluence(url=url)\n"
            "    def prepare():\n        service._session = unknown\n"
            "        return 'rest/api/user/current'\n    service.get(prepare())",
            0,
        ),
        ("service = Confluence(url=url)\n    service.get('path', path='duplicate')", 0),
    ],
)
def test_service_url_contract_requires_a_reachable_request(
    tmp_path: Path, source: str, expected: int
) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX + "from atlassian import Confluence\n"
        "@mcp.tool()\ndef fetch(url: str, other: bool):\n    " + source + "\n",
    )
    assert len(findings) == expected


@pytest.mark.parametrize("guard", ["", CHECK])
@pytest.mark.parametrize("replace_url", [False, True])
def test_sdk_http_getter_retains_the_current_tool_request_state(
    tmp_path: Path, guard: str, replace_url: bool
) -> None:
    findings = scan(
        tmp_path / "target",
        "from fastmcp import FastMCP\n"
        "from fastmcp.server.dependencies import get_http_request\n"
        "from urllib.parse import urlparse\nimport requests\nmcp = FastMCP('test')\n"
        "def downstream():\n"
        "    return requests.get(get_http_request().state.url)\n"
        "@mcp.tool()\ndef fetch():\n"
        "    request = get_http_request()\n"
        "    url = request.query_params.get('url')\n"
        + ("    " + guard if guard else "")
        + "    request.state.url = url\n"
        + (
            "    request.state.url = request.query_params.get('other')\n"
            if replace_url
            else ""
        )
        + "    return downstream()\n",
    )
    assert len(findings) == (0 if guard and not replace_url else 1)


def test_sdk_http_request_state_does_not_leak_between_tools(tmp_path: Path) -> None:
    findings = scan(
        tmp_path / "target",
        "from fastmcp import FastMCP\n"
        "from fastmcp.server.dependencies import get_http_request\n"
        "import requests\nmcp = FastMCP('test')\n"
        "def downstream():\n"
        "    return requests.get(get_http_request().state.url)\n"
        "@mcp.tool()\ndef first():\n"
        "    get_http_request().state.url = 'https://images.example.com'\n"
        "    return downstream()\n"
        "@mcp.tool()\ndef second():\n    return downstream()\n",
    )
    assert len(findings) == 1


@pytest.mark.parametrize("guard", ["", CHECK])
@pytest.mark.parametrize("attach", [False, True])
@pytest.mark.parametrize(
    ("replacement", "intact"),
    [
        ("", True),
        ("mcp.http_app = unknown", False),
        ("App.http_app = unknown", False),
        ("unknown(mcp)", False),
        ("def poison():\n    mcp.http_app = unknown", True),
        ("def poison():\n    mcp.http_app = unknown\npoison()", False),
    ],
)
def test_registered_asgi_middleware_state_reaches_its_tool(
    tmp_path: Path, guard: str, attach: bool, replacement: str, intact: bool
) -> None:
    findings = scan(
        tmp_path / "target",
        "from fastmcp import FastMCP\n"
        "from fastmcp.server.dependencies import get_http_request\n"
        "from starlette.middleware import Middleware\n"
        "from starlette.requests import Request\n"
        "from urllib.parse import urlparse\nimport requests\n"
        "class Guard:\n"
        "    def __init__(self, app): self.app = app\n"
        "    async def __call__(self, scope, receive, send):\n"
        "        request = Request(scope)\n"
        "        url = request.headers.get('X-URL')\n"
        + ("        " + guard.replace("\n", "\n    ").rstrip() + "\n" if guard else "")
        + "        request.state.url = url\n"
        "        hasattr(request.state, 'url')\n"
        "        await self.app(scope, receive, send)\n"
        "class App(FastMCP):\n"
        "    def http_app(self, middleware=None, **kwargs):\n"
        "        return super().http_app(middleware=[Middleware(Guard)], **kwargs)\n"
        "unrelated = App('other')\n"
        + ("mcp = App('target')\n" if attach else "mcp = FastMCP('target')\n")
        + replacement
        + "\n"
        + "@mcp.tool()\ndef fetch():\n"
        "    return requests.get(get_http_request().state.url)\n",
    )
    assert len(findings) == (0 if guard and attach and intact else 1)


@pytest.mark.parametrize(
    ("body", "getter", "expected"),
    [
        ("return", "    get_http_request()\n", 0),
        ("return", "", 1),
        ("return", "    requests.get(url)\n    get_http_request()\n", 1),
        ("await self.app(scope, receive, send)", "    get_http_request()\n", 1),
        (
            "await unknown(self.app, scope, receive, send)",
            "    get_http_request()\n",
            1,
        ),
        (
            "self.app = unknown\nawait self.app(scope, receive, send)",
            "    get_http_request()\n",
            1,
        ),
    ],
)
def test_unknown_middleware_continuation_cannot_prove_refusal(
    tmp_path: Path, body: str, getter: str, expected: int
) -> None:
    findings = scan(
        tmp_path / "target",
        "from fastmcp import FastMCP\n"
        "from fastmcp.server.dependencies import get_http_request\n"
        "from starlette.middleware import Middleware\nimport requests\n"
        "class Guard:\n"
        "    def __init__(self, app): self.app = app\n"
        "    async def __call__(self, scope, receive, send):\n        "
        + body.replace("\n", "\n        ")
        + "\n"
        "class App(FastMCP):\n"
        "    def http_app(self, middleware=None, **kwargs):\n"
        "        return super().http_app(middleware=[Middleware(Guard)], **kwargs)\n"
        "mcp = App('test')\n@mcp.tool()\ndef fetch(url: str):\n"
        + getter
        + "    return requests.get(url)\n",
    )
    assert len(findings) == expected


@pytest.mark.parametrize("checked", ["url", "other"])
def test_returned_ip_error_checks_the_mapped_address_of_the_requested_url(
    tmp_path: Path, checked: str
) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX + "import ipaddress\n"
        "def ip_error(hostname):\n"
        "    try: addr = ipaddress.ip_address(hostname)\n"
        "    except ValueError: return None\n"
        "    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:\n"
        "        addr = addr.ipv4_mapped\n"
        "    if not addr.is_global: return 'blocked address'\n"
        "    return None\n"
        "def url_error(url):\n"
        "    parsed = urlparse(url)\n"
        "    if parsed.scheme not in ('https', 'http'): return 'blocked scheme'\n"
        "    error = ip_error(parsed.hostname)\n"
        "    if error: return error\n"
        "    return None\n"
        "@mcp.tool()\ndef fetch(url: str, other: str):\n"
        f"    error = url_error({checked})\n"
        "    if error: raise ValueError(error)\n"
        "    return requests.get(url)\n",
    )
    assert len(findings) == (0 if checked == "url" else 1)


@pytest.mark.parametrize("checked", ["url", "other"])
@pytest.mark.parametrize("replace_url", [False, True])
def test_optional_url_guard_applies_when_the_same_value_is_later_used(
    tmp_path: Path, checked: str, replace_url: bool
) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX + "@mcp.tool()\ndef fetch(url: str | None, other: str):\n"
        f"    if {checked}:\n"
        "        "
        + CHECK.replace("urlparse(url)", f"urlparse({checked})")
        .replace("\n", "\n    ")
        .rstrip()
        + "\n"
        + ("    url = other\n" if replace_url else "")
        + "    if url: return requests.get(url)\n",
    )
    assert len(findings) == (0 if (checked == "other") == replace_url else 1)


@pytest.mark.parametrize("guard", ["", CHECK])
def test_conditionally_assigned_mapping_retains_its_member_guards(
    tmp_path: Path, guard: str
) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX + "def prepare(state, url):\n"
        "    if not url: return\n"
        + ("    " + guard if guard else "")
        + "    state['headers'] = {'url': url}\n"
        "@mcp.tool()\ndef fetch(url: str | None):\n"
        "    state = {}\n    prepare(state, url)\n"
        "    headers = state.get('headers')\n"
        "    if headers: return requests.get(headers['url'])\n",
    )
    assert len(findings) == (0 if guard else 1)


@pytest.mark.parametrize("guard", ["", CHECK])
def test_reading_dictionary_keys_does_not_escape_its_validated_values(
    tmp_path: Path, guard: str
) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX
        + "@mcp.tool()\ndef fetch(url: str):\n"
        + ("    " + guard if guard else "")
        + "    options = {'url': url}\n"
        "    log(list(options.keys()))\n"
        "    return requests.get(options['url'])\n",
    )
    assert len(findings) == (0 if guard else 1)


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("escaped", [False, True])
def test_known_dictionary_membership_preserves_nested_state(
    tmp_path: Path, enabled: bool, escaped: bool
) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX
        + "@mcp.tool()\ndef fetch(url: str, other: str):\n    "
        + CHECK
        + "    scope = {'state': {'url': url}}\n"
        + ("    unknown(scope)\n" if escaped else "")
        + "    scope = dict(scope)\n"
        + (
            "    if 'state' not in scope:\n"
            if enabled
            else "    if 'state' in scope:\n"
        )
        + "        scope['state'] = {'url': other}\n"
        + "    return requests.get(scope['state']['url'])\n",
    )
    assert len(findings) == (0 if enabled and not escaped else 1)


@pytest.mark.parametrize(
    "mutation",
    [
        "",
        "headers['url'] = other",
        "original['url'] = other",
        "headers.update({'url': other})",
        "unknown(headers, other)",
    ],
)
def test_optional_mapping_with_empty_default_preserves_alias_writes(
    tmp_path: Path, mutation: str
) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX
        + "@mcp.tool()\ndef fetch(url: str, other: str, selected: bool):\n    "
        + CHECK
        + "    original = {'url': url}\n    state = {}\n"
        + "    if selected: state['headers'] = original\n"
        + "    headers = state.get('headers', {})\n"
        + ("    " + mutation + "\n" if mutation else "")
        + "    return requests.get(headers.get('url'))\n",
    )
    assert len(findings) == bool(mutation)


@pytest.mark.parametrize("validate_last", [False, True])
def test_registered_middleware_order_controls_the_requested_value(
    tmp_path: Path, validate_last: bool
) -> None:
    layers = "Overwrite, Validate" if validate_last else "Validate, Overwrite"
    findings = scan(
        tmp_path / "target",
        "from fastmcp import FastMCP\n"
        "from fastmcp.server.dependencies import get_http_request\n"
        "from starlette.middleware import Middleware\n"
        "from starlette.requests import Request\n"
        "from urllib.parse import urlparse\nimport requests\n"
        "class Validate:\n"
        "    def __init__(self, app): self.app = app\n"
        "    async def __call__(self, scope, receive, send):\n"
        "        request = Request(scope)\n"
        "        url = request.state.url\n        "
        + CHECK.replace("\n", "\n    ").rstrip()
        + "\n"
        "        await self.app(scope, receive, send)\n"
        "class Overwrite:\n"
        "    def __init__(self, app): self.app = app\n"
        "    async def __call__(self, scope, receive, send):\n"
        "        request = Request(scope)\n"
        "        request.state.url = request.headers.get('X-URL')\n"
        "        await self.app(scope, receive, send)\n"
        "class App(FastMCP):\n"
        "    def http_app(self, middleware=None, **kwargs):\n"
        "        return super().http_app(middleware=["
        + ", ".join(f"Middleware({name})" for name in layers.split(", "))
        + "], **kwargs)\n"
        "mcp = App('test')\n@mcp.tool()\ndef fetch():\n"
        "    return requests.get(get_http_request().state.url)\n",
    )
    assert len(findings) == (0 if validate_last else 1)


@pytest.mark.parametrize("enabled", [False, True])
def test_plain_boolean_helper_preserves_request_reachability(
    tmp_path: Path, enabled: bool
) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX
        + f"def enabled(): return {enabled!r}\n"
        + "@mcp.tool()\ndef fetch(url: str):\n"
        "    if enabled(): return requests.get(url)\n",
    )
    assert len(findings) == enabled


def test_plain_true_helper_does_not_validate_the_requested_url(tmp_path: Path) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX + "def permitted(url): return True\n"
        "@mcp.tool()\ndef fetch(url: str):\n"
        "    if not permitted(url): raise ValueError('rejected')\n"
        "    return requests.get(url)\n",
    )
    assert len(findings) == 1


@pytest.mark.parametrize(
    ("guard", "expected"),
    [
        ("", 1),
        (
            'const u = new URL(url); if (u.protocol !== "https:" || '
            'u.hostname !== "images.example.com") throw new Error();',
            0,
        ),
        (
            'const u = new URL(req.query.other); if (u.protocol !== "https:" || '
            'u.hostname !== "images.example.com") throw new Error();',
            1,
        ),
    ],
)
def test_typescript_http_url_boundary(
    tmp_path: Path, guard: str, expected: int
) -> None:
    root = tmp_path / "target"
    root.mkdir()
    (root / "package.json").write_text(
        '{"dependencies":{"@modelcontextprotocol/sdk":"1.0.0"}}',
        encoding="utf-8",
    )
    (root / "server.ts").write_text(
        'import express from "express"; const app = express();\n'
        'app.get("/image", async (req, res) => {\n'
        "const url = req.query.url;\n" + guard + "\nreturn fetch(url);\n});\n",
        encoding="utf-8",
    )
    configuration = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-015"]}
    )
    assert (
        len(run_static_scan(configuration, uuid4(), timestamp=NOW).findings) == expected
    )


@pytest.mark.parametrize(
    ("condition", "replace_value", "expected", "expected_calls"),
    [
        ("allowed(url)", False, 0, ["allowed"]),
        ("allowed(url)", True, 1, ["allowed"]),
        ("True or allowed(url)", False, 1, []),
    ],
)
def test_url_guard_interprets_its_validator_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    condition: str,
    replace_value: bool,
    expected: int,
    expected_calls: list[str],
) -> None:
    from sentinel.static.discovery import Symbol
    from sentinel.static.path_flow import Value
    from sentinel.static.rules.sent015 import URLFlow

    original = URLFlow.function
    calls = []

    def traced(self: URLFlow, symbol: Symbol, bindings: dict[str, Value]) -> Value:
        if symbol.name == "allowed":
            calls.append(symbol.name)
        return original(self, symbol, bindings)

    monkeypatch.setattr(URLFlow, "function", traced)
    findings = scan(
        tmp_path / "target",
        PREFIX + "def allowed(value):\n"
        "    parsed = urlparse(value)\n"
        "    return parsed.scheme == 'https' and "
        "parsed.hostname == 'images.example.com'\n"
        "@mcp.tool()\ndef fetch(url: str, other: str):\n"
        f"    if not ({condition}): raise ValueError('rejected')\n"
        + ("    url = other\n" if replace_value else "")
        + "    return requests.get(url)\n",
    )
    assert len(findings) == expected
    assert calls == expected_calls


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


@pytest.mark.parametrize("fallback", ["None", "url"])
def test_guarded_url_in_optional_state(tmp_path: Path, fallback: str) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX + "def prepare(url):\n    state = {}\n"
        "    parsed = urlparse(url)\n"
        "    if parsed.scheme != 'https': return state\n"
        "    if parsed.hostname != 'images.example.com': return state\n"
        "    state['url'] = url\n    return state\n"
        "@mcp.tool()\ndef fetch(url:str):\n    state = prepare(url)\n"
        f"    return requests.get(state.get('url', {fallback}))\n",
    )
    assert len(findings) == (fallback == "url")


@pytest.mark.parametrize("checked", ["url", "other"])
def test_http_request_url_boundary(tmp_path: Path, checked: str) -> None:
    findings = scan(
        tmp_path / "target",
        "from fastapi import FastAPI, Request\nimport requests\n"
        "from urllib.parse import urlparse\napp=FastAPI()\n"
        '@app.get("/fetch")\ndef fetch(request: Request):\n'
        '    url=request.query_params.get("url")\n'
        '    other=request.query_params.get("other")\n    '
        + CHECK.replace("urlparse(url)", f"urlparse({checked})")
        + "    return requests.get(url)\n",
    )
    assert len(findings) == (checked != "url")


def test_unknown_mutator_cannot_preserve_url_member_guard(tmp_path: Path) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX
        + "@mcp.tool()\ndef fetch(url: str, other: str):\n    "
        + CHECK
        + '    state={"url":url}\n    mutate(state,other)\n'
        '    return requests.get(state["url"])\n',
    )
    assert len(findings) == 1


@pytest.mark.parametrize(
    "inspection",
    [
        "len(state)",
        "isinstance(state, dict)",
        "state.keys()",
        "state.items()",
        "state.values()",
    ],
)
def test_builtin_dictionary_inspection_preserves_url_guard(
    tmp_path: Path, inspection: str
) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX
        + "@mcp.tool()\ndef fetch(url: str):\n    "
        + CHECK
        + '    state={"url":url}\n    '
        + inspection
        + "\n"
        + '    return requests.get(state["url"])\n',
    )
    assert not findings


@pytest.mark.parametrize("name", ["len", "isinstance"])
def test_shadowed_inspection_is_not_a_builtin(tmp_path: Path, name: str) -> None:
    findings = scan(
        tmp_path / "target",
        PREFIX
        + name
        + " = unknown_inspection\n"
        + "@mcp.tool()\ndef fetch(url: str, other: str):\n    "
        + CHECK
        + '    state={"url":url}\n    '
        + name
        + "(state, other)\n"
        + '    return requests.get(state["url"])\n',
    )
    assert len(findings) == 1


@pytest.mark.parametrize(
    ("declarations", "body", "expected"),
    [
        (
            "VERSION = 'v24.0'\nBASE = f'https://graph.example.com/{VERSION}'",
            "url = f'{BASE}/{endpoint}'",
            0,
        ),
        (
            "VERSION = 'v24.0'\nBASE = 'https://graph.example.com/' + VERSION",
            "url = BASE + '/' + endpoint",
            0,
        ),
        (
            "BASE = 'https://graph.example.com/'",
            "base = BASE\nurl = f'{base}{endpoint}'",
            0,
        ),
        (
            "BASE = 'https://graph.example.com/'",
            "base = endpoint\nurl = f'{base}/image'",
            1,
        ),
        (
            "HOST = '127.0.0.1'\nBASE = f'http://{HOST}/'",
            "url = f'{BASE}{endpoint}'",
            1,
        ),
        (
            "SCHEME = 'https'\nBASE = f'{SCHEME}://'",
            "url = f'{BASE}{endpoint}/image'",
            1,
        ),
        ("BASE = 'https://graph.example.com'", "url = f'{BASE}{endpoint}'", 1),
        ("BASE = 'https://graph.example.com/'", "url = f'{BASE!r}{endpoint}'", 1),
    ],
)
def test_python_composed_url_authority(
    declarations: str, body: str, expected: int
) -> None:
    from sentinel.static.rules.sent012 import analyze as analyze_python
    from sentinel.static.rules.sent015 import URLFlow
    from tests.test_python_discovery import program

    source = PREFIX + declarations + "\n@mcp.tool()\ndef fetch(endpoint: str):\n"
    source += "\n".join("    " + line for line in body.splitlines())
    source += "\n    return requests.get(url)\n"
    index = program({"server.py": source})
    state = RuleRunState()
    analyze_python(index, state, flow=URLFlow(index, state, time.monotonic() + 10))
    assert len(state.matches) == expected
