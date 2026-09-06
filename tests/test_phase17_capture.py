"""The Phase 17 refresh must use frozen inputs and a separate paid-call budget."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, cast

import pytest

from scripts import capture_phase17_reviews as capture


def _plan() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(capture.PREPARED.read_text()))


def test_prepared_batch_rejects_changed_request_identity() -> None:
    plan = _plan()
    assert len(capture.prepared_batch(plan)) == 4
    plan["request_sha256"] = "0" * 64
    with pytest.raises(RuntimeError, match="inputs changed"):
        capture.prepared_batch(plan)


def test_budget_failure_precedes_key_access_or_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_get = os.environ.get

    def reject(key: str, default: str | None = None) -> str | None:
        if key == "OPENAI_API_KEY":
            raise AssertionError("budget rejection must precede key access")
        return original_get(key, default)

    monkeypatch.setattr(os.environ, "get", reject)
    with pytest.raises(ValueError, match="ceiling"):
        capture.capture(0.000001)


def test_existing_capture_is_never_replaced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "phase17").mkdir()
    monkeypatch.setattr(capture, "CASSETTES", tmp_path)
    with pytest.raises(RuntimeError, match="never replace"):
        capture.capture(1)


def test_demo_selects_current_capture_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sentinel.cli import _materialized_demo_resources

    fixture = tmp_path / "_fixtures" / "vulnerable_server"
    fixture.mkdir(parents=True)
    (fixture / "server.py").write_text("# inert resource-copy control\n")
    for name in ("demo", "phase17"):
        directory = tmp_path / "_cassettes" / name
        directory.mkdir(parents=True)
        (directory / "marker.txt").write_text(name)
    monkeypatch.setattr("sentinel.cli.resources.files", lambda _: tmp_path)
    with _materialized_demo_resources() as (_, cassettes):
        assert (cassettes / "marker.txt").read_text() == "phase17"


def test_capture_reuses_static_inputs_and_replays_one_synthetic_response(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tests.test_gpt_review import FakeTransport

    cassettes = tmp_path / "cassettes"
    cassettes.mkdir()
    monkeypatch.setattr(capture, "CASSETTES", cassettes)
    monkeypatch.setattr(capture, "ARTIFACTS", tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-test-key")
    transport = FakeTransport()
    monkeypatch.setattr(
        "sentinel.llm.semantic_reviewer.OpenAITransport",
        lambda *args: transport,
    )
    capture.capture(0.17)
    assert transport.calls == 1
    destination = cassettes / "phase17"
    assert len(list(destination.glob("*.json"))) == 6
    manifest = json.loads((destination / "manifest.json").read_text())
    assert len(manifest["batches"]) == 1
    assert len(manifest["reused_captures"]) == 4
    replay = json.loads((tmp_path / "checkpoint4-runtime-review.json").read_text())
    assert replay["gpt_review"]["mode"] == "replay"
    assert all(item["status"] == "confirmed" for item in replay["findings"])
