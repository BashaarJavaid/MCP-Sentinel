"""Verify unchanged engineering, complete stopped-budget evidence and final docs."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
OLD = BASE/'v59-timeout-policy'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

checks = ['v60-authorization','v60-compatible-reuse','v60-owned-final','v60-validation','v60-sampler-synthetic','v60-owned-cleanup','v60-assessment-preparation','v60-diagnostic-boundary','v60-reconciliation','v60-final-docs','v60-final-build','v60-final-distributions']
for name in checks:
    assert read(BASE/(name+'.json'))['exit_code']==0,name
engineering = read(OLD/'local-checks.json')['candidate_engineering_files_sha256']
assert len(engineering) == 302
for name, digest in engineering.items():
    assert sha(ROOT/name) == digest, name
    assert sha(Path('/private/tmp/mcp-phase22-frozen-7bf4c6e')/name) == digest, name
binding = read(OLD/'documentation-binding.json')
for name, digest in binding['user_files_sha256'].items():
    assert sha(ROOT/name) == digest, name
for name, digest in read(OUT/'owning-docs.json')['sha256'].items():
    assert sha(ROOT/name) == digest, name
for name, digest in read(BASE/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256'].items():
    assert sha(ROOT/name) == digest, name
for filename in ['corrected-sampling-worker.py','sampler-selfcheck.py','diagnostic.py']:
    expected=(BASE/'v58-credential-regression'/filename).read_text()
    for before,after in [('v58-credential-regression','v60-long-timeout-regression'),('v57-credential-merge','v59-timeout-policy'),('v59-faf-credential-sampling','v61-faf-long-timeout-sampling'),('dc7371513a065457af566f4b589b9ed147130d64','7bf4c6e1cf0c8d83229b1273f80737e7cacc5b82'),('4f3e5b2e9c89f61d179ac82db94ced06e83033f9cf1640644cefb53326e96eb9','40c194dcd47a152f78c9b9dc57b40e5e77026f6052035841c0af63b83f234af6'),('mcp-phase22-frozen-dc73715','mcp-phase22-frozen-7bf4c6e')]:
        expected=expected.replace(before,after)
    if filename=='sampler-selfcheck.py':expected=expected.replace('mcp-phase22-frozen-a36f696','mcp-phase22-frozen-dc73715')
    if filename=='diagnostic.py':expected=expected.replace("supervise(command, OUT/'observation.log', 300)","supervise(command, OUT/'observation.log', 1800)")
    assert (OUT/filename).read_text()==expected,filename
import ast
for helper in OUT.glob('*.py'):ast.parse(helper.read_text(),filename=str(helper))
assert not (BASE/'v59-faf-credential-sampling').exists()
assert not (BASE/'v58-credential-regression/diagnostic-authorization.json').exists()
proposal = read(OUT/'diagnostic-proposal.json')
for name, digest in proposal['files_sha256'].items():
    assert sha(ROOT/name) == digest, name
assert not (OUT/'diagnostic-authorization.json').exists()
assert not (OUT/'diagnostic-consumed.json').exists()
assert not (BASE/'v61-faf-long-timeout-sampling').exists()
assert read(OUT/'assessment.json')['budget']['unstarted_closed'] == 204
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
audit = read(OUT/'audit.json')
assert len(audit['requirements']) == 89 and len(audit['additional_scope_requirements']) == 240
assert audit['requirements'] == read(OLD/'audit.json')['requirements']
assert not audit['technical_acceptance_received'] and not audit['phase22_complete']
assert not subprocess.check_output(['git', 'diff', '7bf4c6e', '--', 'src', 'tests', 'scripts', 'schemas', '.github', 'uv.lock', 'pyproject.toml', 'CHANGELOG.md','docs/architecture.md'])
subprocess.run(['git', 'diff', '--check'], check=True)
subprocess.run(['git', 'merge-base', '--is-ancestor', '8b6b0ddf1d6f6cf5a8da3ab9421471865b801455', 'HEAD'], check=True)
main = Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=main, text=True).strip() == '4cd57593b2585b9ee05c0f175930e6a0d76d362a'
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=main)
failed={p.stem:read(p)['exit_code'] for p in BASE.glob('v60-*.json') if 'exit_code' in read(p) and read(p)['exit_code']!=0}
assert not failed,failed
provenance={'wrapper_commands':{n:read(BASE/(n+'.json')) for n in checks},
 'direct_commands':[
 {'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OLD/'launch.py')],'exit_code':1,'evidence':'v60-credential-regression/execution.json','console':'No direct stdout; child output retained in sequence.log and raw input log.'}],
 'failure_assessment':'The approved native first input hit its1800-second maximum, producing no report. Its204unstarted observations and all remaining budget closed. Output,source,synthetic identity and missing-approval checks passed. The stale-root synthetic control intentionally failed before timer/target access; it is no corpus attempt. No retry or product change occurred.',
 'paid_calls':0,'retry_observations':0, 'read_only_lookup_note':'One rg lookup referenced nonexistent src/sentinel/static/flow_analysis.py and exited 2 before mutation; corrected source lookup found engine.py. No execution or product effect.', 'unused_helper':'inventory.py was prepared but not executed because no report exists.'}
write('check-failure-assessment.json',{'native_execution_exit_code':1,'failed_wrapper_checks':failed,'explanation':provenance['failure_assessment'],'paid_calls':0,'corpus_retries':0})
write('command-provenance.json', provenance)
write('final-checks.json', {'passed': True, 'recorded_at': datetime.now(timezone.utc).isoformat(),
    'scanner': read(OLD/'freeze.json')['scanner'], 'engineering_files_verified': 302, 'prior_evidence_files_verified': len(read(BASE/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']),
    'requirements': 329, 'protected_user_files': 8, 'owning_docs': 16, 'main_and_parent_preserved': True,
    'checks_sha256': {n: sha(BASE/(n+'.json')) for n in checks}, 'diagnostic_proposal_sha256': sha(OUT/'diagnostic-proposal.json'),
    'corpus_budget': read(OUT/'assessment.json')['budget'], 'diagnostic_executions': 0, 'paid_calls': 0,
    'technical_acceptance_received': False, 'phase22_complete': False})
print('Final checks passed:302engineering files,329 requirements,16docs,closed205budget and unexecuted diagnostic.')
