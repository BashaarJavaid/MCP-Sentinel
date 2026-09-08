"""Member writes and helper mutations preserve the actual caller value."""

import time

import pytest

from sentinel.static.model import RuleRunState
from sentinel.static.path_flow import PathFlow
from sentinel.static.rules.sent012 import analyze
from tests.test_python_discovery import program


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (
            'state = {"path": "/fixed"}\n'
            '    state.update({"path": value})\n'
            '    return open(state["path"])',
            1,
        ),
        (
            'state = {"path": value}\n'
            '    state.update(path="/fixed")\n'
            '    return open(state["path"])',
            0,
        ),
        (
            'state = {"path": value}\n'
            "    copied = state.copy()\n"
            '    state["path"] = "/fixed"\n'
            '    return open(copied["path"])',
            1,
        ),
        (
            'state = {"path": value}\n'
            "    copied = dict(state)\n"
            '    copied["path"] = "/fixed"\n'
            '    return open(state["path"])',
            1,
        ),
        (
            'state = {"path": "/fixed"}\n'
            "    key = value\n"
            "    state[key] = value\n"
            '    return open(state["path"])',
            1,
        ),
        ('state = {**value}\n    return open(state["path"])', 1),
        ('state = {"path": "/fixed", **value}\n    return open(state["path"])', 1),
        ('state = {**value, "path": "/fixed"}\n    return open(state["path"])', 0),
        ('state = GLOBAL_STATE\n    return open(state["path"])', 0),
        ('state = {}\n    state["path"] = value\n    return open(state["path"])', 1),
        (
            'state = {"path": "/fixed", "other": value}\n'
            '    return open(state["path"])',
            0,
        ),
        (
            'state = {"path": "/fixed"}\n'
            "    alias = state\n"
            '    alias["path"] = value\n'
            '    return open(state["path"])',
            1,
        ),
        (
            'state = {"path": value}\n'
            "    alias = state\n"
            '    alias["path"] = "/fixed"\n'
            '    return open(state["path"])',
            0,
        ),
        (
            'state = {"path": "/fixed"}\n'
            '    if value: state["path"] = value\n'
            '    return open(state["path"])',
            1,
        ),
        (
            'state = {"nested": {"path": "/fixed"}}\n'
            '    state["nested"]["path"] = value\n'
            '    return open(state["nested"]["path"])',
            1,
        ),
        (
            'state = {"path": "/fixed"}\n'
            "    populate(state, value)\n"
            '    return open(state["path"])',
            1,
        ),
        (
            'state = {"path": "/fixed"}\n'
            "    replace_local(state, value)\n"
            '    return open(state["path"])',
            0,
        ),
        (
            "left = make_state()\n"
            "    right = make_state()\n"
            '    left["path"] = value\n'
            '    return open(right["path"])',
            0,
        ),
    ],
)
def test_member_flow(body: str, expected: int) -> None:
    index = program(
        {
            "server.py": (
                "from mcp.server.fastmcp import FastMCP\n"
                "def populate(state, value): state['path'] = value\n"
                "def make_state(): return {'path': '/fixed'}\n"
                "GLOBAL_STATE = {'path': '/fixed'}\n"
                "def replace_local(state, value): state = {'path': value}\n"
                "mcp=FastMCP('test')\n@mcp.tool()\ndef read(value):\n    " + body + "\n"
            )
        }
    )
    state = RuleRunState()
    analyze(
        index,
        state,
        time.monotonic() + 10,
        flow=PathFlow(index, state, time.monotonic() + 10),
    )
    assert len(state.matches) == expected


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("spec = make_spec(value)\n    return open(spec.path)", 1),
        ("spec = make_spec(value)\n    return spec.reader(spec.path)", 1),
        (
            'spec = make_spec(value)\n    spec.path = "/fixed"\n'
            "    return open(spec.path)",
            0,
        ),
        ('spec = make_spec(value)\n    return open(getattr(spec, "path"))', 1),
    ],
)
def test_factory_record_fields_and_callbacks(body: str, expected: int) -> None:
    index = program(
        {
            "server.py": "from dataclasses import dataclass\n"
            "from mcp.server.fastmcp import FastMCP\n"
            "@dataclass\nclass Spec:\n    path: str\n    reader: object\n"
            "def read_path(path): return open(path)\n"
            "def make_spec(path): return Spec(path=path, reader=read_path)\n"
            'mcp=FastMCP("test")\n@mcp.tool()\ndef read(value):\n    ' + body + "\n"
        }
    )
    state = RuleRunState()
    analyze(index, state, time.monotonic() + 10)
    assert len(state.matches) == expected


@pytest.mark.parametrize("custom", ["", "__init__ = replacement\n"])
def test_dataclass_custom_constructor_is_not_field_binding(custom: str) -> None:
    index = program(
        {
            "server.py": "from dataclasses import dataclass\n"
            "from mcp.server.fastmcp import FastMCP\n"
            "@dataclass\nclass Spec:\n    reader: object\n    " + custom + "\n"
            "def read_path(path): return open(path)\n"
            'mcp=FastMCP("test")\n@mcp.tool()\ndef read(value):\n'
            "    spec=Spec(reader=read_path)\n    return spec.reader(value)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state, time.monotonic() + 10)
    assert len(state.matches) == (not custom)
    if custom:
        assert state.warnings


@pytest.mark.parametrize(
    "invocation", ["return spec.read()", "reader=spec.read\n    return reader()"]
)
def test_record_bound_method_keeps_receiver(invocation: str) -> None:
    index = program(
        {
            "server.py": "from dataclasses import dataclass\n"
            "from mcp.server.fastmcp import FastMCP\n"
            "@dataclass\nclass Spec:\n    path: str\n"
            "    def read(self): return open(self.path)\n"
            'mcp=FastMCP("test")\n@mcp.tool()\ndef read(value):\n'
            "    spec=Spec(path=value)\n    " + invocation + "\n"
        }
    )
    state = RuleRunState()
    analyze(index, state, time.monotonic() + 10)
    assert len(state.matches) == 1


@pytest.mark.parametrize(
    "callback",
    [
        "lambda path: open(path)",
        "lambda path: open(value)",
        'lambda path: open("/fixed")',
    ],
)
def test_factory_lambda_callback(callback: str) -> None:
    index = program(
        {
            "server.py": "from dataclasses import dataclass\n"
            "from mcp.server.fastmcp import FastMCP\n"
            "@dataclass\nclass Spec:\n    reader: object\n"
            "def make_spec(value): return Spec(reader=" + callback + ")\n"
            'mcp=FastMCP("test")\n@mcp.tool()\ndef read(value):\n'
            "    spec=make_spec(value)\n    return spec.reader(value)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state, time.monotonic() + 10)
    assert len(state.matches) == ('"/fixed"' not in callback)
