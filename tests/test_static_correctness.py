"""Phase 16 source-only regressions; assertions describe the accepted end state.

These tests intentionally expose failures before the detector checkpoints. They
are development regressions, not held-out detection-accuracy measurements.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from textwrap import indent
from uuid import uuid4

import pytest

from scripts.capture_gpt_reviews import historical_eval_findings
from sentinel.config import LlmConfig, ReasoningEffort, load_configuration
from sentinel.finding import FileLocation, FindingStatus
from sentinel.llm.cache import ReviewCache
from sentinel.llm.semantic_reviewer import SemanticReviewer
from sentinel.llm.tools import extract_tool_catalog
from sentinel.static.engine import run_static_scan
from sentinel.static.model import StaticScanResult
from tests.conftest import NOW, make_target

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("python", "typescript")

# Locally generated public test vectors signing b"{}"; no private keys retained.
SIGNATURE_VECTORS = {
    "ecdsa-sha256": (
        "-----BEGIN PUBLIC KEY-----\n"
        "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE5ks1yE/F69wrvYXY8Oqfo/GocHun\n"
        "EwKN3ScSzOxds7uU3iOwLEPhmzGm61TcXhM6VWf8hDU2qAvLQmB2KuZP5w==\n"
        "-----END PUBLIC KEY-----\n",
        "30450220102f088e99d13cc970d4687dcaa82de783ecaa959ac701940f2370c3d7248a44022100a5fcb4596a574c78743426b52badf3f267849c47789f50ce55e0cc158e1cd37a",
    ),
    "ed25519": (
        "-----BEGIN PUBLIC KEY-----\n"
        "MCowBQYDK2VwAyEANu5zVoslLI2shz61q+EMLM5FENUQ3RxD3KbibwNThsk=\n"
        "-----END PUBLIC KEY-----\n",
        "3489dda3f218de71b061d53d77a69ba1718c63647a95eebb2db6fcd231e4f211b0741bea9d154239bea721ac0844acb338581b3778396bfd337af23318581f0c",
    ),
    "rsa-pss-sha256": (
        "-----BEGIN PUBLIC KEY-----\n"
        "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwJgXL+w9CIoVFumimwjT\n"
        "201Sx/4A+3jdKs7I9dA3fqo5Q7353LrIjKl+TUYEKVkb/QdUNKG846+VRiFRRF8/\n"
        "tW6jnUfp51JzhaKjCSaEAWsHFhqXg4bgZrEdpbuNHH56d3NBINCPHt9f6bbYkKDv\n"
        "Zre0fOpDPK1wYnWmwX8TXUjELW9MsL8ySpLzvDJm4eS357ckdyuUZuCWzP4cwNHx\n"
        "7UMTJtIiARWsHy3y8StbqJ8CWRRRNTjkoSiDdC15UZZG52Sm/KaexV1poVRDO3bT\n"
        "AWX6cVX9c0IhpUyjOSD0QAwXYUlcFGvmU8ILk3x0Zf/LWjNIAMtqi1qpOxVPT4QJ\n"
        "VwIDAQAB\n"
        "-----END PUBLIC KEY-----\n",
        "783e5ebadba1e8ce2b6a87f49275a201e53683c96a95ad6d28f75d8643506974044094546cf748675452c4c5c7f4aca5c6c9bf32aaf334ca5c5a7563b8c77ea5445d28f50a4b233d2c45c49a45859f60405ee9866797f9a21a57e95463e7eaf2685519d70516291ffbbc3c081509d593ee0fc2ef73126586c1cf133c4b37b550cdb4321b12cdea9ca57829c2a5b564d5215f64e52bf9b79f73427c61a75217f25e8502eed5115ffa9958418b1457fe2614315fd06ede37fe705ba08af2d11fc21da1389ba5a140dd9e984be55bf9885ed0f070485e297ebfcab6edd7eb7bfe536dcceab4a3aab6572fc2fbb10907e8749721405f6fba68c39755b2f1146dbd42",
    ),
}


def _scan(
    tmp_path: Path,
    language: str,
    rule: str,
    source: str,
    *,
    suppressed: bool = False,
    files: dict[str, str | bytes] | None = None,
) -> StaticScanResult:
    configuration = f'[scanner]\nrules = ["{rule}"]\n'
    if rule == "SENT-004":
        sanitizer = "server.sanitize" if language == "python" else "sanitize"
        configuration += f'[rules.SENT-004]\nsanitizers = ["{sanitizer}"]\n'
    root = tmp_path / "target"
    if language == "python":
        make_target(root, scanner_toml=configuration)
        preamble = """\
from pathlib import Path
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("phase16")
Path(__file__).with_name("executed-marker").write_text("executed")
enabled = False
untrusted = 42
replacement = b'{"injected":true}'
"""
        suffix = "py"
    else:
        root.mkdir()
        (root / "package.json").write_text(
            json.dumps(
                {
                    "name": "phase16-control",
                    "version": "0.0.0",
                    "dependencies": {"@modelcontextprotocol/server": "^2.0.0"},
                }
            ),
            encoding="utf-8",
        )
        (root / "sentinel.toml").write_text(configuration, encoding="utf-8")
        preamble = """\
import { McpServer } from "@modelcontextprotocol/server";
import { writeFileSync } from "node:fs";
const server = new McpServer({ name: "phase16", version: "0.0.0" });
writeFileSync(new URL("./executed-marker", import.meta.url), "executed");
const enabled = false;
const untrusted = 42;
const replacement = '{"injected":true}';
"""
        suffix = "ts"
    (root / f"server.{suffix}").write_text(preamble + source, encoding="utf-8")
    (root / "tools.json").write_text("{}", encoding="utf-8")
    for name, text in (files or {}).items():
        if isinstance(text, bytes):
            (root / name).write_bytes(text)
        else:
            (root / name).write_text(text, encoding="utf-8")
    loaded = load_configuration(root, environ={}, static_only=True)
    result = run_static_scan(loaded, uuid4(), timestamp=NOW)
    assert not (root / "executed-marker").exists(), "scanner executed target code"
    for finding in result.findings:
        assert finding.rule_id == rule
        assert finding.status is (
            FindingStatus.SUPPRESSED if suppressed else FindingStatus.NEEDS_REVIEW
        )
        assert isinstance(finding.location, FileLocation)
        assert finding.location.path == f"server.{suffix}"
    return result


def _tool(language: str, body: str, helpers: str = "") -> str:
    if language == "python":
        return helpers + "\n@mcp.tool()\ndef run(value: str):\n" + indent(body, "    ")
    return (
        helpers
        + '\nserver.registerTool("run", {}, ({ value }) => {\n'
        + body
        + "\n});\n"
    )


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize(
    ("python", "typescript", "unsafe"),
    [
        pytest.param("return eval(value)", "return eval(value);", True, id="direct"),
        pytest.param(
            "return execute(value)", "return execute(value);", True, id="helper"
        ),
        pytest.param(
            "return forward(value)", "return forward(value);", True, id="chain"
        ),
        pytest.param(
            "return eval(identity(value))",
            "return eval(identity(value));",
            True,
            id="returned-input",
        ),
        pytest.param(
            "return eval(constant(value))",
            "return eval(constant(value));",
            False,
            id="returned-constant",
        ),
        pytest.param(
            'return execute("1 + 1")',
            'return execute("1 + 1");',
            False,
            id="constant-argument",
        ),
        pytest.param(
            'value = "1 + 1"\nreturn execute(value)',
            'value = "1 + 1";\nreturn execute(value);',
            False,
            id="overwrite",
        ),
        pytest.param("return value", "return value;", False, id="unused-helper"),
        pytest.param(
            "return execute(raw=value)",
            "return destructured({ raw: value });",
            True,
            id="explicit-binding",
        ),
    ],
)
def test_execution_flow(
    tmp_path: Path, language: str, python: str, typescript: str, unsafe: bool
) -> None:
    helpers = (
        """\
def execute(raw):
    return eval(raw)
def forward(raw):
    return execute(raw)
def identity(raw):
    return raw
def constant(raw):
    return "1 + 1"
"""
        if language == "python"
        else """\
function execute(raw) { return eval(raw); }
function forward(raw) { return execute(raw); }
function identity(raw) { return raw; }
function constant(raw) { return "1 + 1"; }
function destructured({ raw }) { return eval(raw); }
"""
    )
    body = python if language == "python" else typescript
    result = _scan(tmp_path, language, "SENT-002", _tool(language, body, helpers))
    assert bool(result.findings) is unsafe
    if unsafe and "eval(" not in body:
        # Helper findings belong to the tool call, not the helper definition.
        for finding in result.findings:
            assert isinstance(finding.location, FileLocation)
            source = (tmp_path / "target" / finding.location.path).read_text()
            line = source.splitlines()[finding.location.range.start_line - 1]
            assert body.strip().removesuffix(";") in line
            assert "eval" in finding.description


@pytest.mark.parametrize("language", LANGUAGES)
def test_helper_renaming_and_placement(tmp_path: Path, language: str) -> None:
    body = "return renamed_bridge(value)"
    helper = "def renamed_bridge(argument):\n    return eval(argument)\n"
    if language == "typescript":
        body += ";"
        helper = "const renamed_bridge = (argument) => eval(argument);\n"
    # Registration precedes the helper definition, but invocation follows it.
    source = _tool(language, body) + "\n" + helper
    result = _scan(tmp_path, language, "SENT-002", source)
    assert result.findings


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize(
    ("python", "typescript"),
    [
        pytest.param(
            "def unresolved(raw):\n    return unresolved(raw)",
            "function unresolved(raw) { return unresolved(raw); }",
            id="recursion",
        ),
        pytest.param(
            "from external_module import unresolved",
            'import { unresolved } from "external-module";',
            id="imported-helper",
        ),
    ],
)
def test_unresolved_flow_is_visible_without_inventing_execution(
    tmp_path: Path, language: str, python: str, typescript: str
) -> None:
    source = _tool(
        language,
        "return unresolved(value)"
        if language == "python"
        else "return unresolved(value);",
        python if language == "python" else typescript,
    )
    result = _scan(tmp_path, language, "SENT-002", source)
    assert result.findings == ()
    filename = "server.py" if language == "python" else "server.ts"
    assert any(filename in warning.message for warning in result.warnings)


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize(
    ("python", "typescript", "unsafe"),
    [
        pytest.param("", "", True, id="unchecked"),
        pytest.param(
            'Model.model_validate({"record_id": "fixed"})',
            'schema.parse({ record_id: "fixed" });',
            True,
            id="unrelated-validation",
        ),
        pytest.param(
            "Model.model_validate(payload)",
            "schema.parse(payload);",
            True,
            id="discarded-parsed-output",
        ),
        pytest.param(
            "payload = Model.model_validate(payload).model_dump()",
            "payload = schema.parse(payload);",
            False,
            id="consumed-parsed-output",
        ),
        pytest.param(
            "if enabled:\n    Model.model_validate(payload)",
            "if (enabled) { schema.parse(payload); }",
            True,
            id="conditional-check",
        ),
        pytest.param(
            'Model.model_validate(payload)\npayload = {"record_id": untrusted}',
            "payload = schema.parse(payload);\npayload = { record_id: untrusted };",
            True,
            id="replacement-after-validation",
        ),
        pytest.param(
            "check(payload)", "check(payload);", False, id="custom-type-guard"
        ),
        pytest.param(
            "jsonschema.validate(payload, SCHEMA)",
            "if (!validate(payload)) { throw new Error(); }",
            False,
            id="non-transforming-schema-validation",
        ),
        pytest.param(
            'jsonschema.validate(payload, SCHEMA)\nother = payload["other"]',
            (
                "if (!validate(payload)) { throw new Error(); }\n"
                "const other = payload.other;"
            ),
            True,
            id="partial-field-coverage",
        ),
        pytest.param(
            (
                'if isinstance(payload.get("record_id"), str):\n'
                "    pass\nelse:\n    return None"
            ),
            (
                "const parsed = schema.safeParse(payload);\n"
                "if (!parsed.success) { throw new Error(); }\n"
                "payload = parsed.data;"
            ),
            False,
            id="checked-success-result",
        ),
        pytest.param(
            'if not isinstance(payload.get("other"), str):\n    raise ValueError()',
            'if (typeof payload.other !== "string") { throw new Error(); }',
            True,
            id="wrong-field",
        ),
        pytest.param(
            'if payload["record_id"] not in ("one", "two"):\n    raise ValueError()',
            'if (!["one", "two"].includes(payload.record_id)) { throw new Error(); }',
            False,
            id="literal-allowlist",
        ),
        pytest.param(
            'if not isinstance(payload.get("record_id"), str):\n    return None',
            'if (typeof payload.record_id !== "string") { return null; }',
            False,
            id="rejecting-early-return",
        ),
        pytest.param(
            "if enabled:\n    check(payload)",
            "if (enabled) { check(payload); }",
            True,
            id="bypassed-custom-validator",
        ),
        pytest.param(
            'valid = isinstance(payload.get("record_id"), str)',
            "const valid = schema.safeParse(payload);",
            True,
            id="ignored-boolean-result",
        ),
        pytest.param(
            'used = payload["record_id"]\nModel.model_validate(payload)',
            "const used = payload.record_id;\nschema.parse(payload);",
            True,
            id="late-validation",
        ),
        pytest.param(
            (
                "check(payload)\n"
                'if len(payload["record_id"]) > 20:\n'
                "    raise ValueError()"
            ),
            (
                "check(payload);\n"
                "if (payload.record_id.length > 20) { throw new Error(); }"
            ),
            False,
            id="type-and-length-bound",
        ),
        pytest.param(
            (
                'if not isinstance(payload.get("record_id"), int):\n'
                "    raise ValueError()\n"
                'if payload["record_id"] < 1:\n'
                "    raise ValueError()"
            ),
            (
                'if (typeof payload.record_id !== "number") { throw new Error(); }\n'
                "if (payload.record_id < 1) { throw new Error(); }"
            ),
            False,
            id="type-and-numeric-bound",
        ),
    ],
)
def test_input_validation(
    tmp_path: Path, language: str, python: str, typescript: str, unsafe: bool
) -> None:
    if language == "python":
        source = """\
import jsonschema
from pydantic import BaseModel
SCHEMA = {"type": "object", "properties": {"record_id": {"type": "string"}},
          "required": ["record_id"]}
class Model(BaseModel):
    record_id: str
def check(payload):
    if not isinstance(payload.get("record_id"), str):
        raise ValueError("record_id must be a string")
@mcp.tool()
def lookup(payload: dict[str, object]):
"""
        source += indent(python + '\nreturn payload["record_id"]\n', "    ")
    else:
        source = """\
import Ajv from "ajv";
import { z } from "zod";
const schema = z.object({ record_id: z.string() });
const validate = new Ajv().compile({
  type: "object", properties: { record_id: { type: "string" } },
  required: ["record_id"],
});
function check(payload) {
  if (typeof payload.record_id !== "string") { throw new Error(); }
}
server.registerTool("lookup", {}, (payload) => {
"""
        source += typescript + "\nreturn payload.record_id;\n});\n"
    result = _scan(tmp_path, language, "SENT-003", source)
    assert bool(result.findings) is unsafe


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize("covers_consumed_field", (True, False))
def test_framework_schema_must_cover_consumed_input(
    tmp_path: Path, language: str, covers_consumed_field: bool
) -> None:
    if language == "python":
        annotation = "str" if covers_consumed_field else "object"
        source = f"""\
@mcp.tool()
def lookup(record_id: {annotation}):
    return record_id
"""
    else:
        schema = "{ record_id: z.string() }" if covers_consumed_field else "{}"
        source = f"""\
import {{ z }} from "zod";
server.registerTool("lookup", {{ inputSchema: {schema} }}, ({{ record_id }}) => {{
  return record_id;
}});
"""
    result = _scan(tmp_path, language, "SENT-003", source)
    assert bool(result.findings) is not covers_consumed_field


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize(
    ("python", "typescript", "unsafe"),
    [
        pytest.param("", "", True, id="missing-check"),
        pytest.param(
            (
                "hmac.compare_digest(authorization, EXPECTED)\n"
                "if False:\n"
                "    raise HTTPException(401)"
            ),
            (
                "timingSafeEqual(Buffer.from(token), Buffer.from(EXPECTED));\n"
                "if (false) { res.status(401).end(); return; }"
            ),
            True,
            id="ignored-result",
        ),
        pytest.param(
            (
                "if not hmac.compare_digest(EXPECTED, EXPECTED):\n"
                "    raise HTTPException(401)"
            ),
            (
                "if (!timingSafeEqual(Buffer.from(EXPECTED), "
                "Buffer.from(EXPECTED))) { res.status(401).end(); return; }"
            ),
            True,
            id="unrelated-credentials",
        ),
        pytest.param(
            (
                'if authorization == "bypass":\n'
                "    return authorization\n"
                "if not hmac.compare_digest(authorization, EXPECTED):\n"
                "    raise HTTPException(401)"
            ),
            (
                'if (token === "bypass") { next(); return; }\n'
                "if (!timingSafeEqual(Buffer.from(token), "
                "Buffer.from(EXPECTED))) { res.status(401).end(); return; }"
            ),
            True,
            id="bypassed-verification",
        ),
        pytest.param(
            (
                "if not hmac.compare_digest(authorization, EXPECTED):\n"
                "    HTTPException(401)"
            ),
            (
                "if (!timingSafeEqual(Buffer.from(token), "
                "Buffer.from(EXPECTED))) { res.status(401); }"
            ),
            True,
            id="non-rejecting-failure",
        ),
        pytest.param(
            (
                "if not hmac.compare_digest(authorization, EXPECTED):\n"
                "    raise HTTPException(401)"
            ),
            (
                "if (!timingSafeEqual(Buffer.from(token), "
                "Buffer.from(EXPECTED))) { res.status(401).end(); return; }"
            ),
            False,
            id="enforced-verification",
        ),
        pytest.param(
            (
                "if not hmac.compare_digest(authorization, authorization):\n"
                "    raise HTTPException(401)"
            ),
            (
                "if (!timingSafeEqual(Buffer.from(token), "
                "Buffer.from(token))) { res.status(401).end(); return; }"
            ),
            True,
            id="request-derived-anchor",
        ),
    ],
)
def test_authentication_enforcement(
    tmp_path: Path, language: str, python: str, typescript: str, unsafe: bool
) -> None:
    if language == "python":
        source = """\
import hmac
from fastapi import Depends, FastAPI, Header, HTTPException
app = FastAPI()
EXPECTED = "expected"
def verify_token(authorization: str = Header()):
"""
        source += indent(python + "\nreturn authorization\n", "    ")
        source += """\
@app.get("/admin", dependencies=[Depends(verify_token)])
def admin():
    return {"secret": "protected"}
"""
    else:
        source = """\
import express from "express";
import { timingSafeEqual } from "node:crypto";
const app = express();
const EXPECTED = "expected";
function verifyToken(req, res, next) {
  const token = req.headers.authorization;
  if (typeof token !== "string" || token.length !== EXPECTED.length) {
    res.status(401).end(); return;
  }
"""
        source += typescript + "\nnext();\n}\n"
        source += (
            'app.get("/admin", verifyToken, (req, res) => res.send("protected"));\n'
        )
    result = _scan(tmp_path, language, "SENT-006", source)
    assert bool(result.findings) is unsafe


@pytest.mark.parametrize("application", ("app", "other"))
def test_authentication_middleware_is_not_route_enforcement(
    tmp_path: Path, application: str
) -> None:
    source = f"""\
from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import AuthenticationBackend
class Backend(AuthenticationBackend):
    async def authenticate(self, conn):
        return None
app = FastAPI()
other = FastAPI()
{application}.add_middleware(AuthenticationMiddleware, backend=Backend())
@app.get("/admin")
def admin():
    return {{"secret": "protected"}}
"""
    result = _scan(tmp_path, "python", "SENT-006", source)
    assert result.findings


@pytest.mark.parametrize("requires_identity", (True, False))
def test_starlette_permission_enforcement(
    tmp_path: Path, requires_identity: bool
) -> None:
    source = """\
import hmac
from starlette.applications import Starlette
from starlette.authentication import (
    AuthenticationBackend, AuthCredentials, SimpleUser, requires,
)
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route
class Backend(AuthenticationBackend):
    async def authenticate(self, conn):
        token = conn.headers.get("authorization", "")
        if not hmac.compare_digest(token, "expected"):
            return None
        return AuthCredentials(["authenticated"]), SimpleUser("maintainer")
"""
    if requires_identity:
        source += '@requires("authenticated")\n'
    source += """\
async def admin(request):
    return JSONResponse({"secret": "protected"})
app = Starlette(
    routes=[Route("/admin", admin)],
    middleware=[Middleware(AuthenticationMiddleware, backend=Backend())],
)
"""
    result = _scan(tmp_path, "python", "SENT-006", source)
    assert bool(result.findings) is not requires_identity


@pytest.mark.parametrize(
    ("setup", "unsafe"),
    [
        pytest.param(
            'app.use("/admin", bearerAuth({ token: "expected" }));',
            False,
            id="enforced-hono",
        ),
        pytest.param(
            'app.use("/admin", bearerAuth({ token: process.env.ADMIN_TOKEN }));',
            False,
            id="environment-token",
        ),
        pytest.param(
            'app.use("/admin", bearerAuth({ verifyToken: () => true }));',
            True,
            id="no-op-verifier",
        ),
        pytest.param(
            'other.use("/admin", bearerAuth({ token: "expected" }));',
            True,
            id="wrong-application",
        ),
        pytest.param(
            'app.use("/public/*", bearerAuth({ token: "expected" }));',
            True,
            id="wrong-path",
        ),
    ],
)
def test_hono_middleware_scope(tmp_path: Path, setup: str, unsafe: bool) -> None:
    source = """\
import { Hono } from "hono";
import { bearerAuth } from "hono/bearer-auth";
const app = new Hono();
const other = new Hono();
"""
    source += setup + '\napp.get("/admin", (c) => c.text("protected"));\n'
    result = _scan(tmp_path, "typescript", "SENT-006", source)
    assert bool(result.findings) is unsafe


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize(
    ("python", "typescript", "unsafe"),
    [
        pytest.param("", "", True, id="unverified"),
        pytest.param(
            "actual = hashlib.sha256(raw).hexdigest()",
            'const actual = createHash("sha256").update(raw).digest("hex");',
            True,
            id="digest-only",
        ),
        pytest.param(
            (
                "actual = hashlib.sha256(raw).hexdigest()\n"
                "hmac.compare_digest(actual, EXPECTED)"
            ),
            (
                'const actual = createHash("sha256").update(raw).digest("hex");\n'
                "actual === EXPECTED;"
            ),
            True,
            id="ignored-comparison",
        ),
        pytest.param(
            (
                'actual = hashlib.sha256(b"{}").hexdigest()\n'
                "if not hmac.compare_digest(actual, EXPECTED):\n"
                "    raise ValueError()"
            ),
            (
                'const actual = createHash("sha256").update("{}").digest("hex");\n'
                "if (actual !== EXPECTED) { throw new Error(); }"
            ),
            True,
            id="unrelated-bytes",
        ),
        pytest.param(
            (
                "actual = hashlib.sha256(raw).hexdigest()\n"
                "if not hmac.compare_digest(actual, actual):\n"
                "    raise ValueError()"
            ),
            (
                'const actual = createHash("sha256").update(raw).digest("hex");\n'
                "if (actual !== actual) { throw new Error(); }"
            ),
            True,
            id="self-comparison",
        ),
        pytest.param(
            (
                "actual = hashlib.sha256(raw).hexdigest()\n"
                "if enabled:\n"
                "    if not hmac.compare_digest(actual, EXPECTED):\n"
                "        raise ValueError()"
            ),
            (
                'const actual = createHash("sha256").update(raw).digest("hex");\n'
                "if (enabled) { if (actual !== EXPECTED) { throw new Error(); } }"
            ),
            True,
            id="conditional-verification",
        ),
        pytest.param(
            (
                "actual = hashlib.sha256(raw).hexdigest()\n"
                "if not hmac.compare_digest(actual, EXPECTED):\n"
                "    ValueError()"
            ),
            (
                'const actual = createHash("sha256").update(raw).digest("hex");\n'
                "if (actual !== EXPECTED) { new Error(); }"
            ),
            True,
            id="non-rejecting-failure",
        ),
        pytest.param(
            (
                "actual = hashlib.sha256(raw).hexdigest()\n"
                "if not hmac.compare_digest(actual, EXPECTED):\n"
                "    raise ValueError()"
            ),
            (
                'const actual = createHash("sha256").update(raw).digest("hex");\n'
                "if (actual !== EXPECTED) { throw new Error(); }"
            ),
            False,
            id="enforced-pinned-digest",
        ),
        pytest.param(
            (
                "actual = hashlib.sha256(raw).hexdigest()\n"
                "if not hmac.compare_digest(actual, EXPECTED):\n"
                "    raise ValueError()\n"
                "raw = replacement"
            ),
            (
                'const actual = createHash("sha256").update(raw).digest("hex");\n'
                "if (actual !== EXPECTED) { throw new Error(); }\n"
                "raw = replacement;"
            ),
            True,
            id="replacement-after-verification",
        ),
    ],
)
def test_manifest_integrity(
    tmp_path: Path, language: str, python: str, typescript: str, unsafe: bool
) -> None:
    expected = hashlib.sha256(b"{}").hexdigest()
    if language == "python":
        source = f'''\
import hashlib
import hmac
import json
EXPECTED = "{expected}"
def load_manifest():
    raw = Path("tools.json").read_bytes()
'''
        source += indent(python + "\nreturn json.loads(raw)\n", "    ")
    else:
        source = f'''\
import {{ readFileSync }} from "node:fs";
import {{ createHash }} from "node:crypto";
const EXPECTED = "{expected}";
function loadTools() {{
  let raw = readFileSync("tools.json", "utf8");
'''
        source += typescript + "\nreturn JSON.parse(raw);\n}\n"
    result = _scan(tmp_path, language, "SENT-007", source)
    assert bool(result.findings) is unsafe


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize(
    ("python", "typescript", "unsafe"),
    [
        pytest.param("safe = text", "let safe = text;", True, id="raw-content"),
        pytest.param(
            "safe = sanitize(text)",
            "let safe = sanitize(text);",
            False,
            id="configured-identity-sanitizer",
        ),
        pytest.param(
            "sanitize(text)\nsafe = text",
            "sanitize(text);\nlet safe = text;",
            True,
            id="discarded-result",
        ),
        pytest.param(
            'sanitize("other")\nsafe = text',
            'sanitize("other");\nlet safe = text;',
            True,
            id="unrelated-content",
        ),
        pytest.param(
            "safe = sanitize(text)\nsafe = text",
            "let safe = sanitize(text);\nsafe = text;",
            True,
            id="overwritten-result",
        ),
        pytest.param(
            "safe = sanitize(text) + text",
            "let safe = sanitize(text) + text;",
            True,
            id="raw-content-reintroduced",
        ),
        pytest.param(
            "if enabled:\n    safe = sanitize(text)\nelse:\n    safe = text",
            "let safe;\nif (enabled) { safe = sanitize(text); } else { safe = text; }",
            True,
            id="branch-bypass",
        ),
        pytest.param(
            "if enabled:\n    safe = sanitize(text)\nelse:\n    safe = sanitize(text)",
            (
                "let safe;\n"
                "if (enabled) { safe = sanitize(text); } else { safe = "
                "sanitize(text); }"
            ),
            False,
            id="both-branches-protected",
        ),
    ],
)
def test_configured_sanitizer_flow(
    tmp_path: Path, language: str, python: str, typescript: str, unsafe: bool
) -> None:
    # Configuration is the trust decision; this is deliberately an identity
    # function, not a claim that removing text guarantees injection safety.
    if language == "python":
        source = """\
def sanitize(value):
    return value
@mcp.prompt()
async def prompt(client):
    result = await client.call_tool("remote", {})
    text = result.content
"""
        source += indent(python + '\nreturn f"Tool context: {safe}"\n', "    ")
    else:
        source = """\
function sanitize(value) { return value; }
async function prompt(client) {
  const result = await client.callTool({ name: "remote" });
  const text = result.content;
"""
        source += typescript + "\nreturn openai.responses.create({ input: safe });\n}\n"
    result = _scan(tmp_path, language, "SENT-004", source)
    assert bool(result.findings) is unsafe


@pytest.mark.parametrize("algorithm", tuple(SIGNATURE_VECTORS))
@pytest.mark.parametrize(
    ("language", "mode"),
    (
        ("python", "enforced"),
        ("python", "unrelated-bytes"),
        ("typescript", "enforced"),
        ("typescript", "unrelated-bytes"),
        ("typescript", "ignored-result"),
    ),
)
def test_signature_enforcement(
    tmp_path: Path, language: str, algorithm: str, mode: str
) -> None:
    public_key, signature = SIGNATURE_VECTORS[algorithm]
    if language == "python":
        data = 'b"{}"' if mode == "unrelated-bytes" else "raw"
        arguments = {
            "ed25519": "",
            "rsa-pss-sha256": (
                ", padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32)"
                ", hashes.SHA256()"
            ),
            "ecdsa-sha256": ", ec.ECDSA(hashes.SHA256())",
        }[algorithm]
        source = f'''\
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding
PUBLIC_KEY = {public_key!r}
key = serialization.load_pem_public_key(PUBLIC_KEY.encode("ascii"))
def load_manifest():
    raw = Path("tools.json").read_bytes()
    signature = bytes.fromhex("{signature}")
    key.verify(signature, {data}{arguments})
    return json.loads(raw)
'''
        # cryptography verify raises on failure: ignoring its None return is safe.
        unsafe = mode == "unrelated-bytes"
    else:
        data = 'Buffer.from("{}")' if mode == "unrelated-bytes" else "raw"
        digest = "null" if algorithm == "ed25519" else '"sha256"'
        key = (
            "{ key: PUBLIC_KEY, padding: constants.RSA_PKCS1_PSS_PADDING, "
            "saltLength: 32 }"
            if algorithm == "rsa-pss-sha256"
            else "PUBLIC_KEY"
        )
        source = f'''\
import {{ readFileSync }} from "node:fs";
import {{ verify, constants }} from "node:crypto";
const PUBLIC_KEY = {json.dumps(public_key)};
function loadTools() {{
  const raw = readFileSync("tools.json");
  const signature = Buffer.from("{signature}", "hex");
  const valid = verify({digest}, {data}, {key}, signature);
'''
        if mode != "ignored-result":
            source += 'if (!valid) { throw new Error("invalid signature"); }\n'
        source += 'return JSON.parse(raw.toString("utf8"));\n}\n'
        unsafe = mode != "enforced"
    result = _scan(tmp_path, language, "SENT-007", source)
    assert bool(result.findings) is unsafe


@pytest.mark.parametrize("effort", (ReasoningEffort.MEDIUM, ReasoningEffort.LOW))
def test_frozen_historical_candidates_replay(effort: ReasoningEffort) -> None:
    snapshot = ROOT / "tests/evals/phase16-prechange-findings.json"
    source = snapshot.read_text(encoding="utf-8")
    assert hashlib.sha256(source.encode()).hexdigest() == (
        "4211f3b6bbd54cefd755609d4e2b6611f20af312d2f1de55decee07cccee84fc"
    )
    findings = historical_eval_findings()
    assert len(findings) == 4
    fixture = ROOT / "tests/fixtures/gpt_review_eval"
    catalog = extract_tool_catalog(fixture)
    outcome = SemanticReviewer(
        root=fixture,
        config=LlmConfig(reasoning_effort=effort, cache_enabled=False),
        max_findings=500,
        mode="replay",
        cache=ReviewCache(enabled=False),
        cassette_root=ROOT / "src/sentinel/_cassettes" / f"eval-{effort.value}",
        catalog=catalog,
    ).review(tuple(findings), allow_degraded=False)
    assert not outcome.fatal
    expected = {
        "unsafe_evaluator": FindingStatus.CONFIRMED,
        "custom_validated": FindingStatus.SUPPRESSED,
        "indirect_reader": FindingStatus.NEEDS_REVIEW,
        "unchecked_lookup": FindingStatus.CONFIRMED,
    }
    if effort is ReasoningEffort.LOW:
        # Retain the captured abstention, not the truth set's desired judgment.
        expected["unchecked_lookup"] = FindingStatus.NEEDS_REVIEW
    observed = {}
    for finding in outcome.findings:
        assert isinstance(finding.location, FileLocation)
        tool = catalog.for_location(
            finding.location.path, finding.location.range.start_line
        )
        assert tool is not None
        observed[tool.name] = finding.status
        assert finding.review.mode == "replay"
    assert observed == expected


def test_current_detector_is_independent_of_historical_review_inputs() -> None:
    fixture = ROOT / "tests/fixtures/gpt_review_eval"
    source = (fixture / "server.py").read_text(encoding="utf-8")
    assert hashlib.sha256(source.encode()).hexdigest() == (
        "39b13db32bfd1383c2f87c8a985ced5342269cc8cbb13e1a313a403b1e7689d0"
    )
    configuration = load_configuration(fixture, environ={}, static_only=True)
    result = run_static_scan(configuration, uuid4(), timestamp=NOW)
    catalog = extract_tool_catalog(fixture)
    observed = set()
    for finding in result.findings:
        assert isinstance(finding.location, FileLocation)
        tool = catalog.for_location(
            finding.location.path, finding.location.range.start_line
        )
        assert tool is not None
        observed.add((finding.rule_id, tool.name))
    assert len(result.findings) == 3
    assert observed == {
        ("SENT-001", "indirect_reader"),
        ("SENT-002", "unsafe_evaluator"),
        ("SENT-003", "unchecked_lookup"),
    }


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize(
    ("python", "typescript", "unsafe"),
    [
        (
            'if enabled:\n    raw = "1"\nreturn raw',
            'if (enabled) { raw = "1"; } return raw;',
            True,
        ),
        (
            'if enabled:\n    return "1"\nreturn "2"',
            'if (enabled) { return "1"; } return "2";',
            False,
        ),
        (
            'if enabled:\n    raw = "1"\nelse:\n    raw = "2"\nreturn raw',
            'if (enabled) { raw = "1"; } else { raw = "2"; } return raw;',
            False,
        ),
        (
            'saved = raw\nraw = "1"\nreturn saved',
            'const saved = raw; raw = "1"; return saved;',
            True,
        ),
    ],
)
def test_helper_return_branches(
    tmp_path: Path, language: str, python: str, typescript: str, unsafe: bool
) -> None:
    helper = (
        "def choose(raw):\n" + indent(python, "    ") + "\n"
        if language == "python"
        else "function choose(raw) { " + typescript + " }\n"
    )
    result = _scan(
        tmp_path,
        language,
        "SENT-002",
        _tool(language, "return eval(choose(value))", helper),
    )
    assert bool(result.findings) is unsafe


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize("selected", (0, 1))
def test_helper_parameter_dependencies(
    tmp_path: Path, language: str, selected: int
) -> None:
    helper = (
        "def choose(first, second):\n    return second\n"
        if language == "python"
        else "function choose(first, second) { return second; }\n"
    )
    arguments = 'value, "1"' if selected == 0 else '"1", value'
    result = _scan(
        tmp_path,
        language,
        "SENT-002",
        _tool(language, f"return eval(choose({arguments}))", helper),
    )
    assert bool(result.findings) is (selected == 1)


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize("kind", ("alias", "nested", "default", "spread", "method"))
def test_unsupported_helper_binding_warns(
    tmp_path: Path, language: str, kind: str
) -> None:
    helper = (
        "def execute(raw, optional=None):\n    return eval(raw)\n"
        if language == "python" and kind == "default"
        else "def execute(raw):\n    return eval(raw)\n"
        if language == "python"
        else "function execute(raw, optional = null) { return eval(raw); }\n"
        if kind == "default"
        else "function execute(raw) { return eval(raw); }\n"
    )
    bodies = {
        "alias": (
            "alias = execute\nreturn alias(value)",
            "const alias = execute; return alias(value);",
        ),
        "nested": (
            'def execute(raw):\n    return "1"\nreturn execute(value)',
            'function execute(raw) { return "1"; } return execute(value);',
        ),
        "default": ("return execute(value)", "return execute(value);"),
        "spread": ("return execute(*[value])", "return execute(...[value]);"),
        "method": ("return service.execute(value)", "return service.execute(value);"),
    }
    body = bodies[kind][0 if language == "python" else 1]
    result = _scan(tmp_path, language, "SENT-002", _tool(language, body, helper))
    assert not result.findings
    assert any(w.code == "static_flow_unresolved" for w in result.warnings)


@pytest.mark.parametrize("language", LANGUAGES)
def test_helper_sink_alias_and_call_site_dedup(tmp_path: Path, language: str) -> None:
    helper = (
        "from builtins import eval as execute\n"
        "def helper(raw):\n    execute(raw)\n    execute(raw)\n"
        if language == "python"
        else 'import { execSync as execute } from "node:child_process";\n'
        "function helper(raw) { execute(raw); execute(raw); }\n"
    )
    result = _scan(
        tmp_path,
        language,
        "SENT-002",
        _tool(language, "helper(value)\nhelper(value)", helper),
    )
    assert len(result.findings) == 2
    assert len({f.dedup_key for f in result.findings}) == 2
    for finding in result.findings:
        assert "execute" in finding.description or "eval" in finding.description
        assert "same-file helper" in finding.description


@pytest.mark.parametrize("language", LANGUAGES)
def test_helper_context_limit_is_explicit(tmp_path: Path, language: str) -> None:
    helper = (
        "def execute(raw):\n    return eval(raw)\n"
        if language == "python"
        else "function execute(raw) { return eval(raw); }\n"
    )
    helper += "\n" * 100
    helper += (
        "def forward(raw):\n    return execute(raw)\n"
        if language == "python"
        else "function forward(raw) { return execute(raw); }\n"
    )
    result = _scan(
        tmp_path,
        language,
        "SENT-002",
        _tool(language, "return forward(value)", helper),
    )
    assert len(result.findings) == 1
    assert any(w.code == "static_review_context_incomplete" for w in result.warnings)


@pytest.mark.parametrize("language", LANGUAGES)
def test_helper_suppression_uses_tool_call(tmp_path: Path, language: str) -> None:
    helper = (
        "def execute(raw):\n    return eval(raw)\n"
        if language == "python"
        else "function execute(raw) { return eval(raw); }\n"
    )
    comment = "#" if language == "python" else "//"
    result = _scan(
        tmp_path,
        language,
        "SENT-002",
        _tool(
            language,
            f"return execute(value)  {comment} "
            "sentinel: ignore[SENT-002] reason=test fixture",
            helper,
        ),
        suppressed=True,
    )
    assert len(result.findings) == 1
    assert result.findings[0].suppression is not None


@pytest.mark.parametrize("language", LANGUAGES)
def test_helper_chain_exceeds_python_recursion_limit(
    tmp_path: Path, language: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Exercise the source recognizers and traversal, independently of Semgrep.
    monkeypatch.setattr("sentinel.static.engine.run_semgrep", lambda *a, **kw: {})
    count = 1100
    helpers = []
    for index in range(count):
        call = f"helper_{index + 1}(raw)" if index + 1 < count else "eval(raw)"
        helpers.append(
            f"def helper_{index}(raw):\n    return {call}\n"
            if language == "python"
            else f"function helper_{index}(raw) {{ return {call}; }}\n"
        )
    result = _scan(
        tmp_path,
        language,
        "SENT-002",
        _tool(language, "return helper_0(value)", "".join(helpers)),
    )
    assert len(result.findings) == 1
    assert "eval at server." in result.findings[0].description
    assert any(w.code == "static_review_context_incomplete" for w in result.warnings)


@pytest.mark.parametrize("unsafe", (False, True))
def test_typescript_destructured_helper_binds_selected_field(
    tmp_path: Path, unsafe: bool
) -> None:
    argument = '{ raw: value, safe: "1" }' if unsafe else '{ raw: "1", safe: value }'
    result = _scan(
        tmp_path,
        "typescript",
        "SENT-002",
        _tool(
            "typescript",
            f"return execute({argument});",
            "function execute({ raw: selected, safe }) { return eval(selected); }\n",
        ),
    )
    assert bool(result.findings) is unsafe


def test_execution_traversal_obeys_scan_deadline() -> None:
    from sentinel.errors import InfrastructureError
    from sentinel.static.execution import Summary, emit
    from sentinel.static.model import RuleRunState

    with pytest.raises(InfrastructureError, match="120-second timeout"):
        emit(Summary(("value",)), {}, RuleRunState(), deadline=0)


def test_typescript_distinguishes_helper_calls_on_one_line(tmp_path: Path) -> None:
    result = _scan(
        tmp_path,
        "typescript",
        "SENT-002",
        _tool(
            "typescript",
            "execute(value); execute(value);",
            "function execute(raw) { return eval(raw); }\n",
        ),
    )
    assert len(result.findings) == 2
    assert len({f.dedup_key for f in result.findings}) == 2


@pytest.mark.parametrize("language", LANGUAGES)
def test_return_flow_outside_review_context_warns(
    tmp_path: Path, language: str
) -> None:
    helper = (
        "def identity(raw):\n    return raw\n"
        if language == "python"
        else "function identity(raw) { return raw; }\n"
    )
    helper += "\n" * 100
    helper += (
        "def forward(raw):\n    return identity(raw)\n"
        if language == "python"
        else "function forward(raw) { return identity(raw); }\n"
    )
    result = _scan(
        tmp_path,
        language,
        "SENT-002",
        _tool(language, "return eval(forward(value))", helper),
    )
    assert len(result.findings) == 1
    assert any(w.code == "static_review_context_incomplete" for w in result.warnings)


@pytest.mark.parametrize("language", LANGUAGES)
def test_rebound_helper_is_unresolved(tmp_path: Path, language: str) -> None:
    helper = (
        'def execute(raw):\n    return "1"\nexecute = external\n'
        if language == "python"
        else 'function execute(raw) { return "1"; }\nexecute = external;\n'
    )
    result = _scan(
        tmp_path,
        language,
        "SENT-002",
        _tool(language, "return eval(execute(value))", helper),
    )
    assert result.findings
    assert any(w.code == "static_flow_unresolved" for w in result.warnings)


@pytest.mark.parametrize("language", LANGUAGES)
def test_unknown_mutation_cannot_prove_a_constant_return(
    tmp_path: Path, language: str
) -> None:
    helper = (
        "def build(raw):\n    items = []\n    items.append(raw)\n    return items\n"
        if language == "python"
        else "function build(raw) { const items = []; "
        "items.push(raw); return items; }\n"
    )
    result = _scan(
        tmp_path,
        language,
        "SENT-002",
        _tool(language, "return eval(build(value))", helper),
    )
    assert result.findings
    assert any(w.code == "static_flow_unresolved" for w in result.warnings)


@pytest.mark.parametrize("language", LANGUAGES)
def test_default_is_not_needed_when_all_arguments_are_bound(
    tmp_path: Path, language: str
) -> None:
    helper = (
        'def execute(raw, unused="1"):\n    return eval(raw)\n'
        if language == "python"
        else 'function execute(raw, unused = "1") { return eval(raw); }\n'
    )
    result = _scan(
        tmp_path,
        language,
        "SENT-002",
        _tool(language, 'return execute(value, "2")', helper),
    )
    assert len(result.findings) == 1


def test_typescript_multiline_assignment_keeps_input_flow(tmp_path: Path) -> None:
    result = _scan(
        tmp_path,
        "typescript",
        "SENT-002",
        _tool(
            "typescript",
            "return execute(value)",
            "function execute(raw) {\nconst copied =\nraw\nreturn eval(copied)\n}\n",
        ),
    )
    assert len(result.findings) == 1


@pytest.mark.parametrize("language", LANGUAGES)
def test_direct_sink_in_unsupported_control_flow_stays_visible(
    tmp_path: Path, language: str
) -> None:
    body = (
        "try:\n    return eval(value)\nexcept Exception:\n    return None"
        if language == "python"
        else "try { return eval(value); } catch (error) { return null; }"
    )
    result = _scan(tmp_path, language, "SENT-002", _tool(language, body))
    assert len(result.findings) == 1
    assert any(w.code == "static_flow_unresolved" for w in result.warnings)


def test_typescript_direct_member_sink_keeps_historical_location(
    tmp_path: Path,
) -> None:
    result = _scan(
        tmp_path,
        "typescript",
        "SENT-002",
        _tool(
            "typescript",
            "return vm.runInContext(value);",
            'import * as vm from "node:vm";\n',
        ),
    )
    assert len(result.findings) == 1
    finding = result.findings[0]
    expected = "runInContext(value);"
    assert finding.evidence.model_dump()["snippet"] == expected
    assert isinstance(finding.location, FileLocation)
    assert finding.location.range.end_column == len(expected) + 1


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize("mutation", (False, True))
def test_validated_field_replacement_invalidates_proof(
    tmp_path: Path, language: str, mutation: bool
) -> None:
    if language == "python":
        body = (
            'if not isinstance(payload.get("record_id"), str):\n'
            "    raise ValueError()\n"
        )
        if mutation:
            body += 'payload["record_id"] = untrusted\n'
        source = "@mcp.tool()\ndef lookup(payload: dict):\n" + indent(
            body + 'return payload["record_id"]\n', "    "
        )
    else:
        body = 'if (typeof payload.record_id !== "string") { throw new Error(); }\n'
        if mutation:
            body += "payload.record_id = untrusted;\n"
        source = (
            'server.registerTool("lookup", {}, (payload) => {\n'
            + body
            + "return payload.record_id;\n});\n"
        )
    result = _scan(tmp_path, language, "SENT-003", source)
    assert bool(result.findings) is mutation


@pytest.mark.parametrize("language", LANGUAGES)
def test_input_consumed_in_condition_requires_validation(
    tmp_path: Path, language: str
) -> None:
    source = (
        "@mcp.tool()\ndef lookup(payload: dict):\n"
        '    if payload["record_id"] == "admin":\n'
        '        return "selected"\n    return "other"\n'
        if language == "python"
        else 'server.registerTool("lookup", {}, (payload) => {\n'
        'if (payload.record_id === "admin") { return "selected"; }\n'
        'return "other"; });\n'
    )
    assert _scan(tmp_path, language, "SENT-003", source).findings


@pytest.mark.parametrize("language", LANGUAGES)
def test_enforced_digest_from_validated_sidecar(tmp_path: Path, language: str) -> None:
    expected = hashlib.sha256(b"{}").hexdigest()
    sidecar = json.dumps(
        {"version": 1, "manifests": {"tools.json": {"sha256": expected}}}
    )
    source = (
        """import yaml
import hashlib
import hmac
import json
anchors = yaml.safe_load(Path("sentinel.integrity.yaml").read_text())
def load_manifest():
    raw = Path("tools.json").read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    expected = anchors["manifests"]["tools.json"]["sha256"]
    if not hmac.compare_digest(actual, expected):
        raise ValueError()
    return json.loads(raw)
"""
        if language == "python"
        else """import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
const anchors = JSON.parse(readFileSync("sentinel.integrity.yaml", "utf8"));
function loadTools() {
  const raw = readFileSync("tools.json", "utf8");
  const actual = createHash("sha256").update(raw).digest("hex");
  const expected = anchors.manifests["tools.json"].sha256;
  if (actual !== expected) { throw new Error(); }
  return JSON.parse(raw);
}
"""
    )
    result = _scan(
        tmp_path,
        language,
        "SENT-007",
        source,
        files={"sentinel.integrity.yaml": sidecar},
    )
    assert not result.findings


@pytest.mark.parametrize("language", LANGUAGES)
def test_signature_anchor_files_are_bound_to_validated_sidecar(
    tmp_path: Path, language: str
) -> None:
    key, signature = SIGNATURE_VECTORS["ed25519"]
    sidecar = json.dumps(
        {
            "version": 1,
            "manifests": {
                "tools.json": {
                    "public_key": "public.pem",
                    "signature": "signature.bin",
                    "algorithm": "ed25519",
                }
            },
        }
    )
    source = (
        """import json
from cryptography.hazmat.primitives import serialization
def load_manifest():
    raw = Path("tools.json").read_bytes()
    key = serialization.load_pem_public_key(Path("public.pem").read_bytes())
    signature = Path("signature.bin").read_bytes()
    key.verify(signature, raw)
    return json.loads(raw)
"""
        if language == "python"
        else """import { readFileSync } from "node:fs";
import { verify } from "node:crypto";
function loadTools() {
  const raw = readFileSync("tools.json");
  const key = readFileSync("public.pem");
  const signature = readFileSync("signature.bin");
  if (!verify(null, raw, key, signature)) { throw new Error(); }
  return JSON.parse(raw.toString("utf8"));
}
"""
    )
    # Signature bytes are fixed local data; scanners do not execute verification.
    result = _scan(
        tmp_path,
        language,
        "SENT-007",
        source,
        files={
            "sentinel.integrity.yaml": sidecar,
            "public.pem": key,
            "signature.bin": bytes.fromhex(signature),
        },
    )
    assert not result.findings


@pytest.mark.parametrize("language", LANGUAGES)
def test_request_value_cannot_shadow_trusted_auth_anchor(
    tmp_path: Path, language: str
) -> None:
    source = (
        """import hmac
from fastapi import FastAPI, Depends, Header, HTTPException
app = FastAPI()
EXPECTED = "expected"
def verify(authorization: str = Header(), EXPECTED: str = Header()):
    if not hmac.compare_digest(authorization, EXPECTED):
        raise HTTPException(401)
    return authorization
@app.get("/admin", dependencies=[Depends(verify)])
def admin():
    return "protected"
"""
        if language == "python"
        else """import express from "express";
import { timingSafeEqual } from "node:crypto";
const app = express();
const EXPECTED = "expected";
function verify(req, res, next) {
    const token = req.headers.authorization;
    const EXPECTED = req.headers.expected;
    if (!timingSafeEqual(Buffer.from(token), Buffer.from(EXPECTED))) {
        res.status(401).end(); return;
    }
    next();
}
app.get("/admin", verify, (req, res) => res.send("protected"));
"""
    )
    assert _scan(tmp_path, language, "SENT-006", source).findings
