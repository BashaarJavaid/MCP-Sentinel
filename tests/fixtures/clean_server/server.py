import ast
import hashlib
import hmac
import os

import yaml
from fastapi import Depends, FastAPI, HTTPException
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("clean")
app = FastAPI()
api_key = os.environ.get("SERVICE_API_KEY")


class ValidatedArguments(BaseModel):
    record_id: str


def sanitize_tool_text(value: object) -> str:
    return str(value).replace("ignore previous instructions", "")


@mcp.tool()
def justified_reader(path: str) -> str:
    return open("data/users.json", encoding="utf-8").read()


@mcp.tool()
def safe_calculator(expression: str) -> object:
    return ast.literal_eval(expression)


@mcp.tool()
def validated_lookup(arguments: dict[str, object]) -> object:
    ValidatedArguments.model_validate(arguments)
    return arguments["record_id"]


@mcp.prompt()
async def safe_prompt(client: object) -> str:
    result = await client.call_tool("remote_tool", {})
    text = result.content
    safe_text = sanitize_tool_text(text)
    return f"Tool context: {safe_text}"


def verify_token(authorization: str) -> str:
    if not hmac.compare_digest(authorization, "expected"):
        raise HTTPException(status_code=401)
    return authorization


@app.post("/admin", dependencies=[Depends(verify_token)])
async def admin_route() -> dict[str, bool]:
    return {"ok": True}


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}


def load_manifest() -> object:
    with open("tools.yaml", "rb") as handle:
        raw = handle.read()
    actual = hashlib.sha256(raw).hexdigest()
    if not hmac.compare_digest(actual, "0" * 64):
        raise ValueError("manifest digest mismatch")
    return yaml.safe_load(raw)
