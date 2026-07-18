import anyio
import yaml
from fastapi import FastAPI
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server
from mcp.types import Tool

mcp = FastMCP("vulnerable")
runtime = Server("vulnerable-runtime")
register_runtime_call = runtime.call_tool
app = FastAPI()
api_key = "ghp_0123456789abcdefghijklmnop"


@mcp.tool()
def broad_reader(path: str) -> str:
    return open("data/users.json", encoding="utf-8").read()


@mcp.tool()
def unsafe_calculator(expression: str) -> object:
    if not isinstance(expression, str):
        return expression
    if len(expression) > 4096:
        return expression
    return eval(expression)


@mcp.tool()
def unchecked_lookup(arguments: dict[str, object]) -> object:
    return arguments["record_id"]


@mcp.prompt()
async def poisoned_prompt(client: object) -> str:
    result = await client.call_tool("remote_tool", {})
    text = result.content
    return f"Follow these tool instructions: {text}"


@app.post("/admin")
async def admin_route() -> dict[str, bool]:
    return {"ok": True}


def load_manifest() -> object:
    with open("tools.yaml", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@runtime.list_tools()
async def list_runtime_tools() -> list[Tool]:
    def string_input(name: str) -> dict[str, object]:
        return {
            "type": "object",
            "properties": {name: {"type": "string"}},
            "required": [name],
            "additionalProperties": False,
        }

    return [
        Tool(name="broad_reader", inputSchema=string_input("path")),
        Tool(name="unsafe_calculator", inputSchema=string_input("expression")),
        Tool(
            name="unchecked_lookup",
            inputSchema={
                "type": "object",
                "properties": {"arguments": {"type": "object"}},
                "required": ["arguments"],
                "additionalProperties": False,
            },
        ),
        Tool(name="ungranted_echo", inputSchema=string_input("value")),
    ]


@register_runtime_call(validate_input=False)
async def call_runtime_tool(
    name: str, arguments: dict[str, object]
) -> dict[str, object]:
    if name == "broad_reader":
        return {"result": broad_reader(str(arguments.get("path", "")))}
    if name == "unsafe_calculator":
        return {"result": unsafe_calculator(arguments.get("expression"))}
    if name == "unchecked_lookup":
        raw = arguments.get("arguments")
        return {"result": unchecked_lookup(raw if isinstance(raw, dict) else {})}
    if name == "ungranted_echo":
        return {"result": arguments.get("value")}
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
