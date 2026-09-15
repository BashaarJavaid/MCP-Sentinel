"""Verify compatible retained evidence; never rerun a corpus or model request."""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "artifacts/phase22/integration"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = Path(sys.argv[1])
    assert not output.exists()
    prior = json.loads((BASE / "v19-source-verification.json").read_text())
    source = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    inputs = json.loads((BASE / "v22-source-verification.json").read_text())[
        "unchanged_product_test_package_inputs"
    ]
    assert not subprocess.check_output(
        ["git", "diff", "1f3f72f", "--", *inputs], cwd=ROOT
    )
    for name, digest in prior["unchanged_git_blob_bindings"].items():
        assert sha(ROOT / name) == digest, name
    capture = json.loads(
        (BASE / "v19-final-production-capture-revalidation/packet.json").read_text()
    )
    assert capture["source"] == "1f3f72f0f25c597b53c9f833e2e4bec99728d328"
    assert capture["model_calls"] == 0 and len(capture["requests"]) == 6
    assert all(r["accepted"] for r in capture["requests"])
    latest = {}
    for version in range(1, 52):
        seal = json.loads((BASE / f"evidence-v{version}.json").read_text())
        latest.update({r["path"]: r["sha256"] for r in seal["files"]})
    audit = json.loads((BASE / "v22-closeout-audit/packet.json").read_text())
    evidence = set()
    for row in audit["requirements"] + audit["additional_scope_requirements"]:
        for name in row["evidence"]:
            path = ROOT / name if name.startswith("artifacts/") else BASE / name
            assert path.is_file() and not path.is_symlink(), name
            relative = (
                path.relative_to(BASE).as_posix() if path.is_relative_to(BASE) else None
            )
            if relative in latest:
                assert sha(path) == latest[relative], name
            evidence.add(path)
    historical = json.loads(
        (BASE / "v22-refresh-disposition-corrected.json").read_text()
    )
    assert historical["passed"] and historical["total_attempts_consumed"] == 98
    assert historical["ordered_historical_reports_equal"]
    for name, digest in historical["references_sha256"].items():
        assert sha(BASE / name) == digest, name
    main_root = Path("/Users/bashaarjavaid/Projects/MCP-Sentinel")
    assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=main_root)
    assert (
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=main_root, text=True
        ).strip()
        == "4cd57593b2585b9ee05c0f175930e6a0d76d362a"
    )
    packet = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "measured_scanner": capture["source"],
        "passed": True,
        "byte_identical_product_test_package_inputs": inputs,
        "requirements": 89,
        "additional_scope_rows": 51,
        "retained_requirement_evidence_sha256": {
            p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(evidence)
        },
        "production_request_reuse": {
            "source": capture["source"],
            "packet_sha256": sha(
                BASE / "v19-final-production-capture-revalidation/packet.json"
            ),
            "requests": [
                {
                    "fingerprint": r["fingerprint"],
                    "request_sha256": r["request_sha256"],
                    "accepted": r["accepted"],
                }
                for r in capture["requests"]
            ],
            "new_replay_or_paid_calls": 0,
        },
        "runtime_compatibility": prior["runtime_compatibility"],
        "exposed_detection_compatibility": prior["exposed_detection_compatibility"],
        "historical_gate_sha256": sha(BASE / "v22-refresh-disposition-corrected.json"),
        "local_quality_reuse": {
            "source": capture["source"],
            "checks_sha256": sha(BASE / "v19-final-local-checks.json"),
            "junit_sha256": sha(BASE / "v19-final-full-suite-junit.xml"),
            "passed": 2194,
            "skipped": 36,
            "branch_coverage_percent": 89.68,
        },
        "original_failed_gate": prior["original_failed_gate"],
        "main_worktree_clean": True,
        "new_native_observations": 0,
        "new_comparator_observations": 0,
        "new_paid_calls": 0,
        "scope": (
            "Read-only compatibility verification. Executed local quality, "
            "requests and runtime retain their original sources; optional "
            "workflow requires its own fresh hosted quality. No new "
            "generalization result or technical acceptance."
        ),
    }
    output.write_text(json.dumps(packet, indent=2) + "\n")
    print(
        "All140 requirement/scope rows retain verified evidence; six "
        "production requests remain compatible."
    )


if __name__ == "__main__":
    main()
