"""Bind final docs, verified sources and sealed preparation before draft delivery."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((BASE/'v33-fresh-v6/documentation-binding.json').read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='8a3db5885981f511b58eb484550229c15d11bca0'
pr=json.loads((OUT/'pre-delivery-pr37.json').read_text());assert pr['headRefOid']==head and pr['isDraft'] and pr['state']=='OPEN' and pr['headRefName']=='phase22/integration' and pr['baseRefName']=='phase22/description-poisoning'
parent=json.loads((OUT/'pre-delivery-pr36.json').read_text());assert parent['headRefOid']=='8b6b0ddf1d6f6cf5a8da3ab9421471865b801455';subprocess.run(['git','merge-base','--is-ancestor',parent['headRefOid'],'HEAD'],check=True)
inputs=[n for n in old['byte_identical_quality_inputs'] if n!='README.md'];assert not subprocess.check_output(['git','diff',head,'--',*inputs])
protected=old['user_files_sha256'];assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())==set(protected)
for n,d in protected.items():assert sha(ROOT/n)==d,n
staged=old['authorized_staged_frozen_artifacts_sha256'];worktrees={}
expected={p:v['revision'] for p,v in old['worktrees'].items()}
expected.update({'/private/tmp/mcp-phase22-frozen-2624578':'2624578c381ae47df5b424e2c91f47a9cb362793','/private/tmp/mcp-phase22-frozen-5b5016e':'5b5016e1caf497088c2cd110e507058d54e6cda3','/private/tmp/mcp-phase22-frozen-a50e9b7':'a50e9b7754a69042394306d5207b428f965d8e1d'})
for folder,revision in expected.items():
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=folder,text=True).strip()==revision
 assert not subprocess.check_output(['git','diff','HEAD'],cwd=folder)
 if folder.endswith('frozen-f85a90f'):
  assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=folder,text=True).splitlines())==set(staged)
  for n,d in staged.items():assert sha(Path(folder)/n)==d,n
  worktrees[folder]={'revision':revision,'tracked_clean':True,'untracked':'Exactly the21 authorized corpus-v6 assets retained with original hashes.'}
 else:
  assert not subprocess.check_output(['git','status','--porcelain'],cwd=folder);worktrees[folder]={'revision':revision,'clean':True}
assert json.loads((BASE/'v34-final-docs.json').read_text())['exit_code']==0
assert json.loads((OUT/'owned-work-final.json').read_text())['owned_processes']==[]
assert json.loads((BASE/'v34-import-quality/packet.json').read_text())['engineering_passed']
proposal=json.loads((OUT/'evaluation-proposal.json').read_text())
for n,d in proposal['files_sha256'].items():assert sha(ROOT/n)==d,n
for folder,row in json.loads((OUT/'older-frozen-source-bindings.json').read_text()).items():
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=folder,text=True).strip()==row['revision']
 assert not subprocess.check_output(['git','diff','HEAD'],cwd=folder)
 assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=folder,text=True).splitlines())==set(row['existing_untracked_files_sha256'])
 for n,d in row['existing_untracked_files_sha256'].items():assert sha(Path(folder)/n)==d,n
assert not (OUT/'evaluation-authorization.json').exists() and not (OUT/'execution-consumed.json').exists()
audit=json.loads((OUT/'audit.json').read_text());assert len(audit['requirements'])==89 and len(audit['additional_scope_requirements'])==94
assert audit['dispositions']=={'passed':69,'explicitly user-deferred':2,'unresolved':18}
for n,d in audit['current_source_and_test_files'].items():
 if n in old['owning_docs_sha256']:
  assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+n])).hexdigest()==d,n
 else:assert sha(ROOT/n)==d,n
seal=json.loads((BASE/'evidence-v61.json').read_text());assert sha(BASE/seal['archive'])==seal['sha256']
for r in seal['files']:assert sha(BASE/r['path'])==r['sha256'],r['path']
dist=json.loads((OUT/'final-distributions.json').read_text());assert sha(ROOT/'README.md')==dist['README_sha256']
for d in dist['distributions']:assert sha(ROOT/d['path'])==d['sha256']
refs=['post-seal-binding-correction.json','bind-delivery-final.py','deliver-final.py','final-verification.json','older-frozen-source-bindings.json','audit.json','summary.md','pr-body.md','evaluation-proposal.json','scoring-rubric.json','freeze.json','source-proof.json','frozen-source-validation.json','compatibility.json','local-checks.json','local-source-binding.json','check-failure-assessment.json','final-distributions.json','verify-delivery.py']
packet={'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':head,'tested_workflow':head,'scanner':proposal['scanner'],'byte_identical_quality_inputs':inputs,'owning_docs_sha256':{n:sha(ROOT/n) for n in old['owning_docs_sha256']},'review_packet_sha256':{n:sha(OUT/n) for n in refs},'user_files_sha256':protected,'worktrees':worktrees,'authorized_staged_frozen_artifacts_sha256':staged,'evidence_seal':{'path':'evidence-v61.tar.gz','sha256':seal['sha256'],'members':len(seal['files'])},'pre_delivery_readbacks_sha256':{n:sha(OUT/n) for n in ['pre-delivery-pr37.json','pre-delivery-pr36.json']},'audit_document_hash_qualification':'The sealed audit includes document hashes at tested8a3db58, before final owning status edits. Those historical document hashes were verified against that Git source; all non-document source/test hashes match current bytes. owning_docs_sha256 in this final binding supplies the final current document hashes. The initial post-seal binder failure is retained separately.','metadata_only_README_change':'Final status prose changes packaged long-description metadata. Final wheel/sdist source members verified; all runtime/schema/fixture bytes equal installed-wheel tested8a3db58. Hosted artifacts retain their actual source.','final_distributions_sha256':sha(OUT/'final-distributions.json'),'new_corpus_observations':0,'new_paid_calls':0,'evaluation_approved':False,'proposed_native_observations':87,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding directly tracked; final remote draft readback follows commit/push. No circular commit identity or new hosted pass is claimed for documentation delivery.'}
path=OUT/'documentation-binding.json';assert not path.exists();path.write_text(json.dumps(packet,indent=2)+'\n');print('Bound final docs,audit89+94,source/package equality,87-observation proposal,seal61 and protected worktrees.')
