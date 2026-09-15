"""Verify the complete review, preserved scopes and stopped owned work before sealing."""
import ast,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];ENG=BASE/'v88-literal-metadata-correction';OLD=BASE/'v86-regression-preparation';RESULTS=BASE/'v87-regression-results'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=lambda *args:subprocess.check_output(args,cwd=ROOT,text=True)
def save(name,p):
 with (OUT/name).open('x') as f:json.dump(p,f,indent=2);f.write('\n')
checks=['v87-complete-validation','v87-complete-reference-inventory','v87-complete-source-assessment','v87-complete-assessment','v87-completion-ownership','v88-local-checks','v88-hosted-audit','v88-freeze','v89-proposal-preparation','v89-review-reconciliation','v89-final-docs','v89-final-generated','v89-final-build','v89-final-distributions']
for n in checks:assert read(BASE/(n+'.json'))['exit_code']==0,n
p=read(OUT/'evaluation-proposal.json');a=read(OUT/'audit.json');old=read(OLD/'audit.json');local=read(ENG/'local-checks.json');freeze=read(ENG/'freeze.json');head=p['scanner']['revision']
assert run('git','rev-parse','HEAD').strip()==head==local['candidate']=='5142a3fbd5bcff63719df6cce3a30543214e7d27'
assert run('git','worktree','list','--porcelain')==freeze['worktrees_after']
assert a['scanner_identity']==p['scanner'] and a['engineering_passed'] and not a['acceptance_packet_ready'] and not a['technical_acceptance_received'] and not a['phase22_complete']
assert len(a['requirements'])==89 and len(a['additional_scope_requirements'])==390 and len(a['current_requirement_interpretations'])==479
for before,after in zip(old['requirements']+old['additional_scope_requirements'],a['requirements']+a['additional_scope_requirements']):assert before==after or after.get('previous_row')==before
assert sum(r['disposition']=='proposed documented limitation awaiting decision' for r in a['requirements']+a['additional_scope_requirements'])==28
assert not (OUT/'evaluation-authorization.json').exists() and not (OUT/'execution-consumed.json').exists() and not (OUT/'source-freeze-authorization.json').exists() and not (BASE/'v90-regression-results').exists()
assert len(p['order'])==6 and len({(r['group'],r['input_id']) for r in p['order']})==3 and sum(r['batch']=='repeat' for r in p['order'])==3
assert p['bounds']['sequence_maximum_minutes']==200 and p['bounds']['internal_stop_minutes']==199
for n,h in p['files_sha256'].items():assert sha(ROOT/n)==h,n
for n,h in local['candidate_engineering_files_sha256'].items():assert sha(ROOT/n)==sha(Path(p['frozen_checkout'])/n)==h,n
assert len(local['candidate_engineering_files_sha256'])==305 and local['states']=={'passed':2596,'skipped':36}
assert len(read(BASE/'v88-candidate-quality-audit/packet.json')['quality'])==12
for n,h in read(OLD/'documentation-binding.json')['additional_normative_docs_sha256'].items():assert sha(ROOT/n)==h,n
docs=read(OUT/'owning-docs.json')['sha256'];assert len(docs)==17
for n,h in docs.items():assert sha(ROOT/n)==h,n
protected=read(ENG/'intake.json')['protected_user_files_sha256'];assert len(protected)==11
for n,h in protected.items():assert sha(ROOT/n)==h,n
assert set(run('git','ls-files','--others','--exclude-standard').splitlines())==set(protected)
assert not run('git','diff','--cached') and not run('git','ls-files','--deleted')
assert set(run('git','diff','--name-only').splitlines())==set(docs)
assert not run('git','diff','HEAD','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md','docs/architecture.md')
run('git','diff','--check');run('git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD')
main='/Users/bashaarjavaid/Projects/MCP-Sentinel';assert run('git','-C',main,'rev-parse','HEAD').strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a' and not run('git','-C',main,'status','--porcelain')
compat=read(ENG/'compatibility.json');assert compat['six_exact_fingerprints_and_full_requests_unchanged'] and len(compat['runtime_component_files_sha256'])==19
for n,h in compat['runtime_component_files_sha256'].items():assert sha(ROOT/n)==h,n
assert sha(BASE/'v88-production-capture-revalidation/packet.json')==compat['production_replay_sha256']
assert sha(BASE/'v68-invalidation-sampling/optimization-proposal.json')=='fa4ffc3760d4b85b4f8236eec5c7b28d979ece894515bb1495046dd1db108cf6' and not (BASE/'v69-ts-literal-key-reuse').exists()
for folder,total in [('v73-corrected-four-results',24),('v75-prior-language-results',181),('v80-unseen-results',12),('v87-regression-results',111)]:
 packet=read(BASE/folder/'raw/packet.json');assert packet['budget_closed'] and packet['remaining_observation_budget']==0 and len(packet['attempts'])==total
 for n,h in packet['files_sha256'].items():assert sha(BASE/folder/'raw'/n)==h,n
assessment=read(RESULTS/'final-assessment/assessment.json')
assert assessment['completed']==111 and assessment['entire_ordered_pairs_equal']==48 and assessment['source_assessment_complete'] and not assessment['all_narrow_conditions_passed']
assert assessment['whole_ordered_reference_equal']==101 and assessment['reports_with_source_assessed_deltas']==10 and assessment['changed_occurrences']==268
assert read(ENG/'source-assessment.json')['unaffected_observations']==105
assert not read(BASE/'v80-unseen-results/final-assessment/assessment.json')['fresh_detection_gate_passed']
assert not read(BASE/'v82-python-module-dispatch/receiver-mutation-controls.json')['all_passed'] and not read(BASE/'v83-global-instance-boundary/class-call-control.json')['passed']
assert read(BASE/'v82-full-suite.json')['exit_code']==2 and read(BASE/'v82-candidate-quality/packet.json')['runs']['ci']['conclusion']=='cancelled'
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
processes={}
for line in run('ps','-axo','pid=,ppid=,command=').splitlines():
 parts=line.strip().split(None,2)
 if len(parts)==3:processes[int(parts[0])]={'parent':int(parts[1]),'command':parts[2]}
ancestors=set();pid=os.getpid()
while pid in processes and pid not in ancestors:ancestors.add(pid);pid=processes[pid]['parent']
markers=['phase22-check.py','v87-','v88-','v89-','/launch.py','/evaluate.py','mcp-phase22-four-fresh-','-m pytest']
owned=[{'pid':pid,**row} for pid,row in processes.items() if pid not in ancestors and any(m in row['command'] for m in markers) and ('phase22' in row['command'] or 'MCP-Sentinel' in row['command'])]
managed=run('docker','ps','-aq','--filter','label=com.securemcp.sentinel=true').splitlines();named=run('docker','ps','-aq','--filter','name=sentinel').splitlines();assert not owned and not managed and not named,(owned,managed,named)
save('owned-final.json',{'owned_processes':owned,'managed_container_ids':managed,'sentinel_named_container_ids':named,'recorded_at':datetime.now(timezone.utc).isoformat(),'unrelated_work_terminated':False})
commands={path.stem:read(path) for path in BASE.glob('v8[789]-*.json') if 'exit_code' in read(path)}
for n,c in commands.items():assert sha(BASE/(n+'.patch'))==c['diff_sha256'] and sha(BASE/c['untracked_source_archive'])==c['untracked_source_sha256'] and (BASE/c['log']).is_file(),n
failures={n:c['exit_code'] for n,c in commands.items() if c['exit_code']}
reasons={
 'v87-authorization-preflight':'Initial source-only authorizer required ignored frozen metadata to be untracked; it failed before authorization/output/token/input. Corrected exact hash/classification preflight passed; one native launch only.',
 'v87-meta-delta-assessment':'Strict full-finding assertion caught omitted evidence mirrors in provenance. Initial helper retained; final helper proves root/provenance equality and applies exact changes to both. No additional observations.',
 'v87-meta-delta-assessment-corrected':'Strict source-role table omitted api314/317in the vulnerable operator variant. Added the actual source roles and passed full268occurrence/3410context assessment. Original helper retained.',
 'v88-initial-metadata-controls':'One failed/141passed synthetic controls: direct del dict was missed by normal bindings. Added explicit rejection; final146module and513focused controls pass.',
 'v88-mypy':'Two mutable-set variance typing errors; explicit set[ast.AST] annotation corrected strict typing without changing runtime logic.',
}
assert set(failures)==set(reasons),('Unassessed check failure',failures)
save('check-failure-assessment.json',{'failed_wrapper_checks':{n:{'exit_code':code,'assessment':reasons[n]} for n,code in failures.items()},'prior_assessment_sha256':sha(OLD/'check-failure-assessment.json'),'qualification':'Every actual failed check retains commands, logs, patches and helper/source archives. Corrections do not erase failures. Exploratory read-only missing paths and truncated prints consumed no native budget; focused subsequent reads completed assessment. No automatic approval-review rejection occurred.','paid_calls':0})
helpers={str(path.relative_to(ROOT)):sha(path) for folder in [RESULTS,ENG,OUT] for path in folder.glob('*.py')}
for n in helpers:ast.parse((ROOT/n).read_text(),filename=n)
save('command-provenance.json',{'wrapper_commands':commands,'logs_sha256':{n:sha(BASE/c['log']) for n,c in commands.items()},'helper_sources_sha256':helpers,'failure_assessment_sha256':sha(OUT/'check-failure-assessment.json'),'paid_calls':0})
save('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':p['scanner'],'requirements':479,'unaccepted_limitations':28,'engineering_files_verified':305,'runtime_components_verified':19,'six_production_requests_reused_without_calls':True,'protected_user_files':11,'owning_docs':17,'main_worktrees_parent_preserved':True,'checks_sha256':{n:sha(BASE/(n+'.json')) for n in checks},'previous_completed_observations':111,'previous_equal_pairs':48,'retained_unaffected_observations':105,'current_source_observations':0,'proposed_observations':6,'proposed_inputs':3,'proposed_pairs':3,'ordinary_faf1800_completion_established':False,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Complete479-row correction/proposal checks pass; all111previous observations assessed and closed. New6-observation approval and later technical acceptance remain.')
