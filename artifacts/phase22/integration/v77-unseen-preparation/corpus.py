"""Six-input artifact schema; reuse production source validation and approval gates."""
from pathlib import Path
from typing import Literal
from unittest.mock import patch

from pydantic import model_validator
from scripts import phase22_corpus as existing
from scripts.phase20_corpus import relative_path


class Pair(existing.Pair):
    rule_id: Literal["SENT-002", "SENT-012"]


class Manifest(existing.Manifest):
    pairs: list[Pair]

    @model_validator(mode="after")
    def check_population(self):
        inputs = {i.id: i for i in self.inputs}
        snapshots = {s.revision: s for s in self.snapshots}
        pairs = {p.id: p for p in self.pairs}
        if (len(inputs), len(self.inputs), len(snapshots), len(self.snapshots), len(pairs), len(self.pairs)) != (6, 6, 4, 4, 2, 2):
            raise ValueError("requires exactly two repositories, four snapshots and six inputs")
        repositories = set()
        languages = set()
        for pair in self.pairs:
            members = [i for i in self.inputs if i.family == pair.id]
            if sorted((i.variant, i.label) for i in members) != [("original", "fixed"), ("original", "vulnerable"), ("safe_control", "safe")]:
                raise ValueError("requires vulnerable/fixed/safe originals; no mutations")
            if len({(i.repository, i.language) for i in members}) != 1:
                raise ValueError("pair crosses repository or language")
            repositories.add(members[0].repository)
            languages.add(members[0].language)
            fixed = next(i for i in members if i.label == "fixed")
            safe = next(i for i in members if i.label == "safe")
            if (fixed.snapshot, fixed.tree_sha256, fixed.scan_root) != (safe.snapshot, safe.tree_sha256, safe.scan_root):
                raise ValueError("safe control must retain complete fixed source")
        if len(repositories) != 2 or languages != {"python", "typescript"}:
            raise ValueError("requires distinct Python and TypeScript repositories")
        if {p.rule_id for p in self.pairs} != {"SENT-002", "SENT-012"}:
            raise ValueError("unexpected named condition rules")
        for item in self.inputs:
            if item.family not in pairs or item.snapshot not in snapshots or item.repository != snapshots[item.snapshot].repository:
                raise ValueError("unknown family/snapshot or mismatched repository")
            if item.split != "held_out" or item.runtime_configuration or item.runtime_applicability != "unsupported" or item.parent or item.overlay or item.transformation:
                raise ValueError("only unchanged source-only first-frozen inputs allowed")
            if self.repository_aliases.get(item.repository.casefold()) != item.repository:
                raise ValueError("missing canonical repository identity")
            if item.scan_root != ".":
                relative_path(item.scan_root)
        return self


def validate(path: Path):
    with patch.object(existing, "Manifest", Manifest):
        return existing.validate(path)


def frozen(*, approval_path: Path):
    with patch.object(existing, "Manifest", Manifest):
        return existing.frozen(approval_path=approval_path)
