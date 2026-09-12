"""Prepared HTTPX requests must retain destination flow and narrow guard evidence."""

from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.finding import StaticEvidence
from sentinel.static.engine import run_static_scan
from sentinel.static.model import StaticScanResult
from tests.conftest import NOW, make_target

PREFIX = """from mcp.server.fastmcp import FastMCP
import httpx
from ipaddress import ip_address, ip_network
from urllib.parse import urlparse, urlunparse
mcp = FastMCP("prepared")
"""


def report(root: Path, source: str) -> StaticScanResult:
    make_target(root, target_yaml="")
    (root / "server.py").write_text(source)
    config = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-015"]}
    )
    return run_static_scan(config, uuid4(), timestamp=NOW)


@pytest.mark.parametrize("client", ["Client", "AsyncClient"])
@pytest.mark.parametrize("keyword", [False, True])
def test_prepared_request_is_analyzed_at_send(
    tmp_path: Path, client: str, keyword: bool
) -> None:
    build = "method='GET', url=url" if keyword else "'GET', url"
    send = "request=request" if keyword else "request"
    result = report(
        tmp_path,
        PREFIX
        + f"""@mcp.tool()
def fetch(url: str):
    client = httpx.{client}()
    request = client.build_request({build})
    return client.send({send}, stream=True)
""",
    )
    assert len(result.findings) == 1
    assert isinstance(result.findings[0].evidence, StaticEvidence)
    assert "client.send(" in result.findings[0].evidence.snippet
    assert not any(
        "client.send" in w.message or "client.build_request" in w.message
        for w in result.warnings
    )


GUARD = """BLOCKED = (ip_network("10.0.0.0/8"), ip_network("100.64.0.0/10"))
def blocked(hostname):
    ip = ip_address(hostname)
    if any(ip in network for network in BLOCKED):
        return True
    return False

def validate(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError()
    hostname = parsed.hostname.rstrip(".").lower()
    if blocked(hostname):
        raise ValueError()
"""


@pytest.mark.parametrize(
    ("guard", "check", "mutation", "qualified"),
    [
        (GUARD, "validate(url)", "pass", True),
        (
            GUARD.replace(
                'ip_network("100.64.0.0/10")', 'ip_network("192.168.0.0/16")'
            ),
            "validate(url)",
            "pass",
            False,
        ),
        (GUARD, "pass", "pass", False),
        (GUARD, "validate(other)", "pass", False),
        (
            GUARD,
            "try:\n        validate(url)\n    except ValueError:\n        pass",
            "pass",
            False,
        ),
        (GUARD, "validate(url)", "request.url = other", False),
        (GUARD, "validate(url)", "alias = request\n    alias.url = other", False),
        (GUARD, "validate(url)", "unknown(request)", False),
        (
            GUARD.replace(
                "if any(ip in network for network in BLOCKED):",
                "if any(ip in network for network in BLOCKED if condition):",
            ),
            "validate(url)",
            "pass",
            False,
        ),
        (GUARD, "unknown(BLOCKED)\n    validate(url)", "pass", False),
        (GUARD, "BLOCKED[1].network_address = other\n    validate(url)", "pass", False),
    ],
)
def test_same_send_path_requires_enforced_shared_space_guard(
    tmp_path: Path, guard: str, check: str, mutation: str, qualified: bool
) -> None:
    result = report(
        tmp_path,
        PREFIX
        + guard
        + f"""@mcp.tool()
def fetch(url: str, other: str):
    {check}
    client = httpx.Client()
    request = client.build_request("GET", url)
    {mutation}
    return client.send(request)
""",
    )
    assert len(result.findings) == 1
    assert isinstance(result.findings[0].evidence, StaticEvidence)
    assert "client.send(request)" in result.findings[0].evidence.snippet
    assert ("100.64.0.0/10" in result.findings[0].description) == qualified
    assert not any(
        "unresolved call to client.send" in w.message for w in result.warnings
    )


@pytest.mark.parametrize(
    "change", ["client.send = unknown", "unknown(client)", "httpx.Client = unknown"]
)
def test_rebound_client_does_not_claim_recognized_send(
    tmp_path: Path, change: str
) -> None:
    prefix = (
        "" if change == "httpx.Client = unknown" else "client = httpx.Client()\n    "
    )
    suffix = (
        "\n    client = httpx.Client()" if change == "httpx.Client = unknown" else ""
    )
    result = report(
        tmp_path,
        PREFIX
        + f"""@mcp.tool()
def fetch(url: str):
    {prefix}{change}{suffix}
    request = client.build_request("GET", url)
    return client.send(request)
""",
    )
    assert not result.findings
    assert any("unresolved call to client.send" in w.message for w in result.warnings)


@pytest.mark.parametrize("guarded", [True, False])
def test_rebuilt_url_keeps_only_initial_rejection_scope(
    tmp_path: Path, guarded: bool
) -> None:
    guard = (
        GUARD
        if guarded
        else GUARD.replace(
            'ip_network("100.64.0.0/10")', 'ip_network("192.168.0.0/16")'
        )
    )
    result = report(
        tmp_path,
        PREFIX
        + guard
        + """
async def checked_send(client, url):
    validate(url)
    parsed = urlparse(url)
    safe_ip = await resolve_address(url)
    target = urlunparse((parsed.scheme, safe_ip, parsed.path,
                        parsed.params, parsed.query, parsed.fragment))
    request = client.build_request("GET", target)
    return await client.send(request)

@mcp.tool()
async def fetch(url: str):
    client = httpx.AsyncClient()
    return await checked_send(client, url)
""",
    )
    assert len(result.findings) == 1
    assert ("100.64.0.0/10" in result.findings[0].description) == guarded
    assert "Other destinations" in result.findings[0].description if guarded else True


@pytest.mark.parametrize("guarded", [True, False])
def test_async_model_and_pinning_keep_guard_sensitive_send(
    tmp_path: Path, guarded: bool
) -> None:
    source = (
        PREFIX
        + """from pydantic import BaseModel, Field, ConfigDict
import asyncio

class StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

class FetchInput(StrictRequest):
    url: str = Field(min_length=1)

BLOCKED = (ip_network("100.64.0.0/10"),)

def normalize(host):
    return host.rstrip(".").lower()

def unsafe(value):
    try:
        ip = ip_address(value)
    except ValueError:
        return False
    if any(ip in network for network in BLOCKED):
        return True
    return any((ip.is_private, ip.is_loopback, ip.is_link_local,
                ip.is_reserved, ip.is_multicast, ip.is_unspecified))

def validate_shape(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError()
    hostname = normalize(parsed.hostname)
    if unsafe(hostname):
        raise ValueError()

async def validate(url):
    validate_shape(url)
    await asyncio.to_thread(resolve_addresses, url)

def pinned(url, address):
    parsed = urlparse(url)
    host = f"[{address}]" if ":" in address else address
    port = parsed.port
    target = host if port is None else f"{host}:{port}"
    return urlunparse((parsed.scheme, target, parsed.path or "/",
                      parsed.params, parsed.query, parsed.fragment))

async def execute(client, url):
    current = url
    for _ in range(4):
        await validate(current)
        address, port = await resolve_safe_address(current)
        request = client.build_request("GET", pinned(current, address))
        response = await client.send(request, stream=True)
        return response

async def fetch_page(url):
    request = FetchInput(url=url)
    try:
        await validate(request.url)
    except ValueError:
        return "blocked"
    async with httpx.AsyncClient() as client:
        return await execute(client, request.url)

@mcp.tool()
async def fetch(url: str):
    return await fetch_page(url)
"""
    )
    if not guarded:
        source = source.replace(
            'ip_network("100.64.0.0/10")', 'ip_network("192.168.0.0/16")'
        )
    result = report(tmp_path, source)
    assert len(result.findings) == 1
    assert isinstance(result.findings[0].evidence, StaticEvidence)
    assert "client.send(request" in result.findings[0].evidence.snippet
    assert ("100.64.0.0/10" in result.findings[0].description) == guarded
    assert not any(
        "unresolved call to client.send" in w.message for w in result.warnings
    )


@pytest.mark.parametrize(
    "expression", ["client.build_request('GET', url)", "httpx.Request('GET', url)"]
)
def test_building_without_sending_is_not_a_request(
    tmp_path: Path, expression: str
) -> None:
    result = report(
        tmp_path,
        PREFIX
        + f"""@mcp.tool()
def fetch(url: str):
    client = httpx.Client()
    return {expression}
""",
    )
    assert not result.findings


@pytest.mark.parametrize("mutation", ["ip._ip = 134744072", "unknown(ip)"])
def test_changed_ip_object_does_not_qualify_the_original_url(
    tmp_path: Path, mutation: str
) -> None:
    guard = GUARD.replace(
        "    if any(ip in network", f"    {mutation}\n    if any(ip in network"
    )
    result = report(
        tmp_path,
        PREFIX
        + guard
        + """@mcp.tool()
def fetch(url: str):
    validate(url)
    client = httpx.Client()
    request = client.build_request("GET", url)
    return client.send(request)
""",
    )
    assert len(result.findings) == 1
    assert "100.64.0.0/10" not in result.findings[0].description


@pytest.mark.parametrize("method", ["build_request", "send"])
def test_unknown_prepared_request_evaluates_arguments_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, method: str
) -> None:
    from sentinel.static.discovery import Symbol
    from sentinel.static.path_flow import Value
    from sentinel.static.rules.sent015 import URLFlow

    original = URLFlow.function
    calls = []

    def traced(self: URLFlow, symbol: Symbol, bindings: dict[str, Value]) -> Value:
        if symbol.name == "argument":
            calls.append(symbol)
        return original(self, symbol, bindings)

    monkeypatch.setattr(URLFlow, "function", traced)
    result = report(
        tmp_path,
        PREFIX
        + f"""def argument(url): return url
@mcp.tool()
def fetch(url: str):
    client = httpx.Client()
    return client.{method}(argument(url))
""",
    )
    assert len(calls) == 1
    assert not result.findings
    assert any(
        f"unresolved call to client.{method}" in w.message for w in result.warnings
    )


def test_module_level_client_replacement_does_not_claim_supported_send(
    tmp_path: Path,
) -> None:
    result = report(
        tmp_path,
        PREFIX
        + """httpx.Client = unknown
@mcp.tool()
def fetch(url: str):
    client = httpx.Client()
    request = client.build_request("GET", url)
    return client.send(request)
""",
    )
    assert not result.findings
    assert any("unresolved call to client.send" in w.message for w in result.warnings)


@pytest.mark.parametrize("module_path", ["ipaddress.py", "ipaddress/__init__.py"])
def test_local_ip_module_cannot_establish_standard_library_rejection(
    tmp_path: Path, module_path: str
) -> None:
    module = tmp_path / module_path
    module.parent.mkdir(parents=True, exist_ok=True)
    module.write_text(
        "def ip_network(value):\n    return ()\n"
        "def ip_address(value):\n    return value\n"
    )
    result = report(
        tmp_path,
        PREFIX
        + GUARD
        + """@mcp.tool()
def fetch(url: str):
    validate(url)
    client = httpx.Client()
    request = client.build_request("GET", url)
    return client.send(request)
""",
    )
    assert len(result.findings) == 1
    assert "100.64.0.0/10" not in result.findings[0].description
