"""Verify completed evidence, unchanged engineering and stopped work before sealing."""
import ast,collections,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];OLD=BASE/'v92-technical-acceptance';RESULTS=BASE/'v90-regression-results';ENG=BASE/'v88-literal-metadata-correction'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();run=lambda *a:subprocess.check_output(a,cwd=ROOT,text=True)
def save(n,p):
 with (OUT/n).open('x') as f:json.dump(p,f,indent=2);f.write('\n')
checks=['v93-intake','v93-accepted-reconciliation','v93-final-docs','v93-final-generated','v93-final-build','v93-final-distributions']
for n in checks:assert read(BASE/(n+'.json'))['exit_code']==0,n
p=read(OLD/'acceptance-proposal.json');a=read(OUT/'audit.json');old=read(OLD/'audit.json');binding=read(OLD/'documentation-binding.json');delivery=read(OLD/'delivery-verification.json');head=delivery['head']
assert run('git','rev-parse','HEAD').strip()==head=='792d92216c0bb7268b6757c61c5133676a1c7509'
expected=binding['worktrees'].replace('worktree '+str(ROOT)+'\nHEAD '+binding['baseline_delivery'],'worktree '+str(ROOT)+'\nHEAD '+head,1)
assert run('git','worktree','list','--porcelain')==expected
assert a['scanner_identity']==p['scanner'] and a['engineering_passed'] and a['acceptance_packet_ready'] and a['technical_acceptance_received'] and not a['phase22_complete']
rows=a['requirements']+a['additional_scope_requirements'];assert len(a['requirements'])==89 and len(rows)==len(a['current_requirement_interpretations'])==493
for before,after in zip(old['requirements']+old['additional_scope_requirements'],rows):assert before==after or after.get('previous_row')==before
assert not any(r['disposition'].startswith('proposed') for r in rows)
receipt=read(OUT/'technical-acceptance.json');plan=read(OUT/'closeout-plan.json')
assert receipt['approved'] and receipt['technical_acceptance_received'] and not receipt['accepted_closeout_delivery_verified']
assert {r['id'] for r in rows if r['disposition']=='explicitly accepted limitation'}==set(receipt['newly_accepted_limitation_ids']+receipt['already_accepted_proxmox_limitation_ids'])
assert len(receipt['newly_accepted_limitation_ids'])==24 and len(receipt['already_accepted_proxmox_limitation_ids'])==6
assert {r['id'] for r in rows if r['disposition']=='unresolved'}==set(plan['delivery_dependent_requirement_ids']) and len(plan['delivery_dependent_requirement_ids'])==9
assert sha(OUT/'audit.json')==plan['audit_sha256'] and sha(OUT/'technical-acceptance.json')==plan['technical_acceptance_receipt_sha256'] and sha(OLD/'acceptance-proposal.json')==plan['accepted_proposal_sha256']
assert p['new_native_observations_authorized']==p['budget']['new_paid_calls']==plan['new_native_observations_authorized']==0
for n,h in p['review_files_sha256'].items():assert sha(ROOT/n)==h,n
proposal=read(BASE/'v89-regression-preparation/evaluation-proposal.json');local=read(ENG/'local-checks.json')
for n,h in proposal['files_sha256'].items():assert sha(ROOT/n)==h,n
for n,h in local['candidate_engineering_files_sha256'].items():assert sha(ROOT/n)==sha(Path(proposal['frozen_checkout'])/n)==h,n
assert len(local['candidate_engineering_files_sha256'])==305 and local['states']=={'passed':2596,'skipped':36}
hosted=read(BASE/'v88-candidate-quality-audit/packet.json');assert len(hosted['quality'])==12 and all(r['passed']==2596 and r['skipped']==36 for r in hosted['quality'])
for n,h in binding['additional_normative_docs_sha256'].items():assert sha(ROOT/n)==h,n
docs=read(OUT/'owning-docs.json')['sha256'];assert len(docs)==17
for n,h in docs.items():assert sha(ROOT/n)==h,n
for n,h in binding['user_files_sha256'].items():assert sha(ROOT/n)==h,n
assert len(binding['user_files_sha256'])==11 and set(run('git','ls-files','--others','--exclude-standard').splitlines())==set(binding['user_files_sha256'])
assert not run('git','diff','--cached') and not run('git','ls-files','--deleted') and set(run('git','diff','--name-only').splitlines())==set(docs)
assert not run('git','diff','HEAD','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md','docs/architecture.md')
run('git','diff','--check');run('git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD')
main='/Users/bashaarjavaid/Projects/MCP-Sentinel';assert run('git','-C',main,'rev-parse','HEAD').strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a' and not run('git','-C',main,'status','--porcelain')
compat=read(ENG/'compatibility.json');assert compat['six_exact_fingerprints_and_full_requests_unchanged'] and len(compat['runtime_component_files_sha256'])==19
for n,h in compat['runtime_component_files_sha256'].items():assert sha(ROOT/n)==h,n
assert sha(BASE/'v88-production-capture-revalidation/packet.json')==compat['production_replay_sha256']
assert sha(BASE/'v68-invalidation-sampling/optimization-proposal.json')=='fa4ffc3760d4b85b4f8236eec5c7b28d979ece894515bb1495046dd1db108cf6' and not (BASE/'v69-ts-literal-key-reuse').exists()
for folder,total in [('v73-corrected-four-results',24),('v75-prior-language-results',181),('v80-unseen-results',12),('v87-regression-results',111),('v90-regression-results',6)]:
 packet=read(BASE/folder/'raw/packet.json');assert packet['budget_closed'] and packet['remaining_observation_budget']==0 and len(packet['attempts'])==total
 for n,h in packet['files_sha256'].items():assert sha(BASE/folder/'raw'/n)==h,n
r=read(RESULTS/'final-assessment/assessment.json');assert r['completed']==6 and r['entire_ordered_pairs_equal']==3 and r['source_assessment_complete'] and not r['all_narrow_conditions_passed'] and r['whole_ordered_reference_equal']==6
assert r['occurrence_and_condition_counts']=={'findings':0,'warnings':6,'unresolved_flows':0,'surfaces':6,'vulnerable_missed':2,'unsupported_negative':4}
assert read(ENG/'source-assessment.json')['unaffected_observations']==105
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
processes={}
for line in run('ps','-axo','pid=,ppid=,command=').splitlines():
 parts=line.strip().split(None,2)
 if len(parts)==3:processes[int(parts[0])]={'parent':int(parts[1]),'command':parts[2]}
ancestors=set();pid=os.getpid()
while pid in processes and pid not in ancestors:ancestors.add(pid);pid=processes[pid]['parent']
markers=['phase22-check.py','v90-','v91-','v92-','v93-','/launch.py','/evaluate.py','mcp-phase22-four-fresh-','-m pytest']
owned=[{'pid':pid,**row} for pid,row in processes.items() if pid not in ancestors and any(m in row['command'] for m in markers) and ('phase22' in row['command'] or 'MCP-Sentinel' in row['command'])]
managed=run('docker','ps','-aq','--filter','label=com.securemcp.sentinel=true').splitlines();named=run('docker','ps','-aq','--filter','name=sentinel').splitlines();assert not owned and not managed and not named,(owned,managed,named)
save('owned-final.json',{'owned_processes':owned,'managed_container_ids':managed,'sentinel_named_container_ids':named,'recorded_at':datetime.now(timezone.utc).isoformat(),'unrelated_work_terminated':False})
commands={path.stem:read(path) for path in BASE.glob('v93-*.json') if 'exit_code' in read(path)}
for n,c in commands.items():assert sha(BASE/(n+'.patch'))==c['diff_sha256'] and sha(BASE/c['untracked_source_archive'])==c['untracked_source_sha256'] and (BASE/c['log']).is_file(),n
failures={n:c['exit_code'] for n,c in commands.items() if c['exit_code']};assert failures=={},failures
save('check-failure-assessment.json',{'failed_wrapper_checks':{},'prior_assessment_sha256':sha(OLD/'check-failure-assessment.json'),'qualification':'No failed wrapper check during this continuation. All prior failed checks/engineering remain preserved in the exact earlier assessment and command archives. No automatic approval-review rejection occurred.','paid_calls':0})
helpers={str(path.relative_to(ROOT)):sha(path) for folder in [RESULTS,OUT] for path in folder.glob('*.py')}
for n in helpers:ast.parse((ROOT/n).read_text(),filename=n)
save('command-provenance.json',{'wrapper_commands':commands,'logs_sha256':{n:sha(BASE/c['log']) for n,c in commands.items()},'helper_sources_sha256':helpers,'failure_assessment_sha256':sha(OUT/'check-failure-assessment.json'),'paid_calls':0})
save('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':p['scanner'],'requirements':493,'unaccepted_limitations':0,'accepted_limitations':30,'delivery_dependent_rows':9,'engineering_files_verified':305,'runtime_components_verified':19,'six_production_requests_reused_without_calls':True,'protected_user_files':11,'owning_docs':17,'main_worktrees_parent_preserved':True,'checks_sha256':{n:sha(BASE/(n+'.json')) for n in checks},'current_source_observations':6,'ordered_pairs_equal':3,'current_proxmox_gate_passed':False,'current_proxmox_limitation_accepted':True,'budget_closed':True,'remaining':0,'new_native_observations_proposed':0,'ordinary_faf1800_completion_established':False,'paid_calls':0,'technical_acceptance_received':True,'phase22_complete':False})
print('493-row accepted audit verified;30acceptedlimitations,2deferrals,9delivery-dependent rows; actual accepted-closeout delivery remains.')
