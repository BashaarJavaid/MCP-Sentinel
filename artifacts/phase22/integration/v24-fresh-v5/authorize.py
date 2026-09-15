"""Record the user's exact approval and validate bindings without scanning."""

import hashlib
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "artifacts/phase22/integration"
ASSETS = BASE / "v23-fresh-v5"
CORPUS = ROOT / "artifacts/phase22/corpus-replacement-v5"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    assert not path.exists(), path
    path.write_text(json.dumps(data, indent=2) + "\n")


def main():
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    assert head == "579eb0ec731af5bef54bca4fe4e9ca81103aa856"
    proposal_path = CORPUS / "evaluation-proposal.json"
    assert (
        sha(proposal_path)
        == "3b3013ae4a116804421bc8c028d8a1fe800fb288ae6637ce593c3d0bd30f19f6"
    )
    proposal = json.loads(proposal_path.read_text())
    assert (
        proposal["checkpoint"]["sha256"]
        == "ae4d6c817446b4cf675ec2b1f74a99323e3e21de5a2b1545f29264e4513cf60e"
    )
    approval = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "user_decision": "approved",
        "approved": True,
        "approval_context": "Approval directly answers the exact replacement-v5 proposal and checkpoint question delivered with source-only checkpoint 579eb0e: 10 native + 5 Semgrep observations, one standard Linux job capped at 90 minutes, 120-second target / 300-second whole-input maximum, zero retries, profiles, target executions or paid calls.",
        "delivery_at_approval": head,
        "proposal_path": proposal_path.relative_to(ROOT).as_posix(),
        "proposal_sha256": sha(proposal_path),
        "checkpoint_sha256": proposal["checkpoint"]["sha256"],
        "scanner": proposal["scanner"],
        "bounds": proposal["bounds"],
        "corpus": {
            "manifest": proposal["manifest"]["path"],
            "sha256": proposal["manifest"]["sha256"],
            "freeze_approved": True,
            "input_ids": proposal["input_order"],
            "treatments": ["rules", "semgrep"],
        },
        "batch_order": proposal["batch_order"],
        "exposure": proposal["prior_results"],
        "stop": proposal["stop"],
        "technical_acceptance": False,
        "paid_calls_authorized": 0,
    }
    write(ASSETS / "authorization.json", approval)
    names = {
        ".github/workflows/ci.yml",
        "artifacts/phase22/integration/v23-fresh-v5/runner.py",
        "artifacts/phase22/integration/v20-linux-diagnostic-v1/runner.py",
        "artifacts/phase22/integration/v23-fresh-v5/authorization.json",
        "artifacts/phase22/integration/v21-fresh-proposal-verification.json",
        proposal_path.relative_to(ROOT).as_posix(),
        "artifacts/phase22/corpus-replacement-v5/preparation.json",
    }
    for key in (
        "checkpoint",
        "manifest",
        "configuration",
        "pre_curation_freeze",
        "comparator_preparation",
        "source_only_authorization",
        "condition_review",
        "novelty",
    ):
        names.add(proposal[key]["path"])
    for path in (
        BASE / "v21-fresh-proposal-verification.json",
        CORPUS / "preparation.json",
    ):
        for name, digest in json.loads(path.read_text())[
            "prepared_files_sha256"
        ].items():
            assert sha(ROOT / name) == digest, name
            names.add(name)
    binding = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "scanner": proposal["scanner"],
        "files": {name: sha(ROOT / name) for name in sorted(names)},
        "tested_workflow_source": "e1ab15c513ae736bedfb7665ac53efabff85f790",
        "ci_run": 34578515990,
        "docs_run": 34578515965,
        "binding_note": "Final runner/workflow files equal the tested source; approval and file binding are new evidence. The immutable proposal remains prepared_not_approved as historical preparation. This actual receipt authorizes one dispatch only. No result or technical acceptance is inferred.",
    }
    write(ASSETS / "binding.json", binding)
    spec = importlib.util.spec_from_file_location("fresh", ASSETS / "runner.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    assert runner.approved() == proposal
    runner.selfcheck()
    paths = [
        "src",
        "tests",
        "scripts",
        "uv.lock",
        "pyproject.toml",
        "action.yml",
        "Makefile",
        "schemas",
        "demo",
    ]
    assert not subprocess.check_output(
        ["git", "diff", proposal["scanner"]["revision"], "--", *paths], cwd=ROOT
    )
    assert not subprocess.check_output(
        [
            "git",
            "diff",
            binding["tested_workflow_source"],
            "--",
            ".github",
            str(ASSETS / "runner.py"),
        ],
        cwd=ROOT,
    )
    tracked = set(
        subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    )
    assert names - tracked == {
        "artifacts/phase22/integration/v23-fresh-v5/authorization.json"
    }
    write(
        BASE / "v24-fresh-v5/authorization-check.json",
        {
            "passed": True,
            "authorization_sha256": sha(ASSETS / "authorization.json"),
            "binding_sha256": sha(ASSETS / "binding.json"),
            "helper_sha256": sha(Path(__file__)),
            "file_count": len(names),
            "tested_workflow_unchanged": True,
            "product_unchanged": True,
            "native_observations": 0,
            "comparator_observations": 0,
            "paid_calls": 0,
            "target_execution": False,
        },
    )
    print("Approval and", len(names), "file bindings verified; zero observations.")


if __name__ == "__main__":
    main()
