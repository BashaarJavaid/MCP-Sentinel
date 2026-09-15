"""Verify complete source-bound review evidence and affected documentation/package checks."""
import ast,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];PRIOR=BASE/'v72-prototype-property-correction'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=lambda *args:subprocess.check_output(args,cwd=ROOT,text=True)
def write(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
checks=['v80-authorization-preflight','v80-unseen-execution','v80-complete-validation','v80-source-inventory','v80-complete-source-assessment','v80-completion-verification','v81-review-reconciliation','v81-final-docs','v81-final-generated','v81-final-build','v81-final-distributions']
for name in checks:assert read(BASE/(name+'.json'))['exit_code']==0,name
p=read(BASE/'v79-unseen-metadata-correction/evaluation-proposal.json');a=read(OUT/'audit.json');old=read(BASE/'v79-unseen-metadata-correction/audit.json');intake=read(BASE/'v77-unseen-preparation/scope-and-precuration-freeze.json');delivery=read(BASE/'v79-unseen-metadata-correction/delivery-verification.json');binding=read(BASE/'v79-unseen-metadata-correction/documentation-binding.json');intake['head']=delivery['head'];intake['worktrees']=binding['worktrees'].replace('worktree '+str(ROOT)+'\nHEAD '+binding['baseline_delivery'],'worktree '+str(ROOT)+'\nHEAD '+delivery['head'],1);intake['protected_user_files_sha256']=intake['protected_files_sha256'];local=read(PRIOR/'local-checks.json')
assert p['scanner']==a['scanner_identity'] and p['scanner']['revision']==local['candidate']=='cec0322e904bbf63c33cd95796e7289101a93e5d'
assert a['current_four_repository_gate_passed'] and a['current_earlier_language_compatibility_established'] and a['budget_closed'] and a['remaining']==0 and not a['technical_acceptance_received'] and not a['phase22_complete']
assert len(a['requirements'])==89 and len(a['additional_scope_requirements'])==359 and len(a['current_requirement_interpretations'])==448
for prior,current in zip(old['requirements']+old['additional_scope_requirements'],a['requirements']+a['additional_scope_requirements']):assert prior==current or current.get('previous_row')==prior
for identity in ['R66','R88','V14-RETENTION','V21-SEQUENCE','V21-FRESH-PROPOSAL','V25-EXPOSED-REGRESSION','V27-REGRESSION','V39-EVALUATION','V44-FOUR-GATE','V49-DIAGNOSTIC-PREPARATION','V55-EQUIVALENCE','V56-EQUIVALENCE','V65-EQUIVALENCE','V68-OPT-DECISION','V70-FOUR-GATE','V76-FAF-DEADLINE']:
 assert next(x for x in a['requirements']+a['additional_scope_requirements'] if x['id']==identity)['disposition']=='proposed documented limitation awaiting decision'
for n in [46,49,53,58,60,63,67]:assert next(x for x in a['additional_scope_requirements'] if x['id']==f'V{n}-REGRESSION-GATE')['disposition']=='proposed documented limitation awaiting decision'
for name,digest in local['candidate_engineering_files_sha256'].items():assert sha(ROOT/name)==sha(Path(p['frozen_checkout'])/name)==digest,name
assert len(local['candidate_engineering_files_sha256'])==303
for name,digest in read(PRIOR/'documentation-binding.json')['additional_normative_docs_sha256'].items():assert sha(ROOT/name)==digest,name
for name,digest in read(OUT/'owning-docs.json')['sha256'].items():assert sha(ROOT/name)==digest,name
for name,digest in intake['protected_user_files_sha256'].items():assert sha(ROOT/name)==digest,name
assert len(intake['protected_user_files_sha256'])==11
assert set(run('git','ls-files','--others','--exclude-standard').splitlines())==set(intake['protected_user_files_sha256'])
assert run('git','rev-parse','HEAD').strip()==intake['head'] and run('git','worktree','list','--porcelain')==intake['worktrees']
assert not run('git','diff','cec0322','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md','docs/architecture.md')
assert not run('git','diff','--cached') and not run('git','ls-files','--deleted')
assert set(run('git','diff','--name-only').splitlines())==set(read(OUT/'owning-docs.json')['sha256'])
run('git','diff','--check');run('git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD')
main='/Users/bashaarjavaid/Projects/MCP-Sentinel';assert run('git','-C',main,'rev-parse','HEAD').strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a';assert not run('git','-C',main,'status','--porcelain')
compat=read(PRIOR/'compatibility.json');assert compat['six_exact_fingerprints_and_full_requests_unchanged'] and len(compat['runtime_component_files_sha256'])==19
for name,digest in compat['runtime_component_files_sha256'].items():assert sha(ROOT/name)==digest,name
assert sha(BASE/'v72-production-capture-revalidation/packet.json')==compat['production_replay_sha256']
pending=BASE/'v68-invalidation-sampling/optimization-proposal.json';assert sha(pending)=='fa4ffc3760d4b85b4f8236eec5c7b28d979ece894515bb1495046dd1db108cf6' and read(pending)['status']=='prepared_not_approved_not_started'
assert not (BASE/'v69-ts-literal-key-reuse').exists()
for folder,expected in [('v73-corrected-four-results',24),('v75-prior-language-results',181),('v80-unseen-results',12)]:
 packet=read(BASE/folder/'raw/packet.json');assert packet['budget_closed'] and len(packet['attempts'])==expected
 for name,digest in packet['files_sha256'].items():assert sha(BASE/folder/'raw'/name)==digest,name
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
fresh=read(BASE/'v80-unseen-results/final-assessment/assessment.json')
assert fresh['source_assessment_complete'] and fresh['execution_gate_passed'] and not fresh['fresh_detection_gate_passed'] and fresh['repository_gates_passed']==1
assert fresh['budget']['closed'] and fresh['budget']['remaining']==0 and fresh['budget']['completed']==12
for name,digest in fresh['assessment_files_sha256'].items():assert sha(BASE/'v80-unseen-results/final-assessment'/name)==digest,name
assert a['acceptance_packet_ready'] and a['new_unseen_scope']['all_gates_passed'] is False and a['new_unseen_scope']['completed']==12
assert len([r for r in a['requirements']+a['additional_scope_requirements'] if r['disposition']=='proposed documented limitation awaiting decision'])==26
for name,digest in p['files_sha256'].items():assert sha(ROOT/name)==digest,name
assert read(BASE/'v78-unseen-results/stop-assessment.json')['budget_closed']
processes={}
for line in run('ps','-axo','pid=,ppid=,command=').splitlines():
 parts=line.strip().split(None,2)
 if len(parts)==3:processes[int(parts[0])]={'parent':int(parts[1]),'command':parts[2]}
ancestors=set();pid=os.getpid()
while pid in processes and pid not in ancestors:ancestors.add(pid);pid=processes[pid]['parent']
markers=['phase22-check.py','v73-','v74-','v75-','v76-','v80-','v81-','/launch.py','/evaluate.py','mcp-phase22-four-fresh-']
owned=[{'pid':pid,**row} for pid,row in processes.items() if pid not in ancestors and any(m in row['command'] for m in markers) and ('phase22' in row['command'] or any(m in row['command'] for m in ['v80-','v81-']))]
managed=run('docker','ps','-aq','--filter','label=com.securemcp.sentinel=true').splitlines();named=run('docker','ps','-aq','--filter','name=sentinel').splitlines();assert not owned and not managed and not named
write('owned-final.json',{'owned_processes':owned,'managed_container_ids':managed,'sentinel_named_container_ids':named,'recorded_at':datetime.now(timezone.utc).isoformat(),'unrelated_work_terminated':False})
commands={path.stem:read(path) for prefix in ['v80-','v81-'] for path in BASE.glob(prefix+'*.json') if 'exit_code' in read(path)}
for name,c in commands.items():
 assert sha(BASE/(name+'.patch'))==c['diff_sha256'] and sha(BASE/c['untracked_source_archive'])==c['untracked_source_sha256'],name
 assert (BASE/c['log']).is_file(),name
failed={name:c['exit_code'] for name,c in commands.items() if c['exit_code']}
assert failed=={},('New failure requires assessment',failed)
write('check-failure-assessment.json',{'failed_wrapper_checks':{},'retained_prior_failure_assessment':{'path':'artifacts/phase22/integration/v79-unseen-metadata-correction/check-failure-assessment.json','sha256':sha(BASE/'v79-unseen-metadata-correction/check-failure-assessment.json')},'qualification':'V80 and V81 checks pass. The initial V78 metadata failure and preflight staged-file correction remain failed/source-bound with closed budget. Original fresh/native/profile/equivalence failures remain explicit; no retrospective pass. Read-only exploratory guessed filenames were corrected without scanner invocation.','paid_calls':0})
helpers={str(path.relative_to(ROOT)):sha(path) for folder in [BASE/'v73-corrected-four-results',BASE/'v74-prior-language-preparation',BASE/'v75-prior-language-results',BASE/'v80-unseen-results',OUT] for path in folder.glob('*.py')}
for name in helpers:ast.parse((ROOT/name).read_text(),filename=name)
write('command-provenance.json',{'wrapper_commands':commands,'logs_sha256':{name:sha(BASE/c['log']) for name,c in commands.items()},'helper_sources_sha256':helpers,'failure_assessment_sha256':sha(OUT/'check-failure-assessment.json'),'qualification':'Exact commands, logs, patches, wrapper helper archives and initial/corrected sources retained. Sole approvedV73/V75executions; read-only assessment/preparation helpers are not new observations.','paid_calls':0})
write('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':p['scanner'],'requirements':448,'engineering_files_verified':303,'runtime_components_verified':19,'six_production_requests_reused_without_calls':True,'protected_user_files':11,'owning_docs':16,'main_worktrees_parent_preserved':True,'checks_sha256':{name:sha(BASE/(name+'.json')) for name in checks},'current_source_observations':205,'new_unseen_completed':12,'new_ordered_pairs':6,'new_repository_gates_passed':1,'new_repository_gates_failed':1,'whole_ordered_pairs_equal':95,'budget_closed':True,'remaining':0,'ordinary_faf1800_completion_established':False,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Complete448-row review checks pass; explicit technical acceptance and subsequent accepted closeout remain required.')
