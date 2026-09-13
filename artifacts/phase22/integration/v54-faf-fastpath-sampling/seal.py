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
    assert json.loads((BASE / "v54-faf-fastpath-sampling/final-checks.json").read_text())["passed"]
    assert json.loads((BASE / "v54-faf-fastpath-sampling/owned-work.json").read_text())["owned_processes"] == []
    assert not (BASE / "v54-faf-fastpath-sampling/optimization-authorization.json").exists()
    assert not (BASE / "v54-faf-fastpath-sampling/optimization-consumed.json").exists()
    archive, manifest = BASE / "evidence-v82.tar.gz", BASE / "evidence-v82.json"
    assert not archive.exists() and not manifest.exists()
    previous, prior_hashes = {}, {}
    for version in range(1, 82):
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
        "version": 82,
        "archive": archive.name,
        "sha256": sha(archive.read_bytes()),
        "files": rows,
        "previous_packet": "evidence-v81.json",
        "prior_archive_hashes": prior_hashes,
        "source_through": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "first_frozen_corpus_scanner": "1f3f72f0f25c597b53c9f833e2e4bec99728d328",
        "verified_corrected_scanner": "a36f696c504e4e8d1f90de5dc84e8942d06316ca",
        "status": "Approved single a36f696 profile timed out at300seconds; four verified worker identities and78769partial samples retained, no report,zero remaining. All283requirements preserved. Full sample/source/caller attribution supports one unapproved source-only singleton combine cache-bypass proposal, with no performance promise. Product remains tested a36f696; final docs/packages passed. Initial cleanup-check ordering failure and settled pass retained; supplemental v53delivery/approval included. All original fresh/native/profile failures remain source-bound. Phase22 incomplete; no acceptance,merge,ready,release,outreach orPhase23.",
        "verification": (
            "All81 prior archives and every new member verified afte"
            "r writers stopped. Restore in numeric order into separa"
            "te staging; existing destinations must match identical "
            "bytes or the recorded prior hash. Stop on unexplained c"
            "onflicts."
        ),
        "exclusions": (
            "Owning docs and post-seal audit/documentation/delivery "
            "bindings and both new corpus draft/final directories remain directly tracked. Generated Python byte"
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
