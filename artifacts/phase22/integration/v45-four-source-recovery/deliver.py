"""Verify and deliver the completed source recovery; authorize no evaluation."""
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
EXPECTED = '17b4784363f35096a13d33913e98967b24cbad14'
TITLE = 'Phase 22: source recovery verified; regression approval pending'
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


def guard(value):
    assert value['state'] == 'OPEN' and value['isDraft']
    assert value['headRefName'] == 'phase22/integration'
    assert value['baseRefName'] == 'phase22/description-poisoning'


binding = read(OUT/'documentation-binding.json')
for field in ['owning_docs_sha256', 'review_packet_sha256', 'user_files_sha256']:
    for name, digest in binding[field].items():
        assert sha(ROOT/name) == digest, name
assert run(['git', 'branch', '--show-current']).strip() == 'phase22/integration'
assert run(['git', 'rev-parse', 'HEAD']).strip() == EXPECTED
assert not run(['git', 'diff', '--cached'])
assert set(run(['git', 'diff', '--name-only']).splitlines()) == set(binding['owning_docs_sha256'])
run(['git', 'diff', '--check'])
run(['git', 'merge-base', '--is-ancestor', '8b6b0ddf1d6f6cf5a8da3ab9421471865b801455', 'HEAD'])
for name in ['evaluation-authorization.json', 'execution-consumed.json']:
    assert not (OUT/name).exists()
assert not (BASE/'v46-four-source-regression').exists()
seal = read(BASE/'evidence-v73.json')
assert sha(BASE/'evidence-v73.json') == binding['evidence_seal']['index_sha256']
assert sha(BASE/seal['archive']) == binding['evidence_seal']['archive_sha256'] == seal['sha256']
with tarfile.open(BASE/seal['archive'], 'r:gz') as archive:
    assert len(archive.getmembers()) == len(seal['files']) == 704
    for row in seal['files']:
        assert sha(BASE/row['path']) == row['sha256'], row['path']
        member = archive.getmember(row['path'])
        assert member.isfile() and member.size == row['bytes']
        assert hashlib.sha256(archive.extractfile(member).read()).hexdigest() == row['sha256']
current = pr()
guard(current)
assert current['headRefOid'] == EXPECTED
assert current['body'] == (OUT/'pr-body-engineering.md').read_text()
assert run(['gh', 'api', 'repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration', '--jq', '.commit.sha']).strip() == EXPECTED
save('pre-delivery-pr37.json', current)
# Preserve the bound initial body; correct its one relative URL and spacing for delivery.
body = (OUT/'pr-body-delivery.md').read_text()
body = body.replace('/blob/phase22/integration/v45-four-source-recovery/distribution-check-correction.json', '/blob/phase22/integration/artifacts/phase22/integration/v45-four-source-recovery/distribution-check-correction.json')
body = body.replace('retains704members (18,413,816rawbytes)', 'retains 704 members (18,413,816 raw bytes)').replace('all72prior', 'all 72 prior')
with (OUT/'pr-body-reviewed.md').open('x') as stream:
    stream.write(body)
save('review-body-correction.json', {'initial_body_sha256': sha(OUT/'pr-body-delivery.md'), 'delivered_body_sha256': sha(OUT/'pr-body-reviewed.md'), 'changes': 'Correct one GitHub artifact URL and missing spaces; all technical scope and immutable proposal/launcher bindings unchanged.'})
selected = set(binding['owning_docs_sha256']) | set(binding['review_packet_sha256'])
extra = [BASE/'evidence-v73.json', BASE/'evidence-v73.tar.gz', OUT/'documentation-binding.json', OUT/'bind-delivery.py', Path(__file__).resolve(), OUT/'pre-delivery-pr37.json', OUT/'pr-body-reviewed.md', OUT/'review-body-correction.json', OUT/'evaluate.py', OUT/'launch.py', OUT/'prepare-regression.py']
extra.extend(BASE.glob('v45-documentation-binding.*'))
selected.update(str(p.relative_to(ROOT)) for p in extra)
assert not selected & set(binding['user_files_sha256'])
save('pre-delivery-verification.json', {'passed': True, 'scanner': binding['corrected_scanner'], 'seal_members_verified': 704, 'documentation_binding_sha256': sha(OUT/'documentation-binding.json'), 'proposal_sha256': binding['proposal_sha256'], 'launcher_binding_sha256': binding['launcher_binding_sha256'], 'new_current_source_observations': 0, 'new_paid_calls': 0, 'selected_paths': sorted(selected)})
selected.add(str((OUT/'pre-delivery-verification.json').relative_to(ROOT)))
run(['git', 'add', '-f', '--', *sorted(selected)])
staged = set(run(['git', 'diff', '--cached', '--name-only']).splitlines())
assert staged <= selected and not staged & set(binding['user_files_sha256'])
assert not any(n.startswith(('src/', 'tests/', 'scripts/', 'schemas/', '.github/')) for n in staged)
run(['git', 'diff', '--cached', '--check', '--', *binding['owning_docs_sha256']])
save('staged-delivery.json', {'paths': sorted(staged), 'sha256': {n: sha(ROOT/n) for n in staged}, 'protected_user_files_not_staged': True})
print(run(['git', 'commit', '-m', 'Deliver verified source recovery and bounded regression proposal [skip ci]']), flush=True)
head = run(['git', 'rev-parse', 'HEAD']).strip()
save('delivery-commit.json', {'head': head, 'parent': EXPECTED, 'proposal_sha256': binding['proposal_sha256'], 'technical_acceptance_received': False})
print(run(['git', 'push', 'origin', 'HEAD:refs/heads/phase22/integration']), flush=True)
print(run(['gh', 'pr', 'edit', '37', '--title', TITLE, '--body-file', str(OUT/'pr-body-reviewed.md')]), flush=True)
history = []
for attempt in range(12):
    current = pr()
    branch = run(['gh', 'api', 'repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration', '--jq', '.commit.sha']).strip()
    guard(current)
    history.append({'recorded_at': datetime.now(timezone.utc).isoformat(), 'pr': current, 'branch_head': branch})
    if current['headRefOid'] == head and branch == head and current['title'] == TITLE and current['body'] == body:
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
receipt = {'passed': True, 'recorded_at': datetime.now(timezone.utc).isoformat(), 'head': head, 'base': 'phase22/description-poisoning', 'draft': True, 'open': True, 'title': TITLE, 'body_sha256': sha(OUT/'pr-body-reviewed.md'), 'proposal_sha256': binding['proposal_sha256'], 'launcher_binding_sha256': binding['launcher_binding_sha256'], 'scanner': binding['corrected_scanner'], 'seal73_sha256': seal['sha256'], 'readback_history_sha256': sha(OUT/'delivery-readback-history.json'), 'documentation_binding_sha256': sha(OUT/'documentation-binding.json'), 'protected_user_files_and_main_preserved': True, 'new_current_source_corpus_observations': 0, 'proposed_observations': 205, 'new_paid_calls': 0, 'technical_acceptance_received': False, 'phase22_complete': False, 'effective_scope_disposition': {'id': 'V45-DELIVERY', 'disposition': 'passed', 'basis': 'Checks, seal, commit, push and exact remote branch/PR head/base/draft/title/body verified; supersedes sealed pre-delivery unresolved row for delivery only.'}, 'effective_additional_counts': {'passed': 128, 'historical_closure_proposals': 6, 'unresolved': 4}, 'provenance': 'Supplemental post-commit receipt, outside seal73 and the commit it verifies; retain in next authorized seal.'}
save('delivery-verification.json', receipt)
print(json.dumps(receipt, indent=2), flush=True)
