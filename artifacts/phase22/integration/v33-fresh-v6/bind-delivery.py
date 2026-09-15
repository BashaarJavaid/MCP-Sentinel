"""Bind final docs, source identity and verified seal before draft delivery."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='8a3c070122a4196df07287ea91807ff3f946cbf2'
pr=json.loads((OUT/'pre-delivery-pr37.json').read_text());assert pr['headRefOid']==head and pr['isDraft'] and pr['state']=='OPEN' and pr['headRefName']=='phase22/integration' and pr['baseRefName']=='phase22/description-poisoning'
parent=json.loads((OUT/'pre-delivery-pr36.json').read_text());assert parent['headRefOid']=='8b6b0ddf1d6f6cf5a8da3ab9421471865b801455';subprocess.run(['git','merge-base','--is-ancestor',parent['headRefOid'],'HEAD'],check=True)
previous=json.loads((BASE/'v32-fresh-v6/documentation-binding.json').read_text());inputs=previous['byte_identical_quality_inputs'];assert not subprocess.check_output(['git','diff','439c3fe','--',*inputs])
protected=previous['user_files_sha256'];assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())==set(protected)
for n,d in protected.items():assert sha(ROOT/n)==d,n
staged=json.loads((OUT/'launch-completed.json').read_text())['known_staged_artifact_files_sha256']
worktrees={}
for folder,expected in previous['clean_worktrees'].items():
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=folder,text=True).strip()==expected
 assert not subprocess.check_output(['git','diff','HEAD'],cwd=folder)
 if folder.endswith('frozen-f85a90f'):
  assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=folder,text=True).splitlines())==set(staged)
  for n,d in staged.items():assert sha(Path(folder)/n)==d,n
  worktrees[folder]={'revision':expected,'tracked_clean':True,'untracked':'Exactly the approved hash-bound staged corpus-v6 assets; preserved.'}
 else:
  assert not subprocess.check_output(['git','status','--porcelain'],cwd=folder);worktrees[folder]={'revision':expected,'clean':True}
assert json.loads((BASE/'v33-final-docs.json').read_text())['exit_code']==0
assert json.loads((OUT/'owned-work-final.json').read_text())['owned_processes']==[]
a=json.loads((OUT/'assessment.json').read_text());assert a['fresh_detection_gate_passed'] and not a['fixed_guard_recognition_established']
proposal=json.loads((OUT/'acceptance-proposal.json').read_text())
for n,d in proposal['files_sha256'].items():assert sha(BASE/n)==d,n
raw=json.loads((OUT/'raw/packet.json').read_text())
for n,d in raw['files_sha256'].items():assert sha(OUT/'raw'/n)==d,n
assert raw['budget_closed'] and raw['unstarted']==[] and len(raw['attempts'])==15
assert not (OUT/'technical-acceptance.json').exists() and not proposal['accepted']
audit=json.loads((OUT/'audit.json').read_text());assert audit['dispositions']=={'passed':86,'explicitly user-deferred':2,'unresolved':1};assert audit['additional_scope_dispositions']=={'passed':82,'proposed documented limitation awaiting decision':6}
assert len({r['id'] for r in audit['requirements']})==89 and len({r['id'] for r in audit['additional_scope_requirements']})==88
# Revalidate complete current product/test source lists through unchanged439c3fe;
# historical per-file source assessments remain bound to their measured revisions.
seal=json.loads((BASE/'evidence-v60.json').read_text());assert sha(BASE/seal['archive'])==seal['sha256']
for r in seal['files']:assert sha(BASE/r['path'])==r['sha256'],r['path']
names=list(previous['owning_docs_sha256']);refs=['assessment.json','audit.json','summary.md','acceptance-proposal.json','pr-body.md','assessment-corrections.json','assess.py','verify-delivery.py']
packet={'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':head,'tested_workflow':previous['tested_workflow'],'scanner':a['scanner'],'byte_identical_quality_inputs':inputs,'owning_docs_sha256':{n:sha(ROOT/n) for n in names},'review_packet_sha256':{n:sha(OUT/n) for n in refs},'user_files_sha256':protected,'worktrees':worktrees,'authorized_staged_frozen_artifacts_sha256':staged,'evidence_seal':{'path':'evidence-v60.tar.gz','sha256':seal['sha256'],'members':len(seal['files'])},'pre_delivery_readbacks_sha256':{n:sha(OUT/n) for n in ['pre-delivery-pr37.json','pre-delivery-pr36.json']},'new_corpus_observations':15,'new_paid_calls':0,'evaluation_approved':True,'fresh_detection_gate_passed':True,'fixed_guard_recognition_established':False,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Supplemental post-seal binding, directly tracked. Final draft delivery readback follows commit/push; no circular commit hash. Frozenf85 tracked bytes unchanged with exactly authorized corpus assets retained as untracked files. Prior scanner/test evidence retains measured identities.'}
with (OUT/'documentation-binding.json').open('x') as f:json.dump(packet,f,indent=2);f.write('\n')
print('Final docs, audit89+88, source equality,15observations,seal60 and protected worktrees verified.')
