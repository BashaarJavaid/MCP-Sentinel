"""Docker image preparation and isolated MCP stdio probe sessions."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import AsyncIterator, Callable, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO, cast
from uuid import UUID

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from sentinel import __version__
from sentinel.config import LoadedConfiguration, TargetConfig
from sentinel.errors import ConfigurationError, InfrastructureError

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - Python 3.10 CI
    import tomli as tomllib

OWNER_LABEL = "com.securemcp.sentinel"
SCAN_LABEL = f"{OWNER_LABEL}.scan_id"
ROLE_LABEL = f"{OWNER_LABEL}.role"
CREATED_LABEL = f"{OWNER_LABEL}.created_at"
ORPHAN_AGE_SECONDS = 120
PROBE_TIMEOUT_SECONDS = 10
PASS_TIMEOUT_SECONDS = 120
SCRATCH_PATH = "/sentinel-scratch"
CANARY_PATH = f"{SCRATCH_PATH}/sent-010-canary"
SQUID_IMAGE = (
    "ubuntu/squid@sha256:"
    "6a097f68bae708cedbabd6188d68c7e2e7a38cedd05a176e1cc0ba29e3bbe029"
)
PYTHON_IMAGES = {
    "3.10": (
        "python@sha256:c1e4e6c01eb489c422288b2de34b0761ca316f7a2d98e2c33f47659a73ed108a"
    ),
    "3.11": (
        "python@sha256:db3ff2e1800a8581e2c48a27c3995339d47bdf046da21c7627accd3d51053a93"
    ),
    "3.12": (
        "python@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de"
    ),
}

CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class DependencyImage:
    reference: str
    cache_key: str
    cache_hit: bool


@dataclass
class ProbeSession:
    client: ClientSession
    container_name: str
    stderr: TextIO
    sandbox: DockerSandbox

    def canary_exists(self) -> bool:
        result = self.sandbox.docker(
            ("exec", self.container_name, "test", "-f", CANARY_PATH),
            check=False,
        )
        return result.returncode == 0

    def logs(self) -> tuple[str, ...]:
        self.stderr.flush()
        self.stderr.seek(0)
        return tuple(self.stderr.read().splitlines()[-50:])


class DockerSandbox:
    """Own all Docker lifecycle operations for one scan."""

    def __init__(
        self,
        configuration: LoadedConfiguration,
        scan_id: UUID,
        *,
        runner: CommandRunner | None = None,
        now: Callable[[], float] = time.time,
    ) -> None:
        if configuration.target is None:
            raise ValueError("dynamic sandbox requires target configuration")
        self.configuration = configuration
        self.scan_id = scan_id
        self.runner = runner or _run_command
        self.now = now

    @property
    def target(self) -> TargetConfig:
        target = self.configuration.target
        if target is None:  # pragma: no cover - guarded by __init__
            raise ValueError("dynamic sandbox requires target configuration")
        return target

    def docker(
        self, args: Sequence[str], *, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        result = self.runner(("docker", *args))
        if check and result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise InfrastructureError(f"Docker command failed: {detail}")
        return result

    def preflight(self) -> None:
        self.docker(("version", "--format", "{{.Server.Version}}"))

    def prepare_dependency_image(self) -> DependencyImage:
        cache_key, dependency_files, requirements = _dependency_inputs(
            self.configuration
        )
        reference = f"mcp-sentinel-deps:{cache_key}"
        existing = self.docker(("image", "inspect", reference), check=False)
        if existing.returncode == 0:
            return DependencyImage(reference, cache_key, True)
        self._build_dependency_image(reference, dependency_files, requirements)
        return DependencyImage(reference, cache_key, False)

    def _build_dependency_image(
        self,
        reference: str,
        dependency_files: tuple[Path, ...],
        requirements: tuple[str, ...],
    ) -> None:
        token = str(self.scan_id).replace("-", "")[:12]
        network = f"sentinel-build-{token}"
        proxy = f"sentinel-proxy-{token}"
        created = str(int(self.now()))
        with tempfile.TemporaryDirectory(prefix="sentinel-deps-") as directory:
            root = Path(directory)
            inputs = root / "inputs"
            wheelhouse = root / "wheelhouse"
            context = root / "context"
            inputs.mkdir()
            wheelhouse.mkdir()
            context.mkdir()
            for path in dependency_files:
                shutil.copy2(path, inputs / path.name)
            requirement_file = inputs / "sentinel-requirements.txt"
            requirement_file.write_text(
                "\n".join(requirements) + "\n", encoding="utf-8"
            )
            squid_config = root / "squid.conf"
            squid_config.write_text(
                _squid_configuration(
                    self.configuration.scanner.sandbox.allowed_registries
                ),
                encoding="utf-8",
            )
            try:
                self.docker(
                    (
                        "network",
                        "create",
                        "--internal",
                        "--label",
                        f"{OWNER_LABEL}=true",
                        "--label",
                        f"{SCAN_LABEL}={self.scan_id}",
                        network,
                    )
                )
                self.docker(
                    (
                        "run",
                        "--detach",
                        "--name",
                        proxy,
                        "--network",
                        network,
                        "--label",
                        f"{OWNER_LABEL}=true",
                        "--label",
                        f"{SCAN_LABEL}={self.scan_id}",
                        "--label",
                        f"{ROLE_LABEL}=proxy",
                        "--label",
                        f"{CREATED_LABEL}={created}",
                        "--volume",
                        f"{squid_config}:/etc/squid/squid.conf:ro",
                        SQUID_IMAGE,
                        "-f",
                        "/etc/squid/squid.conf",
                        "-NYCd1",
                    )
                )
                self.docker(("network", "connect", "bridge", proxy))
                self._wait_for_proxy(proxy)
                base = PYTHON_IMAGES[self.target.python_version]
                self.docker(
                    (
                        "run",
                        "--rm",
                        "--network",
                        network,
                        "--env",
                        f"HTTP_PROXY=http://{proxy}:3128",
                        "--env",
                        f"HTTPS_PROXY=http://{proxy}:3128",
                        "--env",
                        "NO_PROXY=",
                        "--volume",
                        f"{inputs}:/dependency-inputs:ro",
                        "--volume",
                        f"{wheelhouse}:/wheelhouse",
                        base,
                        "python",
                        "-m",
                        "pip",
                        "wheel",
                        "--disable-pip-version-check",
                        "--wheel-dir",
                        "/wheelhouse",
                        "--requirement",
                        "/dependency-inputs/sentinel-requirements.txt",
                    )
                )
                shutil.copytree(wheelhouse, context / "wheelhouse")
                shutil.copy2(requirement_file, context / "requirements.txt")
                (context / "Dockerfile").write_text(
                    _offline_dockerfile(base), encoding="utf-8"
                )
                self.docker(
                    (
                        "buildx",
                        "build",
                        "--network",
                        "none",
                        "--load",
                        "--tag",
                        reference,
                        str(context),
                    )
                )
            finally:
                self.docker(("rm", "--force", proxy), check=False)
                removed = self.docker(("network", "rm", network), check=False)
                if removed.returncode != 0:
                    raise InfrastructureError(
                        "failed to clean dependency-build network"
                    )

    def _wait_for_proxy(self, name: str) -> None:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            state = self.docker(
                ("inspect", "--format", "{{.State.Running}}", name),
                check=False,
            )
            if state.returncode == 0 and state.stdout.strip() == "true":
                checked = self.docker(
                    ("exec", name, "squid", "-k", "check"), check=False
                )
                if checked.returncode == 0:
                    return
            time.sleep(0.2)
        logs = self.docker(("logs", name), check=False)
        detail = (logs.stderr or logs.stdout).strip()
        raise InfrastructureError(f"dependency proxy failed to start: {detail}")

    @asynccontextmanager
    async def probe_session(
        self, image: str, probe_id: str
    ) -> AsyncIterator[ProbeSession]:
        suffix = probe_id.removeprefix("SENT-").lower()
        token = str(self.scan_id).replace("-", "")[:12]
        name = f"sentinel-probe-{token}-{suffix}"
        with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as stderr:
            errlog = cast(TextIO, stderr)
            parameters = StdioServerParameters(
                command="docker",
                args=list(self._probe_run_args(image, name, probe_id)),
                env=None,
            )
            try:
                async with (
                    stdio_client(parameters, errlog=errlog) as (read, write),
                    ClientSession(read, write) as client,
                ):
                    await client.initialize()
                    yield ProbeSession(client, name, errlog, self)
            except BaseException as error:
                if isinstance(error, asyncio.CancelledError):
                    raise
                stderr.flush()
                stderr.seek(0)
                detail = "\n".join(stderr.read().splitlines()[-50:]).strip()
                raise InfrastructureError(
                    f"probe container {name} failed: {detail or error}"
                ) from error
            finally:
                cleanup = self.docker(("rm", "--force", name), check=False)
                if cleanup.returncode not in {0, 1}:
                    raise InfrastructureError(f"failed to clean probe container {name}")

    def _probe_run_args(self, image: str, name: str, probe_id: str) -> tuple[str, ...]:
        target = self.target
        workdir = "/workspace"
        if target.working_dir != ".":
            workdir = f"{workdir}/{target.working_dir}"
        args = [
            "run",
            "--rm",
            "--interactive",
            "--name",
            name,
            "--label",
            f"{OWNER_LABEL}=true",
            "--label",
            f"{SCAN_LABEL}={self.scan_id}",
            "--label",
            f"{ROLE_LABEL}=probe",
            "--label",
            f"{CREATED_LABEL}={int(self.now())}",
            "--network",
            "none",
            "--read-only",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            "64",
            "--cpus",
            "1",
            "--memory",
            "512m",
            "--tmpfs",
            f"{SCRATCH_PATH}:rw,noexec,nosuid,nodev,size=64m",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,nodev,size=64m",
            "--volume",
            f"{self.configuration.scan_root}:/workspace:ro",
            "--workdir",
            workdir,
            "--env",
            "PYTHONDONTWRITEBYTECODE=1",
            "--env",
            f"SENTINEL_PROBE_ID={probe_id}",
        ]
        environment = dict(target.env)
        for name_from_host in target.env_from:
            if name_from_host not in os.environ:
                raise ConfigurationError(
                    f"required environment variable is unset: {name_from_host}"
                )
            environment[name_from_host] = os.environ[name_from_host]
        for key, value in sorted(environment.items()):
            args.extend(("--env", f"{key}={value}"))
        args.extend((image, *target.launch_cmd))
        return tuple(args)


def reap_orphans(
    *, runner: CommandRunner | None = None, now: Callable[[], float] = time.time
) -> None:
    execute = runner or _run_command
    listing = execute(
        (
            "docker",
            "ps",
            "--all",
            "--filter",
            f"label={OWNER_LABEL}=true",
            "--format",
            "{{.Names}}",
        )
    )
    if listing.returncode != 0:
        raise InfrastructureError("cannot list stale Sentinel containers")
    for name in filter(None, listing.stdout.splitlines()):
        inspected = execute(
            (
                "docker",
                "inspect",
                "--format",
                f'{{{{index .Config.Labels "{CREATED_LABEL}"}}}}',
                name,
            )
        )
        if inspected.returncode != 0:
            raise InfrastructureError(f"cannot inspect Sentinel container {name}")
        try:
            created = int(inspected.stdout.strip())
        except ValueError as error:
            raise InfrastructureError(
                f"Sentinel container {name} has an invalid creation label"
            ) from error
        if now() - created <= ORPHAN_AGE_SECONDS:
            continue
        removed = execute(("docker", "rm", "--force", name))
        if removed.returncode != 0:
            raise InfrastructureError(f"cannot reap Sentinel container {name}")


def _dependency_inputs(
    configuration: LoadedConfiguration,
) -> tuple[str, tuple[Path, ...], tuple[str, ...]]:
    target = configuration.target
    if target is None:
        raise ValueError("dynamic dependency resolution requires a target")
    root = configuration.scan_root
    files: list[Path] = []
    requirements: list[str] = []
    if target.install_cmd is not None:
        lowered = tuple(item.lower() for item in target.install_cmd)
        if "pip" not in lowered and lowered[0] not in {"pip", "pip3"}:
            raise ConfigurationError(
                "wheelhouse builds currently require a pip requirements install_cmd"
            )
        for index, item in enumerate(target.install_cmd[:-1]):
            if item.lower() in {"-r", "--requirement"}:
                path = root / target.install_cmd[index + 1]
                files.append(path)
                requirements.extend(_requirement_lines(path))
    else:
        candidates = [
            path
            for path in (root / "requirements.txt", root / "pyproject.toml")
            if path.is_file() and not path.is_symlink()
        ]
        if len(candidates) != 1:
            raise ConfigurationError(
                "dependency source is ambiguous; set a dependency-only install_cmd"
            )
        source = candidates[0]
        files.append(source)
        requirements.extend(
            _requirement_lines(source)
            if source.name == "requirements.txt"
            else _pyproject_dependencies(source)
        )
    if not requirements:
        raise ConfigurationError(
            "target dependency configuration produced no requirements"
        )
    digest = hashlib.sha256()
    digest.update(target.python_version.encode())
    digest.update(json.dumps(target.install_cmd, separators=(",", ":")).encode())
    digest.update(__version__.encode())
    for path in sorted(files):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest(), tuple(files), tuple(requirements)


def _requirement_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "-"))
    ]


def _pyproject_dependencies(path: Path) -> list[str]:
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    dependencies = raw.get("project", {}).get("dependencies", [])
    if not isinstance(dependencies, list) or not all(
        isinstance(item, str) for item in dependencies
    ):
        raise ConfigurationError(
            "pyproject.toml project.dependencies must be a string list"
        )
    return dependencies


def _squid_configuration(registries: tuple[str, ...]) -> str:
    allowed = " ".join(registries)
    return "\n".join(
        (
            "http_port 3128",
            f"acl allowed_registries dstdomain {allowed}",
            "acl ip_literal url_regex ^https?://[0-9a-fA-F:.]+([/:]|$)",
            "http_access deny ip_literal",
            "http_access allow allowed_registries",
            "http_access deny all",
            "access_log daemon:/var/log/squid/access.log",
            "cache_dir ufs /var/spool/squid 16 16 16",
            "cache deny all",
            "",
        )
    )


def _offline_dockerfile(base: str) -> str:
    return "\n".join(
        (
            f"FROM {base}",
            "COPY wheelhouse /wheelhouse",
            "COPY requirements.txt /requirements.txt",
            'RUN ["python", "-m", "pip", "install", "--no-index", '
            '"--find-links=/wheelhouse", "--requirement", "/requirements.txt"]',
            'RUN ["python", "-c", "import pathlib,shutil; '
            "shutil.rmtree(pathlib.Path('/wheelhouse')); "
            "pathlib.Path('/requirements.txt').unlink()\"]",
            "",
        )
    )


def _run_command(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=PASS_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise InfrastructureError(f"cannot execute Docker: {error}") from error
