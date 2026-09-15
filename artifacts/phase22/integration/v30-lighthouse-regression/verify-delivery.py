"""Read back the delivered draft; this does not dispatch an evaluation."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

root = Path.cwd()
out = root / "artifacts/phase22/integration/v30-lighthouse-regression"
head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
fields = "headRefOid,headRefName,baseRefName,isDraft,state,body,url"
raw = subprocess.check_output(["gh", "pr", "view", "37", "--json", fields])
dest = out / "delivery-readback.json"
assert not dest.exists()
dest.write_bytes(raw)
pr = json.loads(raw)
assert pr["headRefOid"] == head
assert pr["headRefName"] == "phase22/integration"
assert pr["baseRefName"] == "phase22/description-poisoning"
assert pr["isDraft"] and pr["state"] == "OPEN"
assert pr["body"] == (out / "pr-body.md").read_text()
parent = json.loads(subprocess.check_output([
    "gh", "pr", "view", "36", "--json", "headRefOid,state,isDraft"
]))
assert parent["headRefOid"] == "8b6b0ddf1d6f6cf5a8da3ab9421471865b801455"
binding = json.loads((out / "documentation-binding.json").read_text())
for name, digest in binding["owning_docs_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
for name, digest in binding["review_packet_sha256"].items():
    assert hashlib.sha256((out / name).read_bytes()).hexdigest() == digest, name
assert not subprocess.check_output([
    "git", "diff", binding["tested_workflow"], "--", *binding["byte_identical_quality_inputs"]
])
assert not subprocess.check_output(["git", "diff", "HEAD"])
assert not subprocess.check_output(["git", "diff", "--cached"])
protected = binding["user_files_sha256"]
assert set(subprocess.check_output([
    "git", "ls-files", "--others", "--exclude-standard"
], text=True).splitlines()) == set(protected)
for name, digest in protected.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
for path, expected in [
    ("/Users/bashaarjavaid/Projects/MCP-Sentinel", "4cd57593b2585b9ee05c0f175930e6a0d76d362a"),
    ("/private/tmp/mcp-phase22-frozen-1f3f72f", "1f3f72f0f25c597b53c9f833e2e4bec99728d328"),
    ("/private/tmp/mcp-phase22-frozen-6db3858", "6db3858f1368033642354ab5ebb53aef76315a16"),
    ("/private/tmp/mcp-phase22-frozen-f85a90f", "f85a90f9ba2d1c43019e8505b977d57f3476a9c9"),
]:
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path, text=True).strip() == expected
    assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=path)
assert not (out.parent / "v30-compatibility-proposal/evaluation-authorization.json").exists()
receipt = {
    "recorded_at": datetime.now(timezone.utc).isoformat(),
    "delivered_revision": head,
    "readback_sha256": hashlib.sha256(raw).hexdigest(),
    "parent": parent,
    "documentation_binding_sha256": hashlib.sha256((out / "documentation-binding.json").read_bytes()).hexdigest(),
    "product_and_workflow_equal_tested_source": True,
    "new_paid_calls": 0,
    "current_source_corpus_observations": 10,
    "prior_scanner_regression_observations_this_continuation": 0,
    "evaluation_approved": True,
    "evaluation_passed": True,
    "next_compatibility_proposal_approved": False,
    "technical_acceptance_received": False,
    "phase22_complete": False,
    "qualification": "Post-delivery ignored receipt; not claimed inside the preceding commit or evidence archive.",
}
path = out / "delivery-verification.json"
assert not path.exists()
path.write_text(json.dumps(receipt, indent=2) + "\n")
print("Verified delivered draft", pr["url"], head)
