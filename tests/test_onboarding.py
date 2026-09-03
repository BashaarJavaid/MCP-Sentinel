"""First-run onboarding tests."""

from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from sentinel.cli import app
from sentinel.config import TargetConfig, load_configuration
from sentinel.errors import InfrastructureError
from sentinel.onboarding import initialize_repository, next_scan_command
from sentinel.permissions import PermissionsManifest, validate_permission_scopes

FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()

SERVER = """\
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("test")

@mcp.tool()
def zebra(value: str) -> str:
    return value

@mcp.tool()
def alpha(value: str) -> str:
    return value

if __name__ == "__main__":
    mcp.run()
"""


def _project(
    root: Path,
    *,
    source: str = SERVER,
    pyproject: str | None = None,
    requirements: str | None = None,
) -> Path:
    root.mkdir()
    (root / "server.py").write_text(source, encoding="utf-8")
    if pyproject is None:
        pyproject = """\
[project]
name = "onboarding-test"
version = "0.0.0"
requires-python = ">=3.10,<3.13"
dependencies = ["mcp>=1,<2"]
"""
    if pyproject:
        (root / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    if requirements is not None:
        (root / "requirements.txt").write_text(requirements, encoding="utf-8")
    return root


@pytest.mark.parametrize(
    ("fixture", "has_install"),
    (("clean_server", False), ("vulnerable_server", True)),
)
def test_init_generates_model_valid_fixture_configuration(
    tmp_path: Path, fixture: str, has_install: bool
) -> None:
    root = tmp_path / fixture
    shutil.copytree(FIXTURES / fixture, root)
    (root / "sentinel.target.yaml").unlink()
    (root / "sentinel.permissions.yaml").unlink()

    result = runner.invoke(app, ["init", str(root)])

    assert result.exit_code == 0
    assert result.stdout == (
        f"Created: {root / 'sentinel.target.yaml'}\n"
        f"Created: {root / 'sentinel.permissions.yaml'}\n"
        f"Next: sentinel scan {root}\n"
    )
    loaded = load_configuration(root, environ={})
    assert loaded.target is not None
    assert (loaded.target.install_cmd is not None) is has_install
    if fixture == "clean_server":
        scan = runner.invoke(app, ["scan", str(root), "--static-only", "--json"])
        assert scan.exit_code == 0
        assert scan.stderr == ""
    permissions_data = yaml.safe_load(
        (root / "sentinel.permissions.yaml").read_text(encoding="utf-8")
    )
    permissions = PermissionsManifest.model_validate(permissions_data)
    validate_permission_scopes(permissions)
    assert list(permissions.tools) == sorted(permissions.tools)
    for tool in permissions.tools.values():
        assert tool.filesystem.read.scopes == ()
        assert tool.filesystem.write.scopes == ()
        assert tool.network.scopes == ()
    assert (
        "broad_scope_justification"
        not in permissions_data["tools"][next(iter(permissions.tools))]["filesystem"][
            "read"
        ]
    )


def test_init_accepts_fastmcp_alias_and_reversed_guard_without_execution(
    tmp_path: Path,
) -> None:
    source = """\
from pathlib import Path
from fastmcp import FastMCP as Application

Path("executed").write_text("bad")
server = Application("test")

@server.tool()
def hello(name: str) -> str:
    return name

if "__main__" == __name__:
    server.run()
"""
    root = _project(
        tmp_path / "fastmcp",
        source=source,
        pyproject="""\
[project]
name = "fastmcp-test"
version = "0"
dependencies = ["fastmcp>=2"]
""",
    )

    result = runner.invoke(app, ["init", str(root)])

    assert result.exit_code == 0
    assert not (root / "executed").exists()
    target = TargetConfig.model_validate(
        yaml.safe_load((root / "sentinel.target.yaml").read_text(encoding="utf-8"))
    )
    assert target.launch_cmd == ("python", "server.py")


@pytest.mark.parametrize(
    ("pyproject", "requirements", "message"),
    (
        ("", None, "missing requirements.txt or pyproject.toml"),
        (None, "requests>=2\n", "requirements.txt must declare"),
        (None, "not a valid requirement !!!\n", "invalid requirement"),
        (None, "mcp @ https://example.test/mcp.whl\n", "unsupported direct URL"),
        (None, "-r requirements/base.txt\n", "unsupported pip directive"),
        (None, "mcp>=1 \\\nmcp<2\n", "unsupported continuation"),
        (None, "git+https://example.test/mcp.git\n", "invalid requirement"),
        (
            """\
[project]
name = "url-test"
version = "0"
dependencies = ["mcp @ https://example.test/mcp.whl"]
""",
            None,
            "unsupported direct URL",
        ),
        (
            """\
[tool.poetry]
name = "poetry-test"
version = "0"
[tool.poetry.dependencies]
mcp = "^1"
""",
            None,
            "Poetry-only",
        ),
        (
            """\
[project]
name = "optional-test"
version = "0"
[project.optional-dependencies]
mcp = ["mcp>=1"]
""",
            None,
            "optional dependency groups",
        ),
        (
            """\
[project]
name = "mismatch"
version = "0"
dependencies = ["requests>=2"]
""",
            None,
            "must declare the official",
        ),
    ),
)
def test_init_rejects_unsupported_dependency_layouts(
    tmp_path: Path,
    pyproject: str | None,
    requirements: str | None,
    message: str,
) -> None:
    root = _project(tmp_path / "target", pyproject=pyproject, requirements=requirements)

    result = runner.invoke(app, ["init", str(root)])

    assert result.exit_code == 2
    assert message in result.stderr
    assert not (root / "sentinel.target.yaml").exists()
    assert not (root / "sentinel.permissions.yaml").exists()


def test_requirements_is_preferred_and_nested_requirements_are_rejected(
    tmp_path: Path,
) -> None:
    preferred = _project(tmp_path / "preferred", requirements="requests>=2\n")
    result = runner.invoke(app, ["init", str(preferred)])
    assert result.exit_code == 2
    assert "requirements.txt must declare" in result.stderr

    nested = _project(tmp_path / "nested", pyproject="")
    (nested / "requirements").mkdir()
    (nested / "requirements" / "base.txt").write_text("mcp>=1\n", encoding="utf-8")
    result = runner.invoke(app, ["init", str(nested)])
    assert result.exit_code == 2
    assert "nested requirements files are unsupported" in result.stderr


@pytest.mark.parametrize(
    ("sources", "message"),
    (
        ({"server.py": "print('no server')\n"}, "could not detect"),
        (
            {"server.py": SERVER, "other.py": SERVER},
            "multiple MCP entry points detected: other.py, server.py",
        ),
        (
            {
                "server.py": SERVER.replace(
                    "from mcp.server.fastmcp import FastMCP",
                    "from fastmcp import FastMCP",
                )
            },
            "could not detect",
        ),
    ),
)
def test_init_rejects_missing_ambiguous_or_mismatched_entry_points(
    tmp_path: Path, sources: dict[str, str], message: str
) -> None:
    root = _project(tmp_path / "target", source=sources.pop("server.py"))
    for name, source in sources.items():
        (root / name).write_text(source, encoding="utf-8")

    result = runner.invoke(app, ["init", str(root)])

    assert result.exit_code == 2
    assert message in result.stderr


def test_gitignore_and_project_ignore_paths_remove_entry_candidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _project(tmp_path / "target")
    (root / "ignored.py").write_text(SERVER, encoding="utf-8")
    (root / "configured.py").write_text(SERVER, encoding="utf-8")
    (root / ".gitignore").write_text("ignored.py\n", encoding="utf-8")
    (root / "sentinel.toml").write_text(
        '[scanner]\nignore_paths = ["configured.py"]\n', encoding="utf-8"
    )
    monkeypatch.setenv("SENTINEL_IGNORE_PATHS", "server.py")

    result = runner.invoke(app, ["init", str(root)])

    assert result.exit_code == 0


def test_malformed_unrelated_configuration_stops_before_writes(tmp_path: Path) -> None:
    root = _project(tmp_path / "target")
    (root / "unrelated.json").write_text("{broken", encoding="utf-8")

    result = runner.invoke(app, ["init", str(root)])

    assert result.exit_code == 2
    assert "cannot parse configuration unrelated.json" in result.stderr
    assert not (root / "sentinel.target.yaml").exists()
    assert not (root / "sentinel.permissions.yaml").exists()


def test_empty_and_duplicate_catalog_warnings(tmp_path: Path) -> None:
    empty = _project(tmp_path / "empty", source=SERVER.replace("@mcp.tool()", "", 2))
    result = runner.invoke(app, ["init", str(empty)])
    assert result.exit_code == 0
    assert "warning: No MCP tools were discovered" in result.stderr
    assert (
        yaml.safe_load(
            (empty / "sentinel.permissions.yaml").read_text(encoding="utf-8")
        )["tools"]
        == {}
    )

    duplicate = _project(tmp_path / "duplicate")
    (duplicate / "second.py").write_text(
        SERVER.replace('if __name__ == "__main__":', "if False:"),
        encoding="utf-8",
    )
    result = runner.invoke(app, ["init", str(duplicate)])
    assert result.exit_code == 0
    assert (
        "warning: Tool 'alpha' is declared at multiple source locations"
        in result.stderr
    )
    manifest = yaml.safe_load(
        (duplicate / "sentinel.permissions.yaml").read_text(encoding="utf-8")
    )
    assert list(manifest["tools"]) == ["alpha", "zebra"]


def test_overwrite_refusal_force_repair_and_identical_preservation(
    tmp_path: Path,
) -> None:
    root = _project(tmp_path / "target")
    created = runner.invoke(app, ["init", str(root)])
    assert created.exit_code == 0
    target = root / "sentinel.target.yaml"
    permissions = root / "sentinel.permissions.yaml"
    original = (target.read_bytes(), permissions.read_bytes())

    (root / "server.py").write_text("invalid python !!!", encoding="utf-8")
    refused = runner.invoke(app, ["init", str(root)])
    assert refused.exit_code == 2
    assert "use --force" in refused.stderr
    assert (target.read_bytes(), permissions.read_bytes()) == original

    (root / "server.py").write_text(SERVER, encoding="utf-8")
    target.write_text("not: [valid", encoding="utf-8")
    permissions.write_text("also: [bad", encoding="utf-8")
    if os.name != "nt":
        target.chmod(0o640)
        permissions.chmod(0o600)
    repaired = runner.invoke(app, ["init", str(root), "--force"])
    assert repaired.exit_code == 0
    assert repaired.stdout == (
        f"Updated: {target}\nUpdated: {permissions}\nNext: sentinel scan {root}\n"
    )
    modes = tuple(stat.S_IMODE(path.stat().st_mode) for path in (target, permissions))
    metadata = tuple(path.stat() for path in (target, permissions))

    unchanged = runner.invoke(app, ["init", str(root), "--force"])
    assert unchanged.exit_code == 0
    assert unchanged.stdout == (
        f"Unchanged: {target}\nUnchanged: {permissions}\nNext: sentinel scan {root}\n"
    )
    assert (
        tuple(stat.S_IMODE(path.stat().st_mode) for path in (target, permissions))
        == modes
    )
    assert tuple(path.stat().st_ino for path in (target, permissions)) == tuple(
        item.st_ino for item in metadata
    )


def test_force_refuses_non_regular_destinations(tmp_path: Path) -> None:
    directory_root = _project(tmp_path / "directory")
    (directory_root / "sentinel.target.yaml").mkdir()
    result = runner.invoke(app, ["init", str(directory_root), "--force"])
    assert result.exit_code == 2
    assert "must be a regular file" in result.stderr

    if os.name != "nt":
        symlink_root = _project(tmp_path / "symlink")
        (symlink_root / "sentinel.target.yaml").symlink_to("missing")
        result = runner.invoke(app, ["init", str(symlink_root), "--force"])
        assert result.exit_code == 2
        assert "must be a regular file" in result.stderr

        fifo_root = _project(tmp_path / "fifo")
        os.mkfifo(fifo_root / "sentinel.target.yaml")
        result = runner.invoke(app, ["init", str(fifo_root), "--force"])
        assert result.exit_code == 2
        assert "must be a regular file" in result.stderr


def test_second_replace_failure_rolls_back_both_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _project(tmp_path / "target")
    target = root / "sentinel.target.yaml"
    permissions = root / "sentinel.permissions.yaml"
    target.write_bytes(b"old target\n")
    permissions.write_bytes(b"old permissions\n")
    if os.name != "nt":
        target.chmod(0o640)
        permissions.chmod(0o600)
    before = tuple(
        (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
        for path in (target, permissions)
    )
    real_replace = os.replace
    calls = 0

    def fail_second(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected second replacement failure")
        real_replace(source, destination)

    monkeypatch.setattr("sentinel.onboarding.os.replace", fail_second)

    result = runner.invoke(app, ["init", str(root), "--force"])

    assert result.exit_code == 3
    assert result.stderr.startswith("infrastructure error: configuration transaction")

    after = tuple(
        (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
        for path in (target, permissions)
    )
    assert after == before


def test_second_replace_failure_removes_new_peer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _project(tmp_path / "target")
    real_replace = os.replace
    calls = 0

    def fail_second(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected second replacement failure")
        real_replace(source, destination)

    monkeypatch.setattr("sentinel.onboarding.os.replace", fail_second)

    with pytest.raises(InfrastructureError, match="configuration transaction failed"):
        initialize_repository(root, force=False)

    assert not (root / "sentinel.target.yaml").exists()
    assert not (root / "sentinel.permissions.yaml").exists()


def test_default_path_output_quoting_and_debug_behavior(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _project(tmp_path / "path with spaces")
    result = runner.invoke(app, ["init", str(root)])
    assert result.exit_code == 0
    if os.name == "nt":
        assert result.stdout.endswith(f'Next: sentinel scan "{root}"\n')
    else:
        assert result.stdout.endswith(f"Next: sentinel scan '{root}'\n")

    monkeypatch.setattr(
        "sentinel.cli.initialize_repository",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("synthetic init")),
    )
    concise = runner.invoke(app, ["init", str(root), "--force"])
    assert concise.exit_code == 3
    assert "Traceback" not in concise.stderr
    debug = runner.invoke(app, ["--debug", "init", str(root), "--force"])
    assert debug.exit_code == 3
    assert "Traceback" in debug.stderr
    assert next_scan_command(".") == "sentinel scan ."
