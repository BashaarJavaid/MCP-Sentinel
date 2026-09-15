"""Consume the one approved dispatch; never resend a dispatch request."""

import hashlib
import importlib.util
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
ASSETS = OUT.parent / "v25-lighthouse-fix"


def run(args):
    return subprocess.check_output(args, cwd=ROOT, text=True)


def main():
    receipt = OUT / "dispatch-consumed.json"
    assert not receipt.exists(), "Single dispatch already consumed; never retry"
    spec = importlib.util.spec_from_file_location("fresh", ASSETS / "evaluate-final.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.approved()
    head = run(["git", "rev-parse", "HEAD"]).strip()
    assert not run(["git", "diff", "HEAD"])
    pr = json.loads(
        run(
            ["gh", "pr", "view", "37", "--json", "headRefOid,baseRefName,state,isDraft"]
        )
    )
    assert pr == {
        "headRefOid": head,
        "baseRefName": "phase22/description-poisoning",
        "state": "OPEN",
        "isDraft": True,
    }
    parent = json.loads(run(["gh", "pr", "view", "36", "--json", "headRefOid"]))
    assert parent["headRefOid"] == "8b6b0ddf1d6f6cf5a8da3ab9421471865b801455"
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", parent["headRefOid"], head],
        cwd=ROOT,
        check=True,
    )
    listing = [
        "gh",
        "run",
        "list",
        "--branch",
        "phase22/integration",
        "--limit",
        "30",
        "--json",
        "databaseId,headSha,event,status,conclusion",
    ]
    before = json.loads(run(listing))
    assert all(r["status"] == "completed" for r in before)
    command = [
        "gh",
        "workflow",
        "run",
        "ci.yml",
        "--ref",
        "phase22/integration",
        "-f",
        "phase22_lighthouse_regression=true",
        "-f",
        "phase22_fresh_v5=false",
        "-f",
        "phase22_historical=false",
    ]
    packet = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "workflow_source": head,
        "authorization_sha256": runner.sha(ASSETS / "evaluation-authorization-final.json"),
        "binding_sha256": runner.sha(OUT / "binding.json"),
        "dispatches_consumed": 1,
        "remaining_dispatches": 0,
        "command": command,
        "runs_before": before,
        "state": "request_about_to_be_sent_no_retry",
        "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    receipt.write_text(json.dumps(packet, indent=2) + "\n")
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    packet.update(
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        state="request_returned",
    )
    receipt.write_text(json.dumps(packet, indent=2) + "\n")
    result.check_returncode()
    known = {r["databaseId"] for r in before}
    for _ in range(20):
        candidates = [
            r
            for r in json.loads(run(listing))
            if r["databaseId"] not in known
            and r["headSha"] == head
            and r["event"] == "workflow_dispatch"
        ]
        if candidates:
            assert len(candidates) == 1
            packet.update(run=candidates[0], state="single_dispatch_identified")
            receipt.write_text(json.dumps(packet, indent=2) + "\n")
            print(json.dumps(packet["run"]), flush=True)
            return
        time.sleep(3)
    raise AssertionError(
        "Run identity unresolved; inspect remotely without another dispatch"
    )


if __name__ == "__main__":
    main()
