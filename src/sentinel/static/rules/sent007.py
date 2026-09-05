"""SENT-007 manifest integrity dataflow analysis."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Literal

import yaml
from pydantic import field_validator, model_validator

from sentinel.errors import ConfigurationError, TargetError
from sentinel.finding import ContractModel
from sentinel.static.ast_utils import (
    import_aliases,
    match_from_node,
    qualified_name,
    resolve_name,
)
from sentinel.static.model import RuleRunState, StaticContext
from sentinel.static.rules.sent002 import _locals
from sentinel.static.safety import (
    Condition,
    constants,
    equal_operands,
    literal,
    paths,
    reference,
    trusted,
)


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
    anchors = load_integrity_manifest(context.configuration.scan_root)
    for file in context.files.python_files:
        file_imports, values = import_aliases(file), constants(file.tree)
        for function in (
            node
            for node in file.tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ):
            if not _is_manifest_function(function):
                continue
            imports = {
                name: value
                for name, value in file_imports.items()
                if name not in _locals(function)
            }
            unsafe: dict[int, ast.Call] = {}
            loads: dict[int, ast.Call] = {}
            for path in paths(function.body, context.deadline):
                aliases: dict[str, str] = {}
                local = {
                    name: value
                    for name, value in values.items()
                    if name not in {arg.arg for arg in function.args.args}
                }
                digests: dict[str, str] = {}
                verified: set[str] = set()
                raw_files: dict[str, str] = {}

                def data(
                    node: ast.AST, aliases: dict[str, str] = aliases
                ) -> str | None:
                    if (
                        isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr in {"decode", "encode"}
                    ):
                        return data(node.func.value)
                    return reference(node, aliases)

                def digest(
                    node: ast.AST,
                    digests: dict[str, str] = digests,
                    imports: dict[str, str] = imports,
                ) -> str | None:
                    if isinstance(node, ast.Name):
                        return digests.get(node.id)
                    if (
                        isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr in {"hexdigest", "digest"}
                    ):
                        inner = node.func.value
                        if (
                            isinstance(inner, ast.Call)
                            and (qualified_name(inner.func) or "").split(".")[0]
                            in imports
                            and resolve_name(qualified_name(inner.func) or "", imports)
                            == "hashlib.sha256"
                            and inner.args
                        ):
                            return data(inner.args[0])
                    return None

                def signature(
                    call: ast.Call,
                    local: dict[str, ast.expr] = local,
                    imports: dict[str, str] = imports,
                    raw_files: dict[str, str] = raw_files,
                ) -> str | None:
                    if (
                        not isinstance(call.func, ast.Attribute)
                        or call.func.attr != "verify"
                        or len(call.args) < 2
                    ):
                        return None
                    key = call.func.value
                    if isinstance(key, ast.Name):
                        key = local.get(key.id, key)
                    if (
                        not isinstance(key, ast.Call)
                        or resolve_name(qualified_name(key.func) or "", imports)
                        != (
                            "cryptography.hazmat.primitives.serialization."
                            "load_pem_public_key"
                        )
                        or not key.args
                    ):
                        return None
                    raw = data(call.args[1])
                    key_value = key.args[0]
                    if (
                        isinstance(key_value, ast.Call)
                        and isinstance(key_value.func, ast.Attribute)
                        and key_value.func.attr == "encode"
                    ):
                        key_value = key_value.func.value
                    pem = literal(key_value, local)
                    if not isinstance(pem, (str, bytes)):
                        declared = anchor_content(
                            context.configuration.scan_root,
                            anchors,
                            raw_files.get(raw or ""),
                            "public_key",
                        )
                        pem = (
                            declared[1]
                            if declared and read_path(key_value, local) == declared[0]
                            else None
                        )
                    algorithm = key_algorithm(pem)
                    signed = trusted(call.args[0], local, imports)
                    if not signed:
                        declared = anchor_content(
                            context.configuration.scan_root,
                            anchors,
                            raw_files.get(raw or ""),
                            "signature",
                        )
                        signed = bool(
                            declared and read_path(call.args[0], local) == declared[0]
                        )

                    def called(argument_node: ast.AST, expected_name: str) -> bool:
                        return (
                            isinstance(argument_node, ast.Call)
                            and resolve_name(
                                qualified_name(argument_node.func) or "", imports
                            )
                            == expected_name
                        )

                    valid_algorithm = algorithm == "ed25519" and len(call.args) == 2
                    if algorithm == "ecdsa-sha256" and len(call.args) == 3:
                        verifier = call.args[2]
                        valid_algorithm = (
                            called(
                                verifier,
                                "cryptography.hazmat.primitives.asymmetric.ec.ECDSA",
                            )
                            and isinstance(verifier, ast.Call)
                            and len(verifier.args) == 1
                            and called(
                                verifier.args[0],
                                "cryptography.hazmat.primitives.hashes.SHA256",
                            )
                        )
                    if algorithm == "rsa-pss-sha256" and len(call.args) == 4:
                        padding = call.args[2]
                        valid_algorithm = called(
                            padding,
                            "cryptography.hazmat.primitives.asymmetric.padding.PSS",
                        ) and called(
                            call.args[3], "cryptography.hazmat.primitives.hashes.SHA256"
                        )
                        if isinstance(padding, ast.Call):
                            mgf = next(
                                (
                                    kw.value
                                    for kw in padding.keywords
                                    if kw.arg == "mgf"
                                ),
                                None,
                            )
                            valid_algorithm = (
                                valid_algorithm
                                and isinstance(mgf, ast.Call)
                                and called(
                                    mgf,
                                    "cryptography.hazmat.primitives.asymmetric.padding.MGF1",
                                )
                                and len(mgf.args) == 1
                                and called(
                                    mgf.args[0],
                                    "cryptography.hazmat.primitives.hashes.SHA256",
                                )
                            )
                    return raw if signed and valid_algorithm else None

                for event in path:
                    if isinstance(event, Condition):
                        pair = equal_operands(event.test, event.truth, imports)
                        if pair:
                            for candidate, anchor in (pair, pair[::-1]):
                                raw = digest(candidate)
                                expected = sidecar_digest(
                                    anchor, local, anchors
                                ) or literal(anchor, local)
                                if (
                                    raw
                                    and isinstance(expected, str)
                                    and re.fullmatch(r"[0-9a-fA-F]{64}", expected)
                                ):
                                    verified.add(raw)
                        continue
                    if isinstance(event, (ast.With, ast.AsyncWith)):
                        for item in event.items:
                            if isinstance(item.optional_vars, ast.Name):
                                local[item.optional_vars.id] = item.context_expr
                    if isinstance(event, ast.Raise):
                        break
                    if isinstance(event, ast.Expr) and isinstance(
                        event.value, ast.Call
                    ):
                        raw = signature(event.value)
                        if raw:
                            verified.add(raw)
                    # Only top-level executed expressions can establish verification.
                    expressions = (
                        [event.value]
                        if isinstance(
                            event, (ast.Assign, ast.AnnAssign, ast.Expr, ast.Return)
                        )
                        and event.value is not None
                        else []
                    )
                    for expression in expressions:
                        for call in ast.walk(expression):
                            if isinstance(call, ast.Call) and _is_manifest_load(call):
                                loads[id(call)] = call
                                if not call.args or data(call.args[0]) not in verified:
                                    unsafe[id(call)] = call
                    if (
                        isinstance(event, (ast.Assign, ast.AnnAssign))
                        and event.value is not None
                    ):
                        targets = (
                            event.targets
                            if isinstance(event, ast.Assign)
                            else [event.target]
                        )
                        raw_digest = digest(event.value)
                        ref = data(event.value) or f"@{event.lineno}"
                        filename = read_path(event.value, local)
                        if filename:
                            raw_files[ref] = filename
                        for target in targets:
                            if isinstance(target, ast.Name):
                                aliases[target.id] = ref
                                local[target.id] = event.value
                                digests.pop(target.id, None)
                                if raw_digest:
                                    digests[target.id] = raw_digest
                    elif isinstance(event, (ast.Try, ast.For, ast.While)):
                        for call in ast.walk(event):
                            if isinstance(call, ast.Call) and _is_manifest_load(call):
                                loads[id(call)] = call
                                unsafe[id(call)] = call
                        verified.clear()
            for identifier, call in loads.items():
                if identifier in unsafe:
                    state.matches.append(
                        match_from_node("SENT-007", file, call, "unverified-manifest")
                    )
                else:
                    state.exempt("verified_manifest")


def load_integrity_manifest(root: Path) -> IntegrityManifest | None:
    path = root / "sentinel.integrity.yaml"
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise ConfigurationError("sentinel.integrity.yaml must be a regular file")
    try:
        value = IntegrityManifest.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
    except Exception as error:
        raise ConfigurationError(f"invalid sentinel.integrity.yaml: {error}") from error
    for manifest, entry in value.manifests.items():
        if Path(manifest).is_absolute() or ".." in Path(manifest).parts:
            raise ConfigurationError(
                "integrity manifest paths must be repository-relative"
            )
        for target in (entry.public_key, entry.signature):
            if target is not None and (
                (root / target).is_symlink()
                or not (root / target).resolve().is_relative_to(root.resolve())
                or not (root / target).is_file()
            ):
                raise TargetError(
                    f"integrity trust-anchor path does not exist: {target}"
                )
    return value


def _is_manifest_load(node: ast.Call) -> bool:
    name = qualified_name(node.func) or ""
    return name in {"json.load", "json.loads", "yaml.safe_load", "yaml.load"}


def _is_manifest_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    name = node.name.lower()
    return "manifest" in name or name in {"load_tools", "register_tools"}


def key_algorithm(pem: str | bytes | None) -> str | None:
    """Parse public-key data with the crypto dependency already required by MCP."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa

    if pem is None:
        return None
    try:
        key = serialization.load_pem_public_key(
            pem.encode() if isinstance(pem, str) else pem
        )
    except (ValueError, TypeError):
        return None
    if isinstance(key, ed25519.Ed25519PublicKey):
        return "ed25519"
    if isinstance(key, rsa.RSAPublicKey):
        return "rsa-pss-sha256"
    return "ecdsa-sha256" if isinstance(key, ec.EllipticCurvePublicKey) else None


def read_path(node: ast.AST, values: dict[str, ast.expr]) -> str | None:
    seen: set[str] = set()
    while isinstance(node, ast.Name) and node.id in values and node.id not in seen:
        seen.add(node.id)
        node = values[node.id]
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr in {
            "read",
            "read_bytes",
            "read_text",
        }:
            return read_path(node.func.value, values)
        if (qualified_name(node.func) or "").split(".")[-1] in {
            "Path",
            "open",
        } and node.args:
            result = literal(node.args[0], values)
            return result if isinstance(result, str) else None
    return None


def anchor_content(
    root: Path, anchors: IntegrityManifest | None, manifest: str | None, field: str
) -> tuple[str, bytes] | None:
    from sentinel.static.traversal import MAX_STATIC_FILE_BYTES

    entry = anchors.manifests.get(manifest) if anchors and manifest else None
    filename = getattr(entry, field, None)
    if not isinstance(filename, str):
        return None
    path = root / filename
    if path.stat().st_size > MAX_STATIC_FILE_BYTES:
        return None
    return filename, path.read_bytes()


def sidecar_digest(
    node: ast.AST, values: dict[str, ast.expr], anchors: IntegrityManifest | None
) -> str | None:
    if anchors is None:
        return None
    seen: set[str] = set()
    while isinstance(node, ast.Name) and node.id in values and node.id not in seen:
        seen.add(node.id)
        node = values[node.id]
    keys: list[object] = []
    while isinstance(node, ast.Subscript):
        keys.insert(0, literal(node.slice, values))
        node = node.value
    while isinstance(node, ast.Name) and node.id in values and node.id not in seen:
        seen.add(node.id)
        node = values[node.id]
    if (
        len(keys) != 3
        or keys[0] != "manifests"
        or keys[2] != "sha256"
        or not isinstance(keys[1], str)
    ):
        return None
    if (
        not isinstance(node, ast.Call)
        or (qualified_name(node.func) or "")
        not in {"yaml.safe_load", "json.loads", "json.load"}
        or not node.args
        or read_path(node.args[0], values) != "sentinel.integrity.yaml"
    ):
        return None
    entry = anchors.manifests.get(keys[1])
    return entry.sha256 if entry else None
