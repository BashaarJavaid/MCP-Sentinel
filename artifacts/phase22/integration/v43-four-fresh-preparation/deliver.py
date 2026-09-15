"""Deliver only the prepared, unapproved packet to the existing draft PR."""
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd(); OUT = Path(__file__).resolve().parent; BASE = OUT.parent
EXPECTED = 'c9637ba6ce0ffdbda5e639ea6eb1baa785599e9b'
TITLE = 'Phase 22: four fresh repositories prepared; evaluation approval pending'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
    return subprocess.check_output(args,cwd=ROOT,text=True,stderr=subprocess.STDOUT,timeout=180)
def save(name,value):
    with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def read_pr():
    return json.loads(run(['gh','pr','view','37','--json','number,state,isDraft,headRefName,headRefOid,baseRefName,title,body']))
def guard(pr):
    assert pr['state']=='OPEN' and pr['isDraft'] is True
    assert pr['headRefName']=='phase22/integration' and pr['baseRefName']=='phase22/description-poisoning'

binding=json.loads((OUT/'documentation-binding.json').read_text())
for field in ['owning_docs_sha256','review_packet_sha256','corpus_files_sha256','user_files_sha256']:
    for name,digest in binding[field].items():assert sha(ROOT/name)==digest,name
assert not (OUT/'evaluation-authorization.json').exists() and not (OUT/'execution-consumed.json').exists()
assert run(['git','branch','--show-current']).strip()=='phase22/integration'
assert run(['git','rev-parse','HEAD']).strip()==EXPECTED
assert not run(['git','diff','--cached'])
pr=read_pr();guard(pr);assert pr['headRefOid']==EXPECTED
assert run(['gh','api','repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration','--jq','.commit.sha']).strip()==EXPECTED
assert pr['body']==(BASE/'v42-path-guard-regression/pr-body.md').read_text()
run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'])
save('pre-delivery-pr37.json',pr)
selected=set(binding['owning_docs_sha256']) | set(binding['review_packet_sha256']) | set(binding['corpus_files_sha256'])
selected.update(str(p.relative_to(ROOT)) for p in [BASE/'evidence-v71.json',BASE/'evidence-v71.tar.gz',OUT/'documentation-binding.json',Path(__file__).resolve(),OUT/'pre-delivery-pr37.json'])
for label in ['faf','no-bash','lightning','engram']:
    for version in ['vulnerable','fixed']:
        selected.add(str((OUT/f'research/source-archives/{label}-{version}.tar.gz').relative_to(ROOT)))
        selected.add(str((OUT/f'research/source-archives/{label}-{version}.tar.json').relative_to(ROOT)))
    for name in [label+'-repository.json',label+('-security-fix.json' if label=='faf' else '-fix.json')]:
        selected.add(str((OUT/'research'/name).relative_to(ROOT)))
selected.update(str((OUT/'research'/n).relative_to(ROOT)) for n in ['faf-advisory.json','faf-release.json','faf-tag.json','faf-old-name.json'])
assert not set(binding['user_files_sha256']) & selected
run(['git','add','-f','--',*sorted(selected)])
staged=set(run(['git','diff','--cached','--name-only']).splitlines())
assert staged <= selected and not staged & set(binding['user_files_sha256'])
assert not any(n.startswith(('src/','tests/','scripts/','schemas/','.github/')) for n in staged)
run(['git','diff','--cached','--check','--',*binding['owning_docs_sha256']])
save('staged-delivery.json',{'paths':sorted(staged),'sha256':{n:sha(ROOT/n) for n in staged},'protected_user_files_not_staged':True,'proposal_sha256':sha(OUT/'evaluation-proposal.json'),'evidence_seal_sha256':sha(BASE/'evidence-v71.json'),'paid_calls':0})
print(run(['git','commit','-m','Prepare four fresh repository cases for exact evaluation approval [skip ci]']),flush=True)
head=run(['git','rev-parse','HEAD']).strip()
save('delivery-commit.json',{'head':head,'parent':EXPECTED,'proposal_sha256':sha(OUT/'evaluation-proposal.json'),'technical_acceptance_received':False})
print(run(['git','push','origin','HEAD:refs/heads/phase22/integration']),flush=True)
print(run(['gh','pr','edit','37','--title',TITLE,'--body-file',str(OUT/'pr-body.md')]),flush=True)
history=[]
for attempt in range(12):
    current=read_pr();branch=run(['gh','api','repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration','--jq','.commit.sha']).strip();guard(current)
    row={'recorded_at':datetime.now(timezone.utc).isoformat(),'pr':current,'branch_head':branch}
    history.append(row)
    if current['headRefOid']==head and branch==head and current['title']==TITLE and current['body']==(OUT/'pr-body.md').read_text():break
    print('Readback not yet current; read-only retry',attempt+1,flush=True);time.sleep(5)
else:
    save('delivery-readback-history.json',history)
    raise AssertionError('Remote readback remains stale; preserve successful mutations and recheck read-only.')
save('delivery-readback-history.json',history)
for name,digest in binding['user_files_sha256'].items():assert sha(ROOT/name)==digest,name
main=Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
receipt={'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'head':head,'base':'phase22/description-poisoning','draft':True,'open':True,'title':TITLE,'body_sha256':sha(OUT/'pr-body.md'),'proposal_sha256':sha(OUT/'evaluation-proposal.json'),'checkpoint_sha256':json.loads((OUT/'evaluation-proposal.json').read_text())['checkpoint']['sha256'],'scanner':binding['measured_scanner'],'seal71_sha256':binding['evidence_seal']['archive_sha256'],'readback_history_sha256':sha(OUT/'delivery-readback-history.json'),'documentation_binding_sha256':sha(OUT/'documentation-binding.json'),'protected_user_files_and_main_preserved':True,'new_paid_calls':0,'new_scanner_observations':0,'target_execution':False,'technical_acceptance_received':False,'phase22_complete':False,'effective_scope_disposition':{'id':'V43-PREPARATION-DELIVERY','disposition':'passed','basis':'All affected checks/seal/commit/push and exact branch/PR head/base/draft/title/body readback complete. This post-commit receipt supersedes the sealed pre-delivery audit row remaining unresolved at its recorded stage.'},'provenance':'Supplemental post-commit verification, not contained in seal71 or the commit it verifies; preserve for the next authorized evidence seal.'}
save('delivery-verification.json',receipt)
print(json.dumps(receipt,indent=2),flush=True)
