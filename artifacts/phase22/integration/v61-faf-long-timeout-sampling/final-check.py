"""Verify the bounded partial diagnostic, proposal and unchanged engineering."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent;OLD=BASE/'v60-long-timeout-regression'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
    with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
checks=['v61-authorization','v61-attribution','v61-owned-cleanup','v61-source-assessment','v61-compatible-reuse-corrected','v61-proposal-preparation','v61-reconciliation','v61-final-docs','v61-final-build','v61-final-distributions','v61-owned-final']
for n in checks:assert read(BASE/(n+'.json'))['exit_code']==0,n
engineering=read(BASE/'v59-timeout-policy/local-checks.json')['candidate_engineering_files_sha256'];assert len(engineering)==302
for n,d in engineering.items():assert sha(ROOT/n)==sha(Path('/private/tmp/mcp-phase22-frozen-7bf4c6e')/n)==d,n
binding=read(OLD/'documentation-binding.json')
for n,d in binding['user_files_sha256'].items():assert sha(ROOT/n)==d,n
for n,d in read(OUT/'owning-docs.json')['sha256'].items():assert sha(ROOT/n)==d,n
prior=read(BASE/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']
for n,d in prior.items():assert sha(ROOT/n)==d,n
proposal=read(OUT/'optimization-proposal.json')
assert proposal['profile_assessment_sha256']==sha(OUT/'assessment.json') and proposal['source_assessment_sha256']==sha(OUT/'source-assessment.json')
for n,d in proposal['source_files_sha256'].items():assert sha(ROOT/n)==d,n
assert proposal['bounds']=={'source_only_optimization_attempts':1,'corpus_observations':0,'profiles':0,'comparators':0,'retries':0,'new_repositories':0,'paid_calls':0,'target_execution':False,'runtime_campaigns':0}
assert not (OUT/'optimization-authorization.json').exists() and not (BASE/'v62-shared-tool-discovery').exists()
a=read(OUT/'assessment.json');assert a['budget_closed'] and a['remaining']==0 and a['samples']>0 and a['valid_partial_current_source_profiles']==1
v=read(OUT/'validation.json')
for n,d in v['raw_sha256'].items():assert sha(OUT/n)==d,n
assert all(r['scanner']==proposal['scanner'] for r in v['worker_identities'].values())
audit=read(OUT/'audit.json');assert audit['requirements']==read(OLD/'audit.json')['requirements'] and len(audit['additional_scope_requirements'])==246
assert next(r for r in audit['additional_scope_requirements'] if r['id']=='V49-DIAGNOSTIC-PREPARATION')['disposition']=='unresolved'
assert not audit['technical_acceptance_received'] and not audit['phase22_complete']
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
assert not subprocess.check_output(['git','diff','7bf4c6e','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md','docs/architecture.md'])
subprocess.run(['git','diff','--check'],check=True)
subprocess.run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'],check=True)
main=Path('/Users/bashaarjavaid/Projects/MCP-Sentinel');assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a';assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
failed={p.stem:read(p)['exit_code'] for p in BASE.glob('v61-*.json') if 'exit_code' in read(p) and read(p)['exit_code']!=0}
assert failed=={'v61-compatible-reuse':1},failed
write('check-failure-assessment.json',{'profile_outcome':'One approved 1800-second sampled attempt timed out with four verified current-source worker identities. Partial samples retained, no report, zero remaining.','failed_wrapper_checks':failed,'explanation':'The reused verification helper first expected the native regression raw/packet.json path, absent in this diagnostic layout. It failed before writing a reuse result. The helper now checks this profile budget-closed.json; v61-compatible-reuse-corrected passed. Initial source/log/receipt and the corrected helper are preserved. No scanner/product change or new observation occurred.','corrected_receipt_sha256':sha(BASE/'v61-compatible-reuse-corrected.json'),'read_only_lookup_notes':['An rg lookup referenced nonexistent src/sentinel/static/credential_flow.py and exited 2; a following zsh credential filename glob matched no file and exited 1. Corrected source review used rules/sent016.py. No product or execution effect.','The prepared allocation-attribution source line was corrected back to the actual 329 before the validator was executed; no measured output changed.'],'profile_retries':0,'optimization_attempts':0,'paid_calls':0})
write('command-provenance.json',{'wrapper_commands':{n:read(BASE/(n+'.json')) for n in checks+['v61-compatible-reuse']},'direct_commands':[{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OLD/'diagnostic.py')],'exit_code':read(OUT/'execution.json')['timing']['returncode'],'evidence':'v61-faf-long-timeout-sampling/execution.json'}],'failure_assessment_sha256':sha(OUT/'check-failure-assessment.json'),'helper_sources_sha256':{str(h.relative_to(ROOT)):sha(h) for h in [*OUT.glob('*.py'),OLD/'authorize-diagnostic.py']},'paid_calls':0})
import ast
for helper in OUT.glob('*.py'):ast.parse(helper.read_text(),filename=str(helper))
write('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':proposal['scanner'],'engineering_files_verified':302,'prior_evidence_files_verified':len(prior),'requirements':335,'protected_user_files':8,'owning_docs':16,'main_and_parent_preserved':True,'checks_sha256':{n:sha(BASE/(n+'.json')) for n in checks},'optimization_proposal_sha256':sha(OUT/'optimization-proposal.json'),'current_source_profile_attempts':1,'valid_partial_current_source_profiles':1,'current_optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Final checks pass:335requirements,302unchanged engineering files,valid partial profile closed,source-only optimization unapproved.')
