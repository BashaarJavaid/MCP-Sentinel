import datetime,hashlib,json,subprocess,time
from pathlib import Path
root=Path('/private/tmp/mcp-phase22-options');b=root/'artifacts/phase22/integration'
run=lambda a:subprocess.check_output(a,cwd=root,text=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda n:json.loads((b/n).read_text())
def write(name,data):
 p=b/name;assert not p.exists(),name;p.write_text(json.dumps(data,indent=2)+'\n')
head='e7131f027383b9471c5691536833a03b1a869bb7';assert run(['git','rev-parse','HEAD']).strip()==head
inputs=['src','tests','scripts','.github','schemas','Makefile','pyproject.toml','uv.lock','action.yml','README.md','LICENSE','CHANGELOG.md','THIRD_PARTY_NOTICES.md','.pre-commit-hooks.yaml','.python-version','.gitattributes','demo','sentinel.toml']
assert not run(['git','diff','HEAD','--',*inputs])
for label in ['v21-verification-command','v21-closeout-command','v21-final-docs-check-corrected']:assert read(label+'.json')['exit_code']==0,label
assert read('v21-hosted/packet.json')['engineering_passed'] and read('v21-hosted/packet.json')['source']==head
fields='number,state,isDraft,title,headRefName,headRefOid,baseRefName,body';before=json.loads(run(['gh','pr','view','37','--json',fields]));parent=json.loads(run(['gh','pr','view','36','--json','headRefOid,headRefName']))
assert before['headRefOid']==head and before['isDraft'] and before['state']=='OPEN' and before['baseRefName']=='phase22/description-poisoning'
assert before['body']==(b/'v20-closeout-draft-body.md').read_text() and parent['headRefOid']=='8b6b0ddf1d6f6cf5a8da3ab9421471865b801455'
subprocess.run(['git','merge-base','--is-ancestor',parent['headRefOid'],head],cwd=root,check=True)
docs=list(read('v20-final-documentation-binding.json')['final_documents_sha256'])
subprocess.run(['git','diff','--check','--',*docs],cwd=root,check=True)
check=read('v21-final-docs-check-corrected.json');assert sha(b/'v21-final-docs-check-corrected.patch')==check['diff_sha256']
seal=read('evidence-v50.json');assert sha(b/seal['archive'])==seal['sha256']
proposal=json.loads((root/'artifacts/phase22/corpus-replacement-v4/evaluation-proposal.json').read_text());assert proposal['scanner']==read('v21-candidate.json')['scanner'] and proposal['status']=='prepared_not_approved_not_dispatched';measurements=read('v21-sequence-assessment/packet.json')['attempts_consumed'];fresh_files=read('v21-fresh-proposal-verification.json')['prepared_files_sha256'];assert all(sha(root/n)==digest for n,digest in fresh_files.items())
binding={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hosted_source':head,'local_full_suite_source':'1f3f72f0f25c597b53c9f833e2e4bec99728d328','scanner':read('v21-source-verification.json')['scanner'],'actual_exposed_measurement_source':'2ac39aa9331818fd7e3a86c8323ee8307522c98c','actual_sequence_scanner':'1f3f72f0f25c597b53c9f833e2e4bec99728d328','final_documents_sha256':{n:sha(root/n) for n in docs},'delivery_helper_sha256':sha(b/'v21-final-delivery-helper.py'),'audit_sha256':sha(b/'v21-closeout-audit/packet.json'),'evidence_manifest_sha256':sha(b/'evidence-v50.json'),'evidence_archive_sha256':seal['sha256'],'proposal_sha256':sha(root/'artifacts/phase22/corpus-replacement-v4/evaluation-proposal.json'),'historical_refresh_proposal_sha256':sha(b/'v21-historical-assessment-refresh-proposal.json'),'draft_body_sha256':sha(b/'v21-closeout-draft-body.md'),'docs_check_sha256':sha(b/'v21-final-docs-check-corrected.json'),'binding':'Current code/test/workflow/package inputs equal tested e7131f0. Scanner/test/package bytes equal1f3f72f, the exact frozen scanner measured in the full approved Linux sequence. Prior exposed measurements retain2ac39aa; compatibility is source-bound in v21-source-verification.json. Final document hashes supersede audit-stage hashes only. This subsequent docs/evidence-only delivery uses authorized CI skip and is not a new hosted code pass.','new_corpus_runs':measurements,'new_paid_calls':0,'phase22_complete':False}
write('v21-final-documentation-binding.json',binding)
write('v21-delivery-verification.json',{'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'delivery_parent':head,'tested_source':head,'remote_before':before,'parent_before':parent,'tested_inputs_identical_to_candidate':inputs,'documents':docs,'binding_sha256':sha(b/'v21-final-documentation-binding.json'),'raw_docs_patch_sha256':check['diff_sha256'],'archive_sha256':seal['sha256'],'policy_approved':True,'full_sequence_approved':True,'new_corpus_runs':measurements,'new_paid_calls':0,'phase22_complete':False,'delivery_binding':'Receipt binds the verified pre-commit tree. Resulting commit and remote readback are stored in the supplemental local receipt; no self-referential hash is invented.'})
core=['v21-final-delivery-helper.py','evidence-v50.json','evidence-v50.tar.gz','v21-candidate.json','v21-full-sequence-authorization.json','v21-source-verification.json','v21-sequence-assessment/packet.json','v21-source-delta-assessment/packet.json','v21-full-sequence-disposition.json','v21-historical-assessment-refresh-proposal.json','v21-kubernetes-source-assessment.json','v21-fresh-proposal-verification.json','v21-closeout-audit/packet.json','v21-closeout-draft-body.md','v21-final-documentation-binding.json','v21-delivery-verification.json']+[f'{label}.{suffix}' for label in ['v21-closeout-command','v21-final-docs-check','v21-final-docs-check-corrected'] for suffix in ['json','log','patch','untracked.tar.gz']]
subprocess.run(['git','add','--',*docs,*fresh_files],cwd=root,check=True)
subprocess.run(['git','add','-f','--',*[str((b/n).relative_to(root)) for n in core]],cwd=root,check=True)
allowed=set(docs)|set(fresh_files)|{str((b/n).relative_to(root)) for n in core};staged=set(run(['git','diff','--cached','--name-only']).splitlines());assert staged<=allowed,staged-allowed
subprocess.run(['git','diff','--cached','--check','--','.',':(exclude)artifacts/phase22/integration/*.patch',':(exclude)artifacts/phase22/corpus-replacement-v4/provenance/full-pair.diff'],cwd=root,check=True)
subprocess.run(['git','commit','-m','Seal approved Linux sequence and fresh-evaluation checkpoint [skip ci]'],cwd=root,check=True)
delivery=run(['git','rev-parse','HEAD']).strip();assert not run(['git','diff',head,delivery,'--',*inputs])
subprocess.run(['git','push','origin','phase22/integration'],cwd=root,check=True)
subprocess.run(['gh','pr','edit','37','--body-file',str(b/'v21-closeout-draft-body.md')],cwd=root,check=True)
for attempt in range(12):
 after=json.loads(run(['gh','pr','view','37','--json',fields]))
 if after['headRefOid']==delivery and after['body']==(b/'v21-closeout-draft-body.md').read_text():break
 time.sleep(3)
assert after['headRefOid']==delivery and after['body']==(b/'v21-closeout-draft-body.md').read_text() and after['isDraft'] and after['state']=='OPEN' and after['baseRefName']==before['baseRefName']
assert not run(['git','diff','HEAD'])
prompts=read('v21-full-sequence-authorization.json')['user_files_sha256'];assert set(run(['git','ls-files','--others','--exclude-standard']).splitlines())==set(prompts)
for name,digest in prompts.items():assert sha(root/name)==digest
for name,digest in binding['final_documents_sha256'].items():assert sha(root/name)==digest
write('v21-final-delivery-readback.json',{'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'delivered_head':delivery,'tested_source':head,'remote_after':after,'verification_sha256':sha(b/'v21-delivery-verification.json'),'binding_sha256':sha(b/'v21-final-documentation-binding.json'),'tested_inputs_equal':True,'tracked_worktree_clean':True,'user_files_preserved':prompts,'new_corpus_runs':measurements,'new_paid_calls':0,'phase22_complete':False,'storage':'Supplemental ignored local post-delivery receipt; the tracked/sealed packet is the delivered Git tree.'})
print(delivery)
