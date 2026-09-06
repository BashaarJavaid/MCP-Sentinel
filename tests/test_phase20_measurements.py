"""Offline benchmark accounting and paid-call gates, using production validation."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from scripts.phase20_measurements import LLM, frozen, serialize_batch, stable_report
from scripts.phase20_review import (
    CheckedCassettes,
    capture_batches,
    request_hash,
    reservation,
    restore_batch,
)
from scripts.phase20_scoring import candidate_identity, metrics, score
from sentinel.llm.semantic_reviewer import SemanticReviewer, _Batch, _BatchResult
from tests.test_gpt_review import FakeTransport


def finding(
    key: str = "a", status: str = "needs_review", *, reviewed: bool = False
) -> dict[str, Any]:
    return {
        "dedup_key": key,
        "status": status,
        "source": "static",
        "review": {"mode": "replay", "reviewed": True, "status": status}
        if reviewed
        else None,
    }


def assess(findings: list[dict[str, Any]], matches: list[str]) -> dict[str, Any]:
    return {
        "candidate_identity": candidate_identity(findings),
        "matches": matches,
        "rationale": "Reviewed the supplied source against the approved condition.",
    }


def test_empty_unrelated_duplicate_and_false_alarm_accounting() -> None:
    empty = score(label="vulnerable", state="completed", findings=[], assessment=None)
    assert empty["completed_miss"]
    unrelated = [finding()]
    unadjudicated = score(
        label="vulnerable", state="completed", findings=unrelated, assessment=None
    )
    assert not unadjudicated["completed_miss"]
    assert unadjudicated["candidate_detected"] is None
    unrelated_result = score(
        label="vulnerable",
        state="completed",
        findings=unrelated,
        assessment=assess(unrelated, []),
    )
    assert unrelated_result["completed_miss"]
    assert unrelated_result["unadjudicated_keys"] == ["a"]
    reviewed_unrelated = [finding(reviewed=True)]
    assert score(
        label="vulnerable",
        state="completed",
        findings=reviewed_unrelated,
        assessment=assess(reviewed_unrelated, []),
    )["review_decisions_all_candidates"] == {"needs_review": 1}
    duplicate = unrelated * 2
    false_alarm = score(
        label="fixed",
        state="completed",
        findings=duplicate,
        assessment=assess(duplicate, ["a"]),
    )
    assert false_alarm["candidate_count"] == 1
    assert false_alarm["duplicate_count"] == 1
    assert false_alarm["false_alarm"]


def test_abstention_and_incorrect_suppression_remain_distinct() -> None:
    findings = [finding("a", reviewed=True), finding("b", "suppressed", reviewed=True)]
    scored = score(
        label="vulnerable",
        state="completed",
        findings=findings,
        assessment=assess(findings, ["a", "b"]),
    )
    assert scored["candidate_detected"] and scored["retained_detected"]
    assert not scored["confirmed_detected"]
    assert scored["abstentions"] == scored["incorrect_suppressions"] == 1
    with pytest.raises(ValueError, match="identity drift"):
        score(
            label="safe",
            state="completed",
            findings=[],
            assessment=assess(findings, []),
        )


def test_incomplete_unsupported_and_zero_denominators() -> None:
    assert metrics([])["candidate"]["completed_recall"] is None
    rows = [
        {
            "label": "vulnerable",
            **score(label="vulnerable", state=state, findings=[], assessment=None),
        }
        for state in ("unsupported", "incomplete", "completed")
    ]
    m = metrics(rows)
    assert (
        m["vulnerable_total"],
        m["vulnerable_applicable"],
        m["vulnerable_completed_adjudicated"],
    ) == (3, 2, 1)
    assert m["candidate"]["completed_recall"] == 0
    assert not rows[0]["completed_miss"] and not rows[1]["completed_miss"]


@pytest.fixture(scope="module")
def batch() -> _Batch:
    # Already-retained exact production request; no live API or target execution.
    value = json.loads(Path("artifacts/phase20/prepare-live/results.json").read_text())
    return restore_batch(next(iter(value["requests"].values())))


def test_request_roundtrip_and_drift(batch: _Batch) -> None:
    saved = json.loads(json.dumps(serialize_batch(batch)))
    assert restore_batch(saved).fingerprint == batch.fingerprint
    changed = json.loads(json.dumps(batch.request))
    data = json.loads(changed["input"])
    data["untrusted_repository_data"]["candidates"][0]["finding_id"] = "other-run-id"
    changed["input"] = json.dumps(data)
    assert request_hash(changed) == request_hash(batch.request)
    saved["request"]["reasoning"] = {"effort": "low"}
    with pytest.raises(ValueError, match="production request"):
        restore_batch(saved)


def test_budget_reserves_cache_writes_output_and_large_context(batch: _Batch) -> None:
    r = reservation(batch.request)
    assert (
        r["cost_micro_usd_reservation"]
        == r["input_token_reservation"] * 5 + r["output_token_reservation"] * 20
    )
    r = reservation({"max_output_tokens": 10, "input": "x" * 280000})
    assert r["cost_micro_usd_reservation"] == r["input_token_reservation"] * 10 + 300


def test_stop_failure_requires_new_decision_and_keeps_reservation(
    tmp_path: Path, batch: _Batch
) -> None:
    calls = []

    async def fail(self: SemanticReviewer, value: _Batch) -> _BatchResult:
        calls.append(value.fingerprint)
        return _BatchResult(value, None, "injected transport failure")

    approval = {"checkpoint": 2, "max_micro_usd": 10000000, "max_requests": 3}
    with (
        patch.object(SemanticReviewer, "_run_batch", fail),
        patch("sentinel.llm.semantic_reviewer.OpenAITransport"),
    ):
        assert (
            asyncio.run(
                capture_batches(
                    [batch, batch], approval, "decision-1", "fake", directory=tmp_path
                )
            )
            == 3
        )
        assert len(calls) == 1
        with pytest.raises(ValueError, match="new user budget decision"):
            asyncio.run(
                capture_batches(
                    [batch], approval, "decision-1", "fake", directory=tmp_path
                )
            )
        approval = {
            **approval,
            "max_micro_usd": reservation(batch.request)["cost_micro_usd_reservation"],
        }
        assert (
            asyncio.run(
                capture_batches(
                    [batch], approval, "decision-2", "fake", directory=tmp_path
                )
            )
            == 3
        )
        assert len(calls) == 1  # Prior failure's reservation is still charged.
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert ledger["attempts"][0]["state"] == "failed"
    assert ledger["attempts"][0]["charged_micro_usd"] > 0


def test_successful_capture_replay_and_drift(tmp_path: Path, batch: _Batch) -> None:
    approval = {"checkpoint": 2, "max_micro_usd": 10000000, "max_requests": 1}
    with patch(
        "sentinel.llm.semantic_reviewer.OpenAITransport", return_value=FakeTransport()
    ):
        assert (
            asyncio.run(
                capture_batches(
                    [batch], approval, "decision-1", "fake", directory=tmp_path
                )
            )
            == 0
        )
    replay = SemanticReviewer(
        root=tmp_path,
        config=LLM,
        max_findings=500,
        mode="replay",
        transport=CheckedCassettes(tmp_path),
    )
    assert asyncio.run(replay._run_batch(batch)).accepted is not None
    path = tmp_path / f"{batch.fingerprint}.json"
    value = json.loads(path.read_text())
    value["latency_ms"] += 1
    path.write_text(json.dumps(value))
    assert asyncio.run(replay._run_batch(batch)).accepted is None
    path.unlink()
    assert asyncio.run(replay._run_batch(batch)).accepted is None


def test_freeze_and_stable_native_reports() -> None:
    assert len(frozen()["manifest_sha256"]) == 64
    report = json.loads(
        Path("artifacts/phase20/rules/git-staging-vulnerable/report.json").read_text()
    )
    changed = json.loads(json.dumps(report))
    changed["scan_id"] = "volatile"
    changed["static_analysis"]["duration_ms"] += 100
    assert stable_report(changed) == stable_report(report)
    changed["analysisComplete"] = False
    assert stable_report(changed) != stable_report(report)


def test_authoritative_runtime_proof_survives_accounting() -> None:
    data = json.loads(
        Path("artifacts/phase17/checkpoint4-review-plan.json").read_text()
    )
    proof = next(
        f
        for f in data["findings"]
        if f["source"] == "dynamic" and f["evidence"].get("proof")
    )
    original = json.dumps(proof, sort_keys=True)
    scored = score(
        label="vulnerable",
        state="inconclusive",
        findings=[proof],
        assessment=assess([proof], [proof["dedup_key"]]),
    )
    assert scored["runtime_confirmations"] == 1
    assert not scored["completed_miss"]
    assert json.dumps(proof, sort_keys=True) == original


def test_capture_process_lock_prevents_second_writer(
    tmp_path: Path, batch: _Batch
) -> None:
    (tmp_path / ".capture.lock").write_text("another approved process")
    with pytest.raises(FileExistsError):
        asyncio.run(
            capture_batches([batch], {}, "decision", "fake", directory=tmp_path)
        )
    assert not (tmp_path / "ledger.json").exists()


def test_offline_measurement_retains_partial_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from scripts.phase20_corpus import validate
    from scripts.phase20_measurements import measure
    from sentinel.errors import InfrastructureError

    manifest = validate()
    manifest = manifest.model_copy(update={"inputs": manifest.inputs[:2]})
    monkeypatch.setenv("OPENAI_API_KEY", "ambient-key-must-not-be-used")
    with patch(
        "scripts.phase20_measurements.run_scan",
        side_effect=InfrastructureError("injected incomplete execution"),
    ):
        result = measure(manifest, "rules", tmp_path / "measurement")
    assert len(result["outcomes"]) == 2
    assert all(o["state"] == "incomplete" for o in result["outcomes"])
    assert result["model_calls"] == 0
    assert all("injected incomplete" in o["reason"] for o in result["outcomes"])


def test_missing_usage_keeps_full_reservation(tmp_path: Path, batch: _Batch) -> None:
    class MissingUsage(FakeTransport):
        async def create(self, request: dict[str, Any]) -> dict[str, Any]:
            response = await super().create(request)
            response["usage"] = {}
            return response

    approval = {"checkpoint": 2, "max_micro_usd": 10000000, "max_requests": 1}
    with patch(
        "sentinel.llm.semantic_reviewer.OpenAITransport", return_value=MissingUsage()
    ):
        assert (
            asyncio.run(
                capture_batches(
                    [batch], approval, "decision", "fake", directory=tmp_path
                )
            )
            == 3
        )
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert ledger["attempts"][0]["state"] == "failed"
    assert (
        ledger["attempts"][0]["charged_micro_usd"]
        == reservation(batch.request)["cost_micro_usd_reservation"]
    )
    assert not (tmp_path / f"{batch.fingerprint}.json").exists()
