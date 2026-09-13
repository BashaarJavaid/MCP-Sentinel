"""Bind final docs and the concrete unexecuted diagnostic after seal74."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
OLD = BASE/'v45-four-source-recovery'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
def save(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
seal = read(BASE/'evidence-v74.json')
assert len(seal['files']) == 112
assert sha(BASE/seal['archive']) == seal['sha256'] == '6a06288474da6e634a417ff46c336f27ddfad2514c4c88b710a674a58abba110'
save('seal-execution.json', {'command': ['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python', 'artifacts/phase22/integration/v46-four-source-regression/seal.py'], 'exit_code': 0, 'stdout': '112 3616591 1147071 6a06288474da6e634a417ff46c336f27ddfad2514c4c88b710a674a58abba110', 'qualification': 'Executed directly with tool-captured stdout; no active wrapper log existed inside the sealed tree. This completion receipt is supplemental after seal74.'})
path = BASE/'README.md'
text = path.read_text().replace('batches 1–73', 'batches 1–74', 1)
first, rest = text.split('\n', 1)
block = f'''\n## Stopped regression evidence seal 74

[Seal 74](evidence-v74.json) retains **112 members / 3,616,591 raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 73 prior archives and every member
verified. This seal preserves the approved first-input timeout, 204 closed
unstarted observations, full 233-row audit, zero-call accounting, unapproved
diagnostic and its synthetic checks, final docs/package checks, the initial
build-command failure and correction, and supplemental v45 delivery receipts.
Restore after seals 1–73 in numeric order into safe separate staging; reject
unsafe paths/symlinks and verify every archive/member before extraction. Stop
on unexplained conflicts. The v73 seal-log correction remains explicitly retained.
No active wrapper log was included during this seal. Current owning docs and
post-seal delivery bindings are supplemental and directly tracked.
**Phase 22 remains incomplete.** No diagnostic or technical acceptance is implied.
'''
path.write_text(first+'\n'+block+rest)
body = (OUT/'pr-body.md').read_text()
url = 'https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
body += f'\n[Seal 74]({url}evidence-v74.json) retains 112 members with archive SHA-256 `{seal["sha256"]}`. All 73 prior archives and members verified. The [initial package-command failure and established offline correction]({url}v46-four-source-regression/build-command-correction.json) remain preserved; final docs and source-member package verification passed. Post-seal documentation/delivery receipts are supplemental.\n'
with (OUT/'pr-body-delivery.md').open('x') as stream:
    stream.write(body)
old = read(OLD/'documentation-binding.json')
worktrees = subprocess.check_output(['git', 'worktree', 'list', '--porcelain'], text=True)
def parse(value):
    return {b.splitlines()[0].removeprefix('worktree '): next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in value.strip().split('\n\n')}
for name, head in parse(old['worktrees']).items():
    assert parse(worktrees)[name] == ('0135461d26688fc286e97a486cdef9336bac6eb1' if name == str(ROOT) else head), name
for name, digest in old['user_files_sha256'].items():
    assert sha(ROOT/name) == digest, name
review = ['assessment.json', 'audit.json', 'validation.json', 'diagnostic-proposal.json', 'sampler-selfcheck/packet.json',
          'summary.md', 'pr-body-delivery.md', 'final-checks.json', 'final-distributions.json', 'command-provenance.json',
          'build-command-correction.json', 'owned-work.json', 'prior-row-preservation.json', 'seal-execution.json',
          '../v45-four-source-recovery/evaluation-authorization.json', '../v45-four-source-recovery/execution-consumed.json',
          '../v45-four-source-recovery/execution-preflight.json', '../v45-four-source-recovery/authorize-regression.py']
save('documentation-binding.json', {'recorded_at': datetime.now(timezone.utc).isoformat(), 'baseline_delivery': '0135461d26688fc286e97a486cdef9336bac6eb1',
    'corrected_scanner': read(OUT/'assessment.json')['scanner'], 'owning_docs_sha256': {name: sha(ROOT/name) for name in read(OUT/'owning-docs.json')['sha256']},
    'review_packet_sha256': {str((OUT/name).resolve().relative_to(ROOT)): sha(OUT/name) for name in review},
    'user_files_sha256': old['user_files_sha256'], 'worktrees': worktrees,
    'evidence_seal': {'index': 'artifacts/phase22/integration/evidence-v74.json', 'index_sha256': sha(BASE/'evidence-v74.json'), 'archive_sha256': seal['sha256']},
    'diagnostic_proposal_sha256': sha(OUT/'diagnostic-proposal.json'), 'corpus_budget': read(OUT/'assessment.json')['budget'],
    'diagnostic_executions': 0, 'paid_calls': 0, 'technical_acceptance_received': False, 'phase22_complete': False,
    'qualification': 'Post-seal owning-doc/review binding; product source retains tested17b4784. A later remote receipt verifies the actual delivery and is supplemental, never circularly included in itself.'})
print('Bound16owning docs and unexecuted diagnostic after verified seal74.')
