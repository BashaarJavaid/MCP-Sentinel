"""Verify complete source-bound review evidence and affected documentation/package checks."""
import ast,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];PRIOR=BASE/'v72-prototype-property-correction'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=lambda *args:subprocess.check_output(args,cwd=ROOT,text=True)
def write(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
checks=['v77-precuration-freeze-corrected','v77-novelty-inventory','v77-corpus-preparation','v77-runner-boundaries','v77-collection-boundaries-alarm-order','v77-exact-proposal','v77-staging-and-approval-boundary','v77-reconciliation','v77-final-docs','v77-final-generated','v77-final-build','v77-final-distributions']
for name in checks:assert read(BASE/(name+'.json'))['exit_code']==0,name
p=read(OUT/'evaluation-proposal.json');a=read(OUT/'audit.json');old=read(BASE/'v76-technical-acceptance/audit.json');intake=read(OUT/'scope-and-precuration-freeze.json');inventory=read(OUT/'workspace-inventory.json');local=read(PRIOR/'local-checks.json')
assert p['scanner']==a['scanner_identity'] and p['scanner']['revision']==local['candidate']=='cec0322e904bbf63c33cd95796e7289101a93e5d'
assert a['current_four_repository_gate_passed'] and a['current_earlier_language_compatibility_established'] and a['budget_closed'] and a['remaining']==0 and not a['technical_acceptance_received'] and not a['phase22_complete']
assert len(a['requirements'])==89 and len(a['additional_scope_requirements'])==346 and len(a['current_requirement_interpretations'])==435
for prior,current in zip(old['requirements']+old['additional_scope_requirements'],a['requirements']+a['additional_scope_requirements']):assert prior==current or current.get('previous_row')==prior
for identity in ['R66','R88','V14-RETENTION','V21-SEQUENCE','V21-FRESH-PROPOSAL','V25-EXPOSED-REGRESSION','V27-REGRESSION','V39-EVALUATION','V44-FOUR-GATE','V49-DIAGNOSTIC-PREPARATION','V55-EQUIVALENCE','V56-EQUIVALENCE','V65-EQUIVALENCE','V68-OPT-DECISION','V70-FOUR-GATE','V76-FAF-DEADLINE']:
 assert next(x for x in a['requirements']+a['additional_scope_requirements'] if x['id']==identity)['disposition']=='proposed documented limitation awaiting decision'
for n in [46,49,53,58,60,63,67]:assert next(x for x in a['additional_scope_requirements'] if x['id']==f'V{n}-REGRESSION-GATE')['disposition']=='proposed documented limitation awaiting decision'
for name,digest in local['candidate_engineering_files_sha256'].items():assert sha(ROOT/name)==sha(Path(p['frozen_checkout'])/name)==digest,name
assert len(local['candidate_engineering_files_sha256'])==303
for name,digest in read(PRIOR/'documentation-binding.json')['additional_normative_docs_sha256'].items():assert sha(ROOT/name)==digest,name
for name,digest in read(OUT/'owning-docs.json')['sha256'].items():assert sha(ROOT/name)==digest,name
for name,digest in intake['protected_files_sha256'].items():assert sha(ROOT/name)==digest,name
assert len(intake['protected_files_sha256'])==11
untracked=set(run('git','ls-files','--others','--exclude-standard').splitlines());assert set(intake['protected_files_sha256'])<=untracked and all(n in intake['protected_files_sha256'] or n.startswith('artifacts/phase22/corpus-unseen-v1/') for n in untracked)
assert run('git','rev-parse','HEAD').strip()==intake['delivery_head'] and run('git','worktree','list','--porcelain')==inventory['worktrees']
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
for folder,expected in [('v73-corrected-four-results',24),('v75-prior-language-results',181)]:
 packet=read(BASE/folder/'raw/packet.json');assert packet['budget_closed'] and len(packet['attempts'])==expected
 for name,digest in packet['files_sha256'].items():assert sha(BASE/folder/'raw'/name)==digest,name
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
assert not a['acceptance_packet_ready'] and not a['new_unseen_scope']['approved'] and a['new_unseen_scope']['observations']==0
for name in ['evaluation-authorization.json','source-freeze-authorization.json','execution-consumed.json']:assert not (OUT/name).exists()
assert not (BASE/'v78-unseen-results').exists()
for name,digest in p['files_sha256'].items():assert sha(ROOT/name)==digest,name
for name,digest in read(OUT/'staging-and-boundary-verification.json')['staged_files_sha256'].items():assert sha(ROOT/name)==sha(Path(p['frozen_checkout'])/name)==digest,name
assert read(OUT/'collection-checks.json')['passed'] and len(read(OUT/'collection-checks.json')['scenarios'])==8
# Validate retained native output without any scanner run; malformed copies must fail both validators.
import sys,copy,difflib
sys.path[:0]=[str(Path(p['frozen_checkout'])/'src'),p['frozen_checkout']]
from sentinel.report.validate_json import validate_report_data
from sentinel.report.validate_sarif import validate_sarif_data
from sentinel.errors import InfrastructureError
packet=read(BASE/'v75-prior-language-results/raw/packet.json')
report=next((BASE/'v75-prior-language-results/raw'/packet['attempts'][0]['directory']).rglob('report.json'))
validate_report_data(read(report));validate_sarif_data(read(report.with_suffix('.sarif')))
for validator,bad in [(validate_report_data,{'findings':'invalid'}),(validate_sarif_data,{'version':'2.1.0','runs':'invalid'})]:
 try:validator(bad)
 except InfrastructureError:pass
 else:raise AssertionError('Malformed native report admitted')
initial=(OUT/'evaluate-initial.py').read_text();final=(OUT/'evaluate.py').read_text()
alarm='    signal.signal(signal.SIGALRM, supervisor.stopped)\n    signal.setitimer(signal.ITIMER_REAL, max(0.001, stop - time.monotonic()))\n'
assert initial.count(alarm)==1 and final.count('    '+alarm.splitlines()[0])==1
assert initial.replace(alarm,'',1)==final.replace('\n'.join('    '+line for line in alarm.splitlines())+'\n','',1)
delta=''.join(difflib.unified_diff(initial.splitlines(True),final.splitlines(True),fromfile='evaluate-initial.py',tofile='evaluate.py'))
with (OUT/'runner-final-correction.patch').open('x') as f:f.write(delta)
write('final-runner-verification.json',{'passed':True,'proposal_sha256':sha(OUT/'evaluation-proposal.json'),'final_runner_sha256':sha(OUT/'evaluate.py'),'initial_runner_sha256':sha(OUT/'evaluate-initial.py'),'sole_post_initial_correction':'Move the two alarm lines inside try after the initial packet and one-use token; every other byte unchanged.','collection_checks_sha256':sha(OUT/'collection-checks.json'),'initial_boundary_checks_sha256':sha(OUT/'runner-boundaries.json'),'retained_native_report':str(report.relative_to(ROOT)),'report_sha256':sha(report),'sarif_sha256':sha(report.with_suffix('.sarif')),'native_schema_positive_and_negative_controls':4,'corpus_observations':0,'paid_calls':0})
processes={}
for line in run('ps','-axo','pid=,ppid=,command=').splitlines():
 parts=line.strip().split(None,2)
 if len(parts)==3:processes[int(parts[0])]={'parent':int(parts[1]),'command':parts[2]}
ancestors=set();pid=os.getpid()
while pid in processes and pid not in ancestors:ancestors.add(pid);pid=processes[pid]['parent']
markers=['phase22-check.py','v73-','v74-','v75-','v76-','v77-','v78-','/launch.py','/evaluate.py','mcp-phase22-four-fresh-']
owned=[{'pid':pid,**row} for pid,row in processes.items() if pid not in ancestors and any(m in row['command'] for m in markers) and ('phase22' in row['command'] or any(m in row['command'] for m in ['v73-','v74-','v75-','v76-','v77-','v78-']))]
managed=run('docker','ps','-aq','--filter','label=com.securemcp.sentinel=true').splitlines();named=run('docker','ps','-aq','--filter','name=sentinel').splitlines();assert not owned and not managed and not named
write('owned-final.json',{'owned_processes':owned,'managed_container_ids':managed,'sentinel_named_container_ids':named,'recorded_at':datetime.now(timezone.utc).isoformat(),'unrelated_work_terminated':False})
commands={path.stem:read(path) for path in BASE.glob('v77-*.json') if 'exit_code' in read(path)}
for name,c in commands.items():
 assert sha(BASE/(name+'.patch'))==c['diff_sha256'] and sha(BASE/c['untracked_source_archive'])==c['untracked_source_sha256'],name
 assert (BASE/c['log']).is_file(),name
failed={name:c['exit_code'] for name,c in commands.items() if c['exit_code']}
known={'v77-precuration-freeze':1,'v77-collection-boundaries':1,'v77-collection-boundaries-readable-host':1,'v77-collection-boundaries-corrected':1}
assert failed==known,('New failed wrapper needs explicit assessment',failed)
write('check-failure-assessment.json',{'failed_wrapper_checks':failed,'explanations':{'v77-precuration-freeze':'Initial helper read budget_closed from the wrong V75 execution summary; corrected to the actual raw packet before successful pre-curation freeze. No source research or observations preceded the successful freeze.','v77-collection-boundaries':'Sandbox sysctl host read was denied; rerun with authorized host read. No numerical input or paid call.','v77-collection-boundaries-readable-host':'Synthetic immediate outer-alarm stop exposed missing initial packet/budget record. Corrected by writing initial packet and one-use token before arming alarm, inside try/finally.','v77-collection-boundaries-corrected':'First correction command asserted on a broad duplicate substring and wrote no change; the unchanged helper failed again. Subsequent exact-line correction passed all eight scenarios.'},'additional_retained_corrections':['Initial evaluate-initial.py retains the pre-correction alarm order. prepare-runner.py and runner-delta.patch preserve the initial adaptation; final runner correction is separately diff-bound and is included in the exact proposal.','Exploratory nonexistent runner/test paths and overlong/truncated source reads were corrected with actual paths and bounded reads; no target execution.'],'original_failures':'All original fresh, exposed, timeout, partial/invalid profile, singleton and strict-equivalence outcomes remain source-bound in the complete prior audit and seals.','paid_calls':0})
helpers={str(path.relative_to(ROOT)):sha(path) for folder in [BASE/'v73-corrected-four-results',BASE/'v74-prior-language-preparation',BASE/'v75-prior-language-results',OUT] for path in folder.glob('*.py')}
for name in helpers:ast.parse((ROOT/name).read_text(),filename=name)
write('command-provenance.json',{'wrapper_commands':commands,'logs_sha256':{name:sha(BASE/c['log']) for name,c in commands.items()},'helper_sources_sha256':helpers,'failure_assessment_sha256':sha(OUT/'check-failure-assessment.json'),'qualification':'Exact commands, logs, patches, wrapper helper archives and initial/corrected sources retained. Sole approvedV73/V75executions; read-only assessment/preparation helpers are not new observations.','paid_calls':0})
write('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':p['scanner'],'requirements':435,'engineering_files_verified':303,'runtime_components_verified':19,'six_production_requests_reused_without_calls':True,'protected_user_files':11,'owning_docs':16,'main_worktrees_parent_preserved':True,'checks_sha256':{name:sha(BASE/(name+'.json')) for name in checks},'current_source_observations':205,'whole_ordered_pairs_equal':95,'budget_closed':True,'remaining':0,'ordinary_faf1800_completion_established':False,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Complete435-row preparation checks pass; numerical approval, fresh assessment, technical acceptance and accepted closeout remain required.')
