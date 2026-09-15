"""Bind the final review packet and owning documents after sealing, before delivery."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pr=json.loads((OUT/'pre-delivery-pr37.json').read_text())
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert pr['headRefOid']==head=='1bdc8fc7a045aed7ee8dd135bdb0e37b68690cb4'
assert pr['headRefName']=='phase22/integration' and pr['baseRefName']=='phase22/description-poisoning'
assert pr['isDraft'] and pr['state']=='OPEN'
parent=json.loads((OUT/'pre-delivery-pr36.json').read_text())
assert parent['headRefOid']=='8b6b0ddf1d6f6cf5a8da3ab9421471865b801455'
subprocess.run(['git','merge-base','--is-ancestor',parent['headRefOid'],'HEAD'],check=True)
protected=json.loads((BASE/'v29-loopback-fix/protected-files.json').read_text())
assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())==set(protected)
for n,d in protected.items():assert sha(ROOT/n)==d,n
previous=json.loads((BASE/'v31-compatibility/documentation-binding.json').read_text())
for folder,expected in previous['clean_worktrees'].items():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=folder,text=True).strip()==expected
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=folder)
inputs=previous['byte_identical_quality_inputs']
assert not subprocess.check_output(['git','diff','439c3fe','--',*inputs])
assert json.loads((BASE/'v32-index-docs.json').read_text())['exit_code']==0
assert json.loads((OUT/'owned-work-final.json').read_text())['owned_processes']==[]
final=json.loads((OUT/'preparation-final.json').read_text())
assert final['passed'] and final['proposal_sha256']==sha(OUT/'evaluation-proposal.json')
proposal=json.loads((OUT/'evaluation-proposal.json').read_text())
for n,d in proposal['files_sha256'].items():assert sha(ROOT/n)==d,n
seal=json.loads((BASE/'evidence-v59.json').read_text())
assert sha(BASE/seal['archive'])==seal['sha256']
for r in seal['files']:assert sha(BASE/r['path'])==r['sha256'],r['path']
assert not (OUT/'evaluation-authorization.json').exists()
assert not (OUT/'execution-consumed.json').exists()
audit=json.loads((OUT/'audit.json').read_text())
assert audit['dispositions']=={'passed':84,'explicitly user-deferred':2,'unresolved':3}
assert audit['additional_scope_dispositions']=={'passed':80,'proposed documented limitation awaiting decision':5,'unresolved':1}
names=list(previous['owning_docs_sha256'])+['artifacts/phase22/corpus-replacement-v6/README.md']
refs=['scope-and-precuration-freeze.json','evaluation-proposal.json','scoring-rubric.json','summary.md','audit.json','pr-body.md','runner.py','preparation-final.json']
packet={'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':head,'tested_workflow':previous['tested_workflow'],'scanner':proposal['scanner'],'byte_identical_quality_inputs':inputs,'owning_docs_sha256':{n:sha(ROOT/n) for n in names},'review_packet_sha256':{n:sha(OUT/n) for n in refs},'user_files_sha256':protected,'clean_worktrees':previous['clean_worktrees'],'evidence_seal':{'path':'evidence-v59.tar.gz','sha256':seal['sha256'],'members':len(seal['files'])},'new_corpus_files_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'artifacts/phase22/corpus-replacement-v6').rglob('*') if p.is_file()},'pre_delivery_readbacks_sha256':{n:sha(OUT/n) for n in ['pre-delivery-pr37.json','pre-delivery-pr36.json']},'new_corpus_observations':0,'new_paid_calls':0,'evaluation_approved':False,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Supplemental post-seal binding; remote readbacks were created after seal59 completed and are not claimed inside it. Documentation and review files are final; actual future delivery is verified after commit/push. Historical scanner/source/test evidence retains its original measured identities.'}
p=OUT/'documentation-binding.json';assert not p.exists();p.write_text(json.dumps(packet,indent=2)+'\n')
print('Final documentation, proposal, seal59, source equality and protected worktrees verified.')
