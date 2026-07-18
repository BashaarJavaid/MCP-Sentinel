"""Budget-gated GPT-5.6 review cassette capture utility."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid4

import tiktoken

from sentinel.config import LlmConfig, ReasoningEffort, load_configuration
from sentinel.finding import Finding, TokenUsage
from sentinel.llm.cache import ReviewCache
from sentinel.llm.context import build_finding_context, sanitize_text
from sentinel.llm.semantic_reviewer import (
    MODEL,
    SemanticReviewer,
    _Batch,
    _build_batches,
    _Candidate,
    _candidate_sort_key,
    _cost,
    _tool_for_finding,
)
from sentinel.llm.tools import ToolCatalog, extract_tool_catalog
from sentinel.static.engine import run_static_scan

ROOT = Path(__file__).resolve().parents[1]
CASSETTES = ROOT / "src" / "sentinel" / "_cassettes"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "checkpoint", choices=("smoke", "eval-medium", "eval-low", "demo")
    )
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--max-usd", type=float)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    effort = (
        ReasoningEffort.LOW if args.checkpoint == "eval-low" else ReasoningEffort.MEDIUM
    )
    batches, config = _planned_batches(args.checkpoint, effort)
    reservations = {
        batch.fingerprint: _reserved_micro_usd(batch) for batch in batches
    }
    reserved = sum(reservations.values())
    print(f"checkpoint: {args.checkpoint}")
    print(f"reasoning effort: {effort.value}")
    print(f"request count: {len(batches)}")
    print(f"finding count: {sum(len(batch.candidates) for batch in batches)}")
    print(f"aggregate worst-case cost: ${reserved / 1_000_000:.6f}")
    if not args.live:
        print("dry run: no API key read and no network call made")
        return 0
    if args.max_usd is None or args.max_usd <= 0:
        parser.error("--live requires a positive --max-usd ceiling")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        parser.error("--live requires OPENAI_API_KEY in the environment")

    checkpoint_dir = CASSETTES / args.checkpoint
    new_batches = [
        batch
        for batch in batches
        if args.replace or not (checkpoint_dir / f"{batch.fingerprint}.json").is_file()
    ]
    budget_micro_usd = round(args.max_usd * 1_000_000)
    largest_reservation = max(
        (reservations[batch.fingerprint] for batch in new_batches), default=0
    )
    if largest_reservation > budget_micro_usd:
        parser.error(
            "an uncaptured request's worst-case reservation exceeds --max-usd"
        )
    return asyncio.run(
        _capture(
            batches,
            new_batches,
            config,
            api_key,
            args.checkpoint,
            checkpoint_dir,
            budget_micro_usd=budget_micro_usd,
            replace=args.replace,
        )
    )


def _planned_batches(
    checkpoint: str, effort: ReasoningEffort
) -> tuple[tuple[_Batch, ...], LlmConfig]:
    fixture = (
        ROOT / "tests" / "fixtures" / "vulnerable_server"
        if checkpoint == "demo"
        else ROOT / "tests" / "fixtures" / "gpt_review_eval"
    )
    loaded = load_configuration(fixture, environ={}, static_only=True)
    llm = loaded.scanner.llm.model_copy(
        update={"reasoning_effort": effort, "max_concurrency": 1, "retries": 0}
    )
    loaded = loaded.model_copy(
        update={"scanner": loaded.scanner.model_copy(update={"llm": llm})}
    )
    findings = run_static_scan(
        loaded, uuid4(), timestamp=datetime.now(timezone.utc)
    ).findings
    catalog = extract_tool_catalog(fixture, loaded.scanner.scanner.ignore_paths)
    if checkpoint == "smoke":
        findings = tuple(
            item
            for item in findings
            if item.rule_id == "SENT-003"
            and _tool_name(catalog, item) == "unchecked_lookup"
        )
    findings = tuple(sorted(findings, key=_candidate_sort_key))
    candidates = tuple(
        _Candidate(
            finding=item,
            context=build_finding_context(fixture, item),
            tool=_tool_for_finding(catalog, item),
        )
        for item in findings
    )
    return _build_batches(candidates, effort), llm


def _tool_name(catalog: ToolCatalog, finding: Finding) -> str | None:
    tool = _tool_for_finding(catalog, finding)
    return tool.name if tool is not None else None


def _reserved_micro_usd(batch: _Batch) -> int:
    request_text = json.dumps(batch.request, sort_keys=True, separators=(",", ":"))
    try:
        encoding = tiktoken.encoding_for_model(MODEL)
        input_tokens = len(encoding.encode(request_text))
    except KeyError:
        # The pinned tokenizer does not yet map this new model. UTF-8 bytes are
        # a conservative, offline upper bound and therefore preserve the hard
        # spending ceiling without fetching tokenizer assets at runtime.
        input_tokens = len(request_text.encode("utf-8"))
    output_tokens = int(batch.request["max_output_tokens"])
    return _cost(TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens))


async def _capture(
    batches: tuple[_Batch, ...],
    new_batches: list[_Batch],
    config: LlmConfig,
    api_key: str,
    checkpoint: str,
    checkpoint_dir: Path,
    *,
    budget_micro_usd: int,
    replace: bool,
) -> int:
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    reviewer = SemanticReviewer(
        root=ROOT,
        config=config,
        max_findings=500,
        mode="live",
        api_key=api_key,
        cache=ReviewCache(enabled=False),
    )
    new_fingerprints = {batch.fingerprint for batch in new_batches}
    manifest_batches: list[dict[str, Any]] = []
    spent_micro_usd = 0
    for batch in batches:
        path = checkpoint_dir / f"{batch.fingerprint}.json"
        if batch.fingerprint not in new_fingerprints:
            print(f"reused: {batch.fingerprint}")
            existing = json.loads(path.read_text(encoding="utf-8"))
            manifest_batches.append(_manifest_entry(existing))
            continue
        reservation = _reserved_micro_usd(batch)
        if spent_micro_usd + reservation > budget_micro_usd:
            raise RuntimeError(
                "remaining live-capture budget cannot reserve the next request"
            )
        result = await reviewer._run_batch(batch)
        if result.accepted is None:
            raise RuntimeError(result.failure or "GPT capture failed")
        accepted = result.accepted
        sanitized = _sanitize_raw_response(accepted.raw, batch.fingerprint)
        cost_micro_usd = _cost(accepted.usage)
        payload = {
            "cassette_version": 1,
            "checkpoint": checkpoint,
            "fingerprint": batch.fingerprint,
            "captured_at": accepted.reviewed_at.isoformat().replace("+00:00", "Z"),
            "requested_model": MODEL,
            "returned_model": accepted.returned_model,
            "reasoning_effort": config.reasoning_effort.value,
            "usage": accepted.usage.model_dump(mode="json"),
            "latency_ms": accepted.latency_ms,
            "retry_count": accepted.retries,
            "batch_id": batch.batch_id,
            "cost_micro_usd": cost_micro_usd,
            "response": sanitized,
        }
        spent_micro_usd += cost_micro_usd
        if path.exists() and not replace:
            raise RuntimeError(f"refusing to replace existing cassette {path.name}")
        _atomic_json(path, payload)
        manifest_batches.append(_manifest_entry(payload))
        print(f"captured: {batch.fingerprint}")
        print(
            "current live spend: "
            f"${spent_micro_usd / 1_000_000:.6f}; "
            "remaining ceiling: "
            f"${(budget_micro_usd - spent_micro_usd) / 1_000_000:.6f}"
        )
    _atomic_json(
        checkpoint_dir / "manifest.json",
        {
            "checkpoint": checkpoint,
            "model": MODEL,
            "reasoning_effort": config.reasoning_effort.value,
            "batches": manifest_batches,
        },
    )
    return 0


def _sanitize_raw_response(raw: dict[str, Any], fingerprint: str) -> dict[str, Any]:
    response = cast(dict[str, Any], json.loads(json.dumps(raw)))
    response["id"] = f"resp_{fingerprint[:24]}"
    runtime_ids = _stable_uuid4s(fingerprint, len(_response_reviews(response)))
    for index, item in enumerate(response.get("output", [])):
        if isinstance(item, dict) and "id" in item:
            item["id"] = f"item_{fingerprint[:16]}_{index}"
    reviews = _response_reviews(response)
    for review, stable_id in zip(reviews, runtime_ids, strict=True):
        review["finding_id"] = str(stable_id)
        review["reasoning"] = sanitize_text(str(review["reasoning"]))
        for evidence in review["evidence_refs"]:
            evidence["claim"] = sanitize_text(str(evidence["claim"]))
    message = next(item for item in response["output"] if item["type"] == "message")
    message["content"][0]["text"] = json.dumps(
        {"reviews": reviews}, sort_keys=True, separators=(",", ":")
    )
    return response


def _response_reviews(response: dict[str, Any]) -> list[dict[str, Any]]:
    message = next(item for item in response["output"] if item["type"] == "message")
    payload = json.loads(message["content"][0]["text"])
    return cast(list[dict[str, Any]], payload["reviews"])


def _stable_uuid4s(fingerprint: str, count: int) -> tuple[UUID, ...]:
    values: list[UUID] = []
    for index in range(count):
        raw = bytearray(hashlib.sha256(f"{fingerprint}:{index}".encode()).digest()[:16])
        raw[6] = (raw[6] & 0x0F) | 0x40
        raw[8] = (raw[8] & 0x3F) | 0x80
        values.append(UUID(bytes=bytes(raw)))
    return tuple(values)


def _manifest_entry(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: payload[key]
        for key in (
            "fingerprint",
            "captured_at",
            "returned_model",
            "usage",
            "latency_ms",
            "cost_micro_usd",
        )
        if key in payload
    }


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
