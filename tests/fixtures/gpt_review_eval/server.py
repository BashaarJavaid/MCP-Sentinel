from mcp.server.fastmcp import FastMCP
from storage import read_one_file

mcp = FastMCP("gpt-review-eval")




# Keep established finding locations stable across the evaluation fixture.
@mcp.tool()
def indirect_reader(path: str) -> str:
    return read_one_file(path)


@mcp.tool()
def unsafe_evaluator(expression: str) -> object:
    return eval(expression)


def validate_record(arguments: dict[str, object]) -> None:
    if not isinstance(arguments.get("record_id"), str):
        raise ValueError("record_id must be a string")


@mcp.tool()
def custom_validated(arguments: dict[str, object]) -> object:
    validate_record(arguments)
    return arguments["record_id"]


@mcp.tool()
def unchecked_lookup(arguments: dict[str, object]) -> object:
    return arguments["record_id"]


if __name__ == "__main__":
    mcp.run()
