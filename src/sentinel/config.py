"""Strict scanner and target configuration loading."""

from __future__ import annotations

import os
import re
import shlex
import sys
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import Any, Literal

import yaml
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version
from pydantic import AliasChoices, Field, field_validator, model_validator

from sentinel.errors import UsageError
from sentinel.finding import ContractModel, FindingStatus, Severity

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - exercised on the Python 3.10 CI job
    import tomli as tomllib

SUPPORTED_RULES = frozenset(f"SENT-{number:03d}" for number in range(1, 12))
DEFAULT_IGNORES = (
    ".venv/",
    "venv/",
    "node_modules/",
    "__pycache__/",
    ".git/",
)
SECRET_NAME_FRAGMENTS = (
    "SECRET",
    "KEY",
    "TOKEN",
    "PASSWORD",
    "PASSWD",
    "CREDENTIAL",
    "PRIVATE",
    "AUTH",
    "COOKIE",
    "SESSION",
)
SECRET_VALUE_PREFIXES = (
    "sk-",
    "ghp_",
    "github_pat_",
    "xoxb-",
    "xoxp-",
    "xoxa-",
    "xoxr-",
    "xoxs-",
    "AKIA",
    "AIza",
)
SHELL_EXECUTABLES = frozenset(
    {"sh", "bash", "zsh", "fish", "dash", "ksh", "cmd", "cmd.exe", "powershell", "pwsh"}
)


class OutputFormat(str, Enum):
    CONSOLE = "console"
    JSON = "json"
    SARIF = "sarif"


class FailThreshold(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class ReasoningEffort(str, Enum):
    LOW = "low"
    MEDIUM = "medium"


class ScannerConfig(ContractModel):
    format: OutputFormat = OutputFormat.CONSOLE
    fail_on: FailThreshold = FailThreshold.HIGH
    rules: tuple[str, ...] = ()
    ignore_paths: tuple[str, ...] = ()
    target_config: str = "sentinel.target.yaml"
    max_findings_per_scan: int = Field(default=500, ge=1)

    @field_validator("rules", "ignore_paths", mode="before")
    @classmethod
    def list_to_tuple(cls, value: Any) -> Any:
        return tuple(value) if isinstance(value, list) else value

    @field_validator("rules")
    @classmethod
    def validate_rules(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for token in value:
            if not re.fullmatch(r"[+-]?SENT-\d{3}", token):
                raise ValueError(f"invalid rule token: {token}")
            rule_id = token.removeprefix("+").removeprefix("-")
            if rule_id not in SUPPORTED_RULES:
                raise ValueError(f"unknown rule ID: {rule_id}")
        return value

    @field_validator("ignore_paths")
    @classmethod
    def validate_ignore_paths(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for item in value:
            _validate_relative_text_path(item, "ignore path")
        return value

    @field_validator("target_config")
    @classmethod
    def validate_target_config(cls, value: str) -> str:
        return _validate_relative_text_path(value, "target config")


class LlmConfig(ContractModel):
    reasoning_effort: ReasoningEffort = ReasoningEffort.MEDIUM
    timeout_seconds: int = Field(default=30, ge=1)
    retries: int = Field(default=2, ge=0)
    max_concurrency: int = Field(default=5, ge=1)
    cache_enabled: bool = True


class SandboxConfig(ContractModel):
    allowed_registries: tuple[str, ...] = (
        "pypi.org",
        "files.pythonhosted.org",
    )

    @field_validator("allowed_registries", mode="before")
    @classmethod
    def list_to_tuple(cls, value: Any) -> Any:
        return tuple(value) if isinstance(value, list) else value

    @field_validator("allowed_registries")
    @classmethod
    def validate_registries(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value:
            raise ValueError("allowed_registries cannot be empty")
        for registry in value:
            if not re.fullmatch(r"[A-Za-z0-9.-]+", registry):
                raise ValueError(f"invalid registry hostname: {registry}")
        return value


class Sent005AllowlistEntry(ContractModel):
    path: str
    fingerprint: str
    reason: str

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return _validate_relative_text_path(value, "SENT-005 allow path")

    @field_validator("fingerprint")
    @classmethod
    def validate_fingerprint(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("SENT-005 fingerprints must be lowercase SHA-256")
        return value

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("SENT-005 allowlist reason cannot be empty")
        return value.strip()


class Sent005Config(ContractModel):
    allowlist: tuple[Sent005AllowlistEntry, ...] = ()

    @field_validator("allowlist", mode="before")
    @classmethod
    def list_to_tuple(cls, value: Any) -> Any:
        return tuple(value) if isinstance(value, list) else value


class Sent004Config(ContractModel):
    sanitizers: tuple[str, ...] = ()

    @field_validator("sanitizers", mode="before")
    @classmethod
    def list_to_tuple(cls, value: Any) -> Any:
        return tuple(value) if isinstance(value, list) else value

    @field_validator("sanitizers")
    @classmethod
    def validate_sanitizers(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for item in value:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", item):
                raise ValueError(f"invalid qualified sanitizer: {item}")
        return value


class Sent006Config(ContractModel):
    public_routes: tuple[str, ...] = ()

    @field_validator("public_routes", mode="before")
    @classmethod
    def list_to_tuple(cls, value: Any) -> Any:
        return tuple(value) if isinstance(value, list) else value

    @field_validator("public_routes")
    @classmethod
    def validate_public_routes(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for item in value:
            if not re.fullmatch(r"[A-Z]+ /\S+", item):
                raise ValueError(
                    "SENT-006 public routes must use 'METHOD /path-pattern'"
                )
        return value


class RulesConfig(ContractModel):
    sent004: Sent004Config = Field(
        default_factory=Sent004Config,
        validation_alias=AliasChoices("SENT-004", "sent004"),
        serialization_alias="SENT-004",
    )
    sent005: Sent005Config = Field(
        default_factory=Sent005Config,
        validation_alias=AliasChoices("SENT-005", "sent005"),
        serialization_alias="SENT-005",
    )
    sent006: Sent006Config = Field(
        default_factory=Sent006Config,
        validation_alias=AliasChoices("SENT-006", "sent006"),
        serialization_alias="SENT-006",
    )


class SentinelConfig(ContractModel):
    scanner: ScannerConfig = Field(default_factory=ScannerConfig)
    llm: LlmConfig = Field(default_factory=LlmConfig)
    sandbox: SandboxConfig = Field(default_factory=SandboxConfig)
    rules: RulesConfig = Field(default_factory=RulesConfig)


class TargetConfig(ContractModel):
    language: Literal["python"]
    launch_cmd: tuple[str, ...]
    install_cmd: tuple[str, ...] | None = None
    transport: Literal["stdio"]
    working_dir: str
    env: dict[str, str] = Field(default_factory=dict)
    env_from: tuple[str, ...] = ()
    python_version: Literal["3.10", "3.11", "3.12"]

    @field_validator("launch_cmd", "install_cmd", "env_from", mode="before")
    @classmethod
    def list_to_tuple(cls, value: Any) -> Any:
        return tuple(value) if isinstance(value, list) else value

    @field_validator("launch_cmd")
    @classmethod
    def validate_launch_cmd(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value or any(not item for item in value):
            raise ValueError("launch_cmd must be a non-empty argv array")
        _reject_shell(value, "launch_cmd")
        return value

    @field_validator("install_cmd")
    @classmethod
    def validate_install_cmd(
        cls, value: tuple[str, ...] | None
    ) -> tuple[str, ...] | None:
        if value is None:
            return None
        if not value or any(not item for item in value):
            raise ValueError("install_cmd must be a non-empty argv array")
        _reject_shell(value, "install_cmd")
        _validate_install_shape(value)
        return value

    @model_validator(mode="after")
    def validate_environment(self) -> TargetConfig:
        for name, value in self.env.items():
            _validate_env_name(name)
            _validate_env_value(value)
        for name in self.env_from:
            _validate_env_name(name)
        return self


class LoadedConfiguration(ContractModel):
    scan_root: Path
    scanner: SentinelConfig
    target: TargetConfig | None
    static_only: bool


ENV_OVERRIDES: dict[str, tuple[str, str]] = {
    "SENTINEL_FORMAT": ("scanner", "format"),
    "SENTINEL_FAIL_ON": ("scanner", "fail_on"),
    "SENTINEL_RULES": ("scanner", "rules"),
    "SENTINEL_IGNORE_PATHS": ("scanner", "ignore_paths"),
    "SENTINEL_TARGET_CONFIG": ("scanner", "target_config"),
    "SENTINEL_MAX_FINDINGS": ("scanner", "max_findings_per_scan"),
    "SENTINEL_LLM_REASONING_EFFORT": ("llm", "reasoning_effort"),
    "SENTINEL_LLM_TIMEOUT_SECONDS": ("llm", "timeout_seconds"),
    "SENTINEL_LLM_RETRIES": ("llm", "retries"),
    "SENTINEL_LLM_MAX_CONCURRENCY": ("llm", "max_concurrency"),
    "SENTINEL_LLM_CACHE_ENABLED": ("llm", "cache_enabled"),
    "SENTINEL_ALLOWED_REGISTRIES": ("sandbox", "allowed_registries"),
}
LIST_ENV_VARS = {
    "SENTINEL_RULES",
    "SENTINEL_IGNORE_PATHS",
    "SENTINEL_ALLOWED_REGISTRIES",
}
INTEGER_ENV_VARS = {
    "SENTINEL_MAX_FINDINGS",
    "SENTINEL_LLM_TIMEOUT_SECONDS",
    "SENTINEL_LLM_RETRIES",
    "SENTINEL_LLM_MAX_CONCURRENCY",
}
BOOLEAN_ENV_VARS = {"SENTINEL_LLM_CACHE_ENABLED"}


def load_configuration(
    scan_path: Path,
    *,
    environ: Mapping[str, str] | None = None,
    cli_overrides: Mapping[str, Any] | None = None,
    target_launch_cmd: str | None = None,
    static_only: bool = False,
) -> LoadedConfiguration:
    """Load and validate scanner/target configuration without executing target code."""

    scan_root = validate_scan_root(scan_path)
    config_data = _read_toml(scan_root / "sentinel.toml", required=False)
    merged = _deep_merge({}, config_data)
    merged = _apply_environment(merged, environ or os.environ)
    merged = _apply_cli(merged, cli_overrides or {})
    try:
        scanner = SentinelConfig.model_validate(merged)
    except Exception as error:
        raise UsageError(f"invalid scanner configuration: {error}") from error

    _require_supported_framework(scan_root)

    target: TargetConfig | None = None
    if not static_only:
        target_path = resolve_within_root(
            scan_root, scanner.scanner.target_config, must_exist=False
        )
        target_data: dict[str, Any]
        if target_path.is_file():
            target_data = _read_yaml(target_path)
            if target_launch_cmd is not None:
                target_data["launch_cmd"] = _parse_launch_override(target_launch_cmd)
        elif target_launch_cmd is not None:
            target_data = {
                "language": "python",
                "launch_cmd": _parse_launch_override(target_launch_cmd),
                "transport": "stdio",
                "working_dir": ".",
                "env": {},
                "env_from": [],
            }
        else:
            raise UsageError(
                "dynamic analysis requires sentinel.target.yaml or "
                "--target-launch-cmd; use --static-only to opt out"
            )
        target_data.setdefault("python_version", infer_python_version(scan_root))
        try:
            target = TargetConfig.model_validate(target_data)
        except Exception as error:
            raise UsageError(f"invalid target configuration: {error}") from error
        _validate_target_paths(scan_root, target)

    return LoadedConfiguration(
        scan_root=scan_root,
        scanner=scanner,
        target=target,
        static_only=static_only,
    )


def validate_scan_root(path: Path) -> Path:
    if path.is_symlink():
        raise UsageError("scan root cannot be a symbolic link")
    if not path.exists():
        raise UsageError(f"scan root does not exist: {path}")
    if not path.is_dir():
        raise UsageError(f"scan root is not a directory: {path}")
    return path.resolve()


def resolve_within_root(root: Path, value: str, *, must_exist: bool = True) -> Path:
    try:
        _validate_relative_text_path(value, "path")
    except ValueError as error:
        raise UsageError(str(error)) from error
    candidate = root.joinpath(value)
    current = root
    for part in Path(value).parts:
        current = current / part
        if current.is_symlink():
            raise UsageError(f"symbolic links are not allowed: {value}")
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise UsageError(f"path escapes the scan root: {value}") from error
    if must_exist and not resolved.exists():
        raise UsageError(f"path does not exist: {value}")
    return resolved


def infer_python_version(root: Path) -> str:
    pyproject = root / "pyproject.toml"
    if pyproject.is_file() and not pyproject.is_symlink():
        data = _read_toml(pyproject, required=True)
        requires_python = data.get("project", {}).get("requires-python")
        if isinstance(requires_python, str):
            try:
                specifier = SpecifierSet(requires_python)
            except InvalidSpecifier as error:
                raise UsageError(
                    f"invalid requires-python: {requires_python}"
                ) from error
            for candidate in ("3.11", "3.12", "3.10"):
                if Version(candidate) in specifier:
                    return candidate
            raise UsageError("target requires-python excludes Python 3.10-3.12")
    version_file = root / ".python-version"
    if version_file.is_file() and not version_file.is_symlink():
        candidate = version_file.read_text(encoding="utf-8").strip()
        if candidate not in {"3.10", "3.11", "3.12"}:
            raise UsageError(".python-version must select Python 3.10, 3.11, or 3.12")
        return candidate
    return "3.11"


def _read_toml(path: Path, *, required: bool) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise UsageError(f"missing TOML file: {path.name}")
        return {}
    if path.is_symlink():
        raise UsageError(f"configuration cannot be a symbolic link: {path.name}")
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise UsageError(f"cannot parse {path.name}: {error}") from error
    if not isinstance(data, dict):
        raise UsageError(f"{path.name} must contain a TOML table")
    return data


def _read_yaml(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise UsageError("target configuration cannot be a symbolic link")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise UsageError(f"cannot parse {path.name}: {error}") from error
    if not isinstance(data, dict):
        raise UsageError(f"{path.name} must contain a YAML mapping")
    return data


def _deep_merge(base: dict[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in overlay.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = _deep_merge(dict(result[key]), value)
        else:
            result[key] = value
    return result


def _apply_environment(
    data: dict[str, Any], environ: Mapping[str, str]
) -> dict[str, Any]:
    result = _deep_merge({}, data)
    for name, (section, key) in ENV_OVERRIDES.items():
        if name not in environ:
            continue
        raw = environ[name]
        value: Any
        if name in LIST_ENV_VARS:
            parts = tuple(part.strip() for part in raw.split(","))
            if not parts or any(not part for part in parts):
                raise UsageError(f"{name} contains an empty list element")
            value = parts
        elif name in INTEGER_ENV_VARS:
            try:
                value = int(raw)
            except ValueError as error:
                raise UsageError(f"{name} must be an integer") from error
        elif name in BOOLEAN_ENV_VARS:
            lowered = raw.strip().lower()
            if lowered not in {"true", "false", "1", "0"}:
                raise UsageError(f"{name} must be true, false, 1, or 0")
            value = lowered in {"true", "1"}
        else:
            value = raw
        result.setdefault(section, {})[key] = value
    return result


def _apply_cli(data: dict[str, Any], overrides: Mapping[str, Any]) -> dict[str, Any]:
    result = _deep_merge({}, data)
    scanner = result.setdefault("scanner", {})
    for key, value in overrides.items():
        if value is not None:
            scanner[key] = value
    return result


def _parse_launch_override(value: str) -> tuple[str, ...]:
    try:
        parsed = tuple(shlex.split(value, posix=True))
    except ValueError as error:
        raise UsageError(f"invalid --target-launch-cmd: {error}") from error
    if not parsed:
        raise UsageError("--target-launch-cmd cannot be empty")
    try:
        _reject_shell(parsed, "--target-launch-cmd")
    except ValueError as error:
        raise UsageError(str(error)) from error
    return parsed


def _reject_shell(command: tuple[str, ...], label: str) -> None:
    executable = Path(command[0]).name.lower()
    if executable in SHELL_EXECUTABLES:
        raise ValueError(f"{label} cannot invoke a shell interpreter")


def _validate_install_shape(command: tuple[str, ...]) -> None:
    lowered = tuple(item.lower() for item in command)
    if any(
        item.startswith(("http://", "https://", "git+"))
        or item in {"-i", "--index-url", "--extra-index-url", "-e", "--editable", "."}
        for item in lowered
    ):
        raise ValueError(
            "install_cmd contains a prohibited URL, index, or project install"
        )

    if lowered[0] in {"pip", "pip3"}:
        args = lowered[1:]
    elif re.fullmatch(r"python(?:3(?:\.\d+)?)?", lowered[0]) and lowered[1:3] == (
        "-m",
        "pip",
    ):
        args = lowered[3:]
    else:
        args = ()
    if args:
        if not args or args[0] != "install":
            raise ValueError("pip install_cmd must use the install subcommand")
        allowed_flags = {
            "-r",
            "--requirement",
            "-c",
            "--constraint",
            "--require-hashes",
            "--no-deps",
            "--disable-pip-version-check",
        }
        index = 1
        saw_file = False
        while index < len(args):
            item = args[index]
            if item in {"-r", "--requirement", "-c", "--constraint"}:
                if index + 1 >= len(args):
                    raise ValueError(f"{item} requires a dependency file")
                _validate_relative_text_path(args[index + 1], "dependency file")
                saw_file = True
                index += 2
            elif item in allowed_flags:
                index += 1
            else:
                raise ValueError(
                    f"unsupported pip install option: {command[-(len(args) - index)]}"
                )
        if not saw_file:
            raise ValueError(
                "pip install_cmd must reference requirements or constraints"
            )
        return

    if lowered[:2] == ("poetry", "install"):
        if "--no-root" not in lowered[2:]:
            raise ValueError("Poetry install_cmd must include --no-root")
        if any(
            item not in {"--no-root", "--no-interaction", "--sync"}
            for item in lowered[2:]
        ):
            raise ValueError("unsupported Poetry install option")
        return

    if lowered[:2] == ("uv", "sync"):
        if "--no-install-project" not in lowered[2:]:
            raise ValueError("uv install_cmd must include --no-install-project")
        allowed = {
            "--no-install-project",
            "--frozen",
            "--locked",
            "--no-dev",
            "--all-groups",
        }
        if any(item not in allowed for item in lowered[2:]):
            raise ValueError("unsupported uv sync option")
        return
    raise ValueError("install_cmd must use pip, Poetry, or uv dependency-only forms")


def _validate_target_paths(root: Path, target: TargetConfig) -> None:
    working_dir = resolve_within_root(root, target.working_dir)
    if not working_dir.is_dir():
        raise UsageError("working_dir must be a directory")
    if target.install_cmd is not None:
        _validate_install_files(root, target.install_cmd)


def _validate_install_files(root: Path, command: tuple[str, ...]) -> None:
    for index, item in enumerate(command[:-1]):
        if item.lower() in {"-r", "--requirement", "-c", "--constraint"}:
            path = resolve_within_root(root, command[index + 1])
            if not path.is_file():
                raise UsageError(
                    f"dependency input is not a file: {command[index + 1]}"
                )


def _validate_env_name(name: str) -> None:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError(f"invalid environment variable name: {name}")
    upper = name.upper()
    if any(fragment in upper for fragment in SECRET_NAME_FRAGMENTS):
        raise ValueError(f"secret-shaped environment variable is prohibited: {name}")


def _validate_env_value(value: str) -> None:
    stripped = value.strip()
    lowered = stripped.lower()
    if lowered.startswith(("bearer ", "basic ")):
        raise ValueError("literal authentication credentials are prohibited")
    if "-----BEGIN " in stripped and "PRIVATE KEY-----" in stripped:
        raise ValueError("literal private keys are prohibited")
    if any(stripped.startswith(prefix) for prefix in SECRET_VALUE_PREFIXES):
        raise ValueError("literal token-like values are prohibited")


def _validate_relative_text_path(value: str, label: str) -> str:
    if not value or Path(value).is_absolute():
        raise ValueError(f"{label} must be a non-empty relative path")
    normalized = value.replace("\\", "/")
    if ".." in normalized.split("/"):
        raise ValueError(f"{label} cannot escape the scan root")
    return normalized


def _require_supported_framework(root: Path) -> None:
    names: set[str] = set()
    pyproject = root / "pyproject.toml"
    if pyproject.is_file() and not pyproject.is_symlink():
        data = _read_toml(pyproject, required=True)
        project_dependencies = data.get("project", {}).get("dependencies", [])
        if isinstance(project_dependencies, list):
            names.update(_requirement_names(project_dependencies))
        poetry_dependencies = (
            data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        )
        if isinstance(poetry_dependencies, dict):
            names.update(_normalize_package_name(name) for name in poetry_dependencies)

    requirement_files = [root / "requirements.txt"]
    requirements_dir = root / "requirements"
    if requirements_dir.is_dir() and not requirements_dir.is_symlink():
        requirement_files.extend(sorted(requirements_dir.glob("*.txt")))
    for path in requirement_files:
        if not path.is_file() or path.is_symlink():
            continue
        entries = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith(("#", "-"))
        ]
        names.update(_requirement_names(entries))

    if not names.intersection({"mcp", "fastmcp"}):
        raise UsageError(
            "unsupported target: declare the official 'mcp' or 'fastmcp' dependency"
        )


def _requirement_names(entries: list[Any]) -> set[str]:
    names: set[str] = set()
    for entry in entries:
        if not isinstance(entry, str):
            continue
        try:
            names.add(_normalize_package_name(Requirement(entry).name))
        except InvalidRequirement:
            continue
    return names


def _normalize_package_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def threshold_severity(value: FailThreshold) -> Severity:
    return Severity(value.value.capitalize())


def status_is_reportable(status: FindingStatus) -> bool:
    return status is not FindingStatus.SUPPRESSED
