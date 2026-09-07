"""Containment checks must protect the actual value before its filesystem use."""

from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import load_configuration
from sentinel.static.engine import run_static_scan
from sentinel.static.model import RuleRunState
from sentinel.static.rules.sent012 import analyze
from tests.conftest import NOW, make_target
from tests.test_python_discovery import program


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
    assert any(
        warning.code == "static_review_context_incomplete"
        for warning in result.warnings
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
