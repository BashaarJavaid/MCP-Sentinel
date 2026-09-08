"""Member writes and helper mutations preserve the actual caller value."""

import time

import pytest

from sentinel.static.model import RuleRunState
from sentinel.static.path_flow import PathFlow
from sentinel.static.rules.sent012 import analyze
from tests.test_python_discovery import program


@pytest.mark.parametrize("inspect_type", [False, True])
@pytest.mark.parametrize(
    ("replacement", "read", "expected"),
    [
        ("path=value", "copy.path", 1),
        ("path=value", "original.path", 0),
        ("other=value", "copy.path", 0),
        ("**{'other': value}", "copy.path", 0),
    ],
)
def test_dataclass_replacement_keeps_exact_field_and_allocation(
    replacement: str, read: str, expected: int, inspect_type: bool
) -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "from dataclasses import dataclass, replace\n"
            "@dataclass\nclass State:\n"
            "    path: str = '/fixed'\n    other: str = ''\n"
            "mcp = FastMCP('test')\n@mcp.tool()\ndef read(value: str):\n"
            "    original = State()\n"
            + ("    if isinstance(original, State): pass\n" if inspect_type else "")
            + f"    copy = replace(original, {replacement})\n"
            f"    return open({read})\n"
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == expected


def test_dataclass_replacement_is_a_shallow_copy() -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "from dataclasses import dataclass, replace\n"
            "@dataclass\nclass State:\n    paths: dict\n"
            "mcp = FastMCP('test')\n@mcp.tool()\ndef read(value: str):\n"
            "    original = State({'path': '/fixed'})\n"
            "    copied = replace(original)\n"
            "    copied.paths['path'] = value\n"
            "    return open(original.paths['path'])\n"
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == 1


@pytest.mark.parametrize("condition", ["mode == 'user'", "mode in ['user', 'local']"])
def test_literal_selector_keeps_unreachable_record_writes_out(condition: str) -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "def select(mode, value):\n"
            "    state = {'path': '/fixed'}\n"
            f"    if {condition}:\n        state['other'] = value\n"
            "    else:\n        state['path'] = value\n"
            "    return state\n"
            "mcp = FastMCP('test')\n@mcp.tool()\ndef read(value: str):\n"
            "    return open(select('user', value)['path'])\n"
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert not state.matches


@pytest.mark.parametrize("custom", ["post_init", "replacement"])
def test_dataclass_replacement_does_not_guess_custom_behavior(custom: str) -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "from dataclasses import dataclass, replace\n"
            "@dataclass\nclass State:\n"
            "    path: str = '/fixed'\n    other: str = ''\n"
            + (
                "    def __post_init__(self): self.path = self.other\n"
                if custom == "post_init"
                else "replace = unknown_replacement\n"
            )
            + "mcp = FastMCP('test')\n@mcp.tool()\ndef read(value: str):\n"
            "    original = State()\n"
            "    copied = replace(original, other=value)\n"
            "    return open(copied.path)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == 1


@pytest.mark.parametrize("custom_type", [False, True])
def test_source_instance_check_distinguishes_classes_without_guessing_metaclasses(
    custom_type: bool,
) -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "from dataclasses import dataclass\n"
            "@dataclass\nclass State:\n    path: str\n    other: str\n"
            + (
                "class Meta(type):\n"
                "    def __instancecheck__(cls, obj):\n"
                "        obj.path = obj.other\n        return False\n"
                "class Other(metaclass=Meta): pass\n"
                if custom_type
                else "@dataclass\nclass Other:\n    path: str\n"
            )
            + "mcp = FastMCP('test')\n@mcp.tool()\ndef read(value: str):\n"
            "    state = State('/fixed', value)\n"
            "    if isinstance(state, Other): state.path = value\n"
            "    return open(state.path)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == int(custom_type)


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


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ('key="path"\n    return open(state.get(key))', 0),
        ('key="other"\n    return open(state.get(key))', 1),
        ('key="path"\n    return open(state[key])', 0),
        ('key="path"\n    state[key]=value\n    return open(state["path"])', 1),
        ('spec=make_spec("path")\n    return open(state.get(spec.path))', 0),
        ('spec=make_spec("other")\n    return open(state.get(spec.path))', 1),
    ],
)
def test_bound_member_names(body: str, expected: int) -> None:
    index = program(
        {
            "server.py": "from dataclasses import dataclass\n"
            "from mcp.server.fastmcp import FastMCP\n"
            "@dataclass\nclass Spec:\n    path: str\n"
            "def make_spec(path): return Spec(path)\n"
            'mcp=FastMCP("test")\n@mcp.tool()\ndef read(value):\n'
            '    state={"path":"/fixed", "other":value}\n    ' + body + "\n"
        }
    )
    state = RuleRunState()
    analyze(index, state, time.monotonic() + 10)
    assert len(state.matches) == expected


@pytest.mark.parametrize("construction", ["Spec(path=value)", 'Spec(**{"path":value})'])
def test_record_defaults_and_explicit_keyword_expansion(construction: str) -> None:
    index = program(
        {
            "server.py": "from dataclasses import dataclass\n"
            "from mcp.server.fastmcp import FastMCP\n"
            "def read_path(path): return open(path)\n"
            "@dataclass\nclass Spec:\n    path: str\n    reader: object = read_path\n"
            'mcp=FastMCP("test")\n@mcp.tool()\ndef read(value):\n'
            "    spec=" + construction + "\n    return spec.reader(spec.path)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state, time.monotonic() + 10)
    assert len(state.matches) == 1


@pytest.mark.parametrize(
    ("initializer", "expected"),
    [
        ("self.path = path", 1),
        (
            "self.path = Path(path).resolve()\n"
            '        self.path.relative_to(Path("/allowed").resolve())',
            0,
        ),
        (
            "self.path = Path(path).resolve()\n"
            '        self.path.relative_to(Path("/allowed").resolve())\n'
            "        self.path = other",
            1,
        ),
        ("self.path = path\n        self.read = replacement", 0),
        ('self.path = path\n        self.__dict__["read"] = replacement', 0),
        (
            'self.path = path\n        getattr(self, "__dict__")["read"] = replacement',
            0,
        ),
        ('self.path = path\n        vars(self)["read"] = replacement', 0),
        ('self.path = path\n        setattr(self, "read", replacement)', 0),
    ],
)
def test_source_constructor_state(initializer: str, expected: int) -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "from pathlib import Path\n"
            "class Reader:\n    def __init__(self, path, other):\n        "
            + initializer
            + "\n"
            "    def read(self): return open(self.path)\n"
            'mcp=FastMCP("test")\n@mcp.tool()\ndef read(path,other):\n'
            "    return Reader(path,other).read()\n"
        }
    )
    state = RuleRunState()
    analyze(index, state, time.monotonic() + 10)
    assert len(state.matches) == expected
    if "replacement" in initializer:
        assert state.warnings


@pytest.mark.parametrize("protocol", [False, True])
@pytest.mark.parametrize(
    "argument", ["path=value", "value", "path=value if unknown else None"]
)
def test_source_mixin_initializer_uses_python_method_order(
    protocol: bool, argument: str
) -> None:
    index = program(
        {
            "app.py": 'from mcp.server.fastmcp import FastMCP\nmcp=FastMCP("test")\n'
            "class Client:\n"
            "    def __init__(self, path): self.path=path\n"
            "    def read(self): return open(self.path)\n"
            + (
                "from typing import Protocol, runtime_checkable\n"
                "@runtime_checkable\nclass Shape(Protocol): pass\n"
                "class First(Client, Shape):\n"
                if protocol
                else "class First(Client):\n"
            )
            + "    def __init__(self, *args, **kwargs):\n"
            "        super().__init__(*args, **kwargs)\n"
            "        hasattr(self, 'path')\n"
            "class Second(Client):\n"
            "    def __init__(self, *args, **kwargs):\n"
            "        super().__init__(*args, **kwargs)\n"
            "class Reader(First, Second): pass\n"
            "@mcp.tool()\ndef read(value):\n"
            f"    reader=Reader({argument})\n    return reader.read()\n"
        }
    )
    state = RuleRunState()
    analyze(index, state, time.monotonic() + 10)
    assert len(state.matches) == 1


@pytest.mark.parametrize("fallback", ['Reader("fixed")', "None"])
def test_constructed_record_truth_keeps_actual_member(fallback: str) -> None:
    index = program(
        {
            "app.py": "from mcp.server.fastmcp import FastMCP\n"
            "from dataclasses import dataclass\n"
            'mcp=FastMCP("test")\n@dataclass\nclass Reader:\n'
            '    path: str\n    ignored: str = ""\n'
            "@mcp.tool()\ndef read(value):\n"
            '    reader=Reader(path="fixed", ignored=value)\n'
            f"    selected=reader or {fallback}\n    return open(selected.path)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state, time.monotonic() + 10)
    assert not state.matches


def test_replaced_truth_method_cannot_protect_an_alternative_record() -> None:
    index = program(
        {
            "app.py": 'from mcp.server.fastmcp import FastMCP\nmcp=FastMCP("test")\n'
            "class Reader:\n    __bool__ = unknown\n"
            "    def __init__(self, path): self.path=path\n"
            "@mcp.tool()\ndef read(value):\n"
            '    selected=Reader("fixed") or Reader(value)\n'
            "    return open(selected.path)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state, time.monotonic() + 10)
    assert len(state.matches) == 1


@pytest.mark.parametrize(
    "method, invocation",
    [
        ("def read(receiver): return open(receiver.path)", "Reader(value).read()"),
        (
            "@staticmethod\n    def read(self): return open(self)",
            'Reader("fixed").read(value)',
        ),
    ],
)
def test_bound_methods_follow_descriptor_binding(method: str, invocation: str) -> None:
    index = program(
        {
            "app.py": 'from mcp.server.fastmcp import FastMCP\nmcp=FastMCP("test")\n'
            "class Reader:\n    def __init__(self, path): self.path=path\n    "
            + method
            + "\n@mcp.tool()\ndef read(value):\n"
            + f"    return {invocation}\n"
        }
    )
    state = RuleRunState()
    analyze(index, state, time.monotonic() + 10)
    assert len(state.matches) == 1


@pytest.mark.parametrize("change", ["protocol_alias", "init_subclass", "unknown_base"])
def test_mixin_construction_keeps_unknown_hooks_unresolved(change: str) -> None:
    source = (
        "from mcp.server.fastmcp import FastMCP\nfrom typing import Protocol\n"
        'mcp=FastMCP("test")\n'
        + ("Protocol=unknown\n" if change == "protocol_alias" else "")
        + "class Shape(Protocol): pass\n"
        + "class Client:\n    def __init__(self, path): self.path=path\n"
        + (
            "    def __init_subclass__(cls): cls.read=unknown\n"
            if change == "init_subclass"
            else ""
        )
        + "    def read(self): return open(self.path)\n"
        + (
            "class Reader(Client, Unknown): pass\n"
            if change == "unknown_base"
            else "class Reader(Client, Shape): pass\n"
        )
        + "@mcp.tool()\ndef read(value): return Reader(value).read()\n"
    )
    index = program({"app.py": source})
    state = RuleRunState()
    analyze(index, state, time.monotonic() + 10)
    assert not state.matches
    assert any("custom construction" in warning.message for warning in state.warnings)
