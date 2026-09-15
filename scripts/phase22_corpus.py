"""Validate the proposed Phase 22 corpus without importing or running targets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from scripts.phase20_corpus import (
    ROOT,
    Artifact,
    Input,
    Record,
    Snapshot,
    digest,
    input_files,
    relative_path,
)

CORPUS = ROOT / "artifacts/phase22/corpus-review"


class Pair(Record):
    id: str
    rule_id: Literal["SENT-012", "SENT-013", "SENT-014", "SENT-015", "SENT-016"]
    fix_origin: Literal["upstream", "evaluator_authored_description_overlay"]
    provenance: list[Artifact] = Field(min_length=1)
    review: str


class Manifest(Record):
    version: Literal[1]
    status: Literal["proposed_pending_user_freeze"]
    freeze_approved: Literal[False]
    methodology: str
    snapshots: list[Snapshot]
    pairs: list[Pair]
    inputs: list[Input]
    packet: list[Artifact]
    repository_aliases: dict[str, str]

    @model_validator(mode="after")
    def check_population(self) -> Manifest:
        inputs = {item.id: item for item in self.inputs}
        snapshots = {item.revision: item for item in self.snapshots}
        pairs = {item.id: item for item in self.pairs}
        if len(inputs) != 50 or len(self.inputs) != 50 or len(pairs) != 10:
            raise ValueError("requires ten pairs, 20 mutations and ten controls")
        if len(snapshots) != len(self.snapshots) or len(pairs) != len(self.pairs):
            raise ValueError("duplicate snapshot or pair identity")
        repositories: dict[str, set[str]] = {}
        for item in self.inputs:
            if item.scan_root != ".":
                relative_path(item.scan_root)
            if item.family not in pairs or item.snapshot not in snapshots:
                raise ValueError("unknown family or snapshot")
            if item.repository != snapshots[item.snapshot].repository:
                raise ValueError("snapshot repository mismatch")
            canonical = self.repository_aliases.get(item.repository.casefold())
            if canonical is None:
                raise ValueError("repository requires a canonical identity")
            repositories.setdefault(canonical.casefold(), set()).add(item.split)
            if (item.variant == "safe_control") != (item.label == "safe"):
                raise ValueError("safe-control label mismatch")
            if (
                item.runtime_configuration
                or item.runtime_applicability != "unsupported"
            ):
                raise ValueError("this source-only packet has no runtime treatment")
            if item.variant == "mutation":
                parent = inputs.get(item.parent or "")
                if (
                    parent is None
                    or parent.variant != "original"
                    or not item.overlay
                    or not item.transformation
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
                ):
                    raise ValueError("invalid mutation lineage or split leakage")
            elif item.parent:
                raise ValueError("only structural mutations have parent IDs")
            elif item.overlay and not (
                item.label == "fixed"
                and pairs[item.family].fix_origin
                == "evaluator_authored_description_overlay"
                and item.transformation
            ):
                raise ValueError("unapproved non-mutation overlay kind")
        if any(len(splits) != 1 for splits in repositories.values()):
            raise ValueError("repository or alias crosses development/held-out split")
        rule_splits: dict[str, list[str]] = {}
        for pair in self.pairs:
            members = [item for item in self.inputs if item.family == pair.id]
            if sorted((item.variant, item.label) for item in members) != [
                ("mutation", "fixed"),
                ("mutation", "vulnerable"),
                ("original", "fixed"),
                ("original", "vulnerable"),
                ("safe_control", "safe"),
            ]:
                raise ValueError(
                    "each pair requires two originals, two mutations, one control"
                )
            if len({(item.repository, item.split) for item in members}) != 1:
                raise ValueError("pair or control crosses repository/split")
            rule_splits.setdefault(pair.rule_id, []).append(members[0].split)
        if len(rule_splits) != 5 or any(
            sorted(splits) != ["development", "held_out"]
            for splits in rule_splits.values()
        ):
            raise ValueError("each rule requires development and held-out pairs")
        return self


def validate(path: Path = CORPUS / "manifest.json", root: Path = ROOT) -> Manifest:
    manifest = Manifest.model_validate_json(path.read_text(encoding="utf-8"))
    for artifact in manifest.packet:
        artifact.read(root)
    for pair in manifest.pairs:
        for artifact in pair.provenance:
            artifact.read(root)
    snapshots = {snapshot.revision: snapshot for snapshot in manifest.snapshots}
    for item in manifest.inputs:
        snapshot = snapshots[item.snapshot]
        files = input_files(item, snapshot, root)
        if item.scan_root != "." and not any(
            name.startswith(item.scan_root + "/") for name in files
        ):
            raise ValueError("scan root absent from snapshot")
        if any(license_path not in files for license_path in snapshot.licenses):
            raise ValueError("missing revision-specific license")
    return manifest


def frozen(root: Path = ROOT, *, approval_path: Path | None = None) -> Manifest:
    """Bind the immutable proposal to the separately recorded user decision."""
    decision = json.loads(
        (approval_path or root / "artifacts/phase22/authorization.json").read_text()
    )
    approval = decision["corpus"]
    path = root / relative_path(approval["manifest"])
    if (
        approval.get("freeze_approved") is not True
        or approval.get("manifest") != path.relative_to(root).as_posix()
        or approval.get("sha256") != digest(path.read_bytes())
    ):
        raise ValueError("Phase 22 corpus lacks matching freeze approval")
    return validate(path, root)


if __name__ == "__main__":
    result = validate()
    print(
        json.dumps(
            {
                "pairs": len(result.pairs),
                "inputs": len(result.inputs),
                "freeze_approved": result.freeze_approved,
            }
        )
    )
