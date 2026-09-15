"""Check prepared workflow and runner controls without corpus measurements."""

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import yaml

ASSETS = Path(__file__).resolve().parent
ROOT = ASSETS.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = Path(sys.argv[1])
    assert not output.exists()
    spec = importlib.util.spec_from_file_location("fresh", ASSETS / "runner.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    proposal = runner.verify_packet()
    runner.selfcheck()
    assert not runner.APPROVAL.exists()
    try:
        runner.approved()
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("runner accepted missing approval")
    with patch.object(runner, "sha", return_value="wrong"):
        try:
            runner.verify_packet()
        except AssertionError:
            pass
        else:
            raise AssertionError("runner accepted proposal drift")
    old = yaml.safe_load(
        subprocess.check_output(
            ["git", "show", "61b19ae:.github/workflows/ci.yml"], cwd=ROOT
        )
    )
    new = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    assert set(new["jobs"]) == set(old["jobs"]) | {"phase22-fresh-v4"}
    for name, job in old["jobs"].items():
        updated = new["jobs"][name]
        assert {k: v for k, v in updated.items() if k != "if"} == {
            k: v for k, v in job.items() if k != "if"
        }, name
        assert "!inputs.phase22_fresh_v4" in updated["if"]
    assert (
        new[True]["workflow_dispatch"]["inputs"]["phase22_fresh_v4"]["default"] is False
    )
    job = new["jobs"]["phase22-fresh-v4"]
    assert "github.event_name == 'workflow_dispatch'" in job["if"]
    assert "!inputs.phase22_historical" in job["if"]
    assert "refs/heads/phase22/integration" in job["if"]
    assert job["timeout-minutes"] == 90 and job["runs-on"] == "ubuntu-latest"
    assert "5280" in job["steps"][0]["run"]
    assert job["steps"][-1]["if"] == "always()"
    assert any(
        s.get("with", {}).get("ref") == proposal["scanner"]["revision"]
        for s in job["steps"]
    )
    assert set(runner.EXCLUDED) == set(
        json.loads(
            (
                ASSETS.parent / "v21-historical-assessment-refresh-proposal.json"
            ).read_text()
        )["conditions"]["excluded_volatile_fields"]
    )
    supervisor = ASSETS.parent / "v23-supervisor-checks/result/selfcheck.json"
    assert json.loads(supervisor.read_text())["passed"]
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
    files = [
        ASSETS / "runner.py",
        ASSETS / "preflight.py",
        ROOT / ".github/workflows/ci.yml",
        ASSETS.parent / "v20-linux-diagnostic-v1/runner.py",
    ]
    packet = {
        "passed": True,
        "status": "prepared_not_approved_not_dispatched",
        "scanner": proposal["scanner"],
        "proposal_sha256": sha(runner.PROPOSAL),
        "checkpoint": proposal["checkpoint"],
        "manifest": proposal["manifest"],
        "files": {p.relative_to(ROOT).as_posix(): sha(p) for p in files},
        "baseline_sha256": sha(ASSETS / "baseline.json"),
        "supervisor_selfcheck_sha256": sha(supervisor),
        "normal_jobs_unchanged_except_mutually_exclusive_dispatch_guards": True,
        "byte_identical_scanner_inputs": paths,
        "checks": [
            "approval required",
            "proposal drift rejected",
            "300-second and cleanup boundaries",
            "failed and timed-out children rejected",
            "exact eleven volatile fields",
            "ordered findings/warnings/coverage changes rejected",
            "separate optional job and standard runner",
            "Linux cleanup including stubborn and orphaned synthetic children",
        ],
        "new_native_observations": 0,
        "new_comparator_observations": 0,
        "new_paid_calls": 0,
        "target_execution": False,
        "dispatch_binding": "After explicit approval, bind the actual receipt, final runner/workflow and all supporting assets before the single dispatch. This preparation is not approval.",
    }
    output.write_text(json.dumps(packet, indent=2) + "\n")
    print("Preparation controls passed; zero observations.")


if __name__ == "__main__":
    main()
