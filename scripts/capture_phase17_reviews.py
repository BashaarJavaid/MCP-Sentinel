"""Prepare exact runtime-review inputs; capture only after separate budget approval."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from scripts.capture_gpt_reviews import (
    CASSETTES,
    ROOT,
    _atomic_json,
    _batches_for_findings,
    _capture,
)
from sentinel.config import LlmConfig, load_configuration
from sentinel.dynamic.prober import run_dynamic_scan
from sentinel.dynamic.sandbox import DockerSandbox, reap_orphans
from sentinel.finding import Finding, TokenUsage
from sentinel.llm.semantic_reviewer import SemanticReviewer, _cost
from sentinel.static.engine import run_static_scan

ARTIFACTS = ROOT / "artifacts" / "phase17"
PREPARED = ARTIFACTS / "checkpoint4-review-plan.json"
FIXTURE = ROOT / "tests" / "fixtures" / "vulnerable_server"
CONFIG = LlmConfig(retries=0, max_concurrency=1, cache_enabled=False)


def _request_sha(request: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()


def prepare() -> None:
    """Replay unchanged static judgments, then collect current Docker proof."""
    loaded = load_configuration(FIXTURE, environ={})
    scan_id, now = uuid4(), datetime.now(timezone.utc)
    static = run_static_scan(loaded, scan_id, timestamp=now)
    reviewed = SemanticReviewer(
        root=FIXTURE,
        config=CONFIG,
        max_findings=500,
        mode="replay",
        cassette_root=CASSETTES / "demo",
    ).review(static.findings, allow_degraded=False)
    if reviewed.fatal:
        raise RuntimeError("static inputs changed; prepare a separately scoped refresh")
    reap_orphans()
    dynamic = run_dynamic_scan(
        DockerSandbox(loaded, scan_id),
        reviewed.findings,
        scan_id=scan_id,
        timestamp=now,
    )
    if not dynamic.complete or not dynamic.execution_successful:
        raise RuntimeError("cannot prepare live review from an incomplete campaign")
    if {item.rule_id for item in dynamic.findings} != {
        "SENT-008",
        "SENT-009",
        "SENT-010",
        "SENT-011",
    }:
        raise RuntimeError("reference campaign did not demonstrate all four violations")
    batches = _batches_for_findings(FIXTURE, dynamic.findings, CONFIG)
    if len(batches) != 1:
        raise RuntimeError("Phase 17 refresh is bounded to one runtime batch")
    batch = batches[0]
    # UTF-8 request bytes conservatively bound tokens; reserve all input at the
    # stored cache-write rate, plus the enforced output ceiling. No tokenizer fetch.
    input_ceiling = len(json.dumps(batch.request, ensure_ascii=False).encode())
    reservation = _cost(
        TokenUsage(
            input_tokens=input_ceiling,
            cache_write_tokens=input_ceiling,
            output_tokens=batch.request["max_output_tokens"],
        )
    )
    reused = []
    for item in reviewed.summary.batches:
        path = CASSETTES / "demo" / f"{item.request_fingerprint}.json"
        reused.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    _atomic_json(
        PREPARED,
        {
            "checkpoint": "phase17",
            "prepared_at": now.isoformat(),
            "purpose": (
                "Review SENT-008/009/010/011 proof with valid baselines; "
                "verify host proof remains authoritative."
            ),
            "model": CONFIG.model,
            "reasoning_effort": CONFIG.reasoning_effort.value,
            "request_count": 1,
            "retries": 0,
            "input_token_ceiling": input_ceiling,
            "output_token_ceiling": batch.request["max_output_tokens"],
            "reservation_micro_usd_at_stored_rates": reservation,
            "stopping_condition": (
                "Stop after one request, or immediately on budget/input drift, "
                "transport, schema, or review-validation failure. "
                "No retry or replacement."
            ),
            "request_fingerprint": batch.fingerprint,
            "request_sha256": _request_sha(batch.request),
            "request": batch.request,
            "reused_captures": reused,
            "dynamic_analysis": dynamic.summary.model_dump(mode="json"),
            "findings": [
                item.model_dump(mode="json", exclude={"severity", "review_disagrees"})
                for item in dynamic.findings
            ],
        },
    )
    print(f"Prepared {PREPARED.relative_to(ROOT)}")
    print(
        f"Reuse {len(reused)} static captures; one new runtime request, "
        f"<= {input_ceiling} input tokens and "
        f"{batch.request['max_output_tokens']} output tokens."
    )
    print(f"Stored-rate reservation with cache writes: ${reservation / 1_000_000:.6f}")


def prepared_batch(data: dict[str, Any]) -> tuple[Finding, ...]:
    findings = tuple(
        Finding.model_validate_json(json.dumps(item)) for item in data["findings"]
    )
    batches = _batches_for_findings(FIXTURE, findings, CONFIG)
    if (
        len(batches) != 1
        or batches[0].fingerprint != data["request_fingerprint"]
        or _request_sha(batches[0].request) != data["request_sha256"]
    ):
        raise RuntimeError(
            "prepared review inputs changed; new preparation/approval required"
        )
    for item in data["reused_captures"]:
        if (
            hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
            != item["sha256"]
        ):
            raise RuntimeError("retained static capture changed")
    return findings


def capture(max_usd: float) -> None:
    data = json.loads(PREPARED.read_text())
    findings = prepared_batch(data)
    reservation = data["reservation_micro_usd_at_stored_rates"]
    if not 0 < reservation <= round(max_usd * 1_000_000):
        raise ValueError("approved ceiling cannot reserve the prepared request")
    destination = CASSETTES / "phase17"
    staging = ARTIFACTS / "checkpoint4-capture"
    if destination.exists() or staging.exists():
        raise RuntimeError("Phase 17 capture already exists; never replace evidence")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY must be provided through the environment")
    batches = _batches_for_findings(FIXTURE, findings, CONFIG)
    asyncio.run(
        _capture(
            batches,
            list(batches),
            CONFIG,
            api_key,
            "phase17",
            staging,
            budget_micro_usd=round(max_usd * 1_000_000),
            replace=False,
        )
    )
    for item in data["reused_captures"]:
        source = ROOT / item["path"]
        shutil.copyfile(source, staging / source.name)
    outcome = SemanticReviewer(
        root=FIXTURE,
        config=CONFIG,
        max_findings=4,
        mode="replay",
        cassette_root=staging,
    ).review(findings, allow_degraded=False)
    if outcome.fatal:
        raise RuntimeError("new runtime capture failed production replay")
    manifest = json.loads((staging / "manifest.json").read_text())
    manifest["reused_captures"] = data["reused_captures"]
    _atomic_json(staging / "manifest.json", manifest)
    os.replace(staging, destination)
    _atomic_json(
        ARTIFACTS / "checkpoint4-runtime-review.json",
        {
            "label": "Replay of the newly captured Phase 17 runtime review",
            "gpt_review": outcome.summary.model_dump(mode="json"),
            "findings": [item.model_dump(mode="json") for item in outcome.findings],
            "reused_captures": data["reused_captures"],
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "capture"))
    parser.add_argument("--max-usd", type=float)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.max_usd is None:
        parser.error("capture requires a separately approved --max-usd ceiling")
    else:
        capture(args.max_usd)


if __name__ == "__main__":
    main()
