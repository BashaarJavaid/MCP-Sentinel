"""The new approval packet must preserve source identity and split isolation."""

import copy

import pytest
from pydantic import ValidationError

from scripts.phase22_corpus import Manifest, validate


def test_phase22_packet_is_complete_but_cannot_approve_itself() -> None:
    manifest = validate()
    assert len(manifest.inputs) == 50
    assert len(manifest.pairs) == 10
    assert manifest.freeze_approved is False

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
