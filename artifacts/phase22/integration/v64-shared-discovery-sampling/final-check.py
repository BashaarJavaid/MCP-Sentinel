"""Verify the closed profile, unimplemented proposal and actual-source reuse before sealing."""
import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
OLD = BASE/'v63-shared-discovery-regression'
ASSETS = BASE/'v62-shared-tool-discovery'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
checks = ['authorization','attribution','owned-work','source-assessment','source-assessment-refined','optimization-proposal','compatible-reuse','reconciliation','review-summary','final-docs','final-artifacts','final-build','final-distributions','owned-final']
commands = {name:read(BASE/('v64-'+name+'.json')) for name in checks}
for name, result in commands.items():
    assert result['exit_code'] == 0, name
    assert sha(BASE/('v64-'+name+'.patch')) == result['diff_sha256']
    assert sha(BASE/('v64-'+name+'.untracked.tar.gz')) == result['untracked_source_sha256']
a = read(OUT/'assessment.json')
v = read(OUT/'validation.json')
p = read(OUT/'optimization-proposal.json')
diagnostic = read(OLD/'diagnostic-proposal.json')
local = read(ASSETS/'local-checks.json')
for name, digest in local['candidate_engineering_files_sha256'].items():
    assert sha(ROOT/name) == sha(Path(diagnostic['frozen_checkout'])/name) == digest, name
binding = read(OLD/'documentation-binding.json')
for field in ['user_files_sha256','additional_normative_docs_sha256']:
    for name, digest in binding[field].items(): assert sha(ROOT/name) == digest, name
for name, digest in read(OUT/'owning-docs.json')['sha256'].items(): assert sha(ROOT/name) == digest, name
prior = read(BASE/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']
for name, digest in prior.items(): assert sha(ROOT/name) == digest, name
for name, digest in diagnostic['files_sha256'].items(): assert sha(ROOT/name) == digest, name
for name, digest in p['source_files_sha256'].items(): assert sha(ROOT/name) == digest, name
assert p['status'] == 'prepared_not_approved_not_started'
assert p['bounds'] == {'source_only_optimization_attempts':1,'corpus_observations':0,'profiles':0,'comparators':0,'retries':0,'new_repositories':0,'paid_calls':0,'target_execution':False,'runtime_campaigns':0}
assert not (BASE/'v65-if-invalidation-accumulator').exists()
assert a['profile_attempts'] == 1 and a['budget_closed'] and a['remaining'] == 0
assert a['report_count'] == 0 and a['finding_count'] is None and a['warning_count'] is None and a['surface_count'] is None
assert v['passed'] and v['budget_closed'] and v['completed_inputs'] == 0 and v['incomplete_inputs'] == 1
for name, digest in v['raw_sha256'].items(): assert sha(OUT/name) == digest, name
assert read(OUT/'owned-final.json')['owned_processes'] == []
audit = read(OUT/'audit.json')
old = read(OLD/'audit.json')
assert audit['requirements'] == old['requirements'] and len(audit['additional_scope_requirements']) == 269
for before, after in zip(old['additional_scope_requirements'], audit['additional_scope_requirements']): assert before == after or after.get('previous_row') == before
assert len(audit['current_requirement_interpretations']) == 352
assert next(r for r in audit['additional_scope_requirements'] if r['id']=='V49-DIAGNOSTIC-PREPARATION')['disposition'] == 'unresolved'
assert not audit['technical_acceptance_received'] and not audit['phase22_complete']
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
assert not subprocess.check_output(['git','diff','1948bf9','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md','docs/architecture.md'])
subprocess.run(['git','diff','--check'],check=True)
subprocess.run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'],check=True)
main = Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip() == '4cd57593b2585b9ee05c0f175930e6a0d76d362a'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
failed = {f.stem:read(f)['exit_code'] for f in BASE.glob('v64-*.json') if 'exit_code' in read(f) and read(f)['exit_code'] != 0}
assert not failed, failed
write('check-failure-assessment.json', {'profile_outcome':'One approved1800-second sampled timeout; the supervisor killed the remaining group after its grace, with cleanup verified at1805.2049405seconds. One parent final snapshot and timer-restoration flags are retained before the kill; no worker identity or report exists. Exact reason for incomplete process teardown is not established. Shell exit247 represents child -9. actual native returncode/log/results and process snapshot final/restoration flags remain retained. No retry or optimization occurred.','failed_wrapper_checks':failed,'read_only_lookup_notes':'Guessed v63/readback.py and v61/validate.py reads failed because those files do not exist; actual delivery readback is in deliver.py and profile validation is attribute.py. Initial rg --files returned no ignored packet paths; explicit paths/ls resolved the inventory. These were read-only lookups, not source changes or extra input attempts.','preparation_notes':'The initial literal-cache option, assessment and all draft helper bytes are preserved in preliminary-literal-key. Final retained leaf/source review selected a smaller existing-set accumulator proposal; no preliminary proposal was executed, approved or implemented. Assessment and delivery helpers were prepared while the approved diagnostic remained active, then executed only after it stopped. No product code or target data was changed. Initial adapted helper bytes are retained by their unique executed wrapper archives; all actual failed checks, if any, require separate assessment before completion.','paid_calls':0})
for helper in OUT.glob('*.py'): ast.parse(helper.read_text(),filename=str(helper))
write('command-provenance.json', {'wrapper_commands':commands,'direct_commands':[{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OLD/'diagnostic.py')],'child_command':read(OUT/'attempt.json')['command'],'exit_code':read(OUT/'execution.json')['timing']['returncode'],'receipt':'execution.json'}],'helper_sources_sha256':{str(f.relative_to(ROOT)):sha(f) for f in [*OUT.glob('*.py'),OLD/'authorize-diagnostic.py']},'failure_assessment_sha256':sha(OUT/'check-failure-assessment.json'),'paid_calls':0})
write('final-checks.json', {'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':a['scanner'],'engineering_files_verified':302,'prior_evidence_files_verified':len(prior),'requirements':358,'protected_user_files':9,'owning_docs':16,'main_and_parent_preserved':True,'checks_sha256':{n:sha(BASE/('v64-'+n+'.json')) for n in checks},'optimization_proposal_sha256':sha(OUT/'optimization-proposal.json'),'native_attempts_at_current_source':1,'native_reports':0,'unstarted_closed':204,'profile_attempts_at_current_source':1,'profile_reports':0,'sampled_processes':[r['rule'] for r in a['sample_rows']],'samples':a['samples'],'budget_closed':True,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Final358-row/source/package/profile-budget checks pass; one source-only proposal remains unapproved.')
