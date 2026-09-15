"""Verify complete source-bound review evidence and affected documentation/package checks."""
import ast,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];PRIOR=BASE/'v72-prototype-property-correction'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=lambda *args:subprocess.check_output(args,cwd=ROOT,text=True)
def write(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
checks=['v75-prior-language-execution','v75-complete-validation','v75-complete-comparison','v75-python-development-source-assessment','v75-python-source-assessment-corrected','v75-complete-assessment','v75-completion-verification','v76-reconciliation','v76-review-documents','v76-final-docs','v76-final-artifacts','v76-final-build','v76-final-distributions']
for name in checks:assert read(BASE/(name+'.json'))['exit_code']==0,name
p=read(BASE/'v74-prior-language-preparation/evaluation-proposal.json');a=read(OUT/'audit.json');old=read(PRIOR/'audit.json');intake=read(BASE/'v73-corrected-regression-intake.json');local=read(PRIOR/'local-checks.json')
assert p['scanner']==a['scanner_identity'] and p['scanner']['revision']==local['candidate']=='cec0322e904bbf63c33cd95796e7289101a93e5d'
assert a['current_four_repository_gate_passed'] and a['current_earlier_language_compatibility_established'] and a['budget_closed'] and a['remaining']==0 and not a['technical_acceptance_received'] and not a['phase22_complete']
assert len(a['requirements'])==89 and len(a['additional_scope_requirements'])==333 and len(a['current_requirement_interpretations'])==422
for prior,current in zip(old['requirements']+old['additional_scope_requirements'],a['requirements']+a['additional_scope_requirements']):assert prior==current or current.get('previous_row')==prior
for identity in ['R66','R88','V14-RETENTION','V21-SEQUENCE','V21-FRESH-PROPOSAL','V25-EXPOSED-REGRESSION','V27-REGRESSION','V39-EVALUATION','V44-FOUR-GATE','V49-DIAGNOSTIC-PREPARATION','V55-EQUIVALENCE','V56-EQUIVALENCE','V65-EQUIVALENCE','V68-OPT-DECISION','V70-FOUR-GATE','V76-FAF-DEADLINE']:
 assert next(x for x in a['requirements']+a['additional_scope_requirements'] if x['id']==identity)['disposition']=='proposed documented limitation awaiting decision'
for n in [46,49,53,58,60,63,67]:assert next(x for x in a['additional_scope_requirements'] if x['id']==f'V{n}-REGRESSION-GATE')['disposition']=='proposed documented limitation awaiting decision'
for name,digest in local['candidate_engineering_files_sha256'].items():assert sha(ROOT/name)==sha(Path(p['frozen_checkout'])/name)==digest,name
assert len(local['candidate_engineering_files_sha256'])==303
for name,digest in read(PRIOR/'documentation-binding.json')['additional_normative_docs_sha256'].items():assert sha(ROOT/name)==digest,name
for name,digest in read(OUT/'owning-docs.json')['sha256'].items():assert sha(ROOT/name)==digest,name
for name,digest in intake['protected_user_files_sha256'].items():assert sha(ROOT/name)==digest,name
assert len(intake['protected_user_files_sha256'])==10
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
for folder,expected in [('v73-corrected-four-results',24),('v75-prior-language-results',181)]:
 packet=read(BASE/folder/'raw/packet.json');assert packet['budget_closed'] and len(packet['attempts'])==expected
 for name,digest in packet['files_sha256'].items():assert sha(BASE/folder/'raw'/name)==digest,name
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
processes={}
for line in run('ps','-axo','pid=,ppid=,command=').splitlines():
 parts=line.strip().split(None,2)
 if len(parts)==3:processes[int(parts[0])]={'parent':int(parts[1]),'command':parts[2]}
ancestors=set();pid=os.getpid()
while pid in processes and pid not in ancestors:ancestors.add(pid);pid=processes[pid]['parent']
markers=['phase22-check.py','v73-','v74-','v75-','v76-','/launch.py','/evaluate.py','mcp-phase22-four-fresh-']
owned=[{'pid':pid,**row} for pid,row in processes.items() if pid not in ancestors and any(m in row['command'] for m in markers) and ('phase22' in row['command'] or any(m in row['command'] for m in ['v73-','v74-','v75-','v76-']))]
managed=run('docker','ps','-aq','--filter','label=com.securemcp.sentinel=true').splitlines();named=run('docker','ps','-aq','--filter','name=sentinel').splitlines();assert not owned and not managed and not named
write('owned-final.json',{'owned_processes':owned,'managed_container_ids':managed,'sentinel_named_container_ids':named,'recorded_at':datetime.now(timezone.utc).isoformat(),'unrelated_work_terminated':False})
commands={path.stem:read(path) for prefix in ['v73-','v74-','v75-','v76-'] for path in BASE.glob(prefix+'*.json') if 'exit_code' in read(path)}
for name,c in commands.items():
 assert sha(BASE/(name+'.patch'))==c['diff_sha256'] and sha(BASE/c['untracked_source_archive'])==c['untracked_source_sha256'],name
 assert (BASE/c['log']).is_file(),name
failed={name:c['exit_code'] for name,c in commands.items() if c['exit_code']}
known={'v75-python-source-assessment':1,'v75-python-historical-first-comparison':1,'v73-intake-verification':1,'v73-faf-first-source-inventory':1,'v74-preparation-verification':1,'v75-assessment-helper-preparation':1,'v75-ddg-source-assessment':1,'v75-git-first-source-assessment':1}
assert failed==known,('New failed wrapper needs explicit assessment',failed)
write('check-failure-assessment.json',{'failed_wrapper_checks':failed,'explanations':{'v75-python-source-assessment':'Different input records share exact frozen Git source/output but retain different target.display_name. Corrected helper verifies only that explicit expected name delta, retaining all other fields and11existing exclusions; original failure retained.','v75-python-historical-first-comparison':'Comparison was started before its dependent validation receipt finished and failed on the absent file. Original failure retained; rerun only after validation exited0, with a new wrapper label. No corpus input reran.','v75-git-first-source-assessment':'Helper used nonexistent rule-outcome matches counter; corrected to actual match_count while retaining complete ordered counter/report checks and original failure.','v73-intake-verification':'Pre-delivery versus5263cb2 HEAD transition check corrected and retained.','v73-faf-first-source-inventory':'Conceptual/nonliteral external dynamic-import warning had no identifier occurrence; corrected file-only source binding, no invented line. Follow-on absent file error retained.','v74-preparation-verification':'Wrong remaining_observation_budget key used forV73execution; actual remaining key checked, no budget changed.','v75-assessment-helper-preparation':'Synthetic line0 source-binding check exposed None-versus-zero helper bug; corrected helper rejects0.','v75-ddg-source-assessment':'Historical repeat receipt incorrectly paired with proposal-bound first report hash; select exact first reference for bothcurrentbatches after independent full repeat check.'},'additional_retained_corrections':['FirstFAF guessed export span was empty; actual232–235supplement retained without overwriting original.','Exploratory group mapping/None assessment, unequal Git finding zip and historical/Mastra scan-root reads corrected without target execution.','Read-only sandbox PS/DNS and numeric seal-regex errors retained; no new auto-review rejection.'],'original_failures':'All prior failed synthetic/corpus/timeout/profile/strict-equivalence/initial interrupted engineering outcomes remain source-bound and retained by complete audit/seals.','paid_calls':0})
helpers={str(path.relative_to(ROOT)):sha(path) for folder in [BASE/'v73-corrected-four-results',BASE/'v74-prior-language-preparation',BASE/'v75-prior-language-results',OUT] for path in folder.glob('*.py')}
for name in helpers:ast.parse((ROOT/name).read_text(),filename=name)
write('command-provenance.json',{'wrapper_commands':commands,'logs_sha256':{name:sha(BASE/c['log']) for name,c in commands.items()},'helper_sources_sha256':helpers,'failure_assessment_sha256':sha(OUT/'check-failure-assessment.json'),'qualification':'Exact commands, logs, patches, wrapper helper archives and initial/corrected sources retained. Sole approvedV73/V75executions; read-only assessment/preparation helpers are not new observations.','paid_calls':0})
write('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':p['scanner'],'requirements':422,'engineering_files_verified':303,'runtime_components_verified':19,'six_production_requests_reused_without_calls':True,'protected_user_files':10,'owning_docs':16,'main_worktrees_parent_preserved':True,'checks_sha256':{name:sha(BASE/(name+'.json')) for name in checks},'current_source_observations':205,'whole_ordered_pairs_equal':95,'budget_closed':True,'remaining':0,'ordinary_faf1800_completion_established':False,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Complete422-row review checks pass; explicit technical acceptance and subsequent accepted closeout remain required.')
