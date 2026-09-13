"""Preserve the entire audit and both failed singleton attempts."""
import copy,hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=Path.cwd();OLD=BASE/'v55-singleton-combine'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
old=read(OLD/'audit.json');rows=copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
    if row['id'] in {'V55-DELIVERY','V55-NARROW-DECISION'}:
        row['previous_row']=copy.deepcopy(row)
        evidence=OLD/'delivery-verification.json' if row['id']=='V55-DELIVERY' else OUT/'authorization.json'
        row.update(disposition='passed',evidence=[str(evidence.relative_to(ROOT))],assessment='Verified8df485e delivery or subsequent exact canonical-unknown approval. No historical failure or Phase22 acceptance follows.')
new=[('V56-AUTH','Bind exact canonical-unknown source-only approval and preserve a36f696 baseline','passed',['authorization.json']),('V56-EQUIVALENCE','Preserve complete Value/environment/flow state, including LRU eviction and identity-sensitive credential markers','unresolved',['synthetic-validation.json','optimization-budget-closed.json']),('V56-ASSESSMENT','Assess both retained ordinary identity cases and the eviction counterexample with target-reachability limits','passed',['assessment.json','check-synthetic.py','assess-source.py']),('V56-RESTORATION','Close the failed attempt and preserve/revert the exact two-line candidate to tested source','passed',['candidate.patch','candidate-path-flow.py','assessment.json']),('V56-REVISION-PREPARATION','Prepare an explicit prospective equal-marker semantic correction plus canonical bypass with separate corrected-reference equivalence','passed',['optimization-proposal.json']),('V56-REVISION-DECISION','Obtain explicit revised-contract/joint-attempt approval before either new source edit','unresolved',['optimization-proposal.json']),('V56-DELIVERY','Verify final docs/package restoration, complete audit retention, seal and exact existing draft delivery','unresolved',[])]
for identity,requirement,disposition,evidence in new:rows.append({'id':identity,'requirement':requirement,'disposition':disposition,'evidence':[str((OUT/name).relative_to(ROOT)) for name in evidence],'assessment':'Canonical bypass failed synthetic cache-eviction environment equivalence; product restored and attempt closed. Real-target impact unestablished. Proposed equal-marker contract revision and bypass are unapproved; neither old failure is accepted or relabeled.'})
audit=copy.deepcopy(old);audit['historical_v55_status_fields']={key:copy.deepcopy(value) for key,value in old.items() if key not in {'requirements','additional_scope_requirements'} and not key.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(),additional_scope_requirements=rows,additional_scope_dispositions=dict(Counter(row['disposition'] for row in rows)),prior_audit={'path':str((OLD/'audit.json').relative_to(ROOT)),'sha256':sha(OLD/'audit.json')},current_optimization_prepared=True,current_optimization_approved=True,current_optimization_attempts=1,optimization_prepared=True,optimization_approved=True,optimization_attempts=1,optimization_synthetic_verified=False,optimization_budget_closed=True,optimization_remaining=0,candidate_retained_in_product=False,next_optimization_prepared=True,next_optimization_approved=False,next_optimization_attempts=0,prospective_contract_revision_prepared=True,prospective_contract_revision_approved=False,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,new_paid_calls=0,status='Canonical UNKNOWN_VALUE bypass fails synthetic environment equivalence after cache eviction; full flow fields agree, real-target impact unestablished. One attempt closed, product restored to tested a36f696. Equal-marker credential join contract revision plus canonical bypass is unapproved/unimplemented. Both prior singleton failures preserved.')
audit['current_evidence']={name:sha(OUT/name) for name in ['authorization.json','assessment.json','synthetic-validation.json','optimization-budget-closed.json','optimization-proposal.json','owned-work.json']}
assert len(old['requirements'])==89 and len(rows)==208
assert audit['additional_scope_dispositions']=={'passed':188,'unresolved':14,'proposed documented limitation awaiting decision':6},audit['additional_scope_dispositions']
for previous,current in zip(old['requirements']+old['additional_scope_requirements'],audit['requirements']+rows):assert previous==current or current.get('previous_row')==previous
save('audit.json',audit)
save('prior-row-preservation.json',{'retained_prior_rows':290,'total_rows':297,'prior_audit_sha256':sha(OLD/'audit.json'),'updated_rows':['V55-DELIVERY','V55-NARROW-DECISION'],'rows':{row['id']:hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest() for row in old['requirements']+old['additional_scope_requirements']}})
summary=(OUT/'summary.md').read_text();url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v56-canonical-unknown/'
for name in ['authorization.json','candidate.patch','synthetic-validation.json','assessment.json','optimization-budget-closed.json','optimization-proposal.json','audit.json']:summary=summary.replace('('+name+')','('+url+name+')')
with (OUT/'pr-body.md').open('x') as stream:stream.write(summary)
status='''## Current v56 canonical bypass: eviction failure retained

The approved canonical `UNKNOWN_VALUE` bypass passes the two retained ordinary
identity cases, then fails synthetic environment equivalence after LRU eviction.
Skipping an empty entry changes whether a tainted value remains interned; the
identity-only credential-marker join then returns different environments. Full
flow fields agree and inputs are unchanged. Real-target reachability/impact of
the adversarial contained-false marker remains unestablished. **One attempt
consumed, zero remaining; exact tested `a36f696` source restored.**

`v56-canonical-unknown/optimization-proposal.json` prepares an **unapproved
prospective contract revision**: equal immutable credential markers would join
consistently by identity or complete equality, followed by the canonical bypass.
The specified baseline marker delta must remain visible; bypass equivalence must
then hold against a correction-only reference with no exclusions. Neither edit
is implemented. No speedup or 300-second completion is promised. No corpus,
profile, retry, target execution or paid call is included.

All prior native/profile/fresh failures and both singleton failures remain
source-bound and closed. The audit retains **297 rows (89 original + 208 added)**,
including six unaccepted historical closure proposals. Restored `a36f696`
retains 2,386 tests / 36 skips locally and in all 12 hosted suites, 29 normal CI
jobs and docs passed; combined coverage 89.98%, branch-only 85.85%. This is no
new hosted code pass. **Phase 22 remains incomplete.** Git stays 312/1,040
incomplete; paid benchmark/pilots deferred, Phase 21 incomplete, Phase 24/15
unchanged. No merge, ready-state change, release, outreach or Phase 23.

'''
heading='## Current v55 singleton attempt: equivalence failure retained'
docs=list(read(OLD/'documentation-binding.json')['owning_docs_sha256'])
for name in docs:
    path=ROOT/name;text=path.read_text();assert text.count(heading)==1,name
    path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
save('owning-docs.json',{'sha256':{name:sha(ROOT/name) for name in docs}})
print('Preserved290prior rows;297total; two failed singleton attempts retained, new contract proposal unapproved.')
