"""Bind final profile/proposal delivery after the immutable evidence seal."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
OLD = BASE/'v46-four-source-regression'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
seal = read(BASE/'evidence-v75.json')
assert len(seal['files']) == 90
assert sha(BASE/seal['archive']) == seal['sha256'] == 'd0b175a52fc7a56c88079c20ba0cabc553e2a8d2b9b4f2d5f0a4b80a424534bb'
save('seal-execution.json', {'command': ['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python', 'artifacts/phase22/integration/v47-faf-sampling/seal.py'], 'exit_code': 0,
    'stdout': '90 120578162 2487675 d0b175a52fc7a56c88079c20ba0cabc553e2a8d2b9b4f2d5f0a4b80a424534bb',
    'qualification': 'Executed directly with tool-captured stdout after writers stopped; no active wrapper log inside the sealed tree. Completion receipt is supplemental after seal75.'})
path = BASE/'README.md'
text = path.read_text().replace('batches 1–74', 'batches 1–75', 1)
first, rest = text.split('\n', 1)
block = f'''\n## FAF profile evidence seal 75

[Seal 75](evidence-v75.json) retains **90 members / 120,578,162 raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 74 prior archives and every member
verified. It preserves the single approved sampled timeout, four raw partial
profiles, source attribution, closed budget, full 239-row audit, unapproved
source-only proposal, final checks and the initial cleanup-check overlap with
its corrected readback. Supplemental v46 delivery and diagnostic approval are
included. Restore after seals 1–74 in numeric order into safe separate staging;
reject unsafe paths/symlinks and verify archive/member hashes before extraction.
Stop on unexplained conflicts. The old v73 seal-log correction remains retained.
No active wrapper log was included in this seal. Owning docs and post-seal
bindings/readback are supplemental. **Phase 22 remains incomplete**; no source
optimization or technical acceptance is authorized by the profile approval.
'''
path.write_text(first+'\n'+block+rest)
url = 'https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
body = (OUT/'pr-body.md').read_text()+f'\n[Seal 75]({url}evidence-v75.json) retains 90 members / 120,578,162 raw bytes; archive SHA-256 `{seal["sha256"]}`. All 74 prior archives and every member verified. Final docs and offline distribution source-member checks pass with unchanged tested code; current documentation/delivery bindings are supplemental after the seal.\n'
with (OUT/'pr-body-delivery.md').open('x') as stream:
    stream.write(body)
old = read(OLD/'documentation-binding.json')
worktrees = subprocess.check_output(['git', 'worktree', 'list', '--porcelain'], text=True)
def parse(value):
    return {b.splitlines()[0].removeprefix('worktree '): next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in value.strip().split('\n\n')}
for name, head in parse(old['worktrees']).items():
    assert parse(worktrees)[name] == ('73d7b61129e2e8ee8c49e491e0a436390ae2142c' if name == str(ROOT) else head), name
for name, digest in old['user_files_sha256'].items():
    assert sha(ROOT/name) == digest, name
review = ['assessment.json', 'sample-attribution.json', 'source-assessment.json', 'frame-source-bindings.json', 'raw-binding.json',
    'audit.json', 'optimization-proposal.json', 'summary.md', 'pr-body-delivery.md', 'final-checks.json', 'final-distributions.json',
    'command-provenance.json', 'cleanup-check-correction.json', 'owned-work.json', 'prior-row-preservation.json', 'seal-execution.json',
    '../v46-four-source-regression/diagnostic-authorization.json', '../v46-four-source-regression/diagnostic-consumed.json',
    '../v46-four-source-regression/diagnostic-preflight.json', '../v46-four-source-regression/authorize-diagnostic.py']
save('documentation-binding.json', {'recorded_at': datetime.now(timezone.utc).isoformat(), 'baseline_delivery': '73d7b61129e2e8ee8c49e491e0a436390ae2142c',
    'corrected_scanner': read(OUT/'assessment.json')['scanner'], 'owning_docs_sha256': {name: sha(ROOT/name) for name in read(OUT/'owning-docs.json')['sha256']},
    'review_packet_sha256': {str((OUT/name).resolve().relative_to(ROOT)): sha(OUT/name) for name in review}, 'user_files_sha256': old['user_files_sha256'], 'worktrees': worktrees,
    'evidence_seal': {'index': 'artifacts/phase22/integration/evidence-v75.json', 'index_sha256': sha(BASE/'evidence-v75.json'), 'archive_sha256': seal['sha256']},
    'optimization_proposal_sha256': sha(OUT/'optimization-proposal.json'), 'sampled_attempts': 1, 'sampled_completed_inputs': 0, 'remaining': 0,
    'budget_closed': True, 'optimization_attempts': 0, 'paid_calls': 0, 'technical_acceptance_received': False, 'phase22_complete': False,
    'qualification': 'Post-seal owning-doc/review binding; engineering source remains tested17b4784. A later supplemental remote receipt verifies the actual delivery; no circular self-binding claim.'})
print('Bound16owning docs and unstarted source-only proposal after seal75.')
