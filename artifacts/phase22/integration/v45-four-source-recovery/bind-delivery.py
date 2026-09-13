"""Bind the post-seal review packet and existing draft delivery scope."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old = read(BASE/'v44-four-fresh-evaluation/documentation-binding.json')
seal = read(BASE/'evidence-v73.json')
assert sha(BASE/seal['archive']) == seal['sha256']
assert len(seal['files']) == 704
assert sha(BASE/'v45-seal-completed.log') == read(BASE/'v45-seal-log-binding-correction.json')['actual_completed_log_sha256']
path = BASE/'README.md'
text = path.read_text().replace('batches 1–72', 'batches 1–73', 1)
assert '## Recovery evidence seal 73' not in text
block = f'''\n## Recovery evidence seal 73

[Seal 73](evidence-v73.json) retains **704 members / 18,413,816 raw bytes**,
archive SHA-256 `{seal['sha256']}`. It binds the verified `17b4784` source
recovery, local/hosted engineering, frozen scanner, unapproved 205-observation
proposal, 227-row audit, helpers, failed checks and supplemental v44 delivery.
All 72 prior archives and every member were verified; old archives/indexes remain
unchanged. Restore after seals 1–72 in numeric order into separate safe staging,
reject unsafe paths/symlinks and verify archive/member hashes before extraction.
Stop on any unexplained existing-file conflict.

The [seal-log binding correction](v45-seal-log-binding-correction.json) records that
the archiver captured its own empty wrapper log before printing its final result.
The indexed empty snapshot is restored at its original path; the intact completed
output is retained separately as [v45-seal-completed.log](v45-seal-completed.log).
No archive/index or completed output was altered or discarded. This correction,
post-seal bindings and future delivery readback are supplemental, outside seal 73.
Future sealing must keep its active log outside the sealed tree. Current owning
docs and these supplemental receipts are directly tracked; no self-sealing claim.
**Phase 22 remains incomplete**: evaluation approval, actual regression/source
assessment, explicit technical acceptance and verified accepted closeout remain.
'''
first, rest = text.split('\n', 1)
path.write_text(first+'\n'+block+rest)
body = (OUT/'pr-body.md').read_text()
body += f'''\nEvidence [seal 73](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/evidence-v73.json) retains704members (18,413,816rawbytes), SHA-256 `{seal['sha256']}`; all72prior archives and members verified. The [supplemental seal-log binding correction](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v45-seal-log-binding-correction.json) preserves both its indexed empty wrapper-log snapshot and the intact later completed output. The archive/index is unchanged. Current post-seal bindings and the eventual delivery readback are separately retained.\n'''
with (OUT/'pr-body-delivery.md').open('x') as stream:
    stream.write(body)
worktrees = subprocess.check_output(['git', 'worktree', 'list', '--porcelain'], text=True)
def parse(value):
    return {block.splitlines()[0].removeprefix('worktree '): next(line[5:] for line in block.splitlines() if line.startswith('HEAD ')) for block in value.strip().split('\n\n')}
previous, current = parse(old['worktrees']), parse(worktrees)
head = '17b4784363f35096a13d33913e98967b24cbad14'
for name, revision in previous.items():
    assert current[name] == (head if name == str(ROOT) else revision), name
assert current['/private/tmp/mcp-phase22-frozen-17b4784'] == head
for name, digest in old['user_files_sha256'].items():
    assert sha(ROOT/name) == digest, name
names = ['authorization.json', 'source-recovery-assessment.json', 'local-checks.json', 'compatibility.json',
         'freeze.json', 'evaluation-proposal.json', 'scoring-rubric.json', 'launcher-binding.json',
         'frozen-source-validation.json', 'summary.md', 'audit.json', 'final-checks.json', 'final-distributions.json',
         'pr-body-delivery.md', 'command-provenance.json', 'check-failure-assessment.json', 'preparation-correction.json',
         'distribution-check-correction.json', 'prior-row-preservation.json', 'checkout-binding.json', 'demo-validation.json']
review = {str((OUT/n).relative_to(ROOT)): sha(OUT/n) for n in names}
for path in [BASE/'v45-candidate-quality/packet.json', BASE/'v45-candidate-quality-audit/packet.json',
             BASE/'v45-seal.json', BASE/'v45-seal-completed.log', BASE/'v45-seal-log-binding-correction.json']:
    review[str(path.relative_to(ROOT))] = sha(path)
record = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'baseline_delivery': head,
          'corrected_scanner': read(OUT/'freeze.json')['scanner'], 'current_scanner_corpus_measured': False,
          'tested_workflow': {'head': head, 'ci': 34737757018, 'docs': 34737757049,
                              'actual_merge': '0511e6a57741ac6152922c809c3e0ad72fee0f7f'},
          'owning_docs_sha256': {name: sha(ROOT/name) for name in old['owning_docs_sha256']},
          'review_packet_sha256': review, 'user_files_sha256': old['user_files_sha256'], 'worktrees': worktrees,
          'evidence_seal': {'index': 'artifacts/phase22/integration/evidence-v73.json', 'index_sha256': sha(BASE/'evidence-v73.json'), 'archive_sha256': seal['sha256']},
          'proposal_sha256': sha(OUT/'evaluation-proposal.json'), 'launcher_binding_sha256': sha(OUT/'launcher-binding.json'),
          'proposed_native_observations': 205, 'new_current_source_corpus_observations': 0, 'new_paid_calls': 0,
          'first_frozen_four_gates_passed': 0, 'technical_acceptance_received': False, 'phase22_complete': False,
          'qualification': 'Owning docs and supplemental review/delivery bindings follow immutable seal73. Source/test/workflow/schema/lock bytes remain tested17b4784. All original measured results retain their actual sources. A later remote receipt verifies the commit and is supplemental, not circularly included in itself.'}
with (OUT/'documentation-binding.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print('Bound15owning docs, proposal/launcher and preserved worktrees after seal73; delivery remains draft.')
