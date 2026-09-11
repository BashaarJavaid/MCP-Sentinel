"Deliver the verified preparation checkpoint; no evaluation or phase acceptance."

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "artifacts/phase22/integration"
ASSETS = Path(__file__).resolve().parent
TESTED = "e1ab15c513ae736bedfb7665ac53efabff85f790"
PRODUCT = [
    "src",
    "tests",
    "scripts",
    ".github",
    "schemas",
    "Makefile",
    "pyproject.toml",
    "uv.lock",
    "action.yml",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "THIRD_PARTY_NOTICES.md",
    ".pre-commit-hooks.yaml",
    ".python-version",
    ".gitattributes",
    "demo",
    "sentinel.toml",
    "artifacts/phase22/integration/v23-fresh-v5/runner.py",
    "artifacts/phase22/integration/v23-fresh-v5/preflight.py",
    ("artifacts/phase22/integration/v20-linux-diagnostic-v1/runner.py"),
]


def run(args):
    return subprocess.check_output(args, cwd=ROOT, text=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((BASE / name).read_text())


def write(name, data):
    path = BASE / name
    assert not path.exists(), name
    path.write_text(json.dumps(data, indent=2) + "\n")


def main():
    assert run(["git", "rev-parse", "HEAD"]).strip() == TESTED
    assert not run(["git", "diff", TESTED, "--", *PRODUCT])
    quality = read("v23-v5-quality/packet.json")
    assert quality["engineering_passed"] and quality["source"] == TESTED
    assessed = read("v23-v5-quality-audit/packet.json")
    assert assessed["source"] == TESTED and len(assessed["quality"]) == 12
    audit = read("v23-checkpoint-audit/packet.json")
    assert (
        len(audit["requirements"]) == 89
        and len(audit["additional_scope_requirements"]) == 56
    )
    assert not audit["phase22_complete"] and not audit["fresh_evaluation_approved"]
    assert (
        not (ASSETS / "authorization.json").exists()
        and not (ASSETS / "binding.json").exists()
    )
    proposal = ROOT / (
        "artifacts/phase22/corpus-replacement-v5/evaluation-proposal.json"
    )
    assert sha(proposal) == (
        "3b3013ae4a116804421bc8c028d8a1fe800fb288ae6637ce593c3d0bd30f19f6"
    )
    seal = read("evidence-v52.json")
    assert sha(BASE / seal["archive"]) == seal["sha256"]
    fields = "number,state,isDraft,title,headRefName,headRefOid,baseRefName,body"
    before = json.loads(run(["gh", "pr", "view", "37", "--json", fields]))
    parent = json.loads(
        run(["gh", "pr", "view", "36", "--json", "headRefOid,headRefName"])
    )
    assert (
        before["headRefOid"] == TESTED
        and before["isDraft"]
        and before["state"] == "OPEN"
    )
    assert before["baseRefName"] == "phase22/description-poisoning"
    assert parent["headRefOid"] == "8b6b0ddf1d6f6cf5a8da3ab9421471865b801455"
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", parent["headRefOid"], TESTED],
        cwd=ROOT,
        check=True,
    )
    docs = list(read("v22-final-documentation-binding.json")["final_documents_sha256"])
    docs = list(
        dict.fromkeys(
            [
                *docs,
                "artifacts/phase22/integration/README.md",
                "artifacts/phase22/integration/requirements.md",
                "artifacts/phase22/integration/progress.md",
                "artifacts/phase22/corpus-replacement-v4/STATUS.md",
                "artifacts/phase22/corpus-replacement-v5/README.md",
                "artifacts/phase22/integration/v23-fresh-v5/README.md",
            ]
        )
    )
    prompts = read("v22-refresh-authorization.json")["user_files_sha256"]
    assert set(
        run(["git", "ls-files", "--others", "--exclude-standard"]).splitlines()
    ) == set(prompts)
    for name, digest in prompts.items():
        assert sha(ROOT / name) == digest, name
    main_root = Path("/Users/bashaarjavaid/Projects/MCP-Sentinel")
    assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=main_root)
    assert (
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=main_root, text=True
        ).strip()
        == "4cd57593b2585b9ee05c0f175930e6a0d76d362a"
    )
    binding = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "hosted_source": TESTED,
        "actual_hosted_checkout": assessed["actual_synthetic_merge"],
        "complete_checkout_tree_equals_head": assessed[
            "complete_checkout_tree_equals_head"
        ],
        "measured_scanner": "1f3f72f0f25c597b53c9f833e2e4bec99728d328",
        "final_documents_sha256": {name: sha(ROOT / name) for name in docs},
        "delivery_helper_sha256": sha(Path(__file__)),
        "audit_sha256": sha(BASE / "v23-checkpoint-audit/packet.json"),
        "evidence_manifest_sha256": sha(BASE / "evidence-v52.json"),
        "evidence_archive_sha256": seal["sha256"],
        "proposal_sha256": sha(proposal),
        "checkpoint_sha256": sha(proposal.parent / "checkpoint-1f3f72f.json"),
        "draft_body_sha256": sha(ASSETS / "final-draft-body.md"),
        "quality_packet_sha256": sha(BASE / "v23-v5-quality/packet.json"),
        "quality_audit_sha256": sha(BASE / "v23-v5-quality-audit/packet.json"),
        "binding": (
            "Documentation/evidence delivery reuses the exact e1ab15"
            "c hosted workflow and 1f3f72f product. No new hosted pa"
            "ss is claimed for the later delivery commit. Historical"
            " measurements retain original sources. Final audit/docs"
            "/receipt are tracked after seal52 without a self-refere"
            "ntial hash."
        ),
        "new_native_observations": 0,
        "new_comparator_observations": 0,
        "new_paid_calls": 0,
        "source_only_recovery_approved": True,
        "fresh_evaluation_approved": False,
        "phase22_complete": False,
    }
    write("v23-final-documentation-binding.json", binding)
    write(
        "v23-delivery-verification.json",
        {
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "delivery_parent": TESTED,
            "tested_source": TESTED,
            "remote_before": before,
            "parent_before": parent,
            "tested_inputs_identical_to_candidate": PRODUCT,
            "documents": docs,
            "binding_sha256": sha(BASE / "v23-final-documentation-binding.json"),
            "user_files_preserved": prompts,
            "new_corpus_runs": 0,
            "new_paid_calls": 0,
            "phase22_complete": False,
        },
    )
    files = [
        "evidence-v52.json",
        "evidence-v52.tar.gz",
        "v23-checkpoint-audit/packet.json",
        "v23-checkpoint-summary.md",
        "v23-final-documentation-binding.json",
        "v23-delivery-verification.json",
        "v23-fresh-v5/final-draft-body.md",
        "v23-fresh-v5/deliver-checkpoint.py",
    ]
    subprocess.run(["git", "add", "--", *docs], cwd=ROOT, check=True)
    subprocess.run(
        [
            "git",
            "add",
            "-f",
            "--",
            *[str((BASE / name).relative_to(ROOT)) for name in files],
        ],
        cwd=ROOT,
        check=True,
    )
    allowed = set(docs) | {str((BASE / name).relative_to(ROOT)) for name in files}
    assert set(run(["git", "diff", "--cached", "--name-only"]).splitlines()) <= allowed
    subprocess.run(["git", "diff", "--cached", "--check"], cwd=ROOT, check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "Seal source-only Phase 22 replacement checkpoint [skip ci]",
        ],
        cwd=ROOT,
        check=True,
    )
    delivery = run(["git", "rev-parse", "HEAD"]).strip()
    assert not run(["git", "diff", TESTED, delivery, "--", *PRODUCT])
    subprocess.run(
        ["git", "push", "origin", "phase22/integration"], cwd=ROOT, check=True
    )
    subprocess.run(
        ["gh", "pr", "edit", "37", "--body-file", str(ASSETS / "final-draft-body.md")],
        cwd=ROOT,
        check=True,
    )
    for _ in range(12):
        after = json.loads(run(["gh", "pr", "view", "37", "--json", fields]))
        if (
            after["headRefOid"] == delivery
            and after["body"] == (ASSETS / "final-draft-body.md").read_text()
        ):
            break
        time.sleep(3)
    assert (
        after["headRefOid"] == delivery
        and after["body"] == (ASSETS / "final-draft-body.md").read_text()
    )
    assert (
        after["isDraft"]
        and after["state"] == "OPEN"
        and after["baseRefName"] == before["baseRefName"]
    )
    assert not run(["git", "diff", "HEAD"])
    for name, digest in prompts.items():
        assert sha(ROOT / name) == digest, name
    write(
        "v23-final-delivery-readback.json",
        {
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "delivered_head": delivery,
            "tested_source": TESTED,
            "remote_after": after,
            "verification_sha256": sha(BASE / "v23-delivery-verification.json"),
            "binding_sha256": sha(BASE / "v23-final-documentation-binding.json"),
            "tested_inputs_equal": True,
            "tracked_worktree_clean": True,
            "user_files_preserved": prompts,
            "new_paid_calls": 0,
            "fresh_evaluation_approved": False,
            "phase22_complete": False,
            "storage": (
                "Supplemental ignored local post-delivery readback; trac"
                "ked Git tree contains the sealed evidence and pre-commi"
                "t verification."
            ),
        },
    )
    print(delivery)


if __name__ == "__main__":
    main()
