"""Configuration precedence and target-boundary tests."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from sentinel.config import (
    EndpointMode,
    LlmConfig,
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
    assert loaded.scanner.llm.model == "gpt-5.6-sol"
    assert loaded.scanner.llm.reasoning_effort.value == "medium"
    assert loaded.scanner.llm.normalized_base_url == "https://api.openai.com/v1/"
    assert loaded.scanner.llm.endpoint_mode is EndpointMode.OPENAI
    assert (
        loaded.scanner.llm.endpoint_url_hash
        == hashlib.sha256(b"https://api.openai.com/v1/").hexdigest()
    )
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
            "SENTINEL_LLM_CACHE_ENABLED": "false",
            "SENTINEL_UNKNOWN": "ignored",
        },
        cli_overrides={"format": OutputFormat.CONSOLE, "rules": ("SENT-003",)},
    )
    assert loaded.scanner.scanner.format is OutputFormat.CONSOLE
    assert loaded.scanner.scanner.rules == ("SENT-003",)
    assert loaded.scanner.scanner.max_findings_per_scan == 20
    assert loaded.scanner.llm.cache_enabled is False


def test_llm_precedence_is_independent_for_all_three_values(tmp_path: Path) -> None:
    target = make_target(
        tmp_path / "target",
        scanner_toml="""\
[llm]
model = "gpt-5.6"
reasoning_effort = "low"
base_url = "https://api.openai.com/v1"
""",
    )
    loaded = load_configuration(
        target,
        environ={
            "SENTINEL_LLM_MODEL": "environment/deployment",
            "SENTINEL_LLM_REASONING_EFFORT": "medium",
            "SENTINEL_LLM_BASE_URL": "https://environment.example/v1",
        },
        llm_cli_overrides={
            "model": "cli:deployment",
            "reasoning_effort": "low",
            "base_url": "https://CLI.EXAMPLE:443/openai/v1/",
        },
    )
    assert loaded.scanner.llm.model == "cli:deployment"
    assert loaded.scanner.llm.reasoning_effort.value == "low"
    assert loaded.scanner.llm.normalized_base_url == "https://cli.example/openai/v1/"
    assert loaded.scanner.llm.endpoint_mode is EndpointMode.COMPATIBLE


@pytest.mark.parametrize(
    ("url", "normalized", "mode"),
    (
        (
            "https://API.OPENAI.COM:443/v1",
            "https://api.openai.com/v1/",
            EndpointMode.OPENAI,
        ),
        (
            "http://localhost:8080/v1",
            "http://localhost:8080/v1/",
            EndpointMode.COMPATIBLE,
        ),
        ("http://127.1.2.3/v1/", "http://127.1.2.3/v1/", EndpointMode.COMPATIBLE),
        (
            "http://[0:0:0:0:0:0:0:1]:80/openai/v1",
            "http://[::1]/openai/v1/",
            EndpointMode.COMPATIBLE,
        ),
        (
            "https://gateway.example/Path/v1///",
            "https://gateway.example/Path/v1/",
            EndpointMode.COMPATIBLE,
        ),
    ),
)
def test_llm_url_normalization(url: str, normalized: str, mode: EndpointMode) -> None:
    config = LlmConfig(base_url=url)
    assert config.normalized_base_url == normalized
    assert config.endpoint_mode is mode
    assert url not in repr(config)
    assert "base_url" not in config.model_dump()


@pytest.mark.parametrize(
    "url",
    (
        "",
        " https://private.example/v1",
        "https://private.example/v1 ",
        "private.example/v1",
        "ftp://private.example/v1",
        "http://private.example/v1",
        "http://localhost.example/v1",
        "https://user:password@private.example/v1",
        "https://private.example/v1?api-version=1",
        "https://private.example/v1#fragment",
        "https://private.example/responses",
    ),
)
def test_invalid_llm_urls_are_rejected(url: str) -> None:
    with pytest.raises(ValueError):
        LlmConfig(base_url=url)


def test_public_model_allowlist_and_compatible_deployment_syntax() -> None:
    assert LlmConfig(model="gpt-5.6").model == "gpt-5.6"
    with pytest.raises(ValueError, match="public OpenAI"):
        LlmConfig(model="custom-deployment")
    assert (
        LlmConfig(
            model="Azure.Deployment_1:/blue",
            base_url="https://compatible.example/v1",
        ).endpoint_mode
        is EndpointMode.COMPATIBLE
    )
    with pytest.raises(ValueError, match="deployment ID"):
        LlmConfig(model="-invalid", base_url="https://compatible.example/v1")
    with pytest.raises(ValueError, match="deployment ID"):
        LlmConfig(model="a" * 129, base_url="https://compatible.example/v1")


def test_repository_endpoint_requires_only_explicit_operator_trust(
    tmp_path: Path,
) -> None:
    target = make_target(
        tmp_path / "target",
        scanner_toml='[llm]\nmodel = "deployment"\nbase_url = "https://private.example/v1"\n',
    )
    with pytest.raises(UsageError, match="requires --trust-llm-endpoint"):
        load_configuration(target, environ={})
    with pytest.raises(UsageError, match="requires --trust-llm-endpoint"):
        load_configuration(target, environ={"SENTINEL_TRUST_LLM_ENDPOINT": "false"})
    assert (
        load_configuration(
            target, environ={"SENTINEL_TRUST_LLM_ENDPOINT": "true"}
        ).scanner.llm.endpoint_mode
        is EndpointMode.COMPATIBLE
    )
    assert (
        load_configuration(
            target, environ={}, trust_llm_endpoint=True
        ).scanner.llm.endpoint_mode
        is EndpointMode.COMPATIBLE
    )


def test_environment_and_cli_endpoints_are_implicitly_trusted(tmp_path: Path) -> None:
    target = make_target(tmp_path / "target")
    environment = load_configuration(
        target,
        environ={
            "SENTINEL_LLM_MODEL": "environment-deployment",
            "SENTINEL_LLM_BASE_URL": "https://environment.example/v1",
        },
    )
    cli = load_configuration(
        target,
        environ={},
        llm_cli_overrides={
            "model": "cli-deployment",
            "base_url": "https://cli.example/v1",
        },
    )
    assert environment.scanner.llm.model == "environment-deployment"
    assert cli.scanner.llm.model == "cli-deployment"


@pytest.mark.parametrize(
    "environ",
    (
        {"SENTINEL_TRUST_LLM_ENDPOINT": "true"},
        {"SENTINEL_TRUST_LLM_ENDPOINT": " true"},
        {"SENTINEL_TRUST_LLM_ENDPOINT": ""},
    ),
)
def test_unused_or_malformed_endpoint_trust_is_rejected(
    target_root: Path, environ: dict[str, str]
) -> None:
    with pytest.raises(UsageError, match=r"trust|must be true"):
        load_configuration(target_root, environ=environ)


@pytest.mark.parametrize("name", ("OPENAI_BASE_URL", "OPENAI_CUSTOM_HEADERS"))
def test_ambient_sdk_routing_is_rejected(target_root: Path, name: str) -> None:
    with pytest.raises(UsageError, match=name):
        load_configuration(target_root, environ={name: "https://private.example/v1"})


def test_invalid_private_url_is_redacted_from_configuration_errors(
    tmp_path: Path,
) -> None:
    private = "http://private.internal/v1"
    target = make_target(
        tmp_path / "target",
        scanner_toml=f'[llm]\nmodel = "deployment"\nbase_url = "{private}"\n',
    )
    with pytest.raises(UsageError) as captured:
        load_configuration(target, environ={})
    assert private not in str(captured.value)
    assert "[REDACTED_LLM_ENDPOINT]" in str(captured.value)


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
    with pytest.raises(UsageError, match="must be true"):
        load_configuration(target, environ={"SENTINEL_LLM_CACHE_ENABLED": "sometimes"})


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
        ("pip", "install", "--requirement", "requirements.txt"),
    ),
)
def test_dependency_only_pip_install_shapes_are_accepted(
    command: tuple[str, ...],
) -> None:
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
        ("poetry", "install", "--no-root"),
        ("uv", "sync", "--no-install-project", "--locked"),
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
