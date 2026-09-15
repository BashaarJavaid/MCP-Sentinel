"""Deliver the authorized complete review packet to existing OPEN DRAFT PR37 only."""
import base64,collections,copy,hashlib,json,subprocess,tarfile,time
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3]
EXPECTED='792d92216c0bb7268b6757c61c5133676a1c7509';TITLE='Phase 22: technically accepted and closed under revised scope'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def run(args):return subprocess.check_output(args,cwd=ROOT,text=True,stderr=subprocess.STDOUT,timeout=180)
def save(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def pr():return json.loads(run(['gh','pr','view','37','--json','number,state,isDraft,headRefName,headRefOid,baseRefName,title,body']))
def guard(d):assert d['number']==37 and d['state']=='OPEN' and d['isDraft'] and d['headRefName']=='phase22/integration' and d['baseRefName']=='phase22/description-poisoning'
b=read(OUT/'documentation-binding.json');a=read(OUT/'audit.json')
assert b['baseline_delivery']==EXPECTED and a['technical_acceptance_received'] and a['current_regression_approved'] and a['current_source_corpus_observations']==6 and not a['current_proxmox_gate_passed']
assert read(BASE/'v90-regression-results/completion-verification.json')['budget_closed'] and read(OUT/'technical-acceptance.json')['approved'] and a['acceptance_packet_ready']
for field in ['owning_docs_sha256','review_packet_sha256','user_files_sha256','additional_normative_docs_sha256']:
 for name,digest in b[field].items():assert sha(ROOT/name)==digest,name
assert sha(BASE/'v92-technical-acceptance/acceptance-proposal.json')==b['acceptance_proposal_sha256']
assert sha(OUT/'technical-acceptance.json')==b['technical_acceptance_receipt_sha256'] and sha(OUT/'closeout-plan.json')==b['closeout_plan_sha256']
assert read(OUT/'technical-acceptance.json')['technical_acceptance_received'] and not a['accepted_closeout_delivery_verified']
assert run(['git','rev-parse','HEAD']).strip()==EXPECTED and run(['git','branch','--show-current']).strip()=='phase22/integration'
assert not run(['git','diff','--cached']) and set(run(['git','diff','--name-only']).splitlines())==set(b['owning_docs_sha256'])
assert run(['git','worktree','list','--porcelain'])==b['worktrees']
run(['git','diff','--check']);run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'])
for name,digest in read(BASE/'v88-literal-metadata-correction/local-checks.json')['candidate_engineering_files_sha256'].items():assert sha(ROOT/name)==digest,name
assert sha(BASE/'v68-invalidation-sampling/optimization-proposal.json')==b['pending_optimization_proposal_sha256'] and not (BASE/'v69-ts-literal-key-reuse').exists()
seal=read(BASE/'evidence-v107.json');assert sha(BASE/'evidence-v107.json')==b['evidence_seal']['index_sha256'] and sha(BASE/seal['archive'])==seal['sha256']==b['evidence_seal']['archive_sha256']
with tarfile.open(BASE/seal['archive']) as archive:
 assert len(archive.getmembers())==len(seal['files'])
 for row in seal['files']:
  assert sha(BASE/row['path'])==row['sha256'],row['path'];member=archive.getmember(row['path']);assert member.isfile() and member.size==row['bytes'] and hashlib.sha256(archive.extractfile(member).read()).hexdigest()==row['sha256']
current=pr();guard(current)
assert current['headRefOid']==EXPECTED and current['title']=='Phase 22: Proxmox limitation accepted; technical acceptance pending'
assert current['body']==(BASE/'v92-technical-acceptance/pr-body-delivery.md').read_text()
assert run(['gh','api','repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration','--jq','.commit.sha']).strip()==EXPECTED
save('pre-delivery-pr37.json',current)
selected=set(b['owning_docs_sha256'])|set(b['review_packet_sha256'])
extra=[BASE/'evidence-v107.json',BASE/'evidence-v107.tar.gz',OUT/'documentation-binding.json',OUT/'pre-delivery-pr37.json',*OUT.glob('*.py'),*BASE.glob('v93-documentation-binding.*')]
selected.update(str(path.relative_to(ROOT)) for path in extra)
assert not selected&set(b['user_files_sha256']) and all((ROOT/name).stat().st_size<100*1024*1024 for name in selected)
run(['git','add','-f','--',*sorted(selected)])
staged=set(run(['git','diff','--cached','--name-only']).splitlines());assert staged<=selected and not staged&set(b['user_files_sha256'])
assert not any(name.startswith(('src/','tests/','scripts/','schemas/','.github/')) for name in staged)
run(['git','diff','--cached','--check','--',*b['owning_docs_sha256']])
save('staged-delivery.json',{'sha256':{name:sha(ROOT/name) for name in sorted(staged)},'protected_user_files_not_staged':True,'approval_basis':'Protected user handoff authorizes integration commits and batched delivery to this exact existing OPEN DRAFT PR37; no merge/ready/release.'})
print(run(['git','commit','-m','Deliver explicitly accepted Phase22 closeout under revised scope [skip ci]']),flush=True)
head=run(['git','rev-parse','HEAD']).strip();save('delivery-commit.json',{'head':head,'parent':EXPECTED,'scanner':b['corrected_scanner'],'technical_acceptance_received':True})
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
# Verify the accepted receipt/plan/audit/seal are the actual remote commit objects.
remote_files={}
for path in [OUT/'technical-acceptance.json',OUT/'audit.json',OUT/'closeout-plan.json',BASE/'evidence-v107.json']:
 name=str(path.relative_to(ROOT));remote=json.loads(run(['gh','api','repos/BashaarJavaid/MCP-Sentinel/contents/'+name+'?ref='+head]))
 blob=run(['git','rev-parse',head+':'+name]).strip();assert remote['sha']==blob and remote['size']==path.stat().st_size
 if remote.get('encoding')=='base64':assert base64.b64decode(remote['content'])==path.read_bytes()
 remote_files[name]={'git_blob':blob,'sha256':sha(path),'bytes':path.stat().st_size,'remote_content_verified':remote.get('encoding')=='base64','remote_commit_object_verified':True}
plan=read(OUT/'closeout-plan.json');pending=set(plan['delivery_dependent_requirement_ids'])
assert len(pending)==9 and {r['id'] for r in a['requirements']+a['additional_scope_requirements'] if r['disposition']=='unresolved'}==pending
assert not any(r['disposition'].startswith('proposed') for r in a['requirements']+a['additional_scope_requirements'])
receipt={'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'head':head,'base':'phase22/description-poisoning','draft':True,'open':True,'title':TITLE,'body_sha256':sha(OUT/'pr-body-delivery.md'),'acceptance_proposal_sha256':b['acceptance_proposal_sha256'],'technical_acceptance_receipt_sha256':b['technical_acceptance_receipt_sha256'],'closeout_plan_sha256':b['closeout_plan_sha256'],'scanner':b['corrected_scanner'],'seal107_sha256':seal['sha256'],'readback_history_sha256':sha(OUT/'delivery-readback-history.json'),'documentation_binding_sha256':sha(OUT/'documentation-binding.json'),'remote_accepted_packet_files':remote_files,'protected_user_files_main_worktrees_preserved':True,'all_previous_seals_and_new_members_verified':True,'current_source_observations':6,'entire_ordered_pairs_equal':3,'new_observations':0,'paid_calls':0,'technical_acceptance_received':True,'phase22_technically_complete_under_accepted_scope':True,'accepted_closeout_delivery_verified':True,'phase22_complete':True,'effective_delivery_resolutions':[{'id':rid,'disposition':'passed','basis':'Explicit human technical acceptance plus actual accepted-closeout commit/push and exact remote head/base/draft/title/body/accepted receipt/audit/plan/seal verification completed.'} for rid in sorted(pending)],'provenance':'Honest supplemental actual delivery receipt outside its own seal/commit; no infinite self-receipt commits. All historical measurements remain at their actual sources. No merge/ready-state/release/outreach/Phase23.'}
save('delivery-verification.json',receipt)
final=copy.deepcopy(a)
for row in final['requirements']+final['additional_scope_requirements']:
 if row['id'] in pending:
  before=copy.deepcopy(row);row.update(previous_row=before,disposition='passed',assessment='Explicit human acceptance and actual accepted-closeout delivery verified at'+head+'. Exact remote branch/PR head/base/draft/title/body and accepted receipt/audit/plan/seal objects match. This closes the delivery requirement only; every original failed measurement remains failed.');row.setdefault('evidence',[]).append(str((OUT/'delivery-verification.json').relative_to(ROOT)))
  interp=final['current_requirement_interpretations'][row['id']];prev=copy.deepcopy(interp);interp.update(previous_interpretation=prev,current_disposition='passed',current_execution_interpretation=row['assessment'],evidence=row['evidence'])
final.update(recorded_at=datetime.now(timezone.utc).isoformat(),status='Phase22technically complete under explicitly accepted revised scope; actual accepted-closeout delivery verified. All493requirements accounted for:461passed,30explicitly accepted limitations,2existing user deferrals. No unresolved or proposed limitation rows remain.',technical_acceptance_received=True,phase22_technically_complete_under_accepted_scope=True,accepted_closeout_delivery_verified=True,phase22_complete=True,final_delivered_head=head,final_delivery_verification_sha256=sha(OUT/'delivery-verification.json'),sealed_predelivery_audit_sha256=sha(OUT/'audit.json'),supplemental_final_audit=True)
final['dispositions']=dict(collections.Counter(r['disposition'] for r in final['requirements']));final['additional_scope_dispositions']=dict(collections.Counter(r['disposition'] for r in final['additional_scope_requirements']))
counts=collections.Counter(r['disposition'] for r in final['requirements']+final['additional_scope_requirements']);assert counts=={'passed':461,'explicitly accepted limitation':30,'explicitly user-deferred':2},counts
assert len(final['current_requirement_interpretations'])==493 and not any(r['disposition']=='unresolved' for r in final['requirements']+final['additional_scope_requirements'])
final['final_dispositions']=dict(counts);save('final-audit.json',final)
summary=f"""# Phase 22 accepted closeout: verified

**Phase 22 is technically complete under the explicitly accepted revised scope, and accepted closeout delivery is verified.**

Delivered revision: `{head}` on existing OPEN DRAFT [PR #37](https://github.com/BashaarJavaid/MCP-Sentinel/pull/37), base `phase22/description-poisoning`.

The [explicit technical acceptance receipt](technical-acceptance.json), [actual delivery verification](delivery-verification.json), [final493-row audit](final-audit.json), [full summary and preserved limits](summary.md) and [seal107](../evidence-v107.json) retain all evidence. Final dispositions:461passed,30explicitly accepted limitations,2existing user deferrals; zero unresolved/proposed rows. The final audit and verification are supplemental after delivery, preserving the sealed pre-delivery audit unchanged.

Measured sources remain5142a3f(current6Proxmoxobservations/3pairs,unsupported),884d376(V87affected111/48pairs) andcec0322(originalTaskwarrior/Proxmox and retainedV73/V75results). Taskwarrior narrow pass remains; all Proxmox misses/unsupported negatives remain failed with recovery deferred. All original failures and source qualifications remain.

Unchanged engineering:2,596tests/36skips locally and12hostedsuites,29normaljobs/docs,sixzero-callreplays,19runtimebindings. Accepted practical limits retain ordinaryFAF1800-secondcompletion unestablished andV68unapproved/unimplemented. Git312/1040incomplete/728deferred;paidbenchmark/pilotsdeferred;Phase21incomplete,Phase24/15unchanged. Historical spend$0.071799;zero new calls. No merge,ready-state,release,outreach,launch orPhase23.
"""
(OUT/'completion-summary.md').write_text(summary)
assert not run(['git','diff','HEAD','--name-only'])
print(json.dumps({'passed':True,'head':head,'technical_acceptance_received':True,'accepted_closeout_delivery_verified':True,'phase22_complete':True,'requirements':493,'final_dispositions':dict(counts),'final_audit_sha256':sha(OUT/'final-audit.json'),'paid_calls':0},indent=2),flush=True)
