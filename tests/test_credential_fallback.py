"""Caller credential absence must not select operator credentials across HTTP."""

from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.static.engine import run_static_scan
from tests.conftest import NOW, make_target


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
        + '    return requests.get("https://api.example.com/", headers=headers)\n',
        encoding="utf-8",
    )
    configuration = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-016"]}
    )
    findings = run_static_scan(configuration, uuid4(), timestamp=NOW).findings
    assert len(findings) == (not replace_token)
