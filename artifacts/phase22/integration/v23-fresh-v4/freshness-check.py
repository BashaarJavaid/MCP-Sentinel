"""Compare proposed replacement sources with original held-out evidence only."""

import difflib
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    from scripts.phase20_corpus import archive_files, tree_digest

    output = Path(sys.argv[1])
    assert not output.exists()
    base = ROOT / "artifacts/phase22/integration"
    old_path = ROOT / "artifacts/phase22/corpus-review/manifest.json"
    new_path = ROOT / "artifacts/phase22/corpus-replacement-v4/manifest.json"
    old, new = json.loads(old_path.read_text()), json.loads(new_path.read_text())
    rows = []
    for label in ("vulnerable", "fixed"):
        pair = []
        for manifest in (old, new):
            item = next(
                i
                for i in manifest["inputs"]
                if i["repository"] == "ymw0407/auth-fetch-mcp"
                and i["label"] == label
                and i["variant"] == "original"
            )
            snapshot = next(
                s for s in manifest["snapshots"] if s["revision"] == item["snapshot"]
            )
            archive = ROOT / snapshot["archive"]["path"]
            assert sha(archive) == snapshot["archive"]["sha256"]
            files = archive_files(archive.read_bytes(), strip_root=True)
            assert {
                n: hashlib.sha256(d).hexdigest() for n, d in files.items()
            } == snapshot["files"]
            pair.append((item, snapshot, files))
        (oi, os, of), (ni, ns, nf) = pair
        identical = sorted(n for n in of.keys() & nf.keys() if of[n] == nf[n])
        changed = sorted(n for n in of.keys() & nf.keys() if of[n] != nf[n])
        rows.append(
            {
                "label": label,
                "original_revision": oi["snapshot"],
                "proposed_revision": ni["snapshot"],
                "original_archive": os["archive"],
                "proposed_archive": ns["archive"],
                "original_tree_sha256": tree_digest(of),
                "proposed_tree_sha256": tree_digest(nf),
                "original_condition": oi["condition"],
                "proposed_condition": ni["condition"],
                "identical_files": identical,
                "changed_files": changed,
                "removed_files": sorted(of.keys() - nf.keys()),
                "added_files": sorted(nf.keys() - of.keys()),
                "diffs": {
                    n: "".join(
                        difflib.unified_diff(
                            of[n].decode().splitlines(keepends=True),
                            nf[n].decode().splitlines(keepends=True),
                            fromfile="original/" + n,
                            tofile="proposed/" + n,
                        )
                    )
                    for n in changed
                },
                "source_file_hashes": {
                    n: hashlib.sha256(nf[n]).hexdigest() for n in identical
                },
            }
        )
        assert not (of.keys() ^ nf.keys())
        assert all(of[n] == nf[n] for n in of if n.startswith("src/"))
    assert len(rows[0]["identical_files"]) == 21 and not rows[0]["changed_files"]
    assert len(rows[1]["identical_files"]) == 19 and rows[1]["changed_files"] == [
        "package-lock.json",
        "package.json",
    ]
    history = []
    for name in (
        "v2-held_out-rules-dcb965f-first/results.json",
        "v2-held_out-semgrep-dcb965f-first/results.json",
        "v3-held_out-rules-final/results.json",
    ):
        path = base / name
        result = json.loads(path.read_text())
        outcomes = [
            r for r in result["outcomes"] if r["input_id"].startswith("authfetch-")
        ]
        assert len(outcomes) == 5 and all(r["state"] == "completed" for r in outcomes)
        hashes = {}
        for row in outcomes:
            native = path.parent / row["input_id"] / "report.json"
            raw = path.parent / row["input_id"] / "raw.json"
            report, digest = (
                (native, row["report_sha256"])
                if native.exists()
                else (raw, row["raw_sha256"])
            )
            assert sha(report) == digest
            hashes[report.relative_to(ROOT).as_posix()] = digest
        history.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha(path),
                "scanner": result["scanner"],
                "started_at": result["started_at"],
                "outcomes": outcomes,
                "report_hashes_verified": hashes,
            }
        )
    packet = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "verification_passed": True,
        "fresh_source_qualification_passed": False,
        "original_manifest_sha256": sha(old_path),
        "proposed_manifest_sha256": sha(new_path),
        "comparisons": rows,
        "prior_completed_evaluations": history,
        "finding": (
            "Replacement-v4 reuses the original held-out repository, "
            "vulnerability and source flow. Its vulnerable21-file tree is byte-"
            "identical; all fixed source files are identical, with only package"
            " metadata differing. Different revision IDs, renamed helpers, "
            "clarified prerequisites and a changed public control do not "
            "establish an independent fresh repository or vulnerability."
        ),
        "scope_consequence": (
            "The unchanged replacement-v4 proposal cannot satisfy R66/R88 as "
            "independent fresh evidence. Do not dispatch or silently waive this"
            " requirement; preserve the proposed packet and obtain a concrete "
            "disposition. No claim is made about current-scanner detection "
            "without a newly approved execution."
        ),
        "preparation_erratum": (
            "The prior v21 and v23 checks verified internal hashes, "
            "materialization and unchanged45 records, but omitted comparison "
            "against the original held-out source trees. Their successful "
            "integrity checks do not establish freshness. The v4 proposal and "
            "this turn's first preparation delivery retain their original "
            "bytes/history."
        ),
        "new_native_observations": 0,
        "new_comparator_observations": 0,
        "new_paid_calls": 0,
        "target_execution": False,
        "dispatches_consumed": 0,
        "measurement_budget_approved": False,
        "unused_proposed_observations": 15,
        "unused_proposal_is_not_authority": True,
        "phase22_complete": False,
        "technical_acceptance_requested": False,
    }
    output.write_text(json.dumps(packet, indent=2) + "\n")
    print(
        "Source comparison verified: replacement-v4 freshness fails; zero "
        "new observations."
    )


if __name__ == "__main__":
    main()
