"""Source-only registration resolution must not guess across ambiguous bindings."""

import ast
from pathlib import Path

import pytest

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


def test_inherited_bound_method_and_conflicting_bases() -> None:
    index = program(
        {
            "server.py": (
                "from reader import Reader\nreader = Reader()\n"
                "server.add_tool(reader.read)\n"
            ),
            "reader.py": (
                "from base import ReaderBase\nclass Reader(ReaderBase):\n    pass\n"
            ),
            "base.py": (
                "class ReaderBase:\n    def read(self, path):\n"
                "        return open(path)\n"
            ),
        }
    )
    tools = index.tools()
    assert len(tools) == 1
    assert tools[0].handler.file.relative_path == "base.py"
    ambiguous = program(
        {
            "server.py": (
                "class First:\n    def read(self, path):\n        return open(path)\n"
                "class Second:\n    def read(self, path):\n        return 'safe'\n"
                "class Reader(First, Second):\n    pass\n"
                "reader = Reader()\nserver.add_tool(reader.read)\n"
            )
        }
    )
    assert not ambiguous.tools()
    assert ambiguous.warnings


@pytest.mark.parametrize(
    "replacement", ["read = replacement", "read: object = replacement"]
)
def test_replaced_inherited_method_remains_unresolved(replacement: str) -> None:
    index = program(
        {
            "server.py": (
                "class Base:\n    def read(self, path):\n        return open(path)\n"
                "class Reader(Base):\n    " + replacement + "\n"
                "reader = Reader()\nserver.add_tool(reader.read)\n"
            )
        }
    )
    assert not index.tools()
    assert index.warnings


@pytest.mark.parametrize("constructor", ["__new__", "__init__"])
def test_custom_construction_does_not_establish_registered_method(
    constructor: str,
) -> None:
    index = program(
        {
            "server.py": (
                f"class Reader:\n    def {constructor}(self):\n"
                "        return replacement()\n"
                "    def read(self, path):\n        return path\n"
                "reader = Reader()\nserver.add_tool(reader.read)\n"
            )
        }
    )
    assert not index.tools()
    assert index.warnings


def test_nested_registered_handler_resolves_lexical_helper() -> None:
    index = program(
        {
            "server.py": "def factory():\n"
            "    def helper(value): return open(value)\n"
            "    @server.tool()\n"
            "    def read(path): return helper(path)\n"
            "    return read\n"
        }
    )
    tool = index.tools()[0]
    helper = index.resolve_in(tool.handler, "helper")
    assert helper is not None and helper.name == "factory.helper"
    assert isinstance(helper.node, ast.FunctionDef)


@pytest.mark.parametrize(
    "replacement",
    [
        "helper = replacement",
        "def helper(value): return value",
    ],
)
def test_ambiguous_nested_helper_is_unresolved(replacement: str) -> None:
    index = program(
        {
            "server.py": "def helper(value): return value\n"
            "def factory():\n"
            "    def helper(value): return open(value)\n"
            "    " + replacement + "\n"
            "    @server.tool()\n"
            "    def read(path): return helper(path)\n"
        }
    )
    assert index.resolve_in(index.tools()[0].handler, "helper") is None


def test_nested_registration_and_returned_handler_alias() -> None:
    index = program(
        {
            "server.py": "def factory():\n"
            "    def read(path): return open(path)\n"
            "    alias = read\n"
            '    server.add_tool(alias, name="nested")\n'
            "    return alias\n"
            "handler = factory()\n"
            'server.add_tool(handler, name="returned")\n'
        }
    )
    tools = index.tools()
    assert {t.name for t in tools} == {"nested", "returned"}
    assert all(t.handler.name == "factory.read" for t in tools)


@pytest.mark.parametrize(
    "body",
    [
        "return handler",
        "if choice: return replacement\n    return read",
        "return callback",
    ],
)
def test_factory_ambiguous_or_recursive_returns_stay_unresolved(body: str) -> None:
    index = program(
        {
            "server.py": "def factory(callback=None, choice=False):\n"
            "    def read(path): return open(path)\n"
            "    " + body + "\n"
            "handler = factory()\nserver.add_tool(handler)\n"
        }
    )
    assert not index.tools()
    assert index.warnings


@pytest.mark.parametrize(
    "constructor",
    [
        "@dataclass\nclass Definition:\n    fn: object\n",
        "@dataclass\nclass Base:\n    fn: object\n"
        "@dataclass\nclass Definition(Base):\n    pass\n",
    ],
)
def test_factory_definitions_follow_field_to_actual_registration(
    constructor: str,
) -> None:
    index = program(
        {
            "definitions.py": "from dataclasses import dataclass\n" + constructor,
            "server.py": "from definitions import Definition\n"
            "def register(definitions):\n"
            "    for definition in definitions:\n"
            "        server.add_tool(fn=definition.fn)\n"
            "def factory():\n"
            "    def read(path): return open(path)\n"
            "    return [Definition(fn=read)]\n"
            "register(factory())\n",
        }
    )
    tools = index.tools()
    assert len(tools) == 1
    assert tools[0].handler.name == "factory.read"
    assert isinstance(tools[0].registration.node, ast.Call)
    assert tools[0].registration.node.lineno == 4


@pytest.mark.parametrize(
    "constructor",
    [
        "class Definition:\n    fn: object\n",
        "@dataclass(init=False)\nclass Definition:\n    fn: object\n",
        "@dataclass\nclass Definition:\n    fn: object\n"
        "    def __post_init__(self): self.fn = replacement\n",
    ],
)
def test_definition_annotation_or_custom_construction_is_not_binding(
    constructor: str,
) -> None:
    index = program(
        {
            "server.py": "from dataclasses import dataclass\n"
            + constructor
            + "def register(definitions):\n"
            "    for definition in definitions:\n"
            "        server.add_tool(fn=definition.fn)\n"
            "def read(path): return open(path)\n"
            "register([Definition(fn=read)])\n"
        }
    )
    assert not index.tools()
    assert index.warnings


def test_registration_resolution_obeys_shared_static_deadline() -> None:
    from sentinel.errors import InfrastructureError

    index = program({"server.py": "def read(p): return p\nserver.add_tool(read)\n"})
    index.deadline = 0
    with pytest.raises(InfrastructureError, match="120-second"):
        index.tools()


def test_warm_resolution_retains_cycle_budgets_and_deadline() -> None:
    from sentinel.errors import InfrastructureError

    index = program({"server.py": "def read(p): return p\n"})
    file = index.files[0]
    symbol = index.resolve(file, "read")
    assert symbol is not None
    assert index.resolve_in(symbol, "read") == symbol
    assert index.resolve(file, "read", frozenset({("server.py", "read")})) is None
    assert (
        index.resolve_in(symbol, "read", frozenset({(id(symbol.node), "read")})) is None
    )
    index.deadline = 0
    with pytest.raises(InfrastructureError, match="120-second"):
        index.resolve(file, "read")
    with pytest.raises(InfrastructureError, match="120-second"):
        index.resolve_in(symbol, "read")


def test_partially_resolved_factory_keeps_unknown_registration_visible() -> None:
    index = program(
        {
            "server.py": "from dataclasses import dataclass\n"
            "@dataclass\nclass Definition:\n    fn: object\n"
            "def register(definitions):\n"
            "    for definition in definitions:\n"
            "        server.add_tool(fn=definition.fn)\n"
            "def factory():\n"
            "    def read(path): return open(path)\n"
            "    return [Definition(fn=read), dynamic_definition()]\n"
            "register(factory())\n"
        }
    )
    assert len(index.tools()) == 1
    assert any(w.code == "static_handler_unresolved" for w in index.warnings)


def test_discovery_reuses_snapshot_and_retains_unknown_bindings() -> None:
    from unittest.mock import patch

    from sentinel.errors import InfrastructureError

    index = program(
        {
            "server.py": "def read(path): return open(path)\n"
            "server.add_tool(read)\nserver.add_tool(missing)\n"
        }
    )
    bindings = index.tools()
    warnings = tuple(index.warnings)
    assert bindings and warnings
    with patch(
        "sentinel.static.discovery.discover_tool_regions",
        side_effect=AssertionError("repeated source discovery"),
    ):
        assert index.tools() == bindings
        assert tuple(index.warnings) == warnings
    index.deadline = 0
    with pytest.raises(InfrastructureError, match="120-second"):
        index.tools()


@pytest.mark.parametrize(
    "field",
    [
        "reader: ClassVar[object]",
        "reader: InitVar[object]",
        "reader: object = []",
        "reader: object\n    @property\n    def reader(self): return replacement",
    ],
)
def test_unsupported_dataclass_layout_is_not_callback_binding(field: str) -> None:
    from sentinel.static.discovery import Symbol
    from sentinel.static.registration_flow import RegistrationFlow

    index = program(
        {
            "server.py": "from dataclasses import dataclass, InitVar\n"
            "from typing import ClassVar\n"
            "@dataclass\nclass Spec:\n    " + field + "\n"
        }
    )
    node = index.files[0].tree.body[-1]
    assert RegistrationFlow(index).fields(Symbol(index.files[0], "Spec", node)) is None
