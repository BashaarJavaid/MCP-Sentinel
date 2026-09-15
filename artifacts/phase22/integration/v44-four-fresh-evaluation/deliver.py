"""Deliver completed failed fresh outcomes and recovery decision to existing draft."""
import hashlib
import json
import subprocess
import time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent;PREP=BASE/'v43-four-fresh-preparation'
EXPECTED='84f89a7308ffdf209981f1791e3fa06f16bf3c18';TITLE='Phase 22: four fresh gates failed; recovery decision pending'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):return subprocess.check_output(args,cwd=ROOT,text=True,stderr=subprocess.STDOUT,timeout=180)
def save(name,value):
    with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def pr():return json.loads(run(['gh','pr','view','37','--json','number,state,isDraft,headRefName,headRefOid,baseRefName,title,body']))
def guard(d):assert d['state']=='OPEN' and d['isDraft'] and d['headRefName']=='phase22/integration' and d['baseRefName']=='phase22/description-poisoning'
binding=json.loads((OUT/'documentation-binding.json').read_text())
for field in ['owning_docs_sha256','review_packet_sha256','user_files_sha256']:
    for name,digest in binding[field].items():assert sha(ROOT/name)==digest,name
assert run(['git','branch','--show-current']).strip()=='phase22/integration' and run(['git','rev-parse','HEAD']).strip()==EXPECTED
assert not run(['git','diff','--cached'])
d=pr();guard(d);assert d['headRefOid']==EXPECTED and d['body']==(PREP/'pr-body.md').read_text()
assert run(['gh','api','repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration','--jq','.commit.sha']).strip()==EXPECTED
run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'])
save('pre-delivery-pr37.json',d)
selected=set(binding['owning_docs_sha256'])|set(binding['review_packet_sha256'])
selected.update(str(path.relative_to(ROOT)) for path in [BASE/'evidence-v72.json',BASE/'evidence-v72.tar.gz',OUT/'documentation-binding.json',Path(__file__).resolve(),OUT/'pre-delivery-pr37.json'])
assert not selected&set(binding['user_files_sha256'])
run(['git','add','-f','--',*sorted(selected)])
staged=set(run(['git','diff','--cached','--name-only']).splitlines());assert staged<=selected and not staged&set(binding['user_files_sha256'])
assert not any(n.startswith(('src/','tests/','scripts/','schemas/','.github/')) for n in staged)
run(['git','diff','--cached','--check','--',*binding['owning_docs_sha256']])
save('staged-delivery.json',{'paths':sorted(staged),'sha256':{n:sha(ROOT/n) for n in staged},'recovery_proposal_sha256':sha(OUT/'recovery-proposal.json'),'evidence_index_sha256':sha(BASE/'evidence-v72.json'),'protected_user_files_not_staged':True})
print(run(['git','commit','-m','Retain four-repository fresh results and recovery decision [skip ci]']),flush=True)
head=run(['git','rev-parse','HEAD']).strip();save('delivery-commit.json',{'head':head,'parent':EXPECTED,'recovery_proposal_sha256':sha(OUT/'recovery-proposal.json'),'technical_acceptance_received':False})
print(run(['git','push','origin','HEAD:refs/heads/phase22/integration']),flush=True)
print(run(['gh','pr','edit','37','--title',TITLE,'--body-file',str(OUT/'pr-body.md')]),flush=True)
history=[]
for attempt in range(12):
    d=pr();branch=run(['gh','api','repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration','--jq','.commit.sha']).strip();guard(d)
    history.append({'recorded_at':datetime.now(timezone.utc).isoformat(),'pr':d,'branch_head':branch})
    if d['headRefOid']==head and branch==head and d['title']==TITLE and d['body']==(OUT/'pr-body.md').read_text():break
    print('Readback not current; checking again read-only.',flush=True);time.sleep(5)
else:
    save('delivery-readback-history.json',history);raise AssertionError('Remote readback stale; preserve mutations and recheck read-only.')
save('delivery-readback-history.json',history)
for name,digest in binding['user_files_sha256'].items():assert sha(ROOT/name)==digest,name
main=Path('/Users/bashaarjavaid/Projects/MCP-Sentinel');assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a';assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
receipt={'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'head':head,'base':'phase22/description-poisoning','draft':True,'open':True,'title':TITLE,'body_sha256':sha(OUT/'pr-body.md'),'recovery_proposal_sha256':sha(OUT/'recovery-proposal.json'),'assessment_sha256':sha(OUT/'assessment.json'),'scanner':binding['measured_scanner'],'seal72_sha256':binding['evidence_seal']['archive_sha256'],'readback_history_sha256':sha(OUT/'delivery-readback-history.json'),'documentation_binding_sha256':sha(OUT/'documentation-binding.json'),'protected_user_files_and_main_preserved':True,'native_observations':24,'remaining_budget':0,'new_paid_calls':0,'target_execution':False,'repository_gates_passed':0,'technical_acceptance_received':False,'phase22_complete':False,'effective_scope_disposition':{'id':'V44-DELIVERY','disposition':'passed','basis':'Affected checks,seal,commit,push and exact branch/PR head/base/draft/title/body readback complete. This receipt supersedes the sealed pre-delivery unresolved row for delivery only.'},'provenance':'Supplemental post-commit verification, not contained in seal72 or the commit it verifies; retain for next authorized seal.'}
save('delivery-verification.json',receipt);print(json.dumps(receipt,indent=2),flush=True)
