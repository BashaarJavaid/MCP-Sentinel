"Seal completed checkpoint evidence without replacing previous seals."

import hashlib
import io
import json
import subprocess
import tarfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert json.loads((BASE / "v92-technical-acceptance/final-checks.json").read_text())["passed"]
    assert json.loads((BASE / "v92-technical-acceptance/owned-final.json").read_text())["owned_processes"] == []
    assert json.loads((BASE / "v80-unseen-results/raw/packet.json").read_text())["budget_closed"]
    assert json.loads((BASE / "v80-unseen-results/final-assessment/assessment.json").read_text())["repository_gates_passed"] == 1
    assert not json.loads((BASE / "v92-technical-acceptance/audit.json").read_text())["technical_acceptance_received"]
    assert json.loads((BASE / "v75-prior-language-results/raw/packet.json").read_text())["budget_closed"]
    assert not (BASE / "v69-ts-literal-key-reuse").exists()
    assert json.loads((BASE / 'v87-regression-results/completion-verification.json').read_text())['budget_closed']
    assert json.loads((BASE / 'v90-regression-results/completion-verification.json').read_text())['budget_closed']
    archive, manifest = BASE / "evidence-v106.tar.gz", BASE / "evidence-v106.json"
    assert not archive.exists() and not manifest.exists()
    previous, prior_hashes = {}, {}
    for version in range(1, 106):
        index = json.loads((BASE / f"evidence-v{version}.json").read_text())
        assert sha((BASE / index["archive"]).read_bytes()) == index["sha256"]
        prior_hashes[index["archive"]] = index["sha256"]
        with tarfile.open(BASE / index["archive"]) as prior:
            members = prior.getmembers()
            assert len(members) == len(index["files"])
            for member, row in zip(members, index["files"], strict=True):
                assert member.isfile() and member.name == row["path"] and member.size == row["bytes"]
                assert sha(prior.extractfile(member).read()) == row["sha256"]
        previous.update({r["path"]: r["sha256"] for r in index["files"]})
    rows = []
    excluded = {
        "requirements.md",
        "progress.md",
        "README.md",
        ".gitignore",
        "dbt-adjudication.json",
        "development-conditions.json",
    }
    with tarfile.open(archive, "w:gz") as output:
        for path in sorted(BASE.rglob("*")):
            name = path.relative_to(BASE).as_posix()
            assert not path.is_symlink(), name
            if (
                not path.is_file()
                or name in excluded
                or name.startswith("evidence-v")
                or "__pycache__" in path.parts
            ):
                continue
            data = path.read_bytes()
            digest = sha(data)
            if previous.get(name) == digest:
                continue
            assert name not in previous, ("Earlier sealed evidence changed", name)
            member = tarfile.TarInfo(name)
            member.size = len(data)
            output.addfile(member, io.BytesIO(data))
            rows.append({"path": name, "bytes": len(data), "sha256": digest})
    with tarfile.open(archive) as stored:
        members = stored.getmembers()
        assert len(members) == len(rows)
        for member, row in zip(members, rows, strict=True):
            assert (
                member.isfile()
                and member.name == row["path"]
                and member.size == row["bytes"]
            )
            assert sha(stored.extractfile(member).read()) == row["sha256"]
    assert archive.stat().st_size < 95 * 1024 * 1024
    packet = {
        "version": 106,
        "archive": archive.name,
        "sha256": sha(archive.read_bytes()),
        "files": rows,
        "previous_packet": "evidence-v105.json",
        "prior_archive_hashes": prior_hashes,
        "source_through": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "first_frozen_corpus_scanner": "1f3f72f0f25c597b53c9f833e2e4bec99728d328",
        "verified_corrected_scanner": "5142a3fbd5bcff63719df6cce3a30543214e7d27",
        "status": "User explicitly accepts Proxmox unsupported limitation and defers recovery; all original/current failures remain failed. Complete490-row technical acceptance review prepared:6acceptedProxmoxlimitations,24otherhistorical/practical limitations pending. Unchanged5142a3fengineering2596tests/36skips locally and12hostedsuites,29jobs/docs,sixzero-call requests,19runtimebindings. All prior budgets closed;zero new observations/paidcalls. OrdinaryFAF1800completion unestablished;V68unapproved/unimplemented. Separate human technical acceptance and verified accepted closeout pending.",
        "verification": (
            "All 105 prior archives and every new member verified afte"
            "r writers stopped. Restore in numeric order into separa"
            "te staging; existing destinations must match identical "
            "bytes or the recorded prior hash. Stop on unexplained c"
            "onflicts."
        ),
        "exclusions": (
            "Owning docs and post-seal documentation/delivery "
            "bindings remain directly tracked. Generated Python byte"
            "code is excluded; existing seals and expanded evidence "
            "are preserved."
        ),
    }
    manifest.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    print(
        len(rows),
        sum(r["bytes"] for r in rows),
        archive.stat().st_size,
        packet["sha256"],
    )


if __name__ == "__main__":
    main()
