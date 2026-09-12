"""Validate a concrete Phase 22 packet; capture only with a separate user approval."""

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
from pathlib import Path

FIXED = Path("/private/tmp/mcp-phase22-verify-v2-source-coordinate-tests")
sys.path[:0] = [str(FIXED / "src"), str(FIXED)]
from scripts.phase20_measurements import LLM, scanner_identity  # noqa: E402
from scripts.phase20_review import (  # noqa: E402
    capture_batches,
    request_hash,
    reservation,
    restore_batch,
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(packet_path):
    packet = json.loads(packet_path.read_text())
    assert packet["paid_evaluation_approved"] is False
    assert packet["settings"] == LLM.model_dump(mode="json")
    assert packet["executor_sha256"] == sha(Path(__file__))
    assert not subprocess.check_output(["git", "diff", "HEAD"], cwd=FIXED)
    identity = scanner_identity()
    assert packet["scanner"] == identity
    assert all(
        sha(FIXED / name) == value
        for name, value in packet["fixed_file_sha256"].items()
    )
    assert packet["environment"]["python"] == sys.version
    assert packet["environment"]["installed_packages"] == {
        d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
    }
    bundle = packet_path.parent / packet["request_bundle"]["path"]
    assert sha(bundle) == packet["request_bundle"]["sha256"]
    planned = json.loads(bundle.read_text())
    assert len(packet["requests"]) == len(
        {r["fingerprint"] for r in packet["requests"]}
    )
    batches = {}
    for row in packet["requests"]:
        fingerprint = row["fingerprint"]
        batch = restore_batch(planned[fingerprint])
        assert batch.fingerprint == fingerprint
        assert row["request_sha256"] == request_hash(batch.request)
        assert row["reservation"] == reservation(batch.request)
        assert row["stage"] in {"static", "runtime"}
        assert row["purpose"]
        batches[fingerprint] = batch
    assert packet["max_requests"] == len(batches)
    assert packet["max_micro_usd"] == sum(
        r["reservation"]["cost_micro_usd_reservation"] for r in packet["requests"]
    )
    return packet, batches


async def approved_capture(packet_path, approval_path):
    packet, batches = validate(packet_path)
    approval = json.loads(approval_path.read_text())
    assert approval["packet_sha256"] == sha(packet_path)
    assert approval["user_decision"] and approval["approved"] is True
    assert (
        type(approval["max_requests"]) is int
        and 0 < approval["max_requests"] <= packet["max_requests"]
    )
    assert (
        type(approval["max_micro_usd"]) is int
        and 0 < approval["max_micro_usd"] <= packet["max_micro_usd"]
    )
    selected = approval["request_fingerprints"]
    assert (
        isinstance(selected, list) and selected and len(selected) == len(set(selected))
    )
    assert all(isinstance(f, str) and f in batches for f in selected)
    assert len(selected) <= approval["max_requests"]
    rows = [r for r in packet["requests"] if r["fingerprint"] in selected]
    assert (
        sum(r["reservation"]["cost_micro_usd_reservation"] for r in rows)
        <= approval["max_micro_usd"]
    )
    # Stage ceilings partition the approved total; no second stage after a failure.
    limits = {
        stage: {
            "max_requests": sum(r["stage"] == stage for r in rows),
            "max_micro_usd": sum(
                r["reservation"]["cost_micro_usd_reservation"]
                for r in rows
                if r["stage"] == stage
            ),
        }
        for stage in ["static", "runtime"]
    }
    directory = packet_path.parent / "captures"
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError("Explicit approval validated, but OPENAI_API_KEY is absent")
    for stage in ["static", "runtime"]:
        if not limits[stage]["max_requests"]:
            continue
        decision = {
            **approval,
            **limits[stage],
            "stage": stage,
            "checkpoint": 2 if stage == "static" else 3,
        }
        code = await capture_batches(
            [batches[r["fingerprint"]] for r in rows if r["stage"] == stage],
            decision,
            sha(approval_path),
            key,
            directory=directory / stage,
        )
        if code:
            return code
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "capture"])
    parser.add_argument("packet", type=Path)
    parser.add_argument("--approval", type=Path)
    args = parser.parse_args()
    if args.command == "check":
        packet, batches = validate(args.packet)
        print(
            json.dumps(
                {
                    "request_count": len(batches),
                    "reserved_micro_usd": packet["max_micro_usd"],
                    "model_calls": 0,
                    "api_key_read": False,
                    "capture_approved": False,
                }
            )
        )
        return 0
    if args.approval is None:
        parser.error("capture requires an explicit user approval file")
    return asyncio.run(approved_capture(args.packet, args.approval))


if __name__ == "__main__":
    sys.exit(main())
