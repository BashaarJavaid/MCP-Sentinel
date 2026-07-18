"""Unit coverage for the Docker isolation boundary."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.config import LoadedConfiguration, load_configuration
from sentinel.dynamic.sandbox import (
    CREATED_LABEL,
    DockerSandbox,
    _dependency_inputs,
    _offline_dockerfile,
    _run_command,
    _squid_configuration,
    reap_orphans,
)
from sentinel.errors import InfrastructureError
from tests.conftest import make_target


class RecordingRunner:
    def __init__(self, *, image_exists: bool = False) -> None:
        self.calls: list[tuple[str, ...]] = []
        self.image_exists = image_exists

    def __call__(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        normalized = tuple(command)
        self.calls.append(normalized)
        if normalized[1:3] == ("image", "inspect"):
            return _completed(normalized, 0 if self.image_exists else 1)
        if normalized[1:2] == ("inspect",):
            return _completed(normalized, stdout="true\n")
        return _completed(normalized)


def _completed(
    command: Sequence[str],
    returncode: int = 0,
    *,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(command, returncode, stdout, stderr)


def test_dependency_image_build_is_proxied_then_offline(tmp_path: Path) -> None:
    root = make_target(tmp_path / "target", dependency="mcp==1.23.3")
    configuration = load_configuration(root, environ={})
    runner = RecordingRunner()
    sandbox = DockerSandbox(configuration, uuid4(), runner=runner, now=lambda: 10)

    image = sandbox.prepare_dependency_image()

    assert image.cache_hit is False
    assert image.reference == f"mcp-sentinel-deps:{image.cache_key}"
    commands = runner.calls
    wheel = next(call for call in commands if "wheel" in call)
    assert "--network" in wheel
    assert "HTTP_PROXY=http://sentinel-proxy-" in " ".join(wheel)
    build = next(call for call in commands if call[1:3] == ("buildx", "build"))
    assert build[build.index("--network") + 1] == "none"
    assert commands[-2][1:3] == ("rm", "--force")
    assert commands[-1][1:3] == ("network", "rm")


def test_dependency_image_cache_hit_skips_build(tmp_path: Path) -> None:
    root = make_target(tmp_path / "target")
    configuration = load_configuration(root, environ={})
    runner = RecordingRunner(image_exists=True)

    image = DockerSandbox(
        configuration, uuid4(), runner=runner
    ).prepare_dependency_image()

    assert image.cache_hit is True
    assert len(runner.calls) == 1


def test_missing_docker_binary_is_an_infrastructure_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing_docker(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise FileNotFoundError("docker")

    monkeypatch.setattr(subprocess, "run", missing_docker)

    with pytest.raises(InfrastructureError, match="cannot execute Docker"):
        _run_command(("docker", "version"))


def test_dependency_build_failure_still_cleans_build_resources(
    tmp_path: Path,
) -> None:
    root = make_target(tmp_path / "target", dependency="mcp==1.23.3")
    configuration = load_configuration(root, environ={})

    class FailingRunner(RecordingRunner):
        def __call__(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
            result = super().__call__(command)
            if "wheel" in command:
                return _completed(command, 1, stderr="wheel build failed")
            return result

    runner = FailingRunner()

    with pytest.raises(InfrastructureError, match="wheel build failed"):
        DockerSandbox(configuration, uuid4(), runner=runner).prepare_dependency_image()

    assert runner.calls[-2][1:3] == ("rm", "--force")
    assert runner.calls[-1][1:3] == ("network", "rm")


def test_dependency_build_cleanup_failure_is_not_silent(tmp_path: Path) -> None:
    root = make_target(tmp_path / "target", dependency="mcp==1.23.3")
    configuration = load_configuration(root, environ={})

    class CleanupFailureRunner(RecordingRunner):
        def __call__(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
            result = super().__call__(command)
            if tuple(command)[1:3] == ("network", "rm"):
                return _completed(command, 1, stderr="network is still in use")
            return result

    with pytest.raises(InfrastructureError, match="clean dependency-build network"):
        DockerSandbox(
            configuration,
            uuid4(),
            runner=CleanupFailureRunner(),
        ).prepare_dependency_image()


def test_dependency_inputs_hash_declared_files_and_support_requirements(
    tmp_path: Path,
) -> None:
    target_yaml = """\
language: python
launch_cmd: [python, server.py]
install_cmd: [python, -m, pip, install, -r, requirements.txt]
transport: stdio
working_dir: .
env: {}
env_from: []
"""
    root = make_target(tmp_path / "target", target_yaml=target_yaml)
    (root / "requirements.txt").write_text(
        "# pinned\nmcp==1.23.3\n\n", encoding="utf-8"
    )
    configuration = load_configuration(root, environ={})

    first, files, requirements = _dependency_inputs(configuration)
    (root / "requirements.txt").write_text("mcp==1.23.2\n", encoding="utf-8")
    second, _, _ = _dependency_inputs(configuration)

    assert first != second
    assert files == (root / "requirements.txt",)
    assert requirements == ("mcp==1.23.3",)


def test_runtime_arguments_enforce_isolation_and_explicit_environment(
    loaded_config: LoadedConfiguration,
) -> None:
    sandbox = DockerSandbox(loaded_config, uuid4(), now=lambda: 20)

    args = sandbox._probe_run_args("deps:test", "probe", "SENT-009")

    joined = " ".join(args)
    assert "--network none" in joined
    assert "--read-only" in args
    assert "no-new-privileges" in args
    assert "--pids-limit 64" in joined
    assert "--cpus 1" in joined
    assert "--memory 512m" in joined
    assert f"{loaded_config.scan_root}:/workspace:ro" in args
    assert "LOG_LEVEL=debug" in args
    assert args[-3:] == ("deps:test", "python", "server.py")


def test_proxy_allowlist_denies_ip_literals_and_everything_else() -> None:
    config = _squid_configuration(("pypi.org", "files.pythonhosted.org"))
    assert "acl allowed_registries dstdomain pypi.org files.pythonhosted.org" in config
    assert config.index("http_access deny ip_literal") < config.index(
        "http_access allow allowed_registries"
    )
    assert config.rstrip().endswith("cache deny all")
    dockerfile = _offline_dockerfile("python@sha256:test")
    assert "--no-index" in dockerfile
    assert "--find-links=/wheelhouse" in dockerfile


def test_reaper_removes_only_stale_labeled_containers() -> None:
    calls: list[tuple[str, ...]] = []

    def runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        normalized = tuple(command)
        calls.append(normalized)
        if normalized[1:3] == ("ps", "--all"):
            return _completed(normalized, stdout="old\nnew\n")
        if normalized[1:2] == ("inspect",):
            created = "1\n" if normalized[-1] == "old" else "190\n"
            return _completed(normalized, stdout=created)
        return _completed(normalized)

    reap_orphans(runner=runner, now=lambda: 200)

    assert ("docker", "rm", "--force", "old") in calls
    assert ("docker", "rm", "--force", "new") not in calls
    assert CREATED_LABEL in " ".join(calls[1])


def test_reaper_fails_closed_on_invalid_creation_label() -> None:
    def runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        normalized = tuple(command)
        if normalized[1:3] == ("ps", "--all"):
            return _completed(normalized, stdout="broken\n")
        return _completed(normalized, stdout="not-an-integer\n")

    with pytest.raises(InfrastructureError, match="invalid creation label"):
        reap_orphans(runner=runner)
