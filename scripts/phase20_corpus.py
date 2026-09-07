"""Phase 20 source identities and extraction; never imports benchmark targets."""

from __future__ import annotations

import hashlib
import io
import re
import tarfile
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/evals/phase20"
SHA256 = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
COMMIT = Annotated[str, Field(pattern=r"^[a-f0-9]{40}$")]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative_path(value: str) -> str:
    """Reject ambiguous/escaping paths on both POSIX and Windows hosts."""
    parts = value.split("/")
    if (
        not value
        or value.startswith("/")
        or any(p in {"", ".", ".."} for p in parts)
        or any(c in value for c in "\\:\x00")
        or any(p.endswith((".", " ")) for p in parts)
        or any(
            re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", p)
            for p in parts
        )
    ):
        raise ValueError(f"unsafe relative path: {value!r}")
    return value


def archive_files(data: bytes, *, strip_root: bool) -> dict[str, bytes]:
    """Read bounded regular files; reject links, devices, collisions and traversal."""
    files: dict[str, bytes] = {}
    seen: set[str] = set()
    roots: set[str] = set()
    total = 0
    if len(data) > 32 * 1024 * 1024:
        raise ValueError("compressed archive size ceiling exceeded")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for index, member in enumerate(archive):
            if index >= 50_000:
                raise ValueError("archive member ceiling exceeded")
            name = relative_path(
                member.name.rstrip("/") if member.isdir() else member.name
            )
            roots.add(name.split("/")[0])
            if member.issparse() or not (member.isfile() or member.isdir()):
                raise ValueError(f"archive links/special files are forbidden: {name}")
            if member.size < 0 or member.size > 16 * 1024 * 1024:
                raise ValueError("archive member size ceiling exceeded")
            total += member.size
            if total > 128 * 1024 * 1024:
                raise ValueError("archive expanded size ceiling exceeded")
            if strip_root:
                _, separator, name = name.partition("/")
                if not separator:
                    if not member.isdir():
                        raise ValueError("expected archive root directory")
                    continue
            folded = unicodedata.normalize("NFC", name).casefold()
            if folded in seen:
                raise ValueError(f"duplicate/case-colliding archive path: {name}")
            seen.add(folded)
            if member.isfile():
                handle = archive.extractfile(member)
                assert handle is not None
                files[name] = handle.read()
    if strip_root and len(roots) != 1:
        raise ValueError("upstream archive must have exactly one root")
    # A file cannot also be the ancestor of another file/directory.
    folded_files = {unicodedata.normalize("NFC", name).casefold() for name in files}
    for name in seen:
        if any(
            str(p) in folded_files for p in PurePosixPath(name).parents if str(p) != "."
        ):
            raise ValueError("archive file/directory collision")
    return files


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Artifact(Record):
    path: str
    sha256: SHA256

    @model_validator(mode="after")
    def check_path(self) -> Artifact:
        relative_path(self.path)
        return self

    def read(self, root: Path = ROOT) -> bytes:
        path = root / self.path
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError(f"symlink artifact: {self.path}")
        data = path.read_bytes()
        if digest(data) != self.sha256:
            raise ValueError(f"artifact hash mismatch: {self.path}")
        return data


class Snapshot(Record):
    repository: str
    revision: COMMIT
    url: str
    archive: Artifact
    files: dict[str, SHA256]
    licenses: list[str] = Field(min_length=1)


class Evidence(Record):
    path: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    sha256: SHA256
    role: str


class Input(Record):
    id: Annotated[str, Field(pattern=r"^[a-z0-9-]+$")]
    family: str
    repository: str
    language: Literal["python", "typescript"]
    split: Literal["development", "held_out"]
    variant: Literal["original", "mutation", "safe_control"]
    label: Literal["vulnerable", "fixed", "safe"]
    snapshot: COMMIT
    scan_root: str
    condition: str
    prerequisites: list[str] = Field(min_length=1)
    static_applicability: str
    runtime_applicability: Literal["eligible", "unsupported"]
    runtime_reason: str
    runtime_configuration: str | None
    evidence: list[Evidence] = Field(min_length=1)
    matching: str
    parent: str | None = None
    transformation: str | None = None
    overlay: Artifact | None = None
    tree_sha256: SHA256


class Family(Record):
    id: str
    advisory: Artifact
    fix_evidence: Artifact
    vulnerable_revision: COMMIT
    fixed_revision: COMMIT
    revision_selection: str


class Manifest(Record):
    version: Literal[1]
    status: Literal["prepared"]
    methodology: str
    snapshots: list[Snapshot]
    families: list[Family]
    inputs: list[Input]
    packet: list[Artifact]

    @model_validator(mode="after")
    def check_membership(self) -> Manifest:
        inputs = {i.id: i for i in self.inputs}
        snapshots = {s.revision: s for s in self.snapshots}
        families = {f.id: f for f in self.families}
        if len(inputs) != len(self.inputs) or len(snapshots) != len(self.snapshots):
            raise ValueError("duplicate input or snapshot identity")
        if len(families) != 10 or len(self.families) != 10 or len(inputs) != 45:
            raise ValueError("corpus requires ten families and 45 labeled inputs")
        repositories: dict[str, set[str]] = {}
        for item in self.inputs:
            if item.family not in families or item.snapshot not in snapshots:
                raise ValueError("unknown family or snapshot")
            if item.repository != snapshots[item.snapshot].repository:
                raise ValueError("snapshot repository mismatch")
            repositories.setdefault(item.repository, set()).add(item.split)
            if item.scan_root != ".":
                relative_path(item.scan_root)
            if item.variant == "mutation":
                parent = inputs.get(item.parent or "")
                if (
                    parent is None
                    or parent.variant != "original"
                    or (
                        parent.family,
                        parent.repository,
                        parent.split,
                        parent.label,
                        parent.snapshot,
                    )
                    != (
                        item.family,
                        item.repository,
                        item.split,
                        item.label,
                        item.snapshot,
                    )
                    or not item.overlay
                    or not item.transformation
                ):
                    raise ValueError("invalid mutation lineage or split leakage")
            elif item.parent or item.overlay or item.transformation:
                raise ValueError("only mutations may have lineage/overlays")
            if (item.variant == "safe_control") != (item.label == "safe"):
                raise ValueError("safe-control label mismatch")
            if (item.runtime_applicability == "eligible") != bool(
                item.runtime_configuration
            ):
                raise ValueError("runtime applicability/configuration mismatch")
        if len(repositories) != 5 or any(len(s) != 1 for s in repositories.values()):
            raise ValueError("repository split leakage or repository count mismatch")
        if repositories != {
            "modelcontextprotocol/servers": {"development"},
            "sooperset/mcp-atlassian": {"held_out"},
            "haris-musa/excel-mcp-server": {"development"},
            "mobile-next/mobile-mcp": {"held_out"},
            "Flux159/mcp-server-kubernetes": {"development"},
        }:
            raise ValueError("repository split differs from approved corpus selection")
        for family in self.families:
            members = [
                i for i in self.inputs if i.family == family.id and i.label != "safe"
            ]
            if sorted((i.variant, i.label) for i in members) != [
                ("mutation", "fixed"),
                ("mutation", "vulnerable"),
                ("original", "fixed"),
                ("original", "vulnerable"),
            ]:
                raise ValueError(
                    "family requires original and mutation vulnerable/fixed pairs"
                )
            for item in members:
                revision = (
                    family.vulnerable_revision
                    if item.label == "vulnerable"
                    else family.fixed_revision
                )
                if item.snapshot != revision:
                    raise ValueError("family revision mismatch")
        for repository in repositories:
            if (
                sum(
                    i.variant == "safe_control" and i.repository == repository
                    for i in self.inputs
                )
                != 1
            ):
                raise ValueError("one safe control required per repository")
        originals = [
            i
            for i in self.inputs
            if i.variant == "original" and i.label == "vulnerable"
        ]
        if sum(i.language == "python" for i in originals) != 7:
            raise ValueError("requires seven Python and three TypeScript families")
        return self


def tree_digest(files: dict[str, bytes]) -> str:
    return digest(
        "".join(
            f"{name}\0{digest(data)}\n" for name, data in sorted(files.items())
        ).encode()
    )


def input_files(item: Input, snapshot: Snapshot, root: Path = ROOT) -> dict[str, bytes]:
    files = archive_files(snapshot.archive.read(root), strip_root=True)
    if {name: digest(data) for name, data in files.items()} != snapshot.files:
        raise ValueError("upstream source inventory mismatch")
    if item.overlay:
        files.update(archive_files(item.overlay.read(root), strip_root=False))
    if tree_digest(files) != item.tree_sha256:
        raise ValueError("input source tree mismatch")
    for evidence in item.evidence:
        relative_path(evidence.path)
        data = files[evidence.path]
        if (
            digest(data) != evidence.sha256
            or not 1
            <= evidence.start_line
            <= evidence.end_line
            <= len(data.splitlines())
        ):
            raise ValueError("source evidence mismatch")
    return files


def validate(path: Path = CORPUS / "manifest.yaml", root: Path = ROOT) -> Manifest:
    manifest = Manifest.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    for artifact in manifest.packet:
        artifact.read(root)
    for family in manifest.families:
        family.advisory.read(root)
        family.fix_evidence.read(root)
    snapshots = {s.revision: s for s in manifest.snapshots}
    packet_paths = {a.path for a in manifest.packet}
    for item in manifest.inputs:
        if (
            item.runtime_configuration
            and item.runtime_configuration not in packet_paths
        ):
            raise ValueError("runtime configuration is not bound by packet hashes")
        snapshot = snapshots[item.snapshot]
        files = input_files(item, snapshot, root)
        for license_path in snapshot.licenses:
            if license_path not in files:
                raise ValueError("missing revision-specific license")
    return manifest


def materialize(
    item: Input,
    snapshot: Snapshot,
    destination: Path,
    packet: list[Artifact],
    root: Path = ROOT,
) -> Path:
    """Write checked bytes into a new temporary tree; never extract tar links."""
    if destination.exists() or any(p.is_symlink() for p in destination.parents):
        raise ValueError(
            "materialization requires a new directory without symlink parents"
        )
    files = input_files(item, snapshot, root)
    destination.mkdir(parents=True)
    for name, data in files.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    scan_root = destination if item.scan_root == "." else destination / item.scan_root
    if not scan_root.is_dir():
        raise ValueError("scan root absent from snapshot")
    if item.runtime_configuration:
        artifacts = {a.path: a for a in packet}
        additions = {
            "git.target.yaml": "sentinel.target.yaml",
            "git.permissions.yaml": "sentinel.permissions.yaml",
            "git-bootstrap.txt": ".phase20/bootstrap.py",
        }
        for source, target in additions.items():
            path = scan_root / target
            if path.exists():
                raise ValueError(
                    "benchmark configuration would overwrite upstream bytes"
                )
            path.parent.mkdir(parents=True, exist_ok=True)
            artifact = artifacts[f"tests/evals/phase20/configuration/{source}"]
            path.write_bytes(artifact.read(root))
    return scan_root
