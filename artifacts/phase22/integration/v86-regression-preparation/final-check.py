"""Verify completed engineering, exact proposal, preserved evidence and clean delivery scope."""
import ast, hashlib, json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];ENG=BASE/'v85-class-call-boundary'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(*args):return subprocess.check_output(args,cwd=ROOT,text=True)
def save(name,p):
 with (OUT/name).open('x') as f:json.dump(p,f,indent=2);f.write('\n')
checks=['v85-local-checks','v85-hosted-audit','v85-freeze','v86-proposal-preparation','v86-review-reconciliation','v86-final-docs','v86-final-generated','v86-final-build','v86-final-distributions']
for name in checks:assert read(BASE/(name+'.json'))['exit_code']==0,name
p=read(OUT/'evaluation-proposal.json');a=read(OUT/'audit.json');old=read(BASE/'v81-technical-acceptance/audit.json');local=read(ENG/'local-checks.json');freeze=read(ENG/'freeze.json')
assert run('git','rev-parse','HEAD').strip()==p['scanner']['revision']==local['candidate']=='884d3763d8d63786e1726932951fd859cb6071c2'
assert run('git','worktree','list','--porcelain')==freeze['worktrees_after']
assert a['scanner_identity']==p['scanner'] and a['engineering_passed'] and not a['acceptance_packet_ready'] and not a['technical_acceptance_received'] and not a['phase22_complete']
assert len(a['requirements'])==89 and len(a['additional_scope_requirements'])==374 and len(a['current_requirement_interpretations'])==463
for before,after in zip(old['requirements']+old['additional_scope_requirements'],a['requirements']+a['additional_scope_requirements']):assert before==after or after.get('previous_row')==before
assert sum(r['disposition']=='proposed documented limitation awaiting decision' for r in a['requirements']+a['additional_scope_requirements'])==26
assert not (OUT/'evaluation-authorization.json').exists() and not (OUT/'execution-consumed.json').exists() and not (BASE/'v87-regression-results').exists()
assert len(p['order'])==111 and len({(r['group'],r['input_id']) for r in p['order']})==63 and sum(r['batch']=='repeat' for r in p['order'])==48
for name,digest in p['files_sha256'].items():assert sha(ROOT/name)==digest,name
for name,digest in local['candidate_engineering_files_sha256'].items():assert sha(ROOT/name)==sha(Path(p['frozen_checkout'])/name)==digest,name
assert len(local['candidate_engineering_files_sha256'])==305 and local['states']=={'passed':2553,'skipped':36}
assert len(read(BASE/'v85-candidate-quality-audit/packet.json')['quality'])==12
prior_binding=read(BASE/'v81-technical-acceptance/documentation-binding.json')
for name,digest in prior_binding['additional_normative_docs_sha256'].items():assert sha(ROOT/name)==digest,name
docs=read(OUT/'owning-docs.json')['sha256']
for name,digest in docs.items():assert sha(ROOT/name)==digest,name
protected=read(BASE/'v82-python-module-dispatch/intake-and-authorization.json')['protected_user_files_sha256']
assert len(protected)==11
for name,digest in protected.items():assert sha(ROOT/name)==digest,name
assert set(run('git','ls-files','--others','--exclude-standard').splitlines())==set(protected)
assert not run('git','diff','--cached') and not run('git','ls-files','--deleted')
assert set(run('git','diff','--name-only').splitlines())==set(docs)
assert not run('git','diff','HEAD','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md','docs/architecture.md')
run('git','diff','--check');run('git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD')
main='/Users/bashaarjavaid/Projects/MCP-Sentinel';assert run('git','-C',main,'rev-parse','HEAD').strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a' and not run('git','-C',main,'status','--porcelain')
compat=read(ENG/'compatibility.json');assert compat['six_exact_fingerprints_and_full_requests_unchanged'] and len(compat['runtime_component_files_sha256'])==19
for name,digest in compat['runtime_component_files_sha256'].items():assert sha(ROOT/name)==digest,name
assert sha(BASE/'v85-production-capture-revalidation/packet.json')==compat['production_replay_sha256']
assert sha(BASE/'v68-invalidation-sampling/optimization-proposal.json')=='fa4ffc3760d4b85b4f8236eec5c7b28d979ece894515bb1495046dd1db108cf6'
assert not (BASE/'v69-ts-literal-key-reuse').exists()
for folder,total in [('v73-corrected-four-results',24),('v75-prior-language-results',181),('v80-unseen-results',12)]:
 packet=read(BASE/folder/'raw/packet.json');assert packet['budget_closed'] and packet['remaining_observation_budget']==0 and len(packet['attempts'])==total
 for name,digest in packet['files_sha256'].items():assert sha(BASE/folder/'raw'/name)==digest,name
assert not read(BASE/'v80-unseen-results/final-assessment/assessment.json')['fresh_detection_gate_passed']
assert not read(BASE/'v82-python-module-dispatch/receiver-mutation-controls.json')['all_passed']
assert read(BASE/'v82-full-suite.json')['exit_code']==2 and read(BASE/'v82-candidate-quality/packet.json')['runs']['ci']['conclusion']=='cancelled'
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
processes={}
for line in run('ps','-axo','pid=,ppid=,command=').splitlines():
 parts=line.strip().split(None,2)
 if len(parts)==3:processes[int(parts[0])]={'parent':int(parts[1]),'command':parts[2]}
ancestors=set();pid=os.getpid()
while pid in processes and pid not in ancestors:ancestors.add(pid);pid=processes[pid]['parent']
markers=['phase22-check.py','v82-','v83-','v85-','v86-','/launch.py','/evaluate.py','mcp-phase22-four-fresh-','-m pytest']
owned=[{'pid':pid,**row} for pid,row in processes.items() if pid not in ancestors and any(m in row['command'] for m in markers) and ('phase22' in row['command'] or 'MCP-Sentinel' in row['command'])]
managed=run('docker','ps','-aq','--filter','label=com.securemcp.sentinel=true').splitlines();named=run('docker','ps','-aq','--filter','name=sentinel').splitlines();assert not owned and not managed and not named,(owned,managed,named)
save('owned-final.json',{'owned_processes':owned,'managed_container_ids':managed,'sentinel_named_container_ids':named,'recorded_at':datetime.now(timezone.utc).isoformat(),'unrelated_work_terminated':False})
commands={path.stem:read(path) for path in BASE.glob('v8[23456]-*.json') if 'exit_code' in read(path)}
for name,c in commands.items():assert sha(BASE/(name+'.patch'))==c['diff_sha256'] and sha(BASE/c['untracked_source_archive'])==c['untracked_source_sha256'] and (BASE/c['log']).is_file(),name
failures={name:c['exit_code'] for name,c in commands.items() if c['exit_code']}
reasons={'v82-initial-quality':'Initial Ruff style checks failed; final lint/format pass.','v82-first-types':'Initial three typing errors corrected; final152-file type check passes.','v82-final-lint':'Five test-string style errors corrected before final lint.','v82-native-synthetic':'Owned terminal-guard case failed because plain global constructor resolved as class; actual global initializer correction verified.','v82-guard-debug':'Initial helper omitted required PathFlow deadline; corrected debug helper retained.','v82-receiver-mutation-controls':'Unsafe candidate preserved: replaced/escaped guards were trusted. V83 explicit conservative receiver/class boundary passes controls.','v82-full-suite':'Interrupted unsafe candidate after45passes,exit2. Cancelled hosted CI retained; no full pass inferred.','v83-lint':'One simplification-style error corrected before final lint.','v83-class-call-control':'The1ee96cb candidate passed its full local suite but falsely qualified a guard replaced by a direct class method. Exact failed control and cancelled hosted run retained; V85 removes the unproved class-call exception.','v84-collection-controls':'Zero-duration synthetic outer timer could interrupt before packet creation. Preserved initial helper; finite60-second admission control is shorter than required1815seconds and deterministically exercises actual refusal. Corrected eight scenarios pass.','v84-schedule-draft':'Initial source-only schedule helper treated temporarily omitted Python groups as TypeScript. Corrected selection defers those groups to the later Python stage; exact111/63/48 schedule verified.'}
assert set(failures)==set(reasons),('Unassessed check failure',failures)
save('check-failure-assessment.json',{'failed_wrapper_checks':{n:{'exit_code':code,'assessment':reasons[n]} for n,code in failures.items()},'prior_assessment_sha256':sha(BASE/'v81-technical-acceptance/check-failure-assessment.json'),'retention_label_erratum':read(ENG/'source-assessment.json')['retention_label_erratum'],'qualification':'All actual failed checks retain commands, logs, patches and helper/source archives. Corrected checks do not erase failures; partial/cancelled engineering is never full. Exploratory read-only key/path mistakes and patch context mismatches did not execute scanners or consume corpus budget.','paid_calls':0})
helpers={str(path.relative_to(ROOT)):sha(path) for folder in [BASE/'v82-python-module-dispatch',ENG,OUT] for path in folder.glob('*.py')}
for name in helpers:ast.parse((ROOT/name).read_text(),filename=name)
save('command-provenance.json',{'wrapper_commands':commands,'logs_sha256':{n:sha(BASE/c['log']) for n,c in commands.items()},'helper_sources_sha256':helpers,'failure_assessment_sha256':sha(OUT/'check-failure-assessment.json'),'paid_calls':0})
save('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':p['scanner'],'requirements':463,'engineering_files_verified':305,'runtime_components_verified':19,'six_production_requests_reused_without_calls':True,'protected_user_files':11,'owning_docs':17,'main_worktrees_parent_preserved':True,'checks_sha256':{n:sha(BASE/(n+'.json')) for n in checks},'current_source_observations':0,'proposed_observations':111,'proposed_inputs':63,'proposed_pairs':48,'ordinary_faf1800_completion_established':False,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Complete463-row correction/proposal checks pass; separate exact regression approval and later human technical acceptance remain.')
