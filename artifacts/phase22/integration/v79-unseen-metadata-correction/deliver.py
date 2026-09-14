"""Deliver the authorized complete review packet to existing OPEN DRAFT PR37 only."""
import hashlib,json,subprocess,tarfile,time
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3]
EXPECTED='161818ac298b2e371d5c8da97f974816a88e7f9d';TITLE='Phase 22: corrected unseen-evaluation proposal pending'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def run(args):return subprocess.check_output(args,cwd=ROOT,text=True,stderr=subprocess.STDOUT,timeout=180)
def save(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def pr():return json.loads(run(['gh','pr','view','37','--json','number,state,isDraft,headRefName,headRefOid,baseRefName,title,body']))
def guard(d):assert d['number']==37 and d['state']=='OPEN' and d['isDraft'] and d['headRefName']=='phase22/integration' and d['baseRefName']=='phase22/description-poisoning'
b=read(OUT/'documentation-binding.json');a=read(OUT/'audit.json')
assert b['baseline_delivery']==EXPECTED and not a['technical_acceptance_received'] and not a['new_unseen_scope']['approved'] and a['new_unseen_scope']['observations']==0
assert not (OUT/'execution-consumed.json').exists() and not (OUT/'evaluation-authorization.json').exists() and not (BASE/'v80-unseen-results').exists()
for field in ['owning_docs_sha256','review_packet_sha256','user_files_sha256','additional_normative_docs_sha256']:
 for name,digest in b[field].items():assert sha(ROOT/name)==digest,name
assert sha(OUT/'evaluation-proposal.json')==b['evaluation_proposal_sha256']
assert run(['git','rev-parse','HEAD']).strip()==EXPECTED and run(['git','branch','--show-current']).strip()=='phase22/integration'
assert not run(['git','diff','--cached']) and set(run(['git','diff','--name-only']).splitlines())==set(b['owning_docs_sha256'])
assert run(['git','worktree','list','--porcelain'])==b['worktrees']
run(['git','diff','--check']);run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'])
for name,digest in read(BASE/'v72-prototype-property-correction/local-checks.json')['candidate_engineering_files_sha256'].items():assert sha(ROOT/name)==digest,name
assert sha(BASE/'v68-invalidation-sampling/optimization-proposal.json')==b['pending_optimization_proposal_sha256'] and not (BASE/'v69-ts-literal-key-reuse').exists()
seal=read(BASE/'evidence-v101.json');assert sha(BASE/'evidence-v101.json')==b['evidence_seal']['index_sha256'] and sha(BASE/seal['archive'])==seal['sha256']==b['evidence_seal']['archive_sha256']
with tarfile.open(BASE/seal['archive']) as archive:
 assert len(archive.getmembers())==len(seal['files'])
 for row in seal['files']:
  assert sha(BASE/row['path'])==row['sha256'],row['path'];member=archive.getmember(row['path']);assert member.isfile() and member.size==row['bytes'] and hashlib.sha256(archive.extractfile(member).read()).hexdigest()==row['sha256']
current=pr();guard(current)
assert current['headRefOid']==EXPECTED and current['title']=='Phase 22: unseen-source evaluation approval pending'
assert current['body']==(BASE/'v77-unseen-preparation/pr-body-delivery.md').read_text()
assert run(['gh','api','repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration','--jq','.commit.sha']).strip()==EXPECTED
save('pre-delivery-pr37.json',current)
selected=set(b['owning_docs_sha256'])|set(b['review_packet_sha256'])
extra=[BASE/'evidence-v101.json',BASE/'evidence-v101.tar.gz',OUT/'documentation-binding.json',OUT/'pre-delivery-pr37.json',*OUT.glob('*.py'),*BASE.glob('v79-documentation-binding.*')]
selected.update(str(path.relative_to(ROOT)) for path in extra)
assert not selected&set(b['user_files_sha256']) and all((ROOT/name).stat().st_size<100*1024*1024 for name in selected)
run(['git','add','-f','--',*sorted(selected)])
staged=set(run(['git','diff','--cached','--name-only']).splitlines());assert staged<=selected and not staged&set(b['user_files_sha256'])
assert not any(name.startswith(('src/','tests/','scripts/','schemas/','.github/')) for name in staged)
run(['git','diff','--cached','--check','--',*b['owning_docs_sha256']])
save('staged-delivery.json',{'sha256':{name:sha(ROOT/name) for name in sorted(staged)},'protected_user_files_not_staged':True,'approval_basis':'Protected user handoff authorizes integration commits and batched delivery to this exact existing OPEN DRAFT PR37; no merge/ready/release.'})
print(run(['git','commit','-m','Preserve stopped unseen run and correct input metadata proposal [skip ci]']),flush=True)
head=run(['git','rev-parse','HEAD']).strip();save('delivery-commit.json',{'head':head,'parent':EXPECTED,'scanner':b['corrected_scanner'],'technical_acceptance_received':False})
print(run(['git','push','https://github.com/BashaarJavaid/MCP-Sentinel.git','HEAD:refs/heads/phase22/integration']),flush=True)
save('metadata-update.json',{'title':TITLE,'body':(OUT/'pr-body-delivery.md').read_text()})
response=json.loads(run(['gh','api','--method','PATCH','repos/BashaarJavaid/MCP-Sentinel/pulls/37','--input',str(OUT/'metadata-update.json'),'--jq','{number,state,draft,title,head:.head.sha,base:.base.ref}']));save('metadata-response.json',response);print(json.dumps(response),flush=True)
history=[]
for attempt in range(12):
 current=pr();branch=run(['gh','api','repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration','--jq','.commit.sha']).strip();guard(current)
 history.append({'recorded_at':datetime.now(timezone.utc).isoformat(),'pr':current,'branch_head':branch})
 if current['headRefOid']==head and branch==head and current['title']==TITLE and current['body']==(OUT/'pr-body-delivery.md').read_text():break
 print('Remote head readback stale; retrying read-only verification.',flush=True);time.sleep(5)
else:
 save('delivery-readback-history.json',history);raise AssertionError('Retain completed writes and retry readback only; do not repeat mutation.')
save('delivery-readback-history.json',history)
for name,digest in b['user_files_sha256'].items():assert sha(ROOT/name)==digest,name
main='/Users/bashaarjavaid/Projects/MCP-Sentinel';assert run(['git','-C',main,'rev-parse','HEAD']).strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a' and not run(['git','-C',main,'status','--porcelain'])
assert not run(['git','diff','HEAD','--name-only'])
expected_worktrees=b['worktrees'].replace('worktree '+str(ROOT)+'\nHEAD '+EXPECTED,'worktree '+str(ROOT)+'\nHEAD '+head,1)
assert run(['git','worktree','list','--porcelain'])==expected_worktrees
counts={**a['additional_scope_dispositions']};counts['passed']+=1;counts['unresolved']-=1
receipt={'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'head':head,'base':'phase22/description-poisoning','draft':True,'open':True,'title':TITLE,'body_sha256':sha(OUT/'pr-body-delivery.md'),'evaluation_proposal_sha256':b['evaluation_proposal_sha256'],'scanner':b['corrected_scanner'],'seal101_sha256':seal['sha256'],'readback_history_sha256':sha(OUT/'delivery-readback-history.json'),'documentation_binding_sha256':sha(OUT/'documentation-binding.json'),'protected_user_files_main_worktrees_preserved':True,'current_source_observations':205,'new_unseen_observations':0,'previous_attempted':1,'previous_incomplete':1,'previous_reports':0,'previous_unstarted_closed':11,'new_numerical_approval_received':False,'whole_ordered_pairs_equal':95,'repository_gates_passed':4,'prior_language_compatibility_passed':True,'budget_closed':True,'remaining':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'effective_scope_disposition':{'id':'V79-DELIVERY','disposition':'passed','basis':'Affected checks, seal, commit/push and exact remote branch/PR head/base/draft/title/body readback verified. This resolves numerical proposal delivery only; exact evaluation approval, execution, full assessment, updated review, explicit technical acceptance and actual accepted closeout remain.'},'effective_additional_scope_dispositions':counts,'provenance':'Supplemental post-commit readback outside its own seal/commit; preserve in next authorized evidence seal without infinite self-receipt commits.'}
save('delivery-verification.json',receipt);print(json.dumps(receipt,indent=2),flush=True)
