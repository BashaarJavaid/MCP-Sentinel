"""The new approval packet must preserve source identity and split isolation."""

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.phase20_corpus import ROOT
from scripts.phase22_corpus import CORPUS, Manifest, frozen, validate


def test_phase22_packet_is_complete_but_cannot_approve_itself() -> None:
    manifest = validate()
    assert len(manifest.inputs) == 50
    assert len(manifest.pairs) == 10
    assert manifest.freeze_approved is False
    assert frozen() == manifest

    for field, value in (("freeze_approved", True), ("status", "approved")):
        changed = manifest.model_dump()
        changed[field] = value
        with pytest.raises(ValidationError):
            Manifest.model_validate(changed)

    changed = manifest.model_dump()
    changed["repository_aliases"]["eyemnv/mcp-tool-poisoning-toolkit"] = (
        "integsec/vulnerablemcp"
    )
    with pytest.raises(ValidationError, match="alias crosses"):
        Manifest.model_validate(changed)

    changed = copy.deepcopy(manifest.model_dump())
    changed["inputs"][0]["scan_root"] = "../outside"
    with pytest.raises(ValidationError, match="unsafe relative path"):
        Manifest.model_validate(changed)

    changed = manifest.model_dump()
    mutation = next(item for item in changed["inputs"] if item["variant"] == "mutation")
    mutation["parent"] = "missing-parent"
    with pytest.raises(ValidationError, match="mutation lineage"):
        Manifest.model_validate(changed)


@pytest.mark.parametrize("changed", ["freeze_approved", "sha256"])
def test_freeze_decision_must_authorize_exact_manifest(
    tmp_path: Path, changed: str
) -> None:
    packet = tmp_path / "artifacts/phase22/corpus-review"
    packet.mkdir(parents=True)
    (packet / "manifest.json").write_bytes((CORPUS / "manifest.json").read_bytes())
    decision = json.loads((ROOT / "artifacts/phase22/authorization.json").read_text())
    decision["corpus"][changed] = False if changed == "freeze_approved" else "0" * 64
    (packet.parent / "authorization.json").write_text(json.dumps(decision))
    with pytest.raises(ValueError, match="matching freeze approval"):
        frozen(tmp_path)
