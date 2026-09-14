"""Bind the completed, sealed uncapped experiment to its review documentation."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
PREV = BASE / 'v68-invalidation-sampling'
PREP = BASE / 'v69-uncapped-four-repository'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    with (OUT / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')

seal = read(BASE / 'evidence-v97.json')
assert sha(BASE / seal['archive']) == seal['sha256']
assert read(OUT / 'final-checks.json')['passed']
save('seal-execution.json', {'command': ['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python', '-I', str(OUT / 'seal.py')], 'exit_code': 0, 'members': len(seal['files']), 'raw_bytes': sum(r['bytes'] for r in seal['files']), 'archive_sha256': seal['sha256'], 'qualification': 'Direct execution after all writers stopped; supplemental completion receipt. Delivery helper sources were prepared before sealing.'})
p = BASE / 'README.md'
s = p.read_text()
assert s.count('batches 1–96') == 1
s = s.replace('batches 1–96', 'batches 1–97', 1)
first, rest = s.split('\n', 1)
block = f'''
## Current uncapped four-repository evidence seal 97

[Seal 97](evidence-v97.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 96 earlier archives and every new member verified.
The sole approved `4145d35` uncapped experiment completed 24 observations and 12
entire ordered pairs. Two narrow gates pass; Lightning qualification and FAF
detection/support fail. All 399 audit rows, source/difference assessments, helper
corrections, final checks/packages and supplemental v68 delivery/status-correction
receipts are preserved. Restore after seals 1–96 in numeric order into safe
separate staging; reject unsafe paths/symlinks, verify all hashes and stop on
unexplained conflicts. The v73 log correction remains preserved. Post-seal
documentation and exact draft readback are supplemental.
**Phase 22 remains incomplete; normal 1800-second policy is unchanged.**
'''
p.write_text(first + '\n' + block + rest)
url = 'https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
with (OUT / 'pr-body-delivery.md').open('x') as f:
    f.write((OUT / 'pr-body.md').read_text() + f'\n[Seal 97]({url}evidence-v97.json): {len(seal["files"])} members, SHA-256 `{seal["sha256"]}`; all 96 earlier archives verified. Final docs/packages pass with unchanged tested `4145d35` product bytes.\n')
old = read(PREV / 'documentation-binding.json')
worktrees = subprocess.check_output(['git', 'worktree', 'list', '--porcelain'], text=True)
def parse(value):
    return {b.splitlines()[0].removeprefix('worktree '): next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in value.strip().split('\n\n')}
actual, expected = parse(worktrees), parse(old['worktrees'])
assert set(actual) == set(expected)
for name, head in expected.items():
    assert actual[name] == ('8f4c4486ab9644ace9adac2e3570d2f3d4afe9fb' if name == str(ROOT) else head), name
for name, digest in old['user_files_sha256'].items():
    assert sha(ROOT / name) == digest, name
review = ['final-assessment/assessment.json', 'final-assessment/validation.json', 'final-assessment/report-difference-inventory.json', 'final-assessment/report-difference-assessment.json', 'compatible-reuse.json', 'audit.json', 'prior-row-preservation.json', 'summary.md', 'pr-body-delivery.md', 'final-checks.json', 'final-distributions.json', 'command-provenance.json', 'check-failure-assessment.json', 'owned-final.json', 'seal-execution.json', 'execution.json', 'launch.json', 'lightning-readonly-diagnosis.json', 'first-faf-assessment/named-source-diagnosis.json', 'first-faf-assessment/source-index-correction.json', 'first21-assessment/faf-fixed-source-assessment.json', 'first21-assessment/assessment-binding-check.json']
extra = [PREV / 'delivery-verification.json', PREV / 'audit-current-status.json', PREV / 'optimization-proposal.json', *[PREP / n for n in ['intake.json', 'evaluation-proposal.json', 'evaluation-authorization.json', 'execution-consumed.json', 'execution-preflight.json', 'launcher-binding.json', 'scoring-rubric.json']]]
review_paths = [OUT / n for n in review] + extra
a = read(OUT / 'final-assessment/assessment.json')
save('documentation-binding.json', {'recorded_at': datetime.now(timezone.utc).isoformat(), 'baseline_delivery': '8f4c4486ab9644ace9adac2e3570d2f3d4afe9fb', 'corrected_scanner': a['scanner'], 'owning_docs_sha256': {n: sha(ROOT / n) for n in old['owning_docs_sha256']}, 'review_packet_sha256': {str(p.relative_to(ROOT)): sha(p) for p in review_paths}, 'additional_normative_docs_sha256': {'docs/architecture.md': sha(ROOT / 'docs/architecture.md')}, 'user_files_sha256': old['user_files_sha256'], 'worktrees': worktrees, 'evidence_seal': {'index': 'artifacts/phase22/integration/evidence-v97.json', 'index_sha256': sha(BASE / 'evidence-v97.json'), 'archive_sha256': seal['sha256']}, 'evaluation_proposal_sha256': sha(PREP / 'evaluation-proposal.json'), 'evaluation_authorization_sha256': sha(PREP / 'evaluation-authorization.json'), 'pending_optimization_proposal_sha256': sha(PREV / 'optimization-proposal.json'), 'experiment_budget': {'attempts': 24, 'completed': 24, 'incomplete': 0, 'ordered_pairs': 12, 'remaining': 0, 'closed': True}, 'current_source_input_accounting': read(OUT / 'audit.json')['current_source_input_accounting'], 'repository_gates_passed': 2, 'profiles_in_this_continuation': 0, 'optimization_approved': False, 'optimization_attempts': 0, 'paid_calls': 0, 'technical_acceptance_received': False, 'phase22_complete': False, 'qualification': 'Post-seal binding. Product/tests/workflows/lock/schema retain tested4145d35; final README metadata rebuilt. The sole uncapped experiment completed, with two failed gates and current earlier-language compatibility pending. Pending source-only literal optimization remains unapproved/unimplemented. Exact supplemental draft readback remains required.'})
print('Bound 16 owning docs and complete uncapped review after seal97; Phase22 remains incomplete.')
