"""Source-only registration resolution must not guess across ambiguous bindings."""

import ast
from pathlib import Path

from sentinel.static.discovery import PythonProgram
from sentinel.static.model import ParsedPythonFile


def program(sources: dict[str, str]) -> PythonProgram:
    return PythonProgram(
        tuple(
            ParsedPythonFile(Path(name), name, source, ast.parse(source))
            for name, source in sources.items()
        )
    )


def test_imported_alias_reexport_and_bound_method() -> None:
    index = program(
        {
            "src/app/server.py": (
                "from .api import handler as imported\n"
                "alias = imported\nserver.add_tool(alias, name='read')\n"
                "from .helpers import Reader\nreader = Reader()\n"
                "server.add_tool(reader.read, name='method')\n"
            ),
            "src/app/api.py": "from .helpers import read as handler\n",
            "src/app/helpers.py": (
                "def read(path):\n    return open(path).read()\n"
                "class Reader:\n    def read(self, path):\n        return open(path)\n"
            ),
        }
    )
    tools = index.tools()
    assert [(t.name, t.handler.file.relative_path) for t in tools] == [
        ("read", "src/app/helpers.py"),
        ("method", "src/app/helpers.py"),
    ]
    assert tools[1].handler.name == "Reader.read"
    assert not index.warnings


def test_rebinding_ambiguity_and_import_escape_are_unresolved() -> None:
    index = program(
        {
            "server.py": (
                "from helpers import read\nread = replacement\n"
                "server.add_tool(read)\n"
                "from ...outside import handler\nserver.add_tool(handler)\n"
                "from duplicate import run\nserver.add_tool(run)\n"
            ),
            "helpers.py": "def read(path):\n    return open(path)\n",
            "a/duplicate.py": "def run(x):\n    return x\n",
            "b/duplicate.py": "def run(x):\n    return x\n",
        }
    )
    assert index.tools() == ()
    assert len(index.warnings) == 3


def test_nested_dispatch_literals_and_enum_members() -> None:
    index = program(
        {
            "server.py": (
                "class Names(str, Enum):\n    READ = 'read'\n"
                "async def serve():\n"
                "    @server.call_tool()\n"
                "    async def dispatch(tool_name, arguments):\n"
                "        match tool_name:\n"
                "            case Names.READ:\n"
                "                return open(arguments['path'])\n"
                "            case 'write':\n                return arguments\n"
            )
        }
    )
    assert [tool.name for tool in index.tools()] == ["read", "write"]


def test_registration_in_comments_or_shadowed_handler_is_not_resolved() -> None:
    index = program(
        {
            "server.py": (
                "def handler(x):\n    return x\n"
                "def configure(handler):\n    server.add_tool(handler)\n"
                "# server.add_tool(handler)\n"
            )
        }
    )
    assert not index.tools()
    assert len(index.warnings) == 1
