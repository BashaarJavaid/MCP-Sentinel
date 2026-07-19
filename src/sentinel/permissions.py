"""Shared permissions-manifest contract for static and dynamic analysis."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import Field, field_validator

from sentinel.errors import ConfigurationError, TargetError
from sentinel.finding import ContractModel


class Capability(ContractModel):
    scopes: tuple[str, ...] = ()
    broad_scope_justification: str | None = None

    @field_validator("scopes", mode="before")
    @classmethod
    def list_to_tuple(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @field_validator("broad_scope_justification")
    @classmethod
    def normalize_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not value.strip():
            raise ValueError("broad scope justification cannot be empty")
        return value.strip()


class FilesystemPermissions(ContractModel):
    read: Capability = Field(default_factory=Capability)
    write: Capability = Field(default_factory=Capability)


class ToolPermissions(ContractModel):
    filesystem: FilesystemPermissions = Field(default_factory=FilesystemPermissions)
    network: Capability = Field(default_factory=Capability)


class PermissionsManifest(ContractModel):
    version: int
    tools: dict[str, ToolPermissions]

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: int) -> int:
        if value != 1:
            raise ValueError("permissions manifest version must be 1")
        return value


def load_permissions_manifest(
    root: Path, *, required: bool
) -> PermissionsManifest | None:
    """Load and validate the target permissions manifest without executing code."""

    path = root / "sentinel.permissions.yaml"
    if not path.exists():
        if required:
            raise TargetError("dynamic analysis requires sentinel.permissions.yaml")
        return None
    if path.is_symlink() or not path.is_file():
        raise ConfigurationError("sentinel.permissions.yaml must be a regular file")
    try:
        manifest = PermissionsManifest.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
    except Exception as error:
        raise ConfigurationError(
            f"invalid sentinel.permissions.yaml: {error}"
        ) from error
    validate_permission_scopes(manifest)
    return manifest


def validate_permission_scopes(manifest: PermissionsManifest) -> None:
    for tool in manifest.tools.values():
        for capability in (tool.filesystem.read, tool.filesystem.write):
            for scope in capability.scopes:
                normalized = scope.replace("\\", "/")
                if normalized.startswith("/") or ".." in normalized.split("/"):
                    raise ConfigurationError(
                        "filesystem permission scopes must be relative"
                    )
                if normalized.startswith("$") and not normalized.startswith("$TMP/"):
                    raise ConfigurationError(
                        "only the $TMP filesystem token is supported"
                    )
        for scope in tool.network.scopes:
            if "://" in scope or "@" in scope or "/" in scope:
                raise ConfigurationError("network scopes must use host[:port] patterns")
