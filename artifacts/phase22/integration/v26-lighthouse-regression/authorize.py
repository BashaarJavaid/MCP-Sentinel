"""Record the exact new user decision; validate source without observations."""
import hashlib
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
ASSETS = OUT.parent / "v25-lighthouse-fix"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def write(path, value):
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2) + "\n")


head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
assert head == "aef8cc75cfc458902b3b9b355aa47370f8a161c4"
proposal_path = ASSETS / "evaluation-proposal-final.json"
assert sha(proposal_path) == "26ac27d01740faa0ac664a13963ef7a4d91f199818bba29d9a257d98f1f4206a"
proposal = json.loads(proposal_path.read_text())
receipt = {
    "recorded_at": datetime.now(timezone.utc).isoformat(),
    "user_decision": "continue",
    "approved": True,
    "approval_context": "Direct response to the exact final ten-observation Lighthouse regression approval question delivered at aef8cc7. This approves that bounded exposed regression only; no other experiment or technical acceptance is inferred.",
    "delivery_at_approval": head,
    "proposal_path": proposal_path.relative_to(ROOT).as_posix(),
    "proposal_sha256": sha(proposal_path),
    "scanner": proposal["scanner"],
    "bounds": proposal["bounds"],
    "corpus": {**proposal["corpus"], "freeze_approved": True},
    "batch_order": proposal["batch_order"],
    "exposure": proposal["exposure"],
    "stop": proposal["stop"],
    "technical_acceptance": False,
    "paid_calls_authorized": 0,
}
write(ASSETS / "evaluation-authorization-final.json", receipt)
spec = importlib.util.spec_from_file_location("regression", ASSETS / "evaluate-final.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
assert runner.approved() == proposal
runner.selfcheck()
quality = json.loads((ASSETS / "documentation-binding.json").read_text())
assert not subprocess.check_output(["git", "diff", quality["tested_workflow"], "--", *quality["byte_identical_quality_inputs"]], cwd=ROOT)
for name, digest in quality["user_files_sha256"].items():
    assert sha(ROOT / name) == digest, name
names = {*proposal["files_sha256"], proposal_path.relative_to(ROOT).as_posix(), (ASSETS / "evaluation-authorization-final.json").relative_to(ROOT).as_posix()}
write(OUT / "binding.json", {
    "recorded_at": datetime.now(timezone.utc).isoformat(),
    "scanner": proposal["scanner"],
    "files": {n: sha(ROOT / n) for n in sorted(names)},
    "tested_workflow_source": quality["tested_workflow"],
    "ci_run": quality["ordinary_ci"]["ci"],
    "docs_run": quality["ordinary_ci"]["docs"],
    "new_corpus_observations": 0,
    "new_paid_calls": 0,
    "binding_note": "Exact tested runner/workflow, frozen proposal and new actual approval. Product/test/package/workflow inputs equal tested51fd2cb. Proposal remains immutable prepared_not_approved history; receipt authorizes one dispatch only.",
})
print("New approval and", len(names), "file bindings verified; zero observations.")
