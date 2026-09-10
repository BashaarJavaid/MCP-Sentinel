"""Member writes and helper mutations preserve the actual caller value."""

import time

import pytest

from sentinel.static.model import RuleRunState
from sentinel.static.path_flow import PathFlow
from sentinel.static.rules.sent012 import analyze
from tests.test_python_discovery import program


def test_repeated_values_preserve_distinct_branch_guards() -> None:
    from dataclasses import replace

    from sentinel.static.path_flow import Value, combine

    guarded = Value(
        sources=frozenset({"caller"}),
        key="same-binding",
        contained=True,
        locations=frozenset({("server.py", 10)}),
        option_safe=True,
        url_checks=frozenset({"private-ip"}),
        operator_credential=True,
        credential_present=True,
        operator_opt_in=frozenset({"enabled"}),
        checked_path_parent=True,
    )
    unsafe = replace(
        guarded,
        contained=False,
        locations=frozenset({("server.py", 20)}),
        option_safe=False,
        url_checks=frozenset(),
        credential_fallback=True,
        credential_present=False,
        operator_opt_in=frozenset(),
        checked_path_parent=False,
    )
    for key in ("", "explicit"):
        for values in (
            [guarded, unsafe],
            [unsafe, guarded],
            [guarded, Value(key="None", maybe_none=True)],
            [guarded, Value(key="#missing", maybe_missing=True)],
            [replace(guarded, sources=frozenset())],
        ):
            repeated = values + values + [values[0]]
            original = tuple(repeated)
            assert combine(repeated, key) == combine(values, key)
            assert tuple(repeated) == original
    merged = combine([guarded, unsafe, guarded])
    assert not merged.contained and not merged.option_safe
    assert not merged.url_checks and not merged.checked_path_parent
    assert merged.credential_fallback and not merged.credential_present
    assert not merged.operator_opt_in
    assert merged.locations == guarded.locations | unsafe.locations


def test_immutable_member_reads_follow_current_state() -> None:
    from dataclasses import replace

    from sentinel.static.discovery import PythonProgram
    from sentinel.static.path_flow import Value

    flow = PathFlow(PythonProgram(()), RuleRunState(), float("inf"))
    owner = Value(key="owner", instance=("server.py", "State"))
    member = flow.member_key(owner, "url")
    flow.record_keys.add(owner.key)
    flow.required_members.add(member)
    flow.member_defaults[member] = Value(maybe_missing=True)
    guarded = Value(
        key="url",
        sources=frozenset({"caller"}),
        locations=frozenset({("server.py", 10)}),
        contained=True,
        url_checks=frozenset({"private-ip"}),
    )
    env = {member: guarded}
    for current in (
        guarded,
        replace(guarded, url_checks=frozenset(), contained=False),
        replace(guarded, locations=frozenset({("server.py", 20)})),
    ):
        env[member] = current
        for _ in range(2):
            assert flow.member(owner, "url", env) == current
            assert flow.member(replace(owner, maybe_none=True), "url", env) == replace(
                current, maybe_missing=True
            )
            assert flow.aggregate(owner, env) == replace(
                owner, sources=current.sources, locations=current.locations
            )
    assert env[member] == current and guarded.contained


def test_http_middleware_validation_tracks_reachable_mutation() -> None:
    from sentinel.errors import InfrastructureError
    from sentinel.static.path_flow import Value

    index = program(
        {
            "server.py": "from starlette.middleware.base import BaseHTTPMiddleware\n"
            "class Guard(BaseHTTPMiddleware):\n"
            "    async def dispatch(self, request, call_next):\n"
            "        return await call_next(request)\n"
            "def mutate(): unknown(Guard)\n"
        }
    )
    flow = PathFlow(index, RuleRunState(), time.monotonic() + 15)
    owner = index.resolve(index.files[0], "Guard")
    mutation = index.resolve(index.files[0], "mutate")
    assert owner is not None and mutation is not None
    flow.callables["guard"] = owner
    context = flow.http_context
    for _ in range(2):
        assert context.base_http_layer(Value(key="guard"), Value(key="next"))
    context.executed_functions.add(mutation.node)
    for _ in range(2):
        assert context.base_http_layer(Value(key="guard"), Value(key="next")) is None
    flow.deadline = 0
    with pytest.raises(InfrastructureError, match="timeout"):
        context.base_http_layer(Value(key="guard"), Value(key="next"))


@pytest.mark.parametrize("transport", ["streamable-http", "stdio"])
@pytest.mark.parametrize(
    ("prefix", "login_continues"),
    [
        ("    if os.getenv('LOGIN'):\n        login()\n        return\n", False),
        (
            "    if os.getenv('LOGIN'):\n"
            "        login()\n        raise RuntimeError('stop')\n",
            False,
        ),
        (
            "    if os.getenv('LOGIN'):\n"
            "        login()\n        if os.getenv('STOP'): return\n",
            True,
        ),
        (
            "    try:\n        if os.getenv('LOGIN'):\n"
            "            login()\n            raise RuntimeError('stop')\n"
            "    except RuntimeError: pass\n",
            True,
        ),
    ],
)
def test_sdk_setup_follows_the_selected_launch_path(
    prefix: str, login_continues: bool, transport: str
) -> None:
    from sentinel.static.launches import for_tool

    index = program(
        {
            "server.py": "import os\nfrom mcp.server.fastmcp import FastMCP\n"
            "mcp=FastMCP('test')\n"
            "def login(): login_side_effect()\n"
            "def setup_http(): http_side_effect()\n"
            "def setup_stdio(): stdio_side_effect()\n"
            "def main():\n" + prefix + "    if os.getenv('HTTP'):\n"
            "        setup_http()\n        mcp.run(transport='streamable-http')\n"
            "    else:\n"
            "        setup_stdio()\n        mcp.run(transport='stdio')\n"
            "@mcp.tool()\ndef read(path: str): return open(path)\n"
        }
    )
    flow = PathFlow(index, RuleRunState(), time.monotonic() + 15)
    tool = index.tools()[0]
    launch = next(item for item in for_tool(index, tool) if item.transport == transport)
    assert flow.http_context.prepare_launch(tool, launch) is not None
    executed = {
        getattr(node, "name", "") for node in flow.http_context.executed_functions
    }
    assert ("setup_http" in executed) == (transport == "streamable-http")
    assert ("login" in executed) == login_continues
    assert ("setup_stdio" in executed) == (transport == "stdio")


@pytest.mark.parametrize("order", ["change,read", "read,change"])
def test_sdk_tools_keep_independent_startup_callbacks(order: str) -> None:
    from unittest.mock import patch

    from sentinel.static.discovery import Function
    from sentinel.static.http_context import HTTPContext

    definitions = {
        "change": "@mcp.tool()\ndef change(path: str):\n"
        "    helpers.current = lambda: path\n"
        "    return open(helpers.current())\n",
        "read": "@mcp.tool()\ndef read(): return open(helpers.current())\n",
    }
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\nimport helpers\n"
            "mcp=FastMCP('test')\n"
            "def main():\n"
            "    helpers.current = lambda: '/fixed/file'\n"
            "    mcp.run(transport='streamable-http')\n"
            + "".join(definitions[name] for name in order.split(",")),
            "helpers.py": "def current(): return '/original/file'\n",
        }
    )
    state = RuleRunState()
    with patch.object(
        HTTPContext,
        "prepare_launch",
        autospec=True,
        side_effect=HTTPContext.prepare_launch,
    ) as prepare:
        analyze(index, state, deadline=time.monotonic() + 15)
        assert prepare.call_count == 1
    assert len({(match.path, match.range.start_line) for match in state.matches}) == 1
    assert "open(helpers.current())" in state.matches[0].snippet
    changed = index.resolve(index.files[0], "change")
    assert changed is not None and isinstance(changed.node, Function)
    assert state.matches[0].range.start_line > changed.node.lineno


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


@pytest.mark.parametrize("local_import", [False, True])
@pytest.mark.parametrize("initially_unsafe", [False, True])
@pytest.mark.parametrize(
    "selected", ["provider.read(path)", "saved(path)", "provider.invoke(path)"]
)
def test_source_module_callback_replacement_keeps_saved_binding(
    local_import: bool, initially_unsafe: bool, selected: str
) -> None:
    imported = "import provider"
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            + ("" if local_import else imported + "\n")
            + "mcp=FastMCP('test')\n"
            "@mcp.tool()\ndef read(path: str):\n"
            + ("    " + imported + "\n" if local_import else "")
            + "    saved = provider.read\n"
            + (
                "    provider.read = lambda path: open('/fixed')\n"
                if initially_unsafe
                else "    provider.read = lambda path: open(path)\n"
            )
            + f"    return {selected}\n",
            "provider.py": (
                "def read(path): return open(path)\n"
                if initially_unsafe
                else "def read(path): return open('/fixed')\n"
            )
            + "def invoke(path): return read(path)\n",
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == (
        initially_unsafe if selected == "saved(path)" else not initially_unsafe
    )


@pytest.mark.parametrize("import_time", ["before", "after"])
def test_source_import_captures_callback_at_the_import_statement(
    import_time: str,
) -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\nimport provider\n"
            + (
                "from provider import read as saved\n"
                if import_time == "before"
                else ""
            )
            + "mcp=FastMCP('test')\n@mcp.tool()\ndef read(path: str):\n"
            "    provider.read = lambda path: open(path)\n"
            + (
                "    from provider import read as saved\n"
                if import_time == "after"
                else ""
            )
            + "    return saved(path)\n",
            "provider.py": "def read(path): return open('/fixed')\n",
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == (import_time == "after")


@pytest.mark.parametrize(
    "replacement",
    [
        "provider.read = unknown",
        "unknown(provider)",
        "provider.read = lambda path: open(path); del provider.read",
    ],
)
@pytest.mark.parametrize("call", ["provider.read(path)", "provider.invoke(path)"])
def test_unknown_source_module_mutation_does_not_restore_the_original_callback(
    replacement: str, call: str
) -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\nimport provider\n"
            "mcp=FastMCP('test')\n@mcp.tool()\ndef read(path: str):\n"
            f"    {replacement}\n    return {call}\n",
            "provider.py": "def read(path): return open(path)\n"
            "def invoke(path): return read(path)\n",
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert not state.matches
    assert state.warnings


@pytest.mark.parametrize(
    "mutation",
    ["provider.__dict__['read'] = unknown", "vars(provider)['read'] = unknown"],
)
def test_source_module_reflection_invalidates_callable_identity(mutation: str) -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\nimport provider\n"
            "mcp=FastMCP('test')\n@mcp.tool()\ndef read(path: str):\n"
            f"    {mutation}\n    return provider.read(path)\n",
            "provider.py": "def read(path): return open(path)\n",
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert not state.matches
    assert state.warnings


@pytest.mark.parametrize("append", [False, True])
def test_known_list_iteration_updates_the_selected_callback(append: bool) -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "mcp=FastMCP('test')\n@mcp.tool()\ndef read(path: str):\n"
            "    callbacks={'read': lambda path: 'safe'}\n"
            "    names=[]\n"
            + ("    names.append('read')\n" if append else "")
            + "    for name in names:\n"
            "        callbacks[name] = lambda path: open(path)\n"
            "    return callbacks['read'](path)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == append


def test_empty_list_does_not_execute_its_loop_body() -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "mcp=FastMCP('test')\n@mcp.tool()\ndef read(path: str):\n"
            "    for name in []:\n        open(path)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert not state.matches


def test_list_iteration_observes_appended_values() -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "mcp=FastMCP('test')\n@mcp.tool()\ndef read(path: str):\n"
            "    paths=['/fixed']\n    for selected in paths:\n"
            "        if selected == '/fixed': paths.append(path)\n"
            "        else: open(selected)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert state.matches


def test_tuple_has_no_builtin_append_method() -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "mcp=FastMCP('test')\n@mcp.tool()\ndef read(path: str):\n"
            "    paths=()\n    paths.append(path)\n"
            "    for selected in paths: open(selected)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert not state.matches
    assert state.warnings


def test_list_append_through_a_helper_preserves_allocation_identity() -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "def append(paths, value): paths.append(value)\n"
            "mcp=FastMCP('test')\n@mcp.tool()\ndef read(path: str):\n"
            "    paths=[]\n    alias=paths\n    append(alias,path)\n"
            "    for selected in paths: open(selected)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == 1


def test_oversized_list_cannot_hide_a_tainted_last_element() -> None:
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "mcp=FastMCP('test')\n@mcp.tool()\ndef read(path: str):\n"
            "    paths=[" + ",".join(["'/fixed'"] * 33 + ["path"]) + "]\n"
            "    for selected in paths: open(selected)\n"
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert state.matches
