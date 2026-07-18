import ast
import hashlib
import hmac
import os

import anyio
import yaml
from fastapi import Depends, FastAPI, HTTPException
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server
from mcp.types import Tool
from pydantic import BaseModel

mcp = FastMCP("clean")
runtime = Server("clean-runtime")
register_runtime_call = runtime.call_tool
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
    if len(expression) > 4096:
        raise ValueError("expression exceeds the 4096-character limit")
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


@runtime.list_tools()
async def list_runtime_tools() -> list[Tool]:
    def string_input(name: str) -> dict[str, object]:
        return {
            "type": "object",
            "properties": {name: {"type": "string", "maxLength": 4096}},
            "required": [name],
            "additionalProperties": False,
        }

    return [
        Tool(name="justified_reader", inputSchema=string_input("path")),
        Tool(name="safe_calculator", inputSchema=string_input("expression")),
        Tool(
            name="validated_lookup",
            inputSchema={
                "type": "object",
                "properties": {"arguments": {"type": "object"}},
                "required": ["arguments"],
                "additionalProperties": False,
            },
        ),
    ]


@register_runtime_call(validate_input=True)
async def call_runtime_tool(
    name: str, arguments: dict[str, object]
) -> dict[str, object]:
    if name == "justified_reader":
        return {"result": justified_reader(str(arguments["path"]))}
    if name == "safe_calculator":
        return {"result": safe_calculator(str(arguments["expression"]))}
    if name == "validated_lookup":
        raw = arguments["arguments"]
        if not isinstance(raw, dict):
            raise ValueError("arguments must be an object")
        return {"result": validated_lookup(raw)}
    raise ValueError("unknown tool")


async def run_stdio() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await runtime.run(
            read_stream,
            write_stream,
            runtime.create_initialization_options(),
        )


if __name__ == "__main__":
    anyio.run(run_stdio)
