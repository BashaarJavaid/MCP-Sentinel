"""Check final documentation, actual tested source, prepared budget and prior evidence."""
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
def save(name, value):
    with (OUT/name).open('x') as f: json.dump(value, f, indent=2); f.write('\n')
checks = ['v59-runner-boundaries', 'v59-quality-audit', 'v59-local-checks', 'v59-freeze', 'v59-prepare-regression', 'v59-frozen-source', 'v59-launcher-binding', 'v59-proposal-check', 'v59-launcher-check', 'v59-check-assessment', 'v59-reconciliation', 'v59-final-docs', 'v59-final-build', 'v59-final-distributions', 'v59-owned-final']
for name in checks: assert read(BASE/(name+'.json'))['exit_code'] == 0, name
freeze = read(OUT/'freeze.json')
engineering = read(OUT/'local-checks.json')['candidate_engineering_files_sha256']
assert len(engineering) == 302
for name, digest in engineering.items():
    assert sha(ROOT/name) == digest and sha(Path(freeze['frozen_checkout'])/name) == digest, name
for name, digest in read(OUT/'authorization.json')['user_files_sha256'].items(): assert sha(ROOT/name) == digest, name
for name, digest in read(OUT/'owning-docs.json')['sha256'].items(): assert sha(ROOT/name) == digest, name
prior = read(BASE/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']
for name, digest in prior.items(): assert sha(ROOT/name) == digest, name
proposal = read(OUT/'evaluation-proposal.json')
for name, digest in proposal['files_sha256'].items(): assert sha(ROOT/name) == digest, name
assert not (OUT/'evaluation-authorization.json').exists() and not (OUT/'execution-consumed.json').exists()
assert not (BASE/'v60-long-timeout-regression').exists()
assert not (BASE/'v59-faf-credential-sampling').exists()
assert not (BASE/'v58-credential-regression/diagnostic-authorization.json').exists()
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
audit = read(OUT/'audit.json')
assert len(audit['requirements']) == 89 and len(audit['additional_scope_requirements']) == 234
assert audit['requirements'] == read(BASE/'v58-credential-regression/audit.json')['requirements']
assert not audit['technical_acceptance_received'] and not audit['phase22_complete']
assert audit['current_source_corpus_observations'] == 0
assert not subprocess.check_output(['git', 'diff', '7bf4c6e', '--', 'src', 'tests', 'scripts', 'schemas', '.github', 'uv.lock', 'pyproject.toml', 'CHANGELOG.md', 'docs/architecture.md'])
subprocess.run(['git', 'diff', '--check'], check=True)
subprocess.run(['git', 'merge-base', '--is-ancestor', '8b6b0ddf1d6f6cf5a8da3ab9421471865b801455', 'HEAD'], check=True)
main = Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=main, text=True).strip() == '4cd57593b2585b9ee05c0f175930e6a0d76d362a'
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=main)
wrappers = {p.stem: read(p) for p in BASE.glob('v59-*.json') if 'exit_code' in read(p)}
assert all(r['exit_code'] == 0 for r in wrappers.values())
save('command-provenance.json', {'wrapper_commands': wrappers, 'qualification': 'Source-policy implementation, engineering and proposal preparation only. Evaluation has not been approved or executed. All earlier measurement failures retain their own commands and closed budgets.', 'corpus_observations': 0, 'paid_calls': 0})
save('final-checks.json', {'passed': True, 'recorded_at': datetime.now(timezone.utc).isoformat(), 'scanner': freeze['scanner'], 'engineering_files_verified': 302, 'prior_evidence_files_verified': len(prior), 'requirements': 323, 'protected_user_files': 8, 'owning_docs': 16, 'additional_normative_doc_sha256': {'docs/architecture.md': sha(ROOT/'docs/architecture.md')}, 'main_and_parent_preserved': True, 'checks_sha256': {n: sha(BASE/(n+'.json')) for n in checks}, 'evaluation_proposal_sha256': sha(OUT/'evaluation-proposal.json'), 'corpus_observations': 0, 'profiles': 0, 'paid_calls': 0, 'technical_acceptance_received': False, 'phase22_complete': False})
print('Final checks pass: 302 engineering files, 323 requirements, 16 status docs, unexecuted longer-timeout proposal.')
