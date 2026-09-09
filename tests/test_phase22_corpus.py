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


def test_phase22_measurement_rejects_unapproved_changes(tmp_path: Path) -> None:
    from scripts.phase20_measurements import measure
    from scripts.phase22_corpus import frozen

    approved = frozen()
    item = next(i for i in approved.inputs if i.split == "development")
    changed = approved.model_copy(
        update={
            "inputs": [item.model_copy(update={"condition": "changed condition"})],
        }
    )
    with pytest.raises(ValueError, match="authorized inputs"):
        measure(changed, "rules", tmp_path / "changed")
    assert not (tmp_path / "changed").exists()
    with pytest.raises(ValueError, match="source-only"):
        measure(approved, "dynamic", tmp_path / "runtime")
    assert not (tmp_path / "runtime").exists()


@pytest.mark.parametrize("treatment", ["prepare-live", "replay", "semgrep"])
def test_phase22_offline_treatments_keep_separate_capture_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, treatment: str
) -> None:
    from scripts import phase20_measurements as measurements
    from scripts import phase20_review
    from sentinel.llm import semantic_reviewer

    approved = frozen()
    item = next(i for i in approved.inputs if i.split == "development")

    def materialize(*args: object) -> Path:
        root = tmp_path / "source"
        root.mkdir()
        (root / "requirements.txt").write_text("mcp==1.29.0\n")
        (root / "server.py").write_text(
            "import subprocess\nfrom mcp.server.fastmcp import FastMCP\n"
            'mcp=FastMCP("test")\n@mcp.tool()\n'
            "def run(command: str):\n"
            "    return subprocess.check_output(command, shell=True)\n"
        )
        return root

    def forbid_live(*args: object, **kwargs: object) -> None:
        pytest.fail("offline corpus treatment constructed a live model transport")

    roots = []
    checked = phase20_review.CheckedCassettes

    def capture_transport(root: Path) -> phase20_review.CheckedCassettes:
        roots.append(root)
        return checked(root)

    monkeypatch.setattr(measurements, "materialize", materialize)
    monkeypatch.setattr(semantic_reviewer, "OpenAITransport", forbid_live)
    monkeypatch.setattr(phase20_review, "CheckedCassettes", capture_transport)
    monkeypatch.setattr(measurements, "verify_rules", lambda root: None)
    monkeypatch.setattr(
        measurements,
        "run_comparator",
        lambda *args: {"state": "completed", "exit_code": 0, "finding_count": 0},
    )
    result = measurements.measure(
        approved.model_copy(update={"inputs": [item]}),
        treatment,
        tmp_path / "measurement",
        rules_dir=tmp_path / "rules",
    )
    assert result["model_calls"] == 0
    assert len(result["outcomes"]) == 1
    outcome = result["outcomes"][0]
    if treatment == "semgrep":
        assert outcome["state"] == "completed"
        assert not roots
    else:
        assert roots == [ROOT / "artifacts/phase22/captures"]
        assert outcome["state"] == (
            "review_pending" if treatment == "prepare-live" else "incomplete"
        )
        assert bool(result["requests"]) is (treatment == "prepare-live")
