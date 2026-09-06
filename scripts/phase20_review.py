"""Exact production-request preparation, approved spending, and checked replay."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.capture_gpt_reviews import _atomic_json, _sanitize_raw_response
from scripts.phase20_corpus import ROOT, digest
from scripts.phase20_measurements import ARTIFACTS, LLM, frozen, scanner_identity
from sentinel.finding import Finding
from sentinel.llm.context import FindingContext
from sentinel.llm.semantic_reviewer import (
    CassetteTransport,
    SemanticReviewer,
    _Batch,
    _Candidate,
    _cost,
    _request,
    _request_fingerprint,
)
from sentinel.llm.tools import ToolMetadata


def request_hash(request: dict[str, Any]) -> str:
    value = {k: v for k, v in request.items() if not k.startswith("_sentinel_")}
    data = json.loads(value["input"])
    for index, candidate in enumerate(data["untrusted_repository_data"]["candidates"]):
        candidate["finding_id"] = f"slot-{index}"
    value["input"] = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def restore_batch(value: dict[str, Any]) -> _Batch:
    candidates = tuple(
        _Candidate(
            Finding.model_validate_json(
                json.dumps(
                    {
                        k: v
                        for k, v in c["finding"].items()
                        if k not in Finding.model_computed_fields
                    }
                )
            ),
            FindingContext.model_validate_json(json.dumps(c["context"])),
            ToolMetadata.model_validate_json(json.dumps(c["tool"]))
            if c["tool"]
            else None,
        )
        for c in value["candidates"]
    )
    fingerprint = _request_fingerprint(candidates, LLM)
    if (
        fingerprint != value["fingerprint"]
        or _request(candidates, LLM, fingerprint) != value["request"]
    ):
        raise ValueError("prepared request differs from current production request")
    return _Batch(candidates, value["request"], fingerprint, value["batch_id"])


def reservation(request: dict[str, Any]) -> dict[str, int]:
    # UTF-8 byte bound avoids tokenizer downloads; add a framing/schema margin.
    tokens = len(json.dumps(request, ensure_ascii=False).encode()) + 4096
    output = int(request["max_output_tokens"])
    long = tokens > 272_000
    return {
        "input_token_reservation": tokens,
        "output_token_reservation": output,
        "cost_micro_usd_reservation": tokens * (10 if long else 5)
        + output * (30 if long else 20),
    }


def prepare_packet(measurement: dict[str, Any], directory: Path) -> dict[str, Any]:
    requests = []
    for fingerprint, value in sorted(measurement["requests"].items()):
        restore_batch(value)
        requests.append(
            {
                "fingerprint": fingerprint,
                "input_ids": value["inputs"],
                "request_sha256": request_hash(value["request"]),
                "candidate_count": len(value["candidates"]),
                **reservation(value["request"]),
            }
        )
    packet = {
        "version": 1,
        "stage": "runtime" if measurement["treatment"] == "dynamic" else "static",
        "checkpoint": 3 if measurement["treatment"] == "dynamic" else 2,
        "manifest_sha256": frozen()["manifest_sha256"],
        "measurement_sha256": digest((directory / "results.json").read_bytes()),
        "scanner_source_sha256": measurement["scanner"]["source_sha256"],
        "settings": LLM.model_dump(mode="json"),
        "pricing": {
            "as_of": "2026-09-06",
            "source": "https://developers.openai.com/api/docs/models/gpt-5.6-sol",
            "input_usd_per_million": 4,
            "cached_input_usd_per_million": 0.4,
            "output_usd_per_million": 20,
            "cache_write_multiplier": 1.25,
            "long_context_threshold_tokens": 272000,
            "long_context_input_multiplier": 2,
            "long_context_output_multiplier": 1.5,
        },
        "reservation_method": (
            "Full serialized request UTF-8 bytes plus 4096 framing tokens; "
            "all input charged at cache-write rate; no cache discount; "
            "long-context premium when bound exceeds 272000; full output cap."
        ),
        "requests": requests,
        "request_count": len(requests),
        "reserved_micro_usd": sum(r["cost_micro_usd_reservation"] for r in requests),
        "approved_ceiling_micro_usd": None,
        "stop_policy": (
            "Serial requests, retries=0, cache disabled. Persist in-flight "
            "reservation before send. Stop on first failure or unaffordable "
            "request. Further attempts require a new user decision; retain "
            "successful captures and unresolved reservations."
        ),
    }
    _atomic_json(directory / "budget-packet.json", packet)
    return packet


class CheckedCassettes(CassetteTransport):
    async def create(self, request: dict[str, Any]) -> dict[str, Any]:
        fingerprint = request["_sentinel_request_fingerprint"]
        payload_path = self.root / f"{fingerprint}.json"
        payload = json.loads(payload_path.read_text())
        if payload["fingerprint"] != fingerprint or payload[
            "request_sha256"
        ] != request_hash(request):
            raise ValueError("cassette request drift")
        ledger = json.loads((self.root / "ledger.json").read_text())
        if not any(
            a.get("state") == "accepted"
            and a["fingerprint"] == fingerprint
            and a["cassette_sha256"] == digest(payload_path.read_bytes())
            for a in ledger["attempts"]
        ):
            raise ValueError("cassette has no matching accepted capture ledger entry")
        return await super().create(request)


def capture(stage: str, approval_path: Path) -> int:
    directory = ARTIFACTS / ("prepare-live" if stage == "static" else "dynamic")
    measurement = json.loads((directory / "results.json").read_text())
    packet = json.loads((directory / "budget-packet.json").read_text())
    approval = json.loads(approval_path.read_text())
    if (
        approval["packet_sha256"]
        != digest((directory / "budget-packet.json").read_bytes())
        or packet["measurement_sha256"]
        != digest((directory / "results.json").read_bytes())
        or packet["manifest_sha256"] != frozen()["manifest_sha256"]
        or packet["scanner_source_sha256"] != scanner_identity()["source_sha256"]
        or approval["checkpoint"] != packet["checkpoint"]
        or approval["stage"] != stage
        or not approval["user_decision"]
        or type(approval["max_micro_usd"]) is not int
        or approval["max_micro_usd"] <= 0
        or type(approval["max_requests"]) is not int
        or approval["max_requests"] < 0
    ):
        raise ValueError("approval, budget, packet, or scanner identity mismatch")
    batches = [
        restore_batch(measurement["requests"][r["fingerprint"]])
        for r in packet["requests"]
    ]
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("approved live capture requires OPENAI_API_KEY")
    return asyncio.run(
        capture_batches(batches, approval, digest(approval_path.read_bytes()), api_key)
    )


async def capture_batches(
    batches: list[_Batch],
    approval: dict[str, Any],
    approval_hash: str,
    api_key: str,
    *,
    directory: Path = ARTIFACTS / "captures",
) -> int:
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / ".capture.lock"
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(approval_hash)
        return await _capture_batches(
            batches, approval, approval_hash, api_key, directory
        )
    finally:
        lock.unlink()


async def _capture_batches(
    batches: list[_Batch],
    approval: dict[str, Any],
    approval_hash: str,
    api_key: str,
    directory: Path,
) -> int:
    directory.mkdir(parents=True, exist_ok=True)
    ledger_path = directory / "ledger.json"
    ledger: dict[str, Any] = (
        json.loads(ledger_path.read_text())
        if ledger_path.exists()
        else {"version": 1, "attempts": [], "decisions": {}}
    )
    prior = ledger["decisions"].get(approval_hash)
    if prior and prior["state"] != "complete":
        raise ValueError(
            "stopped or interrupted capture requires a new user budget decision"
        )
    decision = {"approval": approval, "state": "running"}
    ledger["decisions"][approval_hash] = decision
    _atomic_json(ledger_path, ledger)
    reviewer: SemanticReviewer | None = None
    for batch in batches:
        path = directory / f"{batch.fingerprint}.json"
        if path.exists():
            replay = SemanticReviewer(
                root=ROOT,
                config=LLM,
                max_findings=500,
                mode="replay",
                transport=CheckedCassettes(directory),
            )
            check = await replay._run_batch(batch)
            if check.accepted is None:
                decision.update(
                    state="stopped", reason="existing capture missing or drifted"
                )
                _atomic_json(ledger_path, ledger)
                return 3
            continue
        reserved = reservation(batch.request)["cost_micro_usd_reservation"]
        # Ceilings are cumulative across restarts, including uncertain failed charges.
        stage_attempts = [
            a
            for a in ledger["attempts"]
            if a["stage"] == approval.get("stage", "static")
        ]
        charged = sum(a["charged_micro_usd"] for a in stage_attempts)
        if (
            charged + reserved > approval["max_micro_usd"]
            or len(stage_attempts) >= approval["max_requests"]
        ):
            decision.update(
                state="stopped",
                reason="next request is unaffordable or request ceiling reached",
            )
            _atomic_json(ledger_path, ledger)
            return 3
        attempt = {
            "fingerprint": batch.fingerprint,
            "approval_sha256": approval_hash,
            "stage": approval.get("stage", "static"),
            "state": "in_flight",
            "charged_micro_usd": reserved,
            "reservation_micro_usd": reserved,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        ledger["attempts"].append(attempt)
        _atomic_json(ledger_path, ledger)
        if reviewer is None:
            reviewer = SemanticReviewer(
                root=ROOT, config=LLM, max_findings=500, mode="live", api_key=api_key
            )
        result = await reviewer._run_batch(batch)
        accepted = result.accepted
        if accepted is None:
            attempt.update(state="failed", reason=result.failure)
            decision.update(
                state="stopped",
                reason="first failed request; billing uncertain, reservation retained",
            )
            _atomic_json(ledger_path, ledger)
            return 3
        if accepted.usage.input_tokens is None or accepted.usage.output_tokens is None:
            attempt.update(
                state="failed", reason="response lacks complete usage telemetry"
            )
            decision.update(
                state="stopped", reason="billing uncertain, reservation retained"
            )
            _atomic_json(ledger_path, ledger)
            return 3
        payload = {
            "cassette_version": 1,
            "checkpoint": approval["checkpoint"],
            "fingerprint": batch.fingerprint,
            "request_sha256": request_hash(batch.request),
            "captured_at": accepted.reviewed_at.isoformat(),
            "requested_model": LLM.model,
            "returned_model": accepted.returned_model,
            "reasoning_effort": "medium",
            "usage": accepted.usage.model_dump(mode="json"),
            "latency_ms": accepted.latency_ms,
            "retry_count": accepted.retries,
            "batch_id": batch.batch_id,
            "cost_micro_usd": _cost(accepted.usage),
            "response": _sanitize_raw_response(accepted.raw, batch.fingerprint),
        }
        _atomic_json(path, payload)
        attempt.update(
            state="accepted",
            charged_micro_usd=payload["cost_micro_usd"],
            cassette_sha256=digest(path.read_bytes()),
        )
        _atomic_json(ledger_path, ledger)
        if payload["cost_micro_usd"] > reserved:
            decision.update(
                state="stopped", reason="reported usage exceeded reservation"
            )
            _atomic_json(ledger_path, ledger)
            return 3
    decision["state"] = "complete"
    _atomic_json(ledger_path, ledger)
    return 0
