"""Containment checks must protect the actual value before its filesystem use."""

import json
from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.static.engine import run_static_scan
from sentinel.static.model import RuleRunState
from sentinel.static.rules.sent012 import analyze
from tests.conftest import NOW, make_target
from tests.test_python_discovery import program


@pytest.mark.parametrize("callback", ["read_global", "lambda: open(state['path'])"])
def test_helper_keeps_mutated_global_and_closure_state(callback: str) -> None:
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": "from proxy import invoke\n"
                "state = {'path': '/srv/fixed'}\n"
                "def read_global(): return open(state['path'])\n"
                "@mcp.tool()\ndef read(path):\n"
                "    state['path'] = path\n"
                f"    return invoke({callback})\n",
                "proxy.py": "def invoke(callback): return callback()\n",
            }
        ),
        state,
    )
    assert len(state.matches) == 1
    assert state.matches[0].path == "server.py"


def test_repeated_helper_limit_reports_each_source_reason_once() -> None:
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": "def checked(p): return unknown(p)\n"
                "@mcp.tool()\ndef read_one(path): return open(checked(path))\n"
                "@mcp.tool()\ndef read_two(path): return open(checked(path))\n"
            }
        ),
        state,
    )
    assert len(state.matches) == 2
    assert len(state.warnings) == 1
    assert "server.py:1" in state.warnings[0].message


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("open('/srv/fixed' if True else path)", 0),
        ("open('/srv/fixed' if False else path)", 1),
        ("open('/srv/fixed' if enabled else path)", 1),
        ("open(path) if False else None", 0),
    ],
)
def test_conditional_expression_only_visits_possible_branch(
    expression: str, expected: int
) -> None:
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": "@mcp.tool()\ndef read(path, enabled):\n    return "
                + expression
                + "\n"
            }
        ),
        state,
    )
    assert len(state.matches) == expected


def test_configured_launch_globals_keep_transport_specific_path_evidence() -> None:
    source = (
        "import os\nfrom mcp.server.fastmcp import FastMCP\nmcp = FastMCP('test')\n"
        "ROOT = None\n"
        "def checked(path):\n"
        "    if ROOT is None: return path\n"
        "    root = os.path.realpath(ROOT)\n"
        "    p = os.path.realpath(os.path.join(root, path))\n"
        "    if os.path.commonpath([root, p]) != root: raise ValueError()\n"
        "    return p\n"
        "@mcp.tool()\ndef read(path):\n    return open(checked(path))\n"
        "def http():\n    global ROOT\n    ROOT = os.environ.get('ROOT', '/srv/data')\n"
        "    mcp.run(transport='streamable-http')\n"
        "def stdio():\n    mcp.run(transport='stdio')\n"
    )
    state = RuleRunState()
    analyze(program({"server.py": source}), state)
    assert len(state.matches) == 1
    assert json.loads(state.matches[0].captures["launch_transports"]) == ["stdio"]
    vulnerable = source.replace(
        "    if os.path.commonpath([root, p]) != root: raise ValueError()\n", ""
    )
    state = RuleRunState()
    analyze(program({"server.py": vulnerable}), state)
    assert {
        json.loads(match.captures["launch_transports"])[0] for match in state.matches
    } == {
        "stdio",
        "streamable-http",
    }


@pytest.mark.parametrize(
    "extra", ["mcp.run()", "def other(transport):\n    mcp.run(transport=transport)"]
)
def test_unresolved_launch_cannot_hide_unconfigured_handler(extra: str) -> None:
    source = (
        "import os\nfrom mcp.server.fastmcp import FastMCP\nmcp = FastMCP('test')\n"
        "ROOT = None\n@mcp.tool()\ndef read(path):\n"
        "    if ROOT is None: return open(path)\n"
        "    return open('/srv/data/fixed')\n"
        "def configured():\n    global ROOT\n    ROOT='/srv/data'\n"
        "    mcp.run(transport='streamable-http')\n" + extra + "\n"
    )
    state = RuleRunState()
    analyze(program({"server.py": source}), state)
    assert state.matches
    assert any("launch" in warning.message for warning in state.warnings)


@pytest.mark.parametrize(
    ("guard", "expected"),
    [
        ("if not inside(root, p): raise ValueError()", 0),
        ("if not inside(root, p): return None", 0),
        ("inside(root, p)", 1),
        ("if not inside(root, other): raise ValueError()", 1),
        ("if not inside(root, p): raise ValueError()\np = other_input", 1),
        (
            "try:\n    if not inside(root, p): raise ValueError()\n"
            "except ValueError:\n    pass",
            1,
        ),
    ],
)
def test_realpath_commonpath_boolean_helper(guard: str, expected: int) -> None:
    source = (
        "import os\nfrom mcp.server.fastmcp import FastMCP\nmcp = FastMCP('test')\n"
        "def inside(root, p):\n"
        "    root = os.path.realpath(root)\n    p = os.path.realpath(p)\n"
        "    if p == root: return True\n"
        "    try:\n        return os.path.commonpath([root, p]) == root\n"
        "    except ValueError:\n        return False\n"
        "@mcp.tool()\ndef read(path, other_input):\n"
        "    root = os.path.realpath('/srv/data')\n"
        "    p = os.path.realpath(path)\n"
        "    other = os.path.realpath('/srv/data/fixed')\n"
        + "\n".join("    " + line for line in guard.splitlines())
        + "\n    return open(p)\n"
    )
    state = RuleRunState()
    analyze(program({"server.py": source}), state)
    assert len(state.matches) == expected


@pytest.mark.parametrize(
    ("setup", "guard", "argument", "expected"),
    [
        ("", "", "path", 1),
        ("", "", "filename=path", 1),
        ("", "path = '/srv/data/fixed.xlsx'", "path", 0),
        (
            "",
            "p = Path(path).resolve(); "
            "p.relative_to(Path('/srv/data').resolve()); path = str(p)",
            "path",
            0,
        ),
        ("load = custom", "", "path", 0),
        ("", "load = custom", "path", 0),
    ],
)
def test_source_bound_workbook_path(
    tmp_path: Path, setup: str, guard: str, argument: str, expected: int
) -> None:
    root = make_target(tmp_path / "target", target_yaml="")
    (root / "server.py").write_text(
        "from pathlib import Path\nfrom openpyxl import load_workbook as load\n"
        "from mcp.server.fastmcp import FastMCP\nmcp = FastMCP('test')\n"
        + setup
        + "\n@mcp.tool()\ndef read(path: str):\n"
        + ("    " + guard + "\n" if guard else "")
        + f"    return load({argument})\n",
        encoding="utf-8",
    )
    configuration = load_configuration(
        root, environ={}, static_only=True, cli_overrides={"rules": ["SENT-012"]}
    )
    result = run_static_scan(configuration, uuid4(), timestamp=NOW)
    assert not result.incomplete
    assert len(result.findings) == expected


@pytest.mark.parametrize(
    ("construction", "mutation", "expected"),
    [
        ("Workbook()", "", 1),
        ("load_workbook('/srv/data/fixed.xlsx')", "", 1),
        ("Workbook()", "wb.save = replacement", 0),
        ("Workbook()", "unknown(wb)", 0),
        ("Workbook()", "wb.create_sheet('new')", 1),
        ("custom()", "", 0),
    ],
)
def test_workbook_save_requires_source_bound_receiver(
    construction: str, mutation: str, expected: int
) -> None:
    source = (
        "from openpyxl import Workbook, load_workbook\n"
        "from mcp.server.fastmcp import FastMCP\nmcp=FastMCP('test')\n"
        "@mcp.tool()\ndef write(path):\n"
        f"    wb = {construction}\n"
        + (f"    {mutation}\n" if mutation else "")
        + "    wb.save(filename=path)\n"
    )
    state = RuleRunState()
    analyze(program({"server.py": source}), state)
    assert len(state.matches) == expected


@pytest.mark.parametrize(
    ("body", "unsafe"),
    [
        ("return open(path)", True),
        ("if open(path):\n    return True", True),
        ("return [open(item) for item in path]", True),
        ("return [open(item) for item in ['/srv/data/fixed']]", False),
        ("try:\n    return None\nfinally:\n    open(path)", True),
        ("return open('/srv/data/' + path)", True),
        ("p = Path(path).resolve()\nreturn p.read_text()", True),
        (
            "p = Path(path).resolve()\n"
            "if not str(p).startswith('/srv/data'):\n    raise ValueError()\n"
            "return p.read_text()",
            True,
        ),
        (
            "p = Path(path).resolve()\n"
            "if not p.is_relative_to(Path('/srv/data').resolve()):\n"
            "    raise ValueError()\nreturn p.read_text()",
            False,
        ),
        (
            "p = Path(path).resolve()\n"
            "p.is_relative_to(Path('/srv/data').resolve())\nreturn p.read_text()",
            True,
        ),
        (
            "p = Path(path).resolve()\n"
            "other = Path('/srv/data/fixed').resolve()\n"
            "other.relative_to(Path('/srv/data').resolve())\nreturn p.read_text()",
            True,
        ),
        (
            "p = Path(path).resolve()\n"
            "p.relative_to(Path('/srv/data').resolve())\n"
            "p = Path(replacement).resolve()\nreturn p.read_text()",
            True,
        ),
        (
            "p = Path(path).resolve()\n"
            "p.relative_to(Path('/srv/data').resolve())\nreturn p.read_text()",
            False,
        ),
        (
            "p = Path(path).resolve()\n"
            "p.relative_to(Path('/srv/data').resolve(), walk_up=True)\n"
            "return p.read_text()",
            True,
        ),
        (
            "p = Path(path).resolve()\n"
            "p.relative_to(Path('/srv/data').resolve(), walk_up=replacement)\n"
            "return p.read_text()",
            True,
        ),
        (
            "p = Path(path).expanduser().resolve()\n"
            "p.relative_to(Path('/srv/data').resolve())\nreturn open(path)",
            True,
        ),
        (
            "p = Path(path)\np.relative_to(Path('/srv/data'))\nreturn p.read_text()",
            True,
        ),
        (
            "p = Path(path).resolve()\n"
            "try:\n    p.relative_to(Path('/srv/data').resolve())\n"
            "except ValueError:\n    pass\nreturn p.read_text()",
            True,
        ),
        ("path = '/srv/data/fixed'\nreturn open(path)", False),
    ],
)
def test_path_guard_flow(body: str, unsafe: bool) -> None:
    source = (
        "from pathlib import Path\n@mcp.tool()\ndef read(path, replacement):\n"
        + "\n".join("    " + line for line in body.splitlines())
    )
    state = RuleRunState()
    analyze(program({"server.py": source}), state)
    assert bool(state.matches) == unsafe
    assert state.visits


def test_imported_handler_and_guard_preserve_sink_location() -> None:
    sources = {
        "server.py": "from handlers import read\nmcp.add_tool(read)\n",
        "handlers.py": (
            "from pathlib import Path\nfrom guards import checked\n"
            "def read(path):\n    p = checked(path)\n    return p.read_text()\n"
        ),
        "guards.py": (
            "from pathlib import Path\ndef checked(value):\n"
            "    p = Path(value).resolve()\n"
            "    if not p.is_relative_to(Path('/srv/data').resolve()):\n"
            "        raise ValueError()\n    return p\n"
        ),
    }
    safe = RuleRunState()
    analyze(program(sources), safe)
    assert not safe.matches
    sources["guards.py"] = sources["guards.py"].replace("raise ValueError()", "pass")
    unsafe = RuleRunState()
    analyze(program(sources), unsafe)
    assert len(unsafe.matches) == 1
    assert unsafe.matches[0].path == "handlers.py"
    assert "guards.py" in unsafe.matches[0].captures["flow_locations"]


def test_unknown_helper_is_disclosed_without_inventing_a_sink() -> None:
    state = RuleRunState()
    analyze(
        program(
            {"server.py": "@mcp.tool()\ndef read(path):\n    return plugin(path)\n"}
        ),
        state,
    )
    assert not state.matches
    assert any(w.code == "static_flow_unresolved" for w in state.warnings)


@pytest.mark.parametrize("early_return", [False, True])
def test_void_validator_must_reject_on_every_return_path(early_return: bool) -> None:
    guard = "    if skip:\n        return\n" if early_return else ""
    source = (
        "from pathlib import Path\n"
        "def validate(path, skip):\n" + guard + "    p = Path(path).resolve()\n"
        "    p.relative_to(Path('/srv/data').resolve())\n"
        "@mcp.tool()\ndef read(path, skip):\n"
        "    validate(path, skip)\n    return open(path)\n"
    )
    state = RuleRunState()
    analyze(program({"server.py": source}), state)
    assert bool(state.matches) == early_return


@pytest.mark.parametrize("constructor", ["FakePath", "Path"])
def test_named_path_methods_are_not_proof_without_pathlib(constructor: str) -> None:
    source = (
        "from pathlib import Path\nclass FakePath:\n"
        "    def __init__(self, value):\n        pass\n"
        "    def resolve(self):\n        return self\n"
        "    def relative_to(self, base):\n        return self\n"
        + ("Path = FakePath\n" if constructor == "Path" else "")
        + "@mcp.tool()\ndef read(path):\n"
        f"    p = {constructor}(path).resolve()\n"
        "    p.relative_to(Path('/srv/data').resolve())\n"
        "    return open(path)\n"
    )
    state = RuleRunState()
    analyze(program({"server.py": source}), state)
    assert len(state.matches) == 1


@pytest.mark.parametrize("caller_boundary", [False, True])
def test_optional_operator_root_does_not_become_a_caller_bypass(
    caller_boundary: bool,
) -> None:
    source = (
        "from pathlib import Path\n"
        "def validate(path, root):\n"
        "    if root is None:\n        return\n"
        "    p = Path(path).resolve()\n"
        "    base = Path(root).resolve()\n"
        "    p.relative_to(base)\n"
        "@mcp.tool()\ndef read(path"
        + (", root" if caller_boundary else "")
        + "):\n    validate(path, "
        + ("root" if caller_boundary else "operator_root")
        + ")\n    return open(path)\n"
    )
    state = RuleRunState()
    analyze(program({"server.py": source}), state)
    assert bool(state.matches) == caller_boundary


def test_checking_unknown_transformation_does_not_validate_original_value() -> None:
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": (
                    "from pathlib import Path\n@mcp.tool()\ndef read(path):\n"
                    "    p = Path(transform(path)).resolve()\n"
                    "    p.relative_to(Path('/srv/data').resolve())\n"
                    "    return open(path)\n"
                )
            }
        ),
        state,
    )
    assert len(state.matches) == 1


def test_bound_method_chain_reaches_filesystem_sink() -> None:
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": (
                    "class Reader:\n"
                    "    def read(self, path):\n        return self.fetch(path)\n"
                    "    def fetch(self, value):\n        return open(value)\n"
                    "reader = Reader()\nmcp.add_tool(reader.read)\n"
                )
            }
        ),
        state,
    )
    assert len(state.matches) == 1
    assert state.matches[0].range.start_line == 5


def test_imported_handler_report_preserves_suppression_and_no_execution(
    tmp_path: Path,
) -> None:
    root = make_target(
        tmp_path / "target", scanner_toml='[scanner]\nrules = ["SENT-012"]\n'
    )
    (root / "server.py").write_text(
        "from pathlib import Path\nfrom helpers import read\n"
        "Path(__file__).with_name('executed').touch()\nmcp.add_tool(read)\n"
    )
    (root / "helpers.py").write_text(
        "def read(path):\n"
        "    # sentinel: ignore[SENT-012] reason=intentional unrestricted fixture\n"
        "    return open(path)\n"
    )
    result = run_static_scan(
        load_configuration(root, environ={}, cli_overrides={"rules_only": True}),
        uuid4(),
        timestamp=NOW,
    )
    assert not (root / "executed").exists()
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.location.path == "helpers.py"
    assert finding.suppression is not None
    assert finding.owasp_category.id == "ASI02:2026"
    assert result.summary.coverage is not None
    tool = next(
        surface
        for surface in result.summary.coverage.surfaces
        if surface.name == "read"
    )
    assert tool.location.path == "server.py"
    assert tool.handler is not None and tool.handler.path == "helpers.py"
    assert tool.examined_rule_ids == ("SENT-012",)
    from sentinel.llm.context import build_finding_context

    context = build_finding_context(root, finding)
    assert context.contains("server.py", 4, 4)
    assert context.contains("helpers.py", 3, 3)
    assert not context.omitted_flow_locations
    assert not any(
        w.code == "static_review_context_incomplete" for w in result.warnings
    )


@pytest.mark.parametrize(
    "annotation", ["SDKContext", "Annotated[SDKContext, 'injected']"]
)
def test_sdk_injected_context_is_not_a_caller_path(annotation: str) -> None:
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": (
                    "from mcp.server.fastmcp import Context as SDKContext\n"
                    "from typing import Annotated\n"
                    f"@mcp.tool()\ndef read(path: str, ctx: {annotation}):\n"
                    "    open(ctx.session_id)\n    return open(path)\n"
                )
            }
        ),
        state,
    )
    assert [match.range.start_line for match in state.matches] == [6]


def test_similarly_named_context_is_still_caller_controlled() -> None:
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": (
                    "@mcp.tool()\ndef read(ctx: Context):\n    return open(ctx.path)\n"
                )
            }
        ),
        state,
    )
    assert len(state.matches) == 1


@pytest.mark.parametrize("guarded", [False, True])
def test_factory_returned_method_tracks_cross_file_guard(guarded: bool) -> None:
    validation = (
        "p = Path(path).resolve()\np.relative_to(Path('/allowed').resolve())\n"
        if guarded
        else "p = Path(path)\n"
    )
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": (
                    "from factory import make_reader\n@mcp.tool()\n"
                    "def read(path):\n    reader = make_reader()\n"
                    "    return reader.read(path)\n"
                ),
                "factory.py": (
                    "from reader import Reader\n"
                    "def make_reader():\n    return Reader()\n"
                ),
                "reader.py": (
                    "from pathlib import Path\n"
                    "class Reader:\n    def read(self, path):\n"
                )
                + "".join("        " + line + "\n" for line in validation.splitlines())
                + "        return p.read_text()\n",
            }
        ),
        state,
    )
    assert len(state.matches) == (0 if guarded else 1)
    if state.matches:
        assert state.matches[0].path == "reader.py"


def test_factory_annotation_alone_does_not_establish_implementation() -> None:
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": (
                    "from reader import make_reader\n@mcp.tool()\n"
                    "def read(path):\n    reader = make_reader()\n"
                    "    return reader.read(path)\n"
                ),
                "reader.py": (
                    "class Reader:\n    def read(self, path):\n"
                    "        return open(path)\n"
                    "def make_reader() -> Reader:\n    return reflection()\n"
                ),
            }
        ),
        state,
    )
    assert not state.matches
    assert any("unresolved call" in warning.message for warning in state.warnings)


def test_relative_path_join_preserves_path_type_and_enforced_guard() -> None:
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": (
                    "from pathlib import Path\nimport os\n"
                    "def checked(path, base=None):\n"
                    "    if base is None:\n        base = os.getcwd()\n"
                    "    root = Path(base).resolve()\n    p = Path(path)\n"
                    "    if not p.is_absolute():\n        p = root / p\n"
                    "    p = p.resolve()\n"
                    "    if not p.is_relative_to(root):\n        raise ValueError()\n"
                    "    return p\n"
                    "@mcp.tool()\ndef read(path):\n"
                    "    return open(str(checked(path)))\n"
                )
            }
        ),
        state,
    )
    assert not state.matches


def test_replaced_factory_method_is_not_mistaken_for_original() -> None:
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": (
                    "class Reader:\n    def read(self, path):\n"
                    "        return open(path)\n"
                    "def make_reader():\n    return Reader()\n"
                    "@mcp.tool()\ndef read(path):\n    reader = make_reader()\n"
                    "    reader.read = replacement\n    return reader.read(path)\n"
                )
            }
        ),
        state,
    )
    assert not state.matches
    assert state.warnings


@pytest.mark.parametrize(
    ("guard", "change", "expected"),
    [
        ("if mode not in ['oauth', 'pat', 'basic']: raise ValueError()", "", 0),
        ("if not (mode in ('oauth', 'pat', 'basic')): raise ValueError()", "", 0),
        ("if mode != 'pat': raise ValueError()", "", 0),
        ("if other not in ['oauth', 'pat', 'basic']: raise ValueError()", "", 1),
        ("mode in ['oauth', 'pat', 'basic']", "", 1),
        (
            "if mode not in ['oauth', 'pat', 'basic']: raise ValueError()",
            "mode = other",
            1,
        ),
        (
            "if mode not in ['oauth', 'pat', 'basic']: raise ValueError()",
            "mode = mode + other",
            1,
        ),
        ("if mode not in ['oauth', 'pat', 'basic']: pass", "", 1),
    ],
)
def test_enforced_literal_choices_exclude_impossible_fallthrough(
    guard: str, change: str, expected: int
) -> None:
    state = RuleRunState()
    source = (
        "def choose(mode, path):\n"
        "    if mode == 'oauth': return '/fixed/oauth'\n"
        "    elif mode == 'pat': return '/fixed/pat'\n"
        "    elif mode == 'basic': return '/fixed/basic'\n"
        "    return path\n"
        "@mcp.tool()\ndef read(mode, other, path):\n"
        f"    {guard}\n    {change or 'pass'}\n"
        "    alias = mode\n    return open(choose(alias, path))\n"
    )
    analyze(program({"server.py": source}), state)
    assert len(state.matches) == expected


def test_custom_equality_does_not_establish_literal_choices() -> None:
    source = (
        "class Mode:\n"
        "    def __eq__(self, other): return unknown()\n"
        "@mcp.tool()\ndef read(path):\n"
        "    mode = Mode()\n"
        "    if mode not in ['oauth', 'pat']: raise ValueError()\n"
        "    if mode == 'oauth': return open('/fixed/oauth')\n"
        "    if mode == 'pat': return open('/fixed/pat')\n"
        "    return open(path)\n"
    )
    state = RuleRunState()
    analyze(program({"server.py": source}), state)
    assert len(state.matches) == 1


@pytest.mark.parametrize(
    "configuration",
    [
        "kwargs = {'output': getattr(obj, 'output', None)}; "
        "config = replace(base, **kwargs)",
        "kwargs = {}; kwargs['output'] = getattr(obj, 'output', None); "
        "config = replace(base, **kwargs)",
        "kwargs = dict(output=getattr(obj, 'output', None)); "
        "config = replace(base, **kwargs)",
        "kwargs = {}; kwargs.update(output=getattr(obj, 'output', None)); "
        "config = replace(base, **kwargs)",
        "config = Config(getattr(obj, 'output', None)); config = replace(config)",
    ],
)
def test_assigned_record_fields_exist_when_their_values_are_uncertain(
    configuration: str,
) -> None:
    source = (
        "from dataclasses import dataclass, replace\n"
        "@dataclass\nclass Config:\n    output: str\n"
        "@mcp.tool()\ndef read(obj, path):\n"
        "    base = Config('/fixed')\n"
        f"    {configuration}\n"
        "    if not config: return open(path)\n"
        "    return open('/fixed')\n"
    )
    state = RuleRunState()
    analyze(program({"server.py": source}), state)
    assert not state.matches


def test_rebound_sdk_context_annotation_stays_caller_controlled() -> None:
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": (
                    "from mcp.server.fastmcp import Context\nContext = str\n"
                    "@mcp.tool()\ndef read(ctx: Context):\n    return open(ctx)\n"
                )
            }
        ),
        state,
    )
    assert len(state.matches) == 1


@pytest.mark.parametrize(
    "constructor",
    [
        "def __new__(cls):\n        return replacement()",
        "def __init__(self):\n        self.read = replacement",
    ],
)
def test_custom_factory_construction_stays_explicitly_unresolved(
    constructor: str,
) -> None:
    state = RuleRunState()
    analyze(
        program(
            {
                "server.py": (
                    "class Reader:\n    " + constructor + "\n"
                    "    def read(self, path):\n        return open('/fixed')\n"
                    "def factory():\n    return Reader()\n"
                    "@mcp.tool()\ndef read(path):\n    reader = factory()\n"
                    "    return reader.read(path)\n"
                )
            }
        ),
        state,
    )
    assert not state.matches
    assert any("custom construction" in warning.message for warning in state.warnings)


@pytest.mark.parametrize(
    "mutation",
    [
        "mcp.run = unknown",
        "alias = mcp\nalias.run = unknown",
        "setattr(mcp, 'run', unknown)",
        "del mcp.run",
    ],
)
def test_replaced_launch_cannot_establish_configured_globals(mutation: str) -> None:
    source = (
        "from mcp.server.fastmcp import FastMCP\nmcp = FastMCP('test')\n"
        "ROOT = None\n@mcp.tool()\ndef read(path):\n"
        "    if ROOT is None: return open(path)\n"
        "    return open('/srv/data/fixed')\n" + mutation + "\n"
        "def configured():\n    global ROOT\n    ROOT = '/srv/data'\n"
        "    mcp.run(transport='streamable-http')\n"
    )
    state = RuleRunState()
    analyze(program({"server.py": source}), state)
    assert state.matches
    assert any("launch" in warning.message for warning in state.warnings)


@pytest.mark.parametrize(
    ("wrapper", "expected"),
    [
        ("return func(*args, **kwargs)", 1),
        ("kwargs['path'] = '/srv/fixed'\n        return func(**kwargs)", 0),
        ("return '/srv/fixed'", 0),
        ("func = unknown\n        return func(*args, **kwargs)", 0),
        ("return func(path=kwargs['path'])", 1),
    ],
)
def test_registered_handler_runs_its_included_decorator(
    wrapper: str, expected: int
) -> None:
    from sentinel.static.model import RuleRunState
    from sentinel.static.rules.sent012 import analyze
    from tests.test_python_discovery import program

    index = program(
        {
            "wrapper.py": "from functools import wraps\n"
            "def decorate(func):\n"
            "    @wraps(func)\n"
            "    def wrapped(*args, **kwargs):\n"
            "        " + wrapper + "\n"
            "    return wrapped\n",
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "from wrapper import decorate\nmcp = FastMCP('test')\n"
            "@mcp.tool()\n@decorate\ndef read(path: str):\n"
            "    return open(path).read()\n",
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == expected


@pytest.mark.parametrize(
    ("registration", "expected"), [("inner", 0), ("outer", 1), ("call", 0)]
)
def test_decorator_order_uses_the_callable_captured_at_registration(
    registration: str, expected: int
) -> None:
    from sentinel.static.model import RuleRunState
    from sentinel.static.rules.sent012 import analyze
    from tests.test_python_discovery import program

    decorators = {
        "inner": "@mcp.tool()\n@decorate",
        "outer": "@decorate\n@mcp.tool()",
        "call": "@decorate",
    }[registration]
    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "mcp = FastMCP('test')\n"
            "def decorate(func):\n"
            "    def wrapper(**kwargs): return func(path='/fixed')\n"
            "    return wrapper\n" + decorators + "\ndef read(path: str):\n"
            "    return open(path).read()\n"
            + ("mcp.add_tool(read)\n" if registration == "call" else "")
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == expected


def test_decorator_factory_keeps_each_returned_closure_separate() -> None:
    from sentinel.static.model import RuleRunState
    from sentinel.static.rules.sent012 import analyze
    from tests.test_python_discovery import program

    index = program(
        {
            "server.py": "from mcp.server.fastmcp import FastMCP\n"
            "mcp = FastMCP('test')\n"
            "def choose(forward):\n"
            "    def decorate(func):\n"
            "        def wrapper(**kwargs):\n"
            "            if forward: return func(**kwargs)\n"
            "            return func(path='/fixed')\n"
            "        return wrapper\n"
            "    return decorate\n"
            "@mcp.tool()\n@choose(False)\ndef fixed(path: str):\n"
            "    return open(path).read()\n"
            "@mcp.tool()\n@choose(True)\ndef vulnerable(path: str):\n"
            "    return open(path).read()\n"
        }
    )
    state = RuleRunState()
    analyze(index, state)
    assert len(state.matches) == 1
    assert state.matches[0].range.start_line == 17
