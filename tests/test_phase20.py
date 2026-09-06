"""Preparation gates run offline; none of these tests evaluate corpus targets."""

from __future__ import annotations

import ast
import io
import json
import socket
import tarfile
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from scripts.phase20_corpus import (
    CORPUS,
    ROOT,
    Artifact,
    Manifest,
    archive_files,
    digest,
    input_files,
    materialize,
    relative_path,
    validate,
)
from scripts.prepare_phase20_corpus import mutate, write_overlay
from scripts.prepare_phase20_semgrep import select
from scripts.run_phase20_benchmark import validate_comparator_metadata
from sentinel.config import load_configuration


@pytest.fixture(scope="module")
def manifest() -> Manifest:
    return validate()


def archive(entries: list[tuple[str, bytes, bytes]]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as handle:
        for name, data, kind in entries:
            member = tarfile.TarInfo(name)
            member.type = kind
            member.size = len(data) if kind == tarfile.REGTYPE else 0
            member.linkname = (
                "../outside" if kind in {tarfile.SYMTYPE, tarfile.LNKTYPE} else ""
            )
            handle.addfile(member, io.BytesIO(data))
    return buffer.getvalue()


def test_retained_corpus_integrity_and_labels(manifest: Manifest) -> None:
    assert len(manifest.inputs) == 45
    assert len(manifest.families) == 10
    assert len(manifest.snapshots) == 17
    assert sum(i.split == "held_out" for i in manifest.inputs) == 18
    assert sum(i.runtime_applicability == "eligible" for i in manifest.inputs) == 13
    assert sum(i.label == "vulnerable" for i in manifest.inputs) == 20
    assert sum(i.label == "safe" for i in manifest.inputs) == 5
    assert all(s.licenses for s in manifest.snapshots)


@pytest.mark.parametrize(
    "change", ["duplicate", "split", "lineage", "revision", "missing", "extra"]
)
def test_manifest_rejects_drift(manifest: Manifest, change: str) -> None:
    data = manifest.model_dump(mode="json")
    if change == "duplicate":
        data["inputs"][1]["id"] = data["inputs"][0]["id"]
    elif change == "split":
        data["inputs"][1]["split"] = "held_out"
    elif change == "lineage":
        data["inputs"][1]["parent"] = data["inputs"][4]["id"]
    elif change == "revision":
        data["inputs"][0]["snapshot"] = data["inputs"][2]["snapshot"]
    elif change == "missing":
        data["inputs"].pop()
    else:
        data["approved"] = True
    with pytest.raises(ValidationError):
        Manifest.model_validate(data)


@pytest.mark.parametrize(
    "path",
    [
        "../escape",
        "/absolute",
        "a/../escape",
        "a\\b",
        "C:/file",
        "a//b",
        "a/./b",
        "a\x00b",
        "CON",
        "aux.txt",
        "a./b",
        "a /b",
    ],
)
def test_portable_path_boundary(path: str) -> None:
    with pytest.raises(ValueError, match="unsafe relative path"):
        relative_path(path)


@pytest.mark.parametrize(
    "kind", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.CHRTYPE, tarfile.FIFOTYPE]
)
def test_links_and_special_files_never_extract(kind: bytes) -> None:
    data = archive([("root/linked", b"", kind)])
    with pytest.raises(ValueError, match="links/special"):
        archive_files(data, strip_root=True)


@pytest.mark.parametrize(
    "names",
    [
        ("root/a", "root/a"),
        ("root/A", "root/a"),
        ("root/a", "root/a/b"),
        ("root/é", "root/e\u0301"),
        ("root/a", "other/b"),
    ],
)
def test_archive_collisions(names: tuple[str, str]) -> None:
    data = archive([(n, b"data", tarfile.REGTYPE) for n in names])
    with pytest.raises(ValueError):
        archive_files(data, strip_root=True)


def test_archive_traversal_rejected_before_materialization(tmp_path: Path) -> None:
    data = archive([("root/../../escape", b"data", tarfile.REGTYPE)])
    with pytest.raises(ValueError):
        archive_files(data, strip_root=True)
    assert list(tmp_path.iterdir()) == []


def test_source_checksum_drift_is_fatal(tmp_path: Path) -> None:
    path = tmp_path / "source"
    path.write_bytes(b"original")
    item = Artifact(path="source", sha256=digest(b"original"))
    assert item.read(tmp_path) == b"original"
    path.write_bytes(b"modified")
    with pytest.raises(ValueError, match="hash mismatch"):
        item.read(tmp_path)


def test_artifact_symlink_rejected(tmp_path: Path) -> None:
    path = tmp_path / "source"
    path.write_bytes(b"original")
    link = tmp_path / "link"
    try:
        link.symlink_to(path)
    except OSError:
        pytest.skip("host does not permit creating symlinks")
    with pytest.raises(ValueError, match="symlink"):
        Artifact(path="link", sha256=digest(b"original")).read(tmp_path)


def test_mutations_reproduce_without_execution(
    manifest: Manifest, tmp_path: Path
) -> None:
    snapshots = {s.revision: s for s in manifest.snapshots}
    originals = {i.id: i for i in manifest.inputs if i.variant == "original"}
    for item in manifest.inputs:
        if item.variant != "mutation":
            continue
        assert item.parent is not None and item.overlay is not None
        parent = originals[item.parent]
        before = input_files(parent, snapshots[parent.snapshot])
        changed = mutate(item.family, before, parent.evidence[0].path)
        assert changed
        regenerated = tmp_path / f"{item.id}.tar.gz"
        write_overlay(regenerated, changed)
        assert archive_files(
            regenerated.read_bytes(), strip_root=False
        ) == archive_files(item.overlay.read(), strip_root=False)
        for name, data in changed.items():
            if name.endswith(".py"):
                ast.parse(data, filename=name)
        if item.family == "mobile-output":
            assert changed["src/server.ts"].startswith(b"// Modified for Phase 20:")


def test_materialization_loads_config_without_target_execution(
    manifest: Manifest, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def network_forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("preparation attempted network access")

    monkeypatch.setenv("OPENAI_API_KEY", "dummy-must-not-be-used")
    monkeypatch.setenv("SENTINEL_RULES_ONLY", "false")
    monkeypatch.setenv("SENTINEL_LLM_BASE_URL", "https://invalid.example")
    monkeypatch.setattr(socket, "create_connection", network_forbidden)
    item = manifest.inputs[0]
    snapshot = next(s for s in manifest.snapshots if s.revision == item.snapshot)
    root = materialize(item, snapshot, tmp_path / "input", manifest.packet)
    loaded = load_configuration(
        root,
        environ={},
        cli_overrides={"rules_only": True, "ignore_paths": [".phase20/**"]},
    )
    assert loaded.scanner.scanner.rules_only
    assert loaded.scanner.scanner.max_findings_per_scan == 500
    assert loaded.target is None
    dynamic = load_configuration(root, environ={})
    assert dynamic.target is not None
    assert dynamic.target.env_from == ()
    assert dynamic.target.probe_baselines["git_diff"]["target"] == "HEAD"
    assert not (root / "control.txt").exists()
    with pytest.raises(ValueError, match="new directory"):
        materialize(item, snapshot, tmp_path / "input", manifest.packet)


def test_pending_measurements_cannot_become_completed_misses(
    manifest: Manifest,
) -> None:
    validate_comparator_metadata()
    result = json.loads(
        (ROOT / "artifacts/phase20/preparation-results.json").read_text()
    )
    assert result["metrics"] is None
    assert result["model_requests"] == result["live_spend_micro_usd"] == 0
    assert len(result["outcomes"]) == 45
    for row in result["outcomes"]:
        for treatment in row["treatments"].values():
            assert treatment["state"] == "not_evaluated"
            assert treatment["finding_count"] is None
    assert result["manifest_sha256"] == digest((CORPUS / "manifest.yaml").read_bytes())


def test_comparator_selection_uses_category_and_language() -> None:
    def rule(name: str, language: str, category: str) -> dict[str, Any]:
        return {
            "id": name,
            "languages": [language],
            "pattern": "example()",
            "metadata": {"category": category},
        }

    rules = [
        rule("py", "python", "security"),
        rule("ts", "typescript", "security"),
        rule("style", "python", "style"),
        rule("go", "go", "security"),
    ]
    data = yaml.safe_dump({"rules": rules}).encode()
    configs, identities = select(archive([("root/rules.yaml", data, tarfile.REGTYPE)]))
    assert [r["id"] for r in identities] == ["py", "ts"]
    assert len(yaml.safe_load(configs["rules.yaml"])["rules"]) == 2
    metadata = json.loads(
        (ROOT / "artifacts/phase20/semgrep-preparation.json").read_text()
    )
    assert metadata["rule_count"] == 533
    assert metadata["redistributed_rule_bytes"] is False
