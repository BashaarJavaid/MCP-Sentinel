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
    binding = read("v23-final-documentation-binding.json")
    verification = read("v23-delivery-verification.json")
    docs = verification["documents"]
    prompts = verification["user_files_preserved"]
    before = verification["remote_before"]
    fields = "number,state,isDraft,title,headRefName,headRefOid,baseRefName,body"
    live = json.loads(run(["gh", "pr", "view", "37", "--json", fields]))
    assert live == before
    parent = json.loads(run(["gh", "pr", "view", "36", "--json", "headRefOid,headRefName"]))
    assert parent == verification["parent_before"]
    for name, digest in binding["final_documents_sha256"].items():
        assert sha(ROOT / name) == digest, name
    for name, digest in prompts.items():
        assert sha(ROOT / name) == digest, name
    assert set(run(["git", "ls-files", "--others", "--exclude-standard"]).splitlines()) == set(prompts)
    assert not (ASSETS / "authorization.json").exists()
    assert not (ASSETS / "binding.json").exists()
    assert sha(BASE / "evidence-v52.tar.gz") == binding["evidence_archive_sha256"]
    main_root = Path("/Users/bashaarjavaid/Projects/MCP-Sentinel")
    assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=main_root)
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=main_root, text=True).strip() == "4cd57593b2585b9ee05c0f175930e6a0d76d362a"
    files = [
        "evidence-v52.json",
        "evidence-v52.tar.gz",
        "v23-checkpoint-audit/packet.json",
        "v23-checkpoint-summary.md",
        "v23-final-documentation-binding.json",
        "v23-delivery-verification.json",
        "v23-fresh-v5/final-draft-body.md",
        "v23-fresh-v5/deliver-checkpoint.py",
        "v23-fresh-v5/deliver-checkpoint-corrected.py",
        "v23-delivery-correction.json",
        "v23-delivery-initial-failure.log",
        "v23-fresh-v5/resume-checkpoint-delivery.py",
        "v23-delivery-staging-correction.json",
        "v23-delivery-staging-failure.log",
    ]
    subprocess.run(["git", "add", "-f", "--", *docs], cwd=ROOT, check=True)
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
