"""Correct inherited audit status explicitly without changing sealed records or rows."""
import copy,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;base=out.parent;root=out.parents[3]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):
 with (out/n).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
a=read(out/'audit.json');p=read(out/'optimization-proposal.json');seal=read(base/'evidence-v96.json')
assert next(r['sha256'] for r in seal['files'] if r['path']=='v68-invalidation-sampling/audit.json')==sha(out/'audit.json')
assert p['status']=='prepared_not_approved_not_started' and p['bounds']['source_only_optimization_attempts']==1
assert not (base/'v69-ts-literal-key-reuse').exists()
changes={'optimization_approved':False,'optimization_synthetic_verified':False,'optimization_budget_closed':False,'current_optimization_attempts':0}
assert {k:a[k] for k in changes}=={'optimization_approved':True,'optimization_synthetic_verified':True,'optimization_budget_closed':True,'current_optimization_attempts':1}
status={k:copy.deepcopy(v) for k,v in a.items() if not k.startswith('historical_') and isinstance(v,(str,bool,int,float))}
status.update(changes)
assert not status['current_optimization_approved'] and not status['current_optimization_executed'] and status['optimization_attempts']==status['current_optimization_attempts']==0
save('audit-current-status.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'supersedes':'Optimization status fields only in sealed audit.json; all391requirements, dispositions, preserved prior rows and source-bound evidence remain byte-identical. This correction is supplemental after seal96.','audit_sha256':sha(out/'audit.json'),'proposal_sha256':sha(out/'optimization-proposal.json'),'inherited_fields_before':{k:a[k] for k in changes},'effective_current_status':status,'current_optimization_budget':'Prepared maximum1, unapproved/unopened, zero attempts; no optimization budget is granted. Existing v66 source-only and all native/profile budgets remain closed.','historical_optimization_binding':'The retained v66 accumulator revision was approved, engineering-verified and consumed once. Its status persists in historical_v66_status_fields/historical_v67_status_fields and the full earlier audit. It is not the pending v68 literal serialization proposal.','other_source_bound_fields':'source_recovery_approved, prospective_contract_revision_approved and candidate_retained_in_product refer to the unchanged v66 product at4145d35; no new contract revision is approved.','failure_and_correction':'Final review found copied generic optimization approval/verification/closed flags and current_optimization_attempts=1 from v66. Current proposal and current_optimization_approved/executed were already false, and the summary correctly said unapproved/unimplemented. Earlier final structural checks did not catch the inconsistent inherited metadata. This explicit override corrects it; no attempt or permission was consumed.','requirements':391,'rows_changed':0,'technical_acceptance_received':False,'phase22_complete':False,'paid_calls':0})
body=out/'pr-body-delivery.md'
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v68-invalidation-sampling/'
body.write_text(body.read_text()+f'\n[Current audit status correction]({url}audit-current-status.json) explicitly overrides inherited v66 optimization metadata: the new proposal is unapproved, unverified, unopened and has zero attempts. All391sealed audit rows remain unchanged. The stale inherited fields and missed metadata check are preserved in the correction.\n')
binding=read(out/'documentation-binding.json');save('documentation-binding-before-audit-correction.json',binding)
binding['review_packet_sha256'][str((out/'pr-body-delivery.md').relative_to(root))]=sha(body)
for n in ['audit-current-status.json','documentation-binding-before-audit-correction.json','supplement-audit-status.py']:
 binding['review_packet_sha256'][str((out/n).relative_to(root))]=sha(out/n)
binding['audit_current_status_sha256']=sha(out/'audit-current-status.json')
binding['qualification']+=' Supplemental audit-current-status.json explicitly supersedes four inherited optimization metadata fields; no sealed row or record was rewritten. The original pre-correction documentation binding is preserved.'
(out/'documentation-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
print('Corrected inherited current optimization metadata: unapproved, unverified, unopened, zero attempts; all391sealed rows unchanged.')
