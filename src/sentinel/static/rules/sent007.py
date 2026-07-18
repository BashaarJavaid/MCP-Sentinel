"""SENT-007 manifest integrity dataflow analysis."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Literal

import yaml
from pydantic import field_validator, model_validator

from sentinel.errors import UsageError
from sentinel.finding import ContractModel
from sentinel.static.ast_utils import match_from_node, qualified_name
from sentinel.static.model import RuleRunState, StaticContext


class IntegrityEntry(ContractModel):
    sha256: str | None = None
    public_key: str | None = None
    signature: str | None = None
    algorithm: Literal["ed25519", "rsa-pss-sha256", "ecdsa-sha256"] | None = None

    @model_validator(mode="after")
    def validate_mode(self) -> IntegrityEntry:
        hash_mode = self.sha256 is not None
        signature_mode = all(
            value is not None
            for value in (self.public_key, self.signature, self.algorithm)
        )
        if hash_mode == signature_mode:
            raise ValueError(
                "integrity entry must select exactly one verification mode"
            )
        if self.sha256 is not None and not re.fullmatch(r"[0-9a-f]{64}", self.sha256):
            raise ValueError("integrity SHA-256 must be lowercase hexadecimal")
        for value in (self.public_key, self.signature):
            if value and (Path(value).is_absolute() or ".." in Path(value).parts):
                raise ValueError("integrity paths must be repository-relative")
        return self


class IntegrityManifest(ContractModel):
    version: int
    manifests: dict[str, IntegrityEntry]

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: int) -> int:
        if value != 1:
            raise ValueError("integrity manifest version must be 1")
        return value


def detect(context: StaticContext, state: RuleRunState) -> None:
    anchors = _load_anchors(context.configuration.scan_root)
    del anchors
    for file in context.files.python_files:
        for function in (
            node
            for node in file.tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ):
            if not _is_manifest_function(function):
                continue
            verification_lines = [
                item.lineno
                for item in ast.walk(function)
                if isinstance(item, ast.Call) and _is_verification(item)
            ]
            for item in ast.walk(function):
                if not isinstance(item, ast.Call) or not _is_manifest_load(item):
                    continue
                if any(line < item.lineno for line in verification_lines):
                    state.exempt("verified_manifest")
                else:
                    state.matches.append(
                        match_from_node("SENT-007", file, item, "unverified-manifest")
                    )


def _load_anchors(root: Path) -> IntegrityManifest | None:
    path = root / "sentinel.integrity.yaml"
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise UsageError("sentinel.integrity.yaml must be a regular file")
    try:
        value = IntegrityManifest.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
    except Exception as error:
        raise UsageError(f"invalid sentinel.integrity.yaml: {error}") from error
    for manifest, entry in value.manifests.items():
        if Path(manifest).is_absolute() or ".." in Path(manifest).parts:
            raise UsageError("integrity manifest paths must be repository-relative")
        for target in (entry.public_key, entry.signature):
            if target is not None and not (root / target).is_file():
                raise UsageError(
                    f"integrity trust-anchor path does not exist: {target}"
                )
    return value


def _is_manifest_load(node: ast.Call) -> bool:
    name = qualified_name(node.func) or ""
    return name in {"json.load", "json.loads", "yaml.safe_load", "yaml.load"}


def _is_manifest_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    name = node.name.lower()
    return "manifest" in name or name in {"load_tools", "register_tools"}


def _is_verification(node: ast.Call) -> bool:
    name = qualified_name(node.func) or ""
    return name.endswith(
        ("hashlib.sha256", "hmac.compare_digest", ".verify")
    ) or name in {"hashlib.sha256", "hmac.compare_digest"}
