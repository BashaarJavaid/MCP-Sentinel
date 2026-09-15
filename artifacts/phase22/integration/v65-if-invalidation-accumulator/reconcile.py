"""Retain every prior row and the strict-equivalence failure without accepting it."""
import copy,hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];OLD=BASE/'v64-shared-discovery-sampling'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
 with (OUT/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
a=read(OUT/'assessment.json');old=read(OLD/'audit.json');assert a['source_restored_exactly'] and a['budget_closed']
rows=copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
 if row['id'] in {'V64-DELIVERY','V64-OPT-DECISION'}:
  row['previous_row']=copy.deepcopy(row);row.update(disposition='passed',evidence=[str((OLD/'delivery-verification.json' if row['id']=='V64-DELIVERY' else OUT/'authorization.json').relative_to(ROOT))],assessment='Actual0f36867 draft delivery verified.' if row['id']=='V64-DELIVERY' else 'User approved the exact one-use strict-equivalence attempt. Its later adversarial failure remains failed; no revised contract or technical acceptance is inferred.')
new=[('AUTH','Bind exact source-only approval, protected baselines and stopped owned work','passed',['authorization.json','optimization-consumed.json','owned-initial.json']),('EQUIVALENCE','Preserve complete state and required adversarial alias/shrinking behavior under the original strict contract','unresolved',['equivalence.json','candidate.patch','candidate-typescript-path-flow.py']),('ASSESSMENT','Assess ordinary passes, both failed controls and helper correction with honest source reachability limits','passed',['assessment.json','../v65-equivalence.json','../v65-equivalence-corrected.json']),('RESTORATION','Close the one failed attempt and restore exact tested1948bf9 product bytes','passed',['restoration.json','optimization-budget-closed.json','compatible-reuse.json']),('REVISION-PREPARATION','Prepare an explicit prospective private-interpreter mutation contract revision with no implementation','passed',['optimization-proposal.json']),('REVISION-DECISION','Obtain explicit revised-contract approval before any new source-only attempt or negative-control reclassification','unresolved',['optimization-proposal.json']),('DELIVERY','Seal failed attempt, complete audit and verify concrete next decision on the existing draft','unresolved',[])]
for key,requirement,disposition,evidence in new:rows.append({'id':'V65-'+key,'requirement':requirement,'disposition':disposition,'evidence':[str((OUT/n).resolve().relative_to(ROOT)) for n in evidence],'assessment':'256ordinary full-state comparisons and avoided work pass; captured-arm alias and shrinking-arm controls fail the explicitly approved strict prerequisite. Error/interruption controls agree. Real-target reachability is unestablished. One attempt closed, exact1948bf9 restored; a prospective domain revision is unapproved. No failure or human technical acceptance is inferred.'})
assert len(rows)==276 and len(old['requirements'])==89
for before,after in zip(old['additional_scope_requirements'],rows):assert before==after or after.get('previous_row')==before
current=copy.deepcopy(old);current['historical_v64_status_fields']={k:copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements'} and not k.startswith('historical_')}
current.update(recorded_at=datetime.now(timezone.utc).isoformat(),additional_scope_requirements=rows,additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),prior_audit={'path':str((OLD/'audit.json').relative_to(ROOT)),'sha256':sha(OLD/'audit.json')},optimization_approved=True,optimization_attempts=1,optimization_synthetic_verified=False,optimization_budget_closed=True,optimization_remaining=0,current_optimization_approved=False,current_optimization_attempts=0,candidate_retained_in_product=False,source_restored_exactly=True,prospective_contract_revision_approved=False,acceptance_packet_ready=False,technical_acceptance_received=False,phase22_complete=False,status='Approved If accumulator attempt failed two explicitly required adversarial controls despite256ordinary passes. One attempt closed; exact1948bf9 restored. Prospective mutation-domain revision and one new source-only attempt are prepared,unapproved and unimplemented.')
current['current_optimization_accounting']={'attempted':1,'passed':0,'failed':1,'remaining':0,'closed':True,'new_prospective_attempt_approved':False,'new_prospective_attempted':0}
current['current_budget_interpretation']='All native/profile budgets stay closed and unchanged. This one source-only attempt is also closed. The new explicit mutation-domain revision and one new source-only attempt require separate approval; no negative control or historical failed gate is reclassified now.'
for row in old['requirements']+old['additional_scope_requirements']:
 entry=copy.deepcopy(old.get('current_requirement_interpretations',{}).get(row['id'],{}));entry.update(requirement=row['requirement'],historical_disposition=row['disposition'],current_execution_interpretation='Current product is restored exactly to1948bf9 and retains its actual engineering. The new If accumulator strict-equivalence attempt failed two instrumented adversarial controls and is closed. Real-target reachability remains unestablished. No native/profile observation or technical acceptance was added; all previous failures and source-bound evidence remain.',current_execution_evidence={'assessment_sha256':sha(OUT/'assessment.json'),'restoration_sha256':sha(OUT/'restoration.json'),'compatibility_sha256':sha(OUT/'compatible-reuse.json')});current['current_requirement_interpretations'][row['id']]=entry
assert len(current['current_requirement_interpretations'])==358
assert current['additional_scope_dispositions']=={'passed':252,'unresolved':18,'proposed documented limitation awaiting decision':6}
current['current_evidence']={n:sha(OUT/n) for n in ['assessment.json','equivalence.json','restoration.json','optimization-budget-closed.json','optimization-proposal.json','compatible-reuse.json']}
write('audit.json',current);write('prior-row-preservation.json',{'prior_audit_sha256':sha(OLD/'audit.json'),'retained_prior_rows':358,'total_rows':365,'updated_rows':['V64-DELIVERY','V64-OPT-DECISION'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
status='''## Current v65 invalidation attempt: strict-equivalence failure retained

The approved If invalidation-accumulator attempt passes **256 ordinary full-state
comparisons**, then fails the required synthetic captured-arm alias and shrinking-arm
controls. Error/interruption states agree. Shipped source has no matching removal or
arm-set export; real-target reachability remains unestablished. The strict proposal
still required these controls. **One failed attempt closed; exact tested `1948bf9`
source restored.** The candidate and the initial helper-deadline correction remain.

`v65-if-invalidation-accumulator/optimization-proposal.json` prepares an **unapproved
explicit mutation-domain revision and one new source-only attempt**. Every shipped
writer/reader/subclass must first prove monotone private sets with no escaping arm
alias. Only the two named injected callbacks would become negative controls outside
that prospective domain after explicit approval; their original failures stay failed.
No current reclassification, implementation, corpus/profile/retry, paid call,
resource change or timeout revision is authorized. Full engineering remains required
if a later explicitly approved attempt passes its complete prerequisites.

All **365 requirements (89 original + 276 added)** and every earlier failed gate
remain. Restored `1948bf9` retains **2,418 tests / 36 skips** locally and in all 12
hosted suites, 29 normal CI jobs and docs passed; combined coverage 90.08%,
branch-only 85.92%. Six zero-call production replays and approved runtime bindings
remain compatible. This adds failed-attempt/restoration and docs/package checks,
not a new candidate engineering or hosted code pass.

**Phase 22 remains incomplete**, pending current-source gates, explicit human
technical acceptance and accepted closeout. Git stays 312/1,040 incomplete;
paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged.
No merge, ready-state change, release, outreach or Phase 23 is authorized.

'''
heading='## Current v64 parent-and-worker profile: source-only decision pending';docs=list(read(OLD/'documentation-binding.json')['owning_docs_sha256'])
for name in docs:
 path=ROOT/name;text=path.read_text();assert text.count(heading)==1,name;path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{n:sha(ROOT/n) for n in docs}});(OUT/'status.md').write_text(status)
print('Retained358prior rows;365total. Failed strict contract remains unresolved; revised contract unapproved.')
