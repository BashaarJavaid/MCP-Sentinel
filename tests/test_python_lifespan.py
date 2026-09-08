"""Only source-established registration connects lifespan state to tool context."""

import ast

import pytest

from tests.test_python_discovery import program


@pytest.mark.parametrize("mount", [False, True])
@pytest.mark.parametrize("custom", [False, True])
def test_registered_lifespan_through_local_server_and_mount(
    mount: bool, custom: bool
) -> None:
    from sentinel.static.lifespan import tool_lifespan

    index = program(
        {
            "app.py": "from fastmcp import FastMCP\n"
            "from contextlib import asynccontextmanager\n"
            "from tools import child\n"
            "@asynccontextmanager\nasync def startup(app):\n"
            "    yield {'secret': 'owner'}\n"
            + (
                "class Server(FastMCP):\n    def __init__(self, **kwargs): pass\n"
                if custom
                else "class Server(FastMCP):\n    pass\n"
            )
            + "server=Server(lifespan=startup)\n"
            + (
                "server.mount(child, 'child')\n"
                if mount
                else "@server.tool()\ndef read(ctx: Context): return ctx\n"
            ),
            "tools.py": "from fastmcp import FastMCP, Context\nchild=FastMCP('child')\n"
            "@child.tool()\ndef child_read(ctx: Context): return ctx\n",
        }
    )
    tool = next(
        item
        for item in index.tools()
        if item.name == ("child_read" if mount else "read")
    )
    resolved = tool_lifespan(index, tool)
    assert (resolved is not None) is (not custom)
    if resolved:
        assert isinstance(resolved.node, ast.AsyncFunctionDef)
        assert resolved.node.name == "startup"


@pytest.mark.parametrize("change", ["unregistered", "rebound", "fake", "multiple"])
def test_unestablished_lifespan_remains_unresolved(change: str) -> None:
    from sentinel.static.lifespan import tool_lifespan

    index = program(
        {
            "app.py": "from fastmcp import FastMCP, Context\n"
            "from contextlib import asynccontextmanager\n"
            "@asynccontextmanager\nasync def startup(app): yield {'secret': 'owner'}\n"
            + ("FastMCP=unknown\n" if change == "rebound" else "")
            + ("class FastMCP: pass\n" if change == "fake" else "")
            + (
                "server=FastMCP()\n"
                if change == "unregistered"
                else "server=FastMCP(lifespan=startup)\n"
            )
            + ("server=FastMCP(lifespan=startup)\n" if change == "multiple" else "")
            + "@server.tool()\ndef read(ctx: Context): return ctx\n",
        }
    )
    assert tool_lifespan(index, index.tools()[0]) is None


@pytest.mark.parametrize("inspection", ["", "id(ctx)"])
@pytest.mark.parametrize("optional", [False, True])
def test_lifespan_value_reaches_only_registered_sdk_context(
    inspection: str, optional: bool
) -> None:
    import time

    from sentinel.static.discovery import Symbol
    from sentinel.static.model import RuleRunState
    from sentinel.static.path_flow import PathFlow, Value
    from sentinel.static.rules.sent012 import analyze

    class InspectFlow(PathFlow):
        seen: list[str]

        def call(self, symbol: Symbol, node: ast.Call, env: dict[str, Value]) -> Value:
            if isinstance(node.func, ast.Name) and node.func.id == "consume":
                value = self.expression(symbol, node.args[0], env)
                self.seen.append(value.key)
            return super().call(symbol, node, env)

    for registration in ("startup", "None"):
        index = program(
            {
                "app.py": "from fastmcp import FastMCP, Context\n"
                "from contextlib import asynccontextmanager\n"
                "from dataclasses import dataclass\n"
                "@dataclass\nclass Config:\n    token: str\n"
                "    optional: str | None = None\n"
                "@asynccontextmanager\nasync def startup(app):\n"
                '    yield {"configuration": Config(token="operator-source")}\n'
                f"server=FastMCP(lifespan={registration})\n"
                "@server.tool()\ndef read(ctx: Context):\n"
                f"    {inspection or 'pass'}\n"
                '    config=ctx.request_context.lifespan_context.get("configuration")\n'
                + ("    config=config if unknown else None\n" if optional else "")
                + "    consume(config.token)\n"
            }
        )
        flow = InspectFlow(index, RuleRunState(), time.monotonic() + 10)
        flow.seen = []
        analyze(index, flow.state, flow=flow)
        assert ("'operator-source'" in flow.seen) is (registration == "startup")


def test_repeated_lifespan_analysis_keeps_declared_record_fields_present() -> None:
    from sentinel.static.model import RuleRunState
    from sentinel.static.rules.sent012 import analyze

    index = program(
        {
            "app.py": "from fastmcp import FastMCP, Context\n"
            "from contextlib import asynccontextmanager\n"
            "from dataclasses import dataclass, replace\n"
            "@dataclass\nclass Config:\n    output: str\n"
            "@asynccontextmanager\nasync def startup(app):\n"
            "    config = None\n"
            "    if unknown(): config = Config('/fixed')\n"
            "    yield {'configuration': config}\n"
            "server = FastMCP(lifespan=startup)\n"
            + "".join(
                f"@server.tool()\ndef {name}(path, ctx: Context):\n"
                "    config = ctx.request_context.lifespan_context['configuration']\n"
                "    if not config: raise ValueError()\n"
                "    copied = replace(config)\n"
                "    if not copied: return open(path)\n"
                "    return open('/fixed')\n"
                for name in ("first", "second")
            )
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert not state.matches


def test_local_server_parameter_cannot_borrow_global_lifespan() -> None:
    from sentinel.static.lifespan import tool_lifespan

    index = program(
        {
            "app.py": "from fastmcp import FastMCP\n"
            "from contextlib import asynccontextmanager\n"
            "@asynccontextmanager\nasync def startup(app): yield {}\n"
            "server=FastMCP(lifespan=startup)\n"
            "def register(server):\n"
            "    @server.tool()\n    def read(value): return value\n"
        }
    )
    assert tool_lifespan(index, index.tools()[0]) is None


@pytest.mark.parametrize("mounted", [False, True])
def test_http_application_owner_follows_the_registered_server(mounted: bool) -> None:
    from sentinel.static.lifespan import tool_servers

    index = program(
        {
            "app.py": "from fastmcp import FastMCP\nfrom tools import child\n"
            "class App(FastMCP):\n"
            "    def http_app(self): return super().http_app()\n"
            "parent = App('parent')\n"
            + ("parent.mount(child, 'child')\n" if mounted else ""),
            "tools.py": "from fastmcp import FastMCP\nchild = FastMCP('child')\n"
            "@child.tool()\ndef fetch(): return None\n",
        }
    )
    servers = tool_servers(index, index.tools()[0])
    assert [
        (server.file.relative_path, ast.unparse(server.node)) for server in servers
    ] == [("app.py", "App('parent')") if mounted else ("tools.py", "FastMCP('child')")]


@pytest.mark.parametrize(
    "base",
    [
        "fastmcp.FastMCP",
        "mcp.server.fastmcp.FastMCP",
        "starlette.middleware.base.BaseHTTPMiddleware",
    ],
)
@pytest.mark.parametrize("generic", [False, True])
def test_framework_override_resolution_does_not_assume_unknown_base_methods(
    base: str, generic: bool
) -> None:
    module, _, name = base.rpartition(".")
    index = program(
        {
            "app.py": f"from {module} import {name} as Base\n"
            f"class App({'Base[object]' if generic else 'Base'}):\n"
            "    def selected(self): return None\n"
        }
    )
    owner = index.resolve(index.files[0], "App")
    assert owner is not None
    method = index.instance_method(owner, "selected")
    if generic and base == "starlette.middleware.base.BaseHTTPMiddleware":
        assert method is None
        return
    assert method is not None and method.name == "App.selected"
    assert index.instance_method(owner, "unknown") is None
    assert not index.plain_instance(owner, inspect_init=True)
