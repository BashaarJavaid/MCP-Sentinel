"""Bind unchanged engineering and production replays after the approved execution."""
import hashlib
import json
import subprocess
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
ASSETS = OUT.parent/'v66-invalidation-contract'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = read(ASSETS/'evaluation-proposal.json')
assert read(OUT/'validation.json')['budget_closed']
local = read(ASSETS/'local-checks.json')
assert local['candidate'] == p['scanner']['revision']
assert local['states'] == {'passed': 2419, 'skipped': 36}
assert len(local['candidate_engineering_files_sha256']) == 303
for name, digest in local['candidate_engineering_files_sha256'].items():
    assert sha(ROOT/name) == digest, name
    assert sha(Path(p['frozen_checkout'])/name) == digest, name
assert not subprocess.check_output(['git', 'diff', '4145d35', '--', 'src', 'tests', 'scripts', 'schemas', '.github', 'uv.lock', 'pyproject.toml', 'CHANGELOG.md'])
quality = read(OUT.parent/'v66-candidate-quality-audit/packet.json')
assert quality['source'] == p['scanner']['revision'] and len(quality['quality']) == 12
assert all(r['passed'] == 2419 and r['skipped'] == 36 for r in quality['quality'])
replay = read(OUT.parent/'v66-production-capture-revalidation/packet.json')
assert replay['source'] == p['scanner']['revision'] and replay['model_calls'] == 0
assert len(replay['requests']) == 6 and all(r['accepted'] for r in replay['requests'])
assert read(ASSETS/'compatibility.json')['scanner'] == p['scanner']['revision']
record = {'scanner': p['scanner'], 'engineering_files_sha256': local['candidate_engineering_files_sha256'], 'local_tests': local['states'], 'coverage_totals': local['coverage_totals'], 'hosted_suites': 12, 'normal_ci_jobs': 29, 'ci_run': 34808261686, 'docs_run': 34808261635, 'production_replays': 6, 'bindings_sha256': {str(path.relative_to(ROOT)): sha(path) for path in [ASSETS/'local-checks.json', OUT.parent/'v66-candidate-quality-audit/packet.json', OUT.parent/'v66-production-capture-revalidation/packet.json', ASSETS/'compatibility.json', ASSETS/'demo-validation.json', ASSETS/'final-distributions.json']}, 'qualification': 'No product/test/workflow/schema/lock change during the approved regression. Actual 4145d35 engineering, six zero-call production replays and approved Git runtime/image bindings remain compatible. This is source-bound reuse, not another hosted suite or production capture. Final documentation/package metadata is checked separately.', 'new_paid_calls': 0, 'new_engineering_test_runs': 0, 'git_campaigns': '312/1040 incomplete; 728 deferred', 'technical_acceptance_received': False, 'phase22_complete': False}
with (OUT/'compatible-reuse.json').open('x') as f: json.dump(record, f, indent=2); f.write('\n')
print('303 unchanged engineering inputs and six production replays retain verified 4145d35 source bindings.')
