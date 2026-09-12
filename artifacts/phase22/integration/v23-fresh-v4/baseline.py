"""Verify the handoff and materialize sources without running a detector."""

import hashlib
import importlib.metadata
import json
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

BASE = ROOT / "artifacts/phase22/integration"
CORPUS = ROOT / "artifacts/phase22/corpus-replacement-v4"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main():
    from scripts.phase20_corpus import materialize
    from scripts.phase20_measurements import scanner_identity
    from scripts.phase22_corpus import validate
    from sentinel.config import load_configuration

    output = Path(sys.argv[1])
    assert not output.exists()
    packet = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "head": git("rev-parse", "HEAD"),
    }
    assert git("branch", "--show-current") == "phase22/integration"
    assert packet["head"] == "3c29529e3f1c1f67150fd17aaf3afe57459c732e"
    proposal = json.loads((CORPUS / "evaluation-proposal.json").read_text())
    expected = json.loads((BASE / "v21-fresh-proposal-verification.json").read_text())
    for name, digest in expected["prepared_files_sha256"].items():
        assert sha(ROOT / name) == digest, name
    packet["prepared_files_sha256"] = expected["prepared_files_sha256"]
    checkpoint = json.loads((CORPUS / "checkpoint-1f3f72f.json").read_text())
    for name, digest in checkpoint["harness_and_lock_sha256"].items():
        assert sha(ROOT / name) == digest, name
    identity = scanner_identity()
    assert {**identity, "revision": proposal["scanner"]["revision"]} == proposal[
        "scanner"
    ]
    packet["scanner"] = proposal["scanner"]
    frozen = Path(checkpoint["immutable_checkout"])
    assert (
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=frozen, text=True
        ).strip()
        == proposal["scanner"]["revision"]
    )
    assert not subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=frozen
    )
    inputs = json.loads((BASE / "v22-delivery-verification.json").read_text())[
        "tested_inputs_identical_to_candidate"
    ]
    assert not git("diff", "61b19ae", "HEAD", "--", *inputs)
    packet["tested_input_reuse"] = {
        "source": "61b19aeb56e087ebfeb52a7865aea50deb35e4bd",
        "byte_identical_paths": inputs,
    }
    docs = json.loads((BASE / "v22-final-documentation-binding.json").read_text())
    for name, digest in docs["final_documents_sha256"].items():
        assert sha(ROOT / name) == digest, name
    packet["handoff_documents_verified"] = docs["final_documents_sha256"]
    packet["user_files_sha256"] = {
        p.relative_to(ROOT).as_posix(): sha(p)
        for p in sorted((ROOT / "docs").glob("phase22-*prompt.md"))
    }
    for name, digest in json.loads((BASE / "v22-source-verification.json").read_text())[
        "user_files_sha256"
    ].items():
        assert sha(ROOT / name) == digest, name
    packet["environment"] = {
        "python": sys.version,
        "packages": {
            n: importlib.metadata.version(n)
            for n in ("semgrep", "mcp", "pytest", "pydantic")
        },
    }
    manifest = validate(CORPUS / "manifest.json")
    old = json.loads(
        (ROOT / "artifacts/phase22/corpus-replacement-v3/manifest.json").read_text()
    )
    raw = json.loads((CORPUS / "manifest.json").read_text())
    retained = [i for i in raw["inputs"] if i["id"] not in proposal["input_order"]]
    retained_ids = {i["id"] for i in retained}
    assert (
        retained == [i for i in old["inputs"] if i["id"] in retained_ids]
        and len(retained) == 45
    )
    packet["unchanged_prior_records"] = len(retained)
    snapshots = {s.revision: s for s in manifest.snapshots}
    configs = json.loads((CORPUS / "configurations.json").read_text())
    packet["materialized"] = []
    with tempfile.TemporaryDirectory(prefix="phase22-v23-source-only-") as temporary:
        for item in manifest.inputs:
            if item.id not in proposal["input_order"]:
                continue
            source = materialize(
                item,
                snapshots[item.snapshot],
                Path(temporary).resolve() / item.id,
                manifest.packet,
            )
            config = load_configuration(
                source,
                environ={},
                static_only=True,
                cli_overrides={
                    "rules_only": True,
                    "ignore_paths": [".phase20/**"],
                    "max_findings_per_scan": 500,
                },
                llm_cli_overrides={
                    "model": "gpt-5.6-sol",
                    "reasoning_effort": "medium",
                    "retries": 0,
                    "max_concurrency": 1,
                    "cache_enabled": False,
                },
            )
            payload = {
                "scanner": config.scanner.model_dump(mode="json"),
                "target": None,
                "static_only": config.static_only,
                "language": config.language.value,
            }
            assert payload == configs[item.id]["configuration"]
            assert (
                hashlib.sha256(
                    (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
                ).hexdigest()
                == configs[item.id]["sha256"]
            )
            packet["materialized"].append(
                {
                    "id": item.id,
                    "tree_sha256": item.tree_sha256,
                    "files": len(snapshots[item.snapshot].files),
                    "configuration_sha256": configs[item.id]["sha256"],
                }
            )
    assert [r["id"] for r in packet["materialized"]] == proposal["input_order"]
    packet["seals"] = {}
    for version in range(1, 52):
        index = json.loads((BASE / f"evidence-v{version}.json").read_text())
        archive = BASE / index["archive"]
        assert sha(archive) == index["sha256"]
        with tarfile.open(archive) as stream:
            rows = {r["path"]: r for r in index["files"]}
            members = stream.getmembers()
            assert len(members) == len(rows)
            for member in members:
                row = rows[member.name]
                assert member.isfile() and member.size == row["bytes"]
                assert (
                    hashlib.sha256(stream.extractfile(member).read()).hexdigest()
                    == row["sha256"]
                )
        packet["seals"][archive.name] = {
            "sha256": index["sha256"],
            "members_verified": len(rows),
        }
        print("Verified seal", version, flush=True)
    audit = json.loads((BASE / "v22-closeout-audit/packet.json").read_text())
    assert (
        len(audit["requirements"]) == 89
        and len(audit["additional_scope_requirements"]) == 51
    )
    missing = []
    for row in audit["requirements"] + audit["additional_scope_requirements"]:
        for name in row["evidence"]:
            path = ROOT / name if name.startswith("artifacts/") else BASE / name
            if not path.is_file():
                missing.append(name)
    assert not missing, missing
    packet["audit"] = {
        "sha256": sha(BASE / "v22-closeout-audit/packet.json"),
        "requirements": 89,
        "added_scope_rows": 51,
        "all_references_present": True,
        "dispositions": audit["dispositions"],
    }
    packet.update(
        passed=True,
        native_observations=0,
        comparator_observations=0,
        paid_calls=0,
        target_execution=False,
        evaluation_approved=False,
    )
    output.write_text(json.dumps(packet, indent=2) + "\n")
    print("Baseline and source-only materialization passed; zero observations.")


if __name__ == "__main__":
    main()
