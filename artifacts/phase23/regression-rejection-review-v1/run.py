"""One approved observation with only the promisify binding reversed.

Uses a disposable checkout.
"""

import io
import json
import signal
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from scripts import phase23_regression as helper  # noqa: E402
from scripts.phase20_corpus import Artifact, digest, tree_digest  # noqa: E402

HERE = Path(__file__).resolve().parent
PROPOSAL = HERE / "proposal-revised-v3.json"
APPROVAL = HERE / "authorization-revised-v3.json"


def preflight():
    data = PROPOSAL.read_bytes()
    proposal = json.loads(data)
    approval = json.loads(APPROVAL.read_bytes())
    assert approval.get("decision") == "approved"
    assert approval.get("proposal_sha256") == digest(data)
    assert helper.execution_identity() == proposal["identity"]
    assert digest(Path(__file__).read_bytes()) == proposal["runner_sha256"]
    assert (
        proposal["observations"] == 1 and proposal["input_id"] == "minimized-vulnerable"
    )
    assert proposal["limits"] == {
        "input_seconds": 1800,
        "semgrep_seconds": 10,
        "cleanup_seconds": 15,
        "maximum_workers": 4,
        "outer_seconds": 2100,
        "outer_cleanup_seconds": 15,
    }
    assert not (ROOT / proposal["output"]).exists()
    assert not Path(proposal["disposable_checkout"]).exists()
    assert not APPROVAL.with_suffix(".used.json").exists()
    assert (
        digest((ROOT / proposal["changed_file"]).read_bytes())
        == proposal["before_sha256"]
    )
    Artifact.model_validate(proposal["patch"]).read(ROOT)
    Artifact.model_validate(proposal["reversed_source"]).read(ROOT)
    assert (
        digest(Artifact.model_validate(proposal["reversed_source"]).read(ROOT))
        == proposal["after_sha256"]
    )
    manifest_path = ROOT / proposal["manifest"]["path"]
    assert digest(manifest_path.read_bytes()) == proposal["manifest"]["sha256"]
    manifest = helper.validate(manifest_path)
    item = next(x for x in manifest["inputs"] if x["id"] == proposal["input_id"])
    _, references = helper.ci_references()
    return proposal, item, references[item["id"]]


def main():
    if sys.argv[1:] == ["check"]:
        assert not APPROVAL.exists()
        try:
            preflight()
        except FileNotFoundError as error:
            assert Path(error.filename) == APPROVAL
        else:
            raise AssertionError("Missing approval accepted")
        print(
            "Missing approval rejected before source checkout, budget "
            "or scanner execution."
        )
        return 0
    assert not sys.argv[1:]
    proposal, item, reference = preflight()
    output = ROOT / proposal["output"]
    checkout = Path(proposal["disposable_checkout"])
    with APPROVAL.with_suffix(".used.json").open("x") as f:
        json.dump(
            {"proposal_sha256": digest(PROPOSAL.read_bytes()), "status": "consumed"}, f
        )
    output.mkdir()
    (output / "tmp").mkdir()
    receipt = {
        "status": "running",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "proposal_sha256": digest(PROPOSAL.read_bytes()),
        "remaining_observations": 0,
        "paid_calls": 0,
        "target_executions": 0,
    }
    handlers = {
        sig: signal.signal(sig, handler)
        for sig, handler in [
            (signal.SIGALRM, helper._expired),
            (signal.SIGINT, helper._cancelled),
            (signal.SIGTERM, helper._cancelled),
        ]
    }
    deadline = time.monotonic() + 2100
    helper._alarm(2100)
    try:
        archive = subprocess.check_output(
            [
                "git",
                "archive",
                "HEAD",
                "src",
                "scripts",
                "schemas",
                "pyproject.toml",
                "uv.lock",
            ],
            cwd=ROOT,
        )
        checkout.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(checkout, filter="data")
        # Overlay the reviewed uncommitted candidate bytes, excluding
        # interpreter caches.
        for directory in ["src", "scripts", "schemas"]:
            for source in (ROOT / directory).rglob("*"):
                if source.is_file() and "__pycache__" not in source.parts:
                    target = checkout / source.relative_to(ROOT)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(source.read_bytes())
        for name in ["pyproject.toml", "uv.lock"]:
            (checkout / name).write_bytes((ROOT / name).read_bytes())
        current = {
            p.relative_to(ROOT).as_posix(): p.read_bytes()
            for p in (ROOT / "src/sentinel").rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        }
        copied = {
            p.relative_to(checkout).as_posix(): p.read_bytes()
            for p in (checkout / "src/sentinel").rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        }
        assert copied == current
        (checkout / proposal["changed_file"]).write_bytes(
            Artifact.model_validate(proposal["reversed_source"]).read(ROOT)
        )
        changed = {
            p.relative_to(checkout).as_posix(): p.read_bytes()
            for p in (checkout / "src/sentinel").rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        }
        assert [name for name in current if current[name] != changed[name]] == [
            proposal["changed_file"]
        ]
        receipt["candidate_source_sha256"] = tree_digest(current)
        receipt["reversed_source_sha256"] = tree_digest(changed)
        bootstrap = (
            "import sys,runpy; "
            f"sys.path[:0]={[str(checkout / 'src'), str(checkout)]!r}; "
            "import sentinel; "
            "assert sentinel.__file__=="
            f"{str(checkout / 'src/sentinel/__init__.py')!r}; "
            "runpy.run_module('sentinel',run_name='__main__')"
        )
        original_popen = subprocess.Popen

        def launch(command, **kwargs):
            assert command[1:4] == ["-I", "-m", "sentinel"]
            command[:] = [command[0], "-I", "-c", bootstrap, *command[4:]]
            receipt["actual_command"] = list(command)
            helper._atomic_json(output / "results.json", receipt)
            return original_popen(command, **kwargs)

        config = json.loads(
            (
                ROOT / "artifacts/phase23/candidate-execution-review-v2/proposal.json"
            ).read_bytes()
        )["configurations"][item["id"]]
        with patch.object(subprocess, "Popen", launch):
            outcome, report = helper._observe(
                item,
                output / "observation",
                output / "sources" / item["id"],
                helper.baseline_environment(output),
                deadline,
                config,
            )
        receipt["observation"] = outcome
        assert (
            outcome["state"] == "completed"
            and outcome["cleanup"] == "verified"
            and report is not None
        )
        try:
            helper.ci_report_difference(report, reference, item)
        except ValueError as error:
            assert str(error) == "CI source-matched shell condition failed", str(error)
            receipt["failed_assertion"] = {
                "function": "scripts.phase23_regression.ci_report_difference",
                "type": type(error).__name__,
                "message": str(error),
            }
            (output / "failed-assertion.txt").write_text(
                f"{type(error).__name__}: {error}\n"
            )
        else:
            raise AssertionError(
                "Deliberate regression was not rejected by the source-matched assertion"
            )
        receipt["status"] = "regression_rejected"
        return 0
    except BaseException as error:
        receipt.update(status="failed", reason=f"{type(error).__name__}: {error}")
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        try:
            helper._cleanup(None, checkout)
            receipt["disposable_checkout_cleanup"] = "verified"
        except BaseException as error:
            receipt.update(
                status="failed",
                disposable_checkout_cleanup=f"failed: {type(error).__name__}: {error}",
            )
            raise
        finally:
            for sig, handler in handlers.items():
                signal.signal(sig, handler)
            receipt["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
            helper._atomic_json(output / "results.json", receipt)


if __name__ == "__main__":
    raise SystemExit(main())
