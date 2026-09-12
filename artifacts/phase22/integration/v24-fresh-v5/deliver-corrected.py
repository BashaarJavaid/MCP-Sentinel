"""Deliver the measured limitation checkpoint to the existing draft PR."""

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
EXPECTED = "86cbdc96e73b08d76786933398bcb8d31c190905"
TESTED = "e1ab15c513ae736bedfb7665ac53efabff85f790"


def run(args):
    return subprocess.check_output(args, cwd=ROOT, text=True)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    assert not path.exists(), path
    path.write_text(json.dumps(data, indent=2) + "\n")


def main():
    assert run(["git", "rev-parse", "HEAD"]).strip() == EXPECTED
    reuse = read(OUT / "compatible-reuse.json")
    original = read(BASE / "v23-v5-compatible-reuse.json")
    product = [
        *original["byte_identical_product_test_package_inputs"],
        ".github",
        "artifacts/phase22/integration/v23-fresh-v5/runner.py",
        "artifacts/phase22/integration/v20-linux-diagnostic-v1/runner.py",
    ]
    assert not run(["git", "diff", TESTED, "--", *product])
    for name, digest in read(BASE / "v23-fresh-v5/binding.json")["files"].items():
        assert sha(ROOT / name) == digest, name
    result = read(OUT / "assessment.json")
    audit = read(OUT / "audit.json")
    assert result["execution_checks_passed"] and result["source_assessment_complete"]
    assert not result["detection_limitation_accepted"] and not audit["phase22_complete"]
    assert not audit["technical_acceptance_received"]
    assert (
        len(audit["requirements"]) == 89
        and len(audit["additional_scope_requirements"]) == 60
    )
    seal = read(BASE / "evidence-v53.json")
    assert sha(BASE / seal["archive"]) == seal["sha256"]
    docs = read(OUT / "owning-documents.json")
    for name, digest in reuse["user_files_preserved"].items():
        assert sha(ROOT / name) == digest, name
    assert set(
        run(["git", "ls-files", "--others", "--exclude-standard"]).splitlines()
    ) == set(reuse["user_files_preserved"]) | {
        "artifacts/phase22/corpus-replacement-v5/STATUS.md"
    }
    main_root = Path("/Users/bashaarjavaid/Projects/MCP-Sentinel")
    assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=main_root)
    assert (
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=main_root, text=True
        ).strip()
        == "4cd57593b2585b9ee05c0f175930e6a0d76d362a"
    )
    fields = "headRefOid,baseRefName,state,isDraft,body,title"
    before = json.loads(run(["gh", "pr", "view", "37", "--json", fields]))
    assert (
        before["headRefOid"] == EXPECTED
        and before["state"] == "OPEN"
        and before["isDraft"]
        and before["baseRefName"] == "phase22/description-poisoning"
    )
    parent = json.loads(
        run(["gh", "pr", "view", "36", "--json", "headRefOid,headRefName"])
    )
    assert parent["headRefOid"] == "8b6b0ddf1d6f6cf5a8da3ab9421471865b801455"
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", parent["headRefOid"], EXPECTED],
        cwd=ROOT,
        check=True,
    )
    checks = read(OUT / "final-checks.json")
    assert checks["docs_exit"] == 0 and checks["helper_checks_exit"] == 0
    for name, digest in checks["documents_sha256"].items():
        assert sha(ROOT / name) == digest, name
    binding = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "delivery_parent": EXPECTED,
        "measured_scanner": result["scanner"],
        "measured_workflow": EXPECTED,
        "tested_workflow": TESTED,
        "documents_sha256": {n: sha(ROOT / n) for n in docs},
        "review_packet_sha256": {
            n: sha(OUT / n)
            for n in [
                "summary.md",
                "audit.json",
                "assessment.json",
                "warning-source-assessment.json",
                "limitation-proposal.json",
                "draft-body.md",
                "final-checks.json",
                "deliver.py",
                "deliver-corrected.py",
                "delivery-correction.json",
            ]
        },
        "evidence_archive_sha256": seal["sha256"],
        "evidence_manifest_sha256": sha(BASE / "evidence-v53.json"),
        "product_and_workflow_equal_tested_source": True,
        "technical_acceptance_received": False,
        "limitation_accepted": False,
        "phase22_complete": False,
        "note": "Evidence/docs-only delivery reuses the exact tested workflow and frozen scanner; no new hosted matrix pass is claimed. Final bindings are tracked after seal53. Post-push readback is a separate local receipt.",
    }
    write(OUT / "documentation-binding.json", binding)
    write(
        OUT / "delivery-verification.json",
        {
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "before": before,
            "parent": parent,
            "documentation_binding_sha256": sha(OUT / "documentation-binding.json"),
            "tested_inputs_unchanged": product,
            "user_files_preserved": reuse["user_files_preserved"],
            "new_paid_calls": 0,
            "evaluation_budget_closed": True,
            "phase22_complete": False,
        },
    )
    core = [
        "summary.md",
        "audit.json",
        "assessment.json",
        "warning-source-assessment.json",
        "limitation-proposal.json",
        "draft-body.md",
        "documentation-binding.json",
        "delivery-verification.json",
        "deliver.py",
        "deliver-corrected.py",
        "delivery-correction.json",
        "delivery-initial-failure.log",
        "final-checks.json",
        "compatible-reuse.json",
        "dispatch-consumed.json",
        "hosted/packet.json",
        "owning-documents.json",
    ]
    files = (
        docs
        + [str((OUT / n).relative_to(ROOT)) for n in core]
        + [
            "artifacts/phase22/integration/evidence-v53.json",
            "artifacts/phase22/integration/evidence-v53.tar.gz",
        ]
    )
    subprocess.run(["git", "add", "-f", "--", *files], cwd=ROOT, check=True)
    assert set(run(["git", "diff", "--cached", "--name-only"]).splitlines()) <= set(
        files
    )
    subprocess.run(["git", "diff", "--cached", "--check"], cwd=ROOT, check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "Deliver frozen replacement-v5 results and limitation decision [skip ci]",
        ],
        cwd=ROOT,
        check=True,
    )
    head = run(["git", "rev-parse", "HEAD"]).strip()
    assert not run(["git", "diff", TESTED, head, "--", *product])
    subprocess.run(
        ["git", "push", "origin", "phase22/integration"], cwd=ROOT, check=True
    )
    subprocess.run(
        ["gh", "pr", "edit", "37", "--body-file", str(OUT / "draft-body.md")],
        cwd=ROOT,
        check=True,
    )
    for _ in range(20):
        after = json.loads(run(["gh", "pr", "view", "37", "--json", fields]))
        if (
            after["headRefOid"] == head
            and after["body"] == (OUT / "draft-body.md").read_text()
        ):
            break
        time.sleep(3)
    assert (
        after["headRefOid"] == head
        and after["body"] == (OUT / "draft-body.md").read_text()
    )
    assert (
        after["isDraft"]
        and after["state"] == "OPEN"
        and after["baseRefName"] == before["baseRefName"]
    )
    assert not run(["git", "diff", "HEAD"])
    for name, digest in reuse["user_files_preserved"].items():
        assert sha(ROOT / name) == digest, name
    write(
        OUT / "delivery-readback.json",
        {
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "delivered_head": head,
            "remote_after": after,
            "tested_workflow": TESTED,
            "measured_workflow": EXPECTED,
            "measured_scanner": result["scanner"],
            "tracked_worktree_clean": True,
            "main_worktree_unchanged": True,
            "user_files_preserved": reuse["user_files_preserved"],
            "evidence_sha256": seal["sha256"],
            "documentation_binding_sha256": sha(OUT / "documentation-binding.json"),
            "limitation_accepted": False,
            "technical_acceptance_received": False,
            "phase22_complete": False,
            "new_paid_calls": 0,
            "storage": "Supplemental local post-push receipt; not claimed inside the commit it describes.",
        },
    )
    print(head, flush=True)


if __name__ == "__main__":
    main()
