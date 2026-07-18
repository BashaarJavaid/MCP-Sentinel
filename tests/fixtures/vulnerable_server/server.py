import yaml
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vulnerable")
app = FastAPI()
api_key = "ghp_0123456789abcdefghijklmnop"


@mcp.tool()
def broad_reader(path: str) -> str:
    return open("data/users.json", encoding="utf-8").read()


@mcp.tool()
def unsafe_calculator(expression: str) -> object:
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
