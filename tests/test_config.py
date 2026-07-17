"""Configuration precedence and target-boundary tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from sentinel.config import (
    OutputFormat,
    TargetConfig,
    infer_python_version,
    load_configuration,
)
from sentinel.errors import UsageError
from tests.conftest import make_target


def test_defaults_and_framework_metadata_are_loaded(target_root: Path) -> None:
    loaded = load_configuration(target_root, environ={})
    assert loaded.scanner.scanner.format is OutputFormat.CONSOLE
    assert loaded.scanner.scanner.max_findings_per_scan == 500
    assert loaded.scanner.scanner.rules == ()
    assert loaded.target is not None
    assert loaded.target.python_version == "3.11"


def test_precedence_and_list_replacement(tmp_path: Path) -> None:
    target = make_target(
        tmp_path / "target",
        scanner_toml="""\
[scanner]
format = "sarif"
rules = ["SENT-001", "-SENT-007"]
max_findings_per_scan = 10
""",
    )
    loaded = load_configuration(
        target,
        environ={
            "SENTINEL_FORMAT": "json",
            "SENTINEL_RULES": "SENT-002",
            "SENTINEL_MAX_FINDINGS": "20",
            "SENTINEL_UNKNOWN": "ignored",
        },
        cli_overrides={"format": OutputFormat.CONSOLE, "rules": ("SENT-003",)},
    )
    assert loaded.scanner.scanner.format is OutputFormat.CONSOLE
    assert loaded.scanner.scanner.rules == ("SENT-003",)
    assert loaded.scanner.scanner.max_findings_per_scan == 20


def test_unknown_file_key_and_invalid_env_list_fail(tmp_path: Path) -> None:
    target = make_target(
        tmp_path / "target", scanner_toml="[scanner]\nunknown = true\n"
    )
    with pytest.raises(UsageError, match="invalid scanner"):
        load_configuration(target, environ={})

    target = make_target(tmp_path / "other")
    with pytest.raises(UsageError, match="empty list"):
        load_configuration(target, environ={"SENTINEL_RULES": "SENT-001,"})
    with pytest.raises(UsageError, match="invalid rule token"):
        load_configuration(target, environ={"SENTINEL_RULES": "++SENT-001"})


def test_static_only_skips_target_config_but_not_framework_check(
    tmp_path: Path,
) -> None:
    target = make_target(tmp_path / "target", target_yaml="")
    loaded = load_configuration(target, environ={}, static_only=True)
    assert loaded.target is None
    with pytest.raises(UsageError, match=r"requires sentinel\.target\.yaml"):
        load_configuration(target, environ={})

    unsupported = make_target(tmp_path / "unsupported", dependency="requests>=2")
    with pytest.raises(UsageError, match="unsupported target"):
        load_configuration(unsupported, environ={}, static_only=True)


def test_launch_override_supplies_safe_defaults(tmp_path: Path) -> None:
    target = make_target(tmp_path / "target", target_yaml="")
    loaded = load_configuration(
        target, environ={}, target_launch_cmd="python server.py"
    )
    assert loaded.target is not None
    assert loaded.target.launch_cmd == ("python", "server.py")
    assert loaded.target.transport == "stdio"
    assert loaded.target.working_dir == "."


@pytest.mark.parametrize(
    "target_yaml",
    (
        "\n".join(
            (
                "language: python",
                "launch_cmd: [bash, -c, echo]",
                "transport: stdio",
                "working_dir: .",
            )
        ),
        "\n".join(
            (
                "language: python",
                "launch_cmd: [python, server.py]",
                "transport: http",
                "working_dir: .",
                "port: 8000",
            )
        ),
        "\n".join(
            (
                "language: python",
                "launch_cmd: [python, server.py]",
                "transport: stdio",
                "working_dir: ../",
            )
        ),
    ),
)
def test_unsafe_or_unsupported_target_config_fails(
    tmp_path: Path, target_yaml: str
) -> None:
    target = make_target(tmp_path / "target", target_yaml=target_yaml)
    with pytest.raises(UsageError):
        load_configuration(target, environ={})


@pytest.mark.parametrize(
    "name",
    ("API_KEY", "SESSION_MODE", "AUTH_LEVEL", "PASSWORD_HINT"),
)
def test_secret_shaped_environment_names_fail(tmp_path: Path, name: str) -> None:
    target = make_target(
        tmp_path / name,
        target_yaml=f"""\
language: python
launch_cmd: [python, server.py]
transport: stdio
working_dir: .
env_from: [{name}]
""",
    )
    with pytest.raises(UsageError, match="secret-shaped"):
        load_configuration(target, environ={})


@pytest.mark.parametrize(
    "value",
    (
        "Bearer abc",
        "Basic abc",
        "sk-example",
        "ghp_example",
        "AKIAEXAMPLE",
        "AIzaExample",
        "-----BEGIN PRIVATE KEY-----",
    ),
)
def test_secret_literal_values_fail(tmp_path: Path, value: str) -> None:
    target = make_target(
        tmp_path / "target",
        target_yaml=f"""\
language: python
launch_cmd: [python, server.py]
transport: stdio
working_dir: .
env:
  SAFE_NAME: {value!r}
""",
    )
    with pytest.raises(UsageError, match="prohibited"):
        load_configuration(target, environ={})


@pytest.mark.parametrize(
    "command",
    (
        ("python", "-m", "pip", "install", "-r", "requirements.txt"),
        ("poetry", "install", "--no-root"),
        ("uv", "sync", "--no-install-project", "--locked"),
    ),
)
def test_dependency_only_install_shapes_are_accepted(command: tuple[str, ...]) -> None:
    config = TargetConfig(
        language="python",
        launch_cmd=("python", "server.py"),
        install_cmd=command,
        transport="stdio",
        working_dir=".",
        python_version="3.11",
    )
    assert config.install_cmd == command


@pytest.mark.parametrize(
    "command",
    (
        ("pip", "install", "."),
        (
            "pip",
            "install",
            "--index-url",
            "https://example.invalid",
            "-r",
            "requirements.txt",
        ),
        ("poetry", "install"),
        ("uv", "sync"),
        ("npm", "install"),
    ),
)
def test_unsafe_install_shapes_are_rejected(command: tuple[str, ...]) -> None:
    with pytest.raises(ValueError):
        TargetConfig(
            language="python",
            launch_cmd=("python", "server.py"),
            install_cmd=command,
            transport="stdio",
            working_dir=".",
            python_version="3.11",
        )


def test_python_version_inference_and_symlink_rejection(tmp_path: Path) -> None:
    target = make_target(tmp_path / "target")
    assert infer_python_version(target) == "3.11"
    (target / "pyproject.toml").unlink()
    (target / ".python-version").write_text("3.12\n", encoding="utf-8")
    assert infer_python_version(target) == "3.12"

    link = tmp_path / "linked"
    os.symlink(target, link)
    with pytest.raises(UsageError, match="symbolic link"):
        load_configuration(link, environ={}, static_only=True)
