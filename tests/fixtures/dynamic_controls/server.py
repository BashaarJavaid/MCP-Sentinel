"""Independent deterministic controls. Run only in Sentinel's Docker sandbox."""

import os
from pathlib import Path

import anyio
from jsonschema import Draft202012Validator
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

runtime = Server("phase17-independent-control")
CASE = os.environ["CONTROL_CASE"]
CANARY = Path("/sentinel-scratch/sent-010-canary")
FIELD = {"type": "string"}
if CASE.startswith("object_"):
    FIELD = {"type": "object"}
if CASE.startswith("size_"):
    FIELD = {"type": "string", "maxLength": 4096}
if CASE == "array_limit":
    FIELD = {"type": "array", "maxItems": 3}
if CASE == "object_limit":
    FIELD = {"type": "object", "maxProperties": 3}
SCHEMA = {
    "type": "object",
    "properties": {"value": FIELD},
    "required": ["value"],
    "additionalProperties": False,
}
if CASE == "unsupported_schema":
    SCHEMA["properties"]["value"] = {"$ref": "https://example.invalid/schema"}
if CASE == "preexisting_canary":
    CANARY.touch()
if CASE == "startup_crash":
    os._exit(17)


@runtime.list_tools()
async def list_tools():
    if CASE == "multi_tool":
        return [
            Tool(name="process", inputSchema=SCHEMA),
            Tool(
                name="unprobed",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "nested": {
                            "type": "object",
                            "properties": {
                                "field": {"type": "string"},
                            },
                            "additionalProperties": False,
                        },
                    },
                    "additionalProperties": False,
                },
            ),
        ]
    names = ["process", "denied"] if CASE.startswith("grant_") else ["process"]
    return [Tool(name=name, inputSchema=SCHEMA) for name in names]


@runtime.call_tool(validate_input=False)
async def call_tool(name, arguments):
    if name == "denied" and CASE == "grant_safe":
        raise ValueError("tool name is not granted")
    if name not in {"process", "denied"} and CASE != "unknown_success":
        raise ValueError("unknown tool")
    if CASE in {"object_safe", "size_safe"}:
        Draft202012Validator(SCHEMA).validate(arguments)
    value = arguments.get("value")
    large = isinstance(value, str) and len(value) > 4096
    injection = isinstance(value, str) and "sent-010-canary" in value
    if CASE == "failing_baseline" and not large:
        raise ValueError("legitimate workflow fails")
    if CASE == "missing_prerequisite":
        raise ValueError("required test record is missing")
    if CASE == "slow_baseline" and not large:
        await anyio.sleep(30)
    if CASE == "timeout_attack" and large:
        await anyio.sleep(30)
    if CASE == "crash" and large:
        os._exit(17)
    if CASE == "oom" and large:
        allocation = bytearray(2 * 1024**3)
        allocation[::4096] = b"x" * (len(allocation) // 4096)
    if CASE == "baseline_canary" and not injection:
        CANARY.touch()
    if CASE in {"canary", "canary_error"} and injection:
        CANARY.touch()
        if CASE == "canary_error":
            raise ValueError("error after the observed side effect")
    return {"processed": True}


async def main():
    if CASE == "startup_slow":
        await anyio.sleep(30)
    async with stdio_server() as (read, write):
        await runtime.run(read, write, runtime.create_initialization_options())


if __name__ == "__main__":
    anyio.run(main)
