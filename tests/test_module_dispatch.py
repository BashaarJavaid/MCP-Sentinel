"""Module routing must prove the name, receiver and unchanged arguments."""

import ast
from pathlib import Path

import pytest

from sentinel.static.model import RuleRunState
from sentinel.static.rules.sent012 import analyze
from tests.test_python_discovery import program

SERVER = """from .tools import storage
MODULES = [storage]
def build():
    table = {}
    for module in MODULES:
        for tool in module.get_tools():
            if tool.name in table:
                raise ValueError('duplicate')
            table[tool.name] = module
    return table
DISPATCH = build()
@server.list_tools()
async def list_tools():
    tools = []
    for module in MODULES:
        tools.extend(module.get_tools())
    return tools
@server.call_tool()
async def dispatch(name, arguments):
    module = DISPATCH.get(name)
    if module is None:
        raise ValueError('unknown')
    result = module.handle_tool(name, arguments)
    return result
"""
PROVIDER = """from mcp.types import Tool
from ..client import read
def get_tools():
    return [Tool(name='upload', description='Read a file', inputSchema={})]
def handle_tool(name, arguments):
    if name == 'upload':
        return read(arguments['path'])
    raise ValueError('unknown')
"""


def sources(server: str = SERVER, provider: str = PROVIDER) -> dict[str, str]:
    return {
        "app/server.py": server,
        "app/tools/storage.py": provider,
        "app/client.py": "def read(path): return open(path)\n",
    }


@pytest.mark.parametrize("guarded", [False, True])
def test_module_dispatch_reaches_actual_imported_sink(guarded: bool) -> None:
    source = sources()
    if guarded:
        source["app/client.py"] = (
            "from pathlib import Path\n"
            "def read(path):\n"
            "    resolved = Path(path).resolve()\n"
            "    resolved.relative_to(Path('/srv/data').resolve())\n"
            "    return open(resolved)\n"
        )
    index = program(source)
    before = [ast.dump(file.tree, include_attributes=True) for file in index.files]
    tools = index.tools()
    assert [(tool.name, tool.handler.file.relative_path) for tool in tools] == [
        ("upload", "app/tools/storage.py")
    ]
    assert tools[0].registration.file.relative_path == "app/server.py"
    assert isinstance(tools[0].registration.node, ast.Call)
    assert tools[0].registration.node.lineno == 23
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == (0 if guarded else 1)
    if not guarded:
        assert state.matches[0].path == "app/client.py"
    assert not state.warnings
    assert before == [
        ast.dump(file.tree, include_attributes=True) for file in index.files
    ]
    assert index.tools() is tools


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("MODULES = [storage]", "MODULES = [unknown]"),
        ("MODULES = [storage]", "MODULES = [storage, storage]"),
        ("MODULES = [storage]", "MODULES = [storage]\nMODULES.append(other)"),
        ("MODULES = [storage]", "MODULES = [storage]\nescaped = MODULES"),
        ("MODULES = [storage]", "MODULES = [storage]\nstorage.handle_tool = other"),
        ("MODULES = [storage]", "MODULES = [storage]\nescaped = storage"),
        (
            "MODULES = [storage]",
            "MODULES = [storage]\nsetattr(storage, 'handle_tool', other)",
        ),
        ("DISPATCH = build()", "DISPATCH = build()\nDISPATCH['upload'] = other"),
        ("DISPATCH = build()", "DISPATCH = build()\nDISPATCH.update(other)"),
        ("DISPATCH = build()", "DISPATCH = build()\nDISPATCH = unknown"),
        ("DISPATCH = build()", "DISPATCH = build()\nescaped = DISPATCH"),
        ("DISPATCH = build()", "DISPATCH = build()\nbuild = unknown"),
        ("table[tool.name] = module", "table[tool.name] = other"),
        ("table[tool.name] = module", "table['upload'] = module"),
        (
            "table[tool.name] = module",
            "table[tool.name] = module\n            mutate(table)",
        ),
        ("module.get_tools()", "module.get_tools(config)"),
        ("DISPATCH.get(name)", "DISPATCH.get(arguments['name'])"),
        ("DISPATCH.get(name)", "DISPATCH.get(name, fallback)"),
        ("module.handle_tool(name, arguments)", "other.handle_tool(name, arguments)"),
        ("module.handle_tool(name, arguments)", "module.missing(name, arguments)"),
        (
            "module.handle_tool(name, arguments)",
            "module.handle_tool('different', arguments)",
        ),
        ("module.handle_tool(name, arguments)", "module.handle_tool(name, {})"),
        (
            "module.handle_tool(name, arguments)",
            "module.handle_tool(name, normalize(arguments))",
        ),
        ("return result", "escape(module)\n    return result"),
        ("return result", "module.handle_tool = other\n    return result"),
        ("if module is None:", "if module is not None:"),
        (
            "async def dispatch(name, arguments):",
            "async def dispatch(name, arguments, DISPATCH):",
        ),
    ],
)
def test_unproved_dispatch_stays_unsupported(old: str, new: str) -> None:
    assert old in SERVER
    index = program(sources(SERVER.replace(old, new)))
    assert not index.tools()
    state = RuleRunState()
    analyze(index, state)
    assert not state.matches


@pytest.mark.parametrize(
    "change",
    [
        "get_tools = replacement\n",
        "handle_tool = replacement\n",
        "def change():\n    global handle_tool\n    handle_tool = replacement\n",
        "def change():\n    globals()['handle_tool'] = replacement\n",
    ],
)
def test_provider_replacement_is_not_a_tool_binding(change: str) -> None:
    assert not program(sources(provider=PROVIDER + change)).tools()


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("name='upload'", "name=runtime_name"),
        ("description='Read a file'", "description=mutate()"),
        ("from mcp.types import Tool", "from fake import Tool"),
        ("from mcp.types import Tool", "from mcp.types import Tool\nTool = other"),
        ("return [Tool", "return unknown([Tool"),
        ("def get_tools():", "@replace\ndef get_tools():"),
        (
            "def handle_tool(name, arguments):",
            "@replace\ndef handle_tool(name, arguments):",
        ),
        ("def handle_tool(name, arguments):", "def handle_tool(arguments):"),
    ],
)
def test_unproved_provider_is_not_a_tool_binding(old: str, new: str) -> None:
    source = PROVIDER.replace(old, new)
    if new == "return unknown([Tool":
        source = source.replace("inputSchema={})]", "inputSchema={})])")
    assert not program(sources(provider=source)).tools()


def test_unknown_route_and_unregistered_module_are_not_entries() -> None:
    source = sources()
    source["app/tools/unregistered.py"] = PROVIDER.replace("'upload'", "'hidden'")
    index = program(source)
    assert [tool.name for tool in index.tools()] == ["upload"]
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == 1


def test_module_discovery_keeps_shared_deadline() -> None:
    from sentinel.errors import InfrastructureError

    index = program(sources())
    assert index.tools()
    index.deadline = 0
    with pytest.raises(InfrastructureError, match="deadline"):
        index.tools()


@pytest.mark.parametrize(
    "mutation",
    [
        "from .server import DISPATCH\nDISPATCH['upload'] = other\n",
        "from .server import DISPATCH\nescaped = DISPATCH\n",
        "from .server import MODULES\nMODULES.clear()\n",
        "from .tools import storage\nstorage.handle_tool = other\n",
        "from .tools import storage\nescaped = storage\n",
        "from .tools.storage import handle_tool\nescaped = handle_tool\n",
        "def change():\n    from .tools import storage\n"
        "    storage.handle_tool = other\n",
        "def change():\n    from .server import DISPATCH\n    DISPATCH.clear()\n",
        "from . import server\nsetattr(server, 'DISPATCH', other)\n",
        "from .tools.storage import *\n",
    ],
)
def test_imported_mutation_or_escape_rejects_the_route(mutation: str) -> None:
    source = sources(SERVER + "from . import plugin\n")
    source["app/plugin.py"] = mutation
    assert not program(source).tools()


@pytest.mark.parametrize("duplicate", [False, True])
def test_two_modules_keep_name_and_handler_identity(duplicate: bool) -> None:
    source = sources(
        SERVER.replace("import storage", "import storage, second").replace(
            "[storage]", "[storage, second]"
        )
    )
    source["app/tools/second.py"] = PROVIDER.replace(
        "'upload'", "'upload'" if duplicate else "'second'"
    )
    tools = program(source).tools()
    assert [(t.name, t.handler.file.relative_path) for t in tools] == (
        []
        if duplicate
        else [("upload", "app/tools/storage.py"), ("second", "app/tools/second.py")]
    )


@pytest.mark.parametrize("supported", [False, True])
def test_coverage_reports_actual_dispatch_support(
    tmp_path: Path, supported: bool
) -> None:
    from sentinel.config import load_configuration
    from sentinel.static.coverage import inventory
    from sentinel.static.model import StaticContext, StaticFileSet
    from tests.conftest import make_target

    index = program(
        sources(SERVER if supported else SERVER.replace("get(name)", "get(other)"))
    )
    state = RuleRunState()
    analyze(index, state)
    config = load_configuration(
        make_target(tmp_path / "target"), environ={}, static_only=True
    )
    files = StaticFileSet(index.files, (), (), len(index.files), 0, ())
    context = StaticContext(config, files)
    coverage = inventory(context, {"SENT-012": state})
    tools = [surface for surface in coverage.surfaces if surface.kind == "tool"]
    assert len(tools) == 1
    assert tools[0].status == ("recognized" if supported else "unsupported")
    assert ("SENT-012" in tools[0].examined_rule_ids) is supported
    if supported:
        assert tools[0].name == "upload"
        assert tools[0].handler is not None
        assert tools[0].handler.path == "app/tools/storage.py"


@pytest.mark.parametrize(
    "variant", ["plain", "annotated", "renamed", "direct", "no_duplicate_guard"]
)
def test_equivalent_bounded_builder_forms(variant: str) -> None:
    server = SERVER
    if variant == "annotated":
        server = server.replace("table = {}", "table: dict[str, object] = {}")
    elif variant == "renamed":
        for old, new in [
            ("MODULES", "REGISTRY"),
            ("DISPATCH", "ROUTES"),
            ("get_tools", "definitions"),
            ("handle_tool", "invoke"),
        ]:
            server = server.replace(old, new)
    elif variant == "direct":
        server = server.replace(
            "result = module.handle_tool(name, arguments)\n    return result",
            "return module.handle_tool(name, arguments)",
        )
    elif variant == "no_duplicate_guard":
        server = server.replace(
            "            if tool.name in table:\n"
            "                raise ValueError('duplicate')\n",
            "",
        )
    provider = PROVIDER
    if variant == "renamed":
        provider = provider.replace("get_tools", "definitions").replace(
            "handle_tool", "invoke"
        )
    assert [t.name for t in program(sources(server, provider)).tools()] == ["upload"]


def test_colliding_builder_variables_are_not_module_routes() -> None:
    server = SERVER.replace("for tool in", "for module in").replace(
        "tool.name", "module.name"
    )
    assert not program(sources(server)).tools()


def test_direct_source_calls_do_not_replace_module_members() -> None:
    source = sources(SERVER + "from . import helper\n")
    source["app/helper.py"] = (
        "from .tools import storage\n"
        "def check(): return storage.handle_tool('upload', {})\n"
    )
    assert [t.name for t in program(source).tools()] == ["upload"]


@pytest.mark.parametrize(
    "replacement",
    ["storage = replacement\n", "def __getattr__(name): return replacement\n"],
)
def test_package_attribute_cannot_impersonate_included_module(replacement: str) -> None:
    source = sources()
    source["app/tools/__init__.py"] = replacement
    assert not program(source).tools()


def test_package_namespace_escape_cannot_establish_module_identity() -> None:
    source = sources(SERVER + "from . import plugin\n")
    source["app/tools/__init__.py"] = ""
    source["app/plugin.py"] = (
        "from . import tools\nsetattr(tools, 'storage', replacement)\n"
    )
    assert not program(source).tools()


@pytest.mark.parametrize(
    "binding",
    [
        "reader = Reader()",
        "original = Reader()\nreader = original",
        "Constructor = Reader\nreader = Constructor()",
    ],
)
@pytest.mark.parametrize("receiver", ["self", "other"])
def test_global_instance_retains_actual_nested_guard_receiver(
    binding: str, receiver: str
) -> None:
    source = {
        "server.py": "from reader import reader\n@mcp.tool()\n"
        "def load(path): return reader.read(path)\n",
        "reader.py": "from pathlib import Path\n"
        "class Reader:\n"
        "    def checked(self, path):\n"
        "        value = Path(path).resolve()\n"
        "        value.relative_to(Path('/srv/data').resolve())\n"
        "        return value\n"
        "    def read(self, path):\n"
        f"        return open({receiver}.checked(path))\n" + binding + "\n",
    }
    state = RuleRunState()
    analyze(program(source), state)
    assert len(state.matches) == (0 if receiver == "self" else 1)
    assert bool(state.warnings) is (receiver != "self")


@pytest.mark.parametrize("guarded", [False, True])
@pytest.mark.parametrize("initialized", [False, True])
def test_module_dispatch_complete_serial_parallel_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, guarded: bool, initialized: bool
) -> None:
    import dataclasses
    import os

    from sentinel.config import load_configuration
    from sentinel.static import engine, workers
    from tests.conftest import NOW, SCAN_ID, make_target

    root = make_target(tmp_path / "target")
    source = sources()
    source["app/client.py"] = (
        "import os\n"
        "class Reader:\n"
        "    def checked(self, path):\n"
        "        root = os.environ.get('UPLOAD_DIR')\n"
        "        if not root: raise ValueError('disabled')\n"
        "        root = os.path.realpath(root)\n"
        "        resolved = os.path.realpath(os.path.join(root, path) "
        "if not os.path.isabs(path) else path)\n"
        "        if os.path.commonpath([root, resolved]) != root:\n"
        "            raise ValueError('outside')\n"
        "        return resolved\n"
        "    def read(self, path):\n"
        + ("        path = self.checked(path)\n" if guarded else "")
        + "        return open(path)\n"
        "reader = Reader()\n"
        "def read(path): return reader.read(path)\n"
    )
    if initialized:
        source["app/client.py"] = source["app/client.py"].replace(
            "class Reader:\n",
            "class Reader:\n    def __init__(self): self.api = None\n",
        )
    for name, text in source.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    marker = tmp_path / "target-executed"
    (root / "sentinel.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n"
    )
    configuration = load_configuration(
        root,
        environ={},
        cli_overrides={"rules_only": True, "rules": sorted(workers.FLOW_RULES)},
    )
    monkeypatch.setattr(workers, "MIN_SOURCE_SIZE", 0)
    monkeypatch.setattr(os, "cpu_count", lambda: 4)
    with monkeypatch.context() as serial_patch:
        serial_patch.setattr(engine, "run_flow_rules", lambda *_: {})
        serial = engine.run_static_scan(configuration, SCAN_ID, timestamp=NOW)
    parallel = engine.run_static_scan(configuration, SCAN_ID, timestamp=NOW)
    records = [dataclasses.asdict(result) for result in (serial, parallel)]
    for record in records:
        record["findings"] = [
            finding.model_dump(exclude={"finding_id"}) for finding in record["findings"]
        ]
        record["summary"] = record["summary"].model_dump(exclude={"duration_ms"})
    assert records[0] == records[1]
    assert len([f for f in parallel.findings if f.rule_id == "SENT-012"]) == (
        0 if guarded else 1
    )
    assert not parallel.incomplete
    assert not marker.exists()
