"""Deliver stopped regression and unapproved parent-and-worker diagnostic to the existing draft only."""
import hashlib
import json
import subprocess
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
OLD = OUT
EXPECTED = 'da7557076b122611dbfedd3587450796073af288'
TITLE = 'Phase 22: invalidation regression timed out; diagnostic pending'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
def run(args):
    return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.STDOUT, timeout=180)
def save(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
def pr():
    return json.loads(run(['gh', 'pr', 'view', '37', '--json', 'number,state,isDraft,headRefName,headRefOid,baseRefName,title,body']))
def guard(d):
    assert d['state'] == 'OPEN' and d['isDraft'] and d['headRefName'] == 'phase22/integration' and d['baseRefName'] == 'phase22/description-poisoning'
binding = read(OUT/'documentation-binding.json')
for field in ['owning_docs_sha256', 'review_packet_sha256', 'user_files_sha256']:
    for name, digest in binding[field].items():
        assert sha(ROOT/name) == digest, name
assert run(['git', 'rev-parse', 'HEAD']).strip() == EXPECTED
assert run(['git', 'branch', '--show-current']).strip() == 'phase22/integration'
assert not run(['git', 'diff', '--cached'])
assert set(run(['git', 'diff', '--name-only']).splitlines()) == set(binding['owning_docs_sha256'])
run(['git', 'diff', '--check'])
run(['git', 'merge-base', '--is-ancestor', '8b6b0ddf1d6f6cf5a8da3ab9421471865b801455', 'HEAD'])
assert not (OUT/'diagnostic-authorization.json').exists() and not (OUT/'diagnostic-consumed.json').exists()
assert not (BASE/'v68-invalidation-sampling').exists()
seal = read(BASE/'evidence-v95.json')
assert sha(BASE/'evidence-v95.json') == binding['evidence_seal']['index_sha256']
assert sha(BASE/seal['archive']) == seal['sha256'] == binding['evidence_seal']['archive_sha256']
with tarfile.open(BASE/seal['archive']) as archive:
    assert len(archive.getmembers()) == len(seal['files'])
    for row in seal['files']:
        assert sha(BASE/row['path']) == row['sha256'], row['path']
        member = archive.getmember(row['path'])
        assert member.isfile() and member.size == row['bytes']
        assert hashlib.sha256(archive.extractfile(member).read()).hexdigest() == row['sha256']
for name, digest in read(BASE/'v66-invalidation-contract/local-checks.json')['candidate_engineering_files_sha256'].items():
    if name != 'README.md': assert sha(ROOT/name) == digest, name
current = pr()
guard(current)
assert current['title'] == 'Phase 22: invalidation accumulator verified; regression pending'
assert current['headRefOid'] == EXPECTED and current['body'] == (BASE/'v66-invalidation-contract/pr-body-delivery.md').read_text()
assert run(['gh', 'api', 'repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration', '--jq', '.commit.sha']).strip() == EXPECTED
save('pre-delivery-pr37.json', current)
selected = set(binding['owning_docs_sha256']) | set(binding['review_packet_sha256'])
extra = [BASE/'evidence-v95.json', BASE/'evidence-v95.tar.gz', OUT/'documentation-binding.json', OUT/'pre-delivery-pr37.json']
extra.extend(OUT.glob('*.py'))
extra.extend(BASE.glob('v67-documentation-binding.*'))
selected.update(str(p.relative_to(ROOT)) for p in extra)
assert not selected & set(binding['user_files_sha256'])
run(['git', 'add', '-f', '--', *sorted(selected)])
staged = set(run(['git', 'diff', '--cached', '--name-only']).splitlines())
assert staged <= selected and not staged & set(binding['user_files_sha256'])
assert not any(n.startswith(('src/', 'tests/', 'scripts/', 'schemas/', '.github/')) for n in staged)
run(['git', 'diff', '--cached', '--check', '--', *binding['owning_docs_sha256']])
save('staged-delivery.json', {'sha256': {n: sha(ROOT/n) for n in sorted(staged)}, 'protected_user_files_not_staged': True, 'diagnostic_proposal_sha256': binding['diagnostic_proposal_sha256']})
print(run(['git', 'commit', '-m', 'Assess invalidation regression timeout and prepare bounded diagnostic [skip ci]']), flush=True)
head = run(['git', 'rev-parse', 'HEAD']).strip()
save('delivery-commit.json', {'head': head, 'parent': EXPECTED, 'diagnostic_proposal_sha256': binding['diagnostic_proposal_sha256'], 'technical_acceptance_received': False})
print(run(['git', 'push', 'https://github.com/BashaarJavaid/MCP-Sentinel.git', 'HEAD:refs/heads/phase22/integration']), flush=True)
save('metadata-update.json', {'title': TITLE, 'body': (OUT/'pr-body-delivery.md').read_text()})
response=json.loads(run(['gh','api','--method','PATCH','repos/BashaarJavaid/MCP-Sentinel/pulls/37','--input',str(OUT/'metadata-update.json'),'--jq','{number,state,draft,title,head:.head.sha,base:.base.ref}']));save('metadata-response.json',response);print(json.dumps(response),flush=True)
history = []
for attempt in range(12):
    current = pr()
    branch = run(['gh', 'api', 'repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration', '--jq', '.commit.sha']).strip()
    guard(current)
    history.append({'recorded_at': datetime.now(timezone.utc).isoformat(), 'pr': current, 'branch_head': branch})
    if current['headRefOid'] == head and branch == head and current['title'] == TITLE and current['body'] == (OUT/'pr-body-delivery.md').read_text():
        break
    print('Remote readback stale; retrying read only.', flush=True)
    time.sleep(5)
else:
    save('delivery-readback-history.json', history)
    raise AssertionError('Remote readback stale; preserve completed mutations and recheck read only.')
save('delivery-readback-history.json', history)
for name, digest in binding['user_files_sha256'].items():
    assert sha(ROOT/name) == digest, name
main = Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=main, text=True).strip() == '4cd57593b2585b9ee05c0f175930e6a0d76d362a'
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=main)
assert not run(['git', 'diff', 'HEAD', '--name-only'])
receipt = {'passed': True, 'recorded_at': datetime.now(timezone.utc).isoformat(), 'head': head, 'base': 'phase22/description-poisoning', 'draft': True, 'open': True, 'title': TITLE,
    'body_sha256': sha(OUT/'pr-body-delivery.md'), 'diagnostic_proposal_sha256': binding['diagnostic_proposal_sha256'], 'scanner': binding['corrected_scanner'],
    'seal95_sha256': seal['sha256'], 'readback_history_sha256': sha(OUT/'delivery-readback-history.json'), 'documentation_binding_sha256': sha(OUT/'documentation-binding.json'),
    'protected_user_files_and_main_preserved': True, 'optimization_attempts': 0, 'current_source_corpus_observations': 1, 'corpus_budget': binding['corpus_budget'], 'profiles': 0, 'diagnostic_approved': False, 'regression_approved': True, 'paid_calls': 0,
    'technical_acceptance_received': False, 'phase22_complete': False,
    'effective_scope_disposition': {'id': 'V67-DELIVERY', 'disposition': 'passed', 'basis': 'Final docs/package/source checks, seal, commit/push and exact remote branch/PR head/base/draft/title/body readback verified. Supersedes sealed pending row for delivery only.'},
    'effective_additional_counts': {'passed': 270, 'historical_closure_proposals': 6, 'unresolved': 18},
    'provenance': 'Supplemental post-commit readback, outside seal95 and the commit it verifies; retain in next authorized seal.'}
save('delivery-verification.json', receipt)
print(json.dumps(receipt, indent=2), flush=True)
