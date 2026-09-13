"""Verify unchanged engineering, complete stopped-budget evidence and final docs."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
OLD = BASE/'v52-merge-fastpath'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

checks = ['v53-validation','v53-sampler-synthetic','v53-owned-cleanup','v53-assessment-preparation','v53-diagnostic-boundary','v53-reconciliation','v53-final-docs','v53-final-build','v53-final-distributions']
for name in checks:
    assert read(BASE/(name+'.json'))['exit_code']==0,name
engineering = read(OLD/'local-checks.json')['candidate_engineering_files_sha256']
assert len(engineering) == 302
for name, digest in engineering.items():
    assert sha(ROOT/name) == digest, name
    assert sha(Path('/private/tmp/mcp-phase22-frozen-a36f696')/name) == digest, name
binding = read(OLD/'documentation-binding.json')
for name, digest in binding['user_files_sha256'].items():
    assert sha(ROOT/name) == digest, name
for name, digest in read(OUT/'owning-docs.json')['sha256'].items():
    assert sha(ROOT/name) == digest, name
for name, digest in read(BASE/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256'].items():
    assert sha(ROOT/name) == digest, name
for filename in ['corrected-sampling-worker.py','sampler-selfcheck.py','diagnostic.py']:
    expected=(BASE/'v50-faf-allocation-sampling'/filename).read_text().replace('v50-faf-allocation-sampling','v53-fastpath-regression').replace('v48-merge-allocation','v52-merge-fastpath').replace('v51-faf-bound-sampling','v54-faf-fastpath-sampling').replace('6e4fd671a97d92f6297dffc900c4dd9e18faad2c','a36f696c504e4e8d1f90de5dc84e8942d06316ca').replace('d1d24e53db3dc112639aaedcfd6a03102188e29d3007fcfc823d2b1b015cc2ed','2f4a49aeb2173ca2174b984b8108174d96d6df42cec93e58522caf713efbaeab').replace('mcp-phase22-frozen-6e4fd67','mcp-phase22-frozen-a36f696')
    if filename=='sampler-selfcheck.py':expected=expected.replace('mcp-phase22-frozen-17b4784','mcp-phase22-frozen-6e4fd67')
    assert (OUT/filename).read_text()==expected,filename
proposal = read(OUT/'diagnostic-proposal.json')
for name, digest in proposal['files_sha256'].items():
    assert sha(ROOT/name) == digest, name
assert not (OUT/'diagnostic-authorization.json').exists()
assert not (OUT/'diagnostic-consumed.json').exists()
assert not (BASE/'v54-faf-fastpath-sampling').exists()
assert read(OUT/'assessment.json')['budget']['unstarted_closed'] == 204
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
audit = read(OUT/'audit.json')
assert len(audit['requirements']) == 89 and len(audit['additional_scope_requirements']) == 188
assert audit['requirements'] == read(OLD/'audit.json')['requirements']
assert not audit['technical_acceptance_received'] and not audit['phase22_complete']
assert not subprocess.check_output(['git', 'diff', 'a36f696', '--', 'src', 'tests', 'scripts', 'schemas', '.github', 'uv.lock', 'pyproject.toml', 'CHANGELOG.md'])
subprocess.run(['git', 'diff', '--check'], check=True)
subprocess.run(['git', 'merge-base', '--is-ancestor', '8b6b0ddf1d6f6cf5a8da3ab9421471865b801455', 'HEAD'], check=True)
main = Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=main, text=True).strip() == '4cd57593b2585b9ee05c0f175930e6a0d76d362a'
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=main)
failed={p.stem:read(p)['exit_code'] for p in BASE.glob('v53-*.json') if 'exit_code' in read(p) and read(p)['exit_code']!=0}
assert not failed,failed
provenance={'wrapper_commands':{n:read(BASE/(n+'.json')) for n in checks},
 'direct_commands':[
 {'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OLD/'authorize-regression.py')],'exit_code':0,'evidence':'v52-merge-fastpath/execution-preflight.json'},
 {'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OLD/'launch.py')],'exit_code':1,'evidence':'v53-fastpath-regression/execution.json','console':'No direct stdout; child output retained in sequence.log and raw input log.'}],
 'failure_assessment':'The approved native first input hit its300-second maximum, producing no report. Its204unstarted observations and all remaining budget closed. Output,source,synthetic identity and missing-approval checks passed. The stale-root synthetic control intentionally failed before timer/target access; it is no corpus attempt. No retry or product change occurred.',
 'paid_calls':0,'retry_observations':0}
write('check-failure-assessment.json',{'native_execution_exit_code':1,'failed_wrapper_checks':failed,'explanation':provenance['failure_assessment'],'paid_calls':0,'corpus_retries':0})
write('command-provenance.json', provenance)
write('final-checks.json', {'passed': True, 'recorded_at': datetime.now(timezone.utc).isoformat(),
    'scanner': read(OLD/'freeze.json')['scanner'], 'engineering_files_verified': 302, 'prior_evidence_files_verified': len(read(BASE/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']),
    'requirements': 277, 'protected_user_files': 8, 'owning_docs': 16, 'main_and_parent_preserved': True,
    'checks_sha256': {n: sha(BASE/(n+'.json')) for n in checks}, 'diagnostic_proposal_sha256': sha(OUT/'diagnostic-proposal.json'),
    'corpus_budget': read(OUT/'assessment.json')['budget'], 'diagnostic_executions': 0, 'paid_calls': 0,
    'technical_acceptance_received': False, 'phase22_complete': False})
print('Final checks passed:302engineering files,277requirements,16docs,closed205budget and unexecuted diagnostic.')
