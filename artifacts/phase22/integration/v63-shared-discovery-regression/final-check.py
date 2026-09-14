"""Verify stopped execution, unapproved diagnostic and unchanged engineering before sealing."""
import ast,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path.cwd();out=Path(__file__).resolve().parent;base=out.parent;assets=base/'v62-shared-tool-discovery';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
 with (out/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
checks=['authorization','validation','owned-work','parent-sampler-selfcheck','sampler-selfcheck','assessment-preparation','proposal-clarification','diagnostic-boundary','compatible-reuse','reconciliation','review-summary','final-docs','final-artifacts','final-build','final-distributions','owned-final']
for n in checks:assert read(base/('v63-'+n+'.json'))['exit_code']==0,n
proposal=read(out/'diagnostic-proposal.json');a=read(out/'assessment.json');v=read(out/'validation.json');local=read(assets/'local-checks.json')
for n,d in local['candidate_engineering_files_sha256'].items():assert sha(root/n)==sha(Path(proposal['frozen_checkout'])/n)==d,n
binding=read(assets/'documentation-binding.json')
for key in ['user_files_sha256','additional_normative_docs_sha256']:
 for n,d in binding[key].items():assert sha(root/n)==d,n
for n,d in read(out/'owning-docs.json')['sha256'].items():assert sha(root/n)==d,n
prior=read(base/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']
for n,d in prior.items():assert sha(root/n)==d,n
for n,d in proposal['files_sha256'].items():assert sha(root/n)==d,n
assert proposal['bounds']['total_input_executions']==1 and proposal['bounds']['whole_input_maximum_seconds']==1800 and proposal['bounds']['cleanup_maximum_seconds']==15
assert proposal['bounds']['maximum_sampled_processes']==5 and proposal['bounds']['optimization_attempts']==proposal['bounds']['retries']==proposal['bounds']['paid_calls']==0
assert not (out/'diagnostic-authorization.json').exists() and not (out/'diagnostic-consumed.json').exists() and not (base/'v64-shared-discovery-sampling').exists()
assert a['report_count']==0 and a['budget']=={'planned':205,'attempted':1,'completed':0,'incomplete':1,'unstarted_closed':204,'remaining':0,'closed':True}
for n,d in read(out/'raw/packet.json')['files_sha256'].items():assert sha(out/'raw'/n)==d,n
assert v['validation_passed'] and v['budget_closed'] and not v['execution_gate_passed']
audit=read(out/'audit.json');old=read(assets/'audit.json');assert audit['requirements']==old['requirements'] and len(audit['additional_scope_requirements'])==263
for p,c in zip(old['additional_scope_requirements'],audit['additional_scope_requirements']):assert p==c or c.get('previous_row')==p
assert len(audit['current_requirement_interpretations'])==345
assert next(r for r in audit['additional_scope_requirements'] if r['id']=='V49-DIAGNOSTIC-PREPARATION')['disposition']=='unresolved'
assert not audit['technical_acceptance_received'] and not audit['phase22_complete']
assert read(out/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
assert not subprocess.check_output(['git','diff','1948bf9','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md','docs/architecture.md'])
subprocess.run(['git','diff','--check'],check=True);subprocess.run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'],check=True)
main=Path('/Users/bashaarjavaid/Projects/MCP-Sentinel');assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a';assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
commands={n:read(base/('v63-'+n+'.json')) for n in checks}
for n,r in commands.items():
 assert sha(base/('v63-'+n+'.patch'))==r['diff_sha256'];assert sha(base/('v63-'+n+'.untracked.tar.gz'))==r['untracked_source_sha256']
failed={p.stem:read(p)['exit_code'] for p in base.glob('v63-*.json') if 'exit_code' in read(p) and read(p)['exit_code']!=0};assert not failed,failed
write('check-failure-assessment.json',{'native_outcome':'One approved1800-second native timeout,no report,204unstarted closed. The launcher exit1 and evaluator completion assertion are retained in execution.json and sequence.log. No retry or profile ran.','failed_wrapper_checks':failed,'read_only_lookup_notes':'A guessed authorize-evaluation.py lookup failed; rg found authorize-regression.py. No product/execution effect.','preparation_clarifications':'Initial diagnostic prose was clarified to distinguish read-only launcher preflight,attempted-input1800-second timer and separate15-second cleanup; initial proposal retained. Initial generated status spacing was cleaned with the initial block retained. No timing,runner,source or result change.','paid_calls':0})
for helper in out.glob('*.py'):ast.parse(helper.read_text(),filename=str(helper))
write('command-provenance.json',{'wrapper_commands':commands,'direct_commands':[{'command':read(out/'launch.json')['command'],'outer_launcher_command':read(assets/'launcher-binding.json')['command'],'exit_code':read(out/'execution.json')['timing']['returncode'],'receipt':'execution.json'}],'helper_sources_sha256':{str(p.relative_to(root)):sha(p) for p in [*out.glob('*.py'),assets/'authorize-regression.py']},'failure_assessment_sha256':sha(out/'check-failure-assessment.json'),'paid_calls':0})
write('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':proposal['scanner'],'engineering_files_verified':302,'prior_evidence_files_verified':len(prior),'requirements':352,'protected_user_files':9,'owning_docs':16,'main_and_parent_preserved':True,'checks_sha256':{n:sha(base/('v63-'+n+'.json')) for n in checks},'diagnostic_proposal_sha256':sha(out/'diagnostic-proposal.json'),'native_attempts':1,'native_reports':0,'unstarted_closed':204,'budget_closed':True,'profiles':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Final352-row/source/package/budget checks pass; single parent-and-worker diagnostic remains unapproved.')
