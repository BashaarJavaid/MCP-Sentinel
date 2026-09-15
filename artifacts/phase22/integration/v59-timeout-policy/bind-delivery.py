"""Bind the verified policy/proposal and review documents after seal 87."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
OLD = BASE/'v58-credential-regression'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value):
    with (OUT/name).open('x') as f: json.dump(value, f, indent=2); f.write('\n')
seal = read(BASE/'evidence-v87.json')
assert sha(BASE/seal['archive']) == seal['sha256']
save('seal-execution.json', {'command': ['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python', 'artifacts/phase22/integration/v59-timeout-policy/seal.py'], 'exit_code': 0, 'members': len(seal['files']), 'raw_bytes': sum(r['bytes'] for r in seal['files']), 'archive_sha256': seal['sha256'], 'qualification': 'Direct execution after all writers stopped; supplemental completion receipt.'})
path = BASE/'README.md'
text = path.read_text()
assert text.count('batches 1–86') == 1
text = text.replace('batches 1–86', 'batches 1–87', 1)
first, rest = text.split('\n', 1)
block = f'''
## Timeout policy evidence seal 87

[Seal 87](evidence-v87.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 86 prior archives and every member verified.
This retains the approved 30-minute policy, actual `7bf4c6e` local/hosted engineering,
323 audit rows, unchanged source/condition bindings and the unapproved 205-observation
proposal. Earlier native/profile/fresh failures and supplemental v58 delivery remain.
Restore after seals 1–86 in numeric order into safe separate staging; reject unsafe
paths/symlinks, verify archive/member hashes and stop on unexplained conflicts.
The v73 log correction remains preserved. Post-seal documentation/draft readback
are supplemental. **Phase 22 remains incomplete.**
'''
path.write_text(first+'\n'+block+rest)
url = 'https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
with (OUT/'pr-body-delivery.md').open('x') as f:
    f.write((OUT/'pr-body.md').read_text()+f'\n[Seal 87]({url}evidence-v87.json): {len(seal["files"])} members, SHA-256 `{seal["sha256"]}`; all 86 earlier archives verified. Final docs/package checks pass with product bytes identical to tested `7bf4c6e`.\n')
old = read(OLD/'documentation-binding.json')
worktrees = subprocess.check_output(['git', 'worktree', 'list', '--porcelain'], text=True)
def parse(value):
    return {b.splitlines()[0].removeprefix('worktree '): next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in value.strip().split('\n\n')}
for name, head in parse(old['worktrees']).items():
    assert parse(worktrees)[name] == ('7bf4c6e1cf0c8d83229b1273f80737e7cacc5b82' if name == str(ROOT) else head), name
for name, digest in old['user_files_sha256'].items(): assert sha(ROOT/name) == digest, name
review = ['authorization.json', 'timeout-confirmation.json', 'source-checkpoint.json', 'source-proof.json', 'audit.json', 'prior-row-preservation.json', 'local-checks.json', 'compatibility.json', 'demo-validation.json', 'freeze.json', 'frozen-source-validation.json', 'evaluation-proposal.json', 'scoring-rubric.json', 'runner-boundaries.json', 'launcher-binding.json', 'summary.md', 'pr-body-delivery.md', 'final-checks.json', 'final-distributions.json', 'command-provenance.json', 'check-failure-assessment.json', 'owned-final.json', 'budget-closed.json', 'seal-execution.json']
save('documentation-binding.json', {'recorded_at': datetime.now(timezone.utc).isoformat(), 'baseline_delivery': 'b168738236d9f0b637fa8764f1ad0f3bbcae50d8', 'candidate_head': '7bf4c6e1cf0c8d83229b1273f80737e7cacc5b82', 'corrected_scanner': read(OUT/'freeze.json')['scanner'], 'owning_docs_sha256': {n: sha(ROOT/n) for n in old['owning_docs_sha256']}, 'review_packet_sha256': {str((OUT/n).resolve().relative_to(ROOT)): sha(OUT/n) for n in review}, 'additional_normative_docs_sha256': {'docs/architecture.md': sha(ROOT/'docs/architecture.md')}, 'user_files_sha256': old['user_files_sha256'], 'worktrees': worktrees, 'evidence_seal': {'index': 'artifacts/phase22/integration/evidence-v87.json', 'index_sha256': sha(BASE/'evidence-v87.json'), 'archive_sha256': seal['sha256']}, 'evaluation_proposal_sha256': sha(OUT/'evaluation-proposal.json'), 'corpus_budget': read(OUT/'budget-closed.json'), 'paid_calls': 0, 'technical_acceptance_received': False, 'phase22_complete': False, 'qualification': 'Post-seal binding. Product/tests/workflows/lock/schema bytes equal tested 7bf4c6e. Final README metadata separately rebuilt. The newly prepared numerical regression is unapproved and unexecuted. Draft delivery requires exact supplemental readback.'})
print('Bound 16 owning docs and unexecuted 30-minute evaluation proposal after seal 87.')
