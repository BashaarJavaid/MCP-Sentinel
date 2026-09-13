"""Retain every prior requirement and the actual stopped regression outcome."""
import copy
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = OUT.parents[3]
OLD = BASE/'v57-credential-merge'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

a = read(OUT/'assessment.json')
assert a['budget'] == {'planned':205,'attempted':1,'completed':0,'incomplete':1,'unstarted_closed':204,'remaining':0,'closed':True}
assert read(BASE/'v58-diagnostic-boundary.json')['exit_code'] == 0
old = read(OLD/'audit.json')
rows = copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
    if row['id'] in {'V57-DELIVERY', 'V57-REGRESSION-DECISION'}:
        row['previous_row'] = copy.deepcopy(row)
        name = 'delivery-verification.json' if row['id']=='V57-DELIVERY' else 'evaluation-authorization.json'
        row.update(disposition='passed', evidence=[str((OLD/name).relative_to(ROOT))], assessment='Verified 53d3045 draft delivery or the subsequent exact approved decision. This passes delivery/authorization only; it does not accept the later timeout or Phase 22.')
new = [
    ('V58-AUTH','Bind the exact 205-observation approval to proposal, launcher, scanner and bounds','passed',['../v57-credential-merge/evaluation-authorization.json','../v57-credential-merge/execution-preflight.json']),
    ('V58-STOP','Preserve timeout/incomplete output and close 204 unstarted observations with verified cleanup','passed',['validation.json','assessment.json','owned-work.json']),
    ('V58-ASSESSMENT','Assess every retained output without inventing report contents or current-source compatibility','passed',['assessment.json']),
    ('V58-DIAGNOSTIC-PREPARATION','Prepare one separately gated sampled input with synthetic and missing-approval checks, without execution','passed',['diagnostic-proposal.json','sampler-selfcheck/packet.json','../v58-diagnostic-boundary.json']),
    ('V58-REGRESSION-GATE','Complete current-source four-repository and affected compatibility gates or obtain explicit disposition of this actual failure','unresolved',['assessment.json']),
    ('V58-DELIVERY','Seal the stopped execution and complete audit, then verify delivery of the concrete next decision to the existing draft','unresolved',[]),
]
for identity, requirement, disposition, evidence in new:
    rows.append({'id':identity,'requirement':requirement,'disposition':disposition,'evidence':[str((OUT/n).resolve().relative_to(ROOT)) for n in evidence],'assessment':'One incomplete timed-out input, zero reports, 204 unstarted closed and zero remaining. No current-source discrimination, compatibility, speedup or human acceptance is established.'})
assert len(old['requirements']) == 89 and len(old['additional_scope_requirements']) == 219
assert len(rows) == 225 and len({r['id'] for r in old['requirements']+rows}) == 314
audit = copy.deepcopy(old)
audit['historical_v57_status_fields'] = {k:copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements'} and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(),additional_scope_requirements=rows,additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),prior_audit={'path':str((OLD/'audit.json').relative_to(ROOT)),'sha256':sha(OLD/'audit.json')},regression_approved=True,regression_executed=True,current_regression_approved=True,current_regression_executed=True,current_source_corpus_observations=1,current_source_completed_observations=0,current_source_incomplete_observations=1,unstarted_closed=204,remaining=0,budget_closed=True,execution_gate_passed=False,diagnostic_prepared=True,diagnostic_approved=False,diagnostic_executed=False,current_diagnostic_prepared=True,current_diagnostic_approved=False,current_diagnostic_executed=False,diagnostic_attempts=0,diagnostic_completed_inputs=0,diagnostic_budget_closed=False,diagnostic_remaining=0,valid_current_source_profiles=0,current_budget_interpretation='The approved 205-observation sequence stopped on the first timeout: one incomplete, 204 unstarted closed, zero remaining. Earlier joint source-only correction remains verified and closed. One new sampled input is proposed, unapproved and unexecuted; no old numerical budget is reused.',new_paid_calls=0,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,status='Approved dc73715 regression timed out on its first FAF input. One incomplete, no report, 204 unstarted closed. Current-source detection/compatibility remain unresolved. One 300-second sampled input is prepared, unapproved and unexecuted; all earlier failures retain their source bindings.')
assert audit['additional_scope_dispositions']=={'passed':205,'unresolved':14,'proposed documented limitation awaiting decision':6}
audit['current_evidence']={n:sha(OUT/n) for n in ['assessment.json','validation.json','diagnostic-proposal.json','sampler-selfcheck/packet.json','owned-work.json']}
for identity in ['R66','R88']:
    audit['current_requirement_interpretations'][identity]='Original 24 fresh observations and all four failed repository gates remain at 2e0efb2. The exposed dc73715 regression timed out on the first FAF input with no report and 204 unstarted closed. Current-source detection/compatibility and human acceptance remain unestablished. No historical failure is relabeled or accepted.'
for prior,current in zip(old['requirements']+old['additional_scope_requirements'],audit['requirements']+rows):
    assert prior==current or current.get('previous_row')==prior
write('audit.json',audit)
write('prior-row-preservation.json',{'prior_audit_sha256':sha(OLD/'audit.json'),'retained_prior_rows':308,'total_rows':314,'updated_rows':['V57-DELIVERY','V57-REGRESSION-DECISION'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
summary=f'''# Credential-corrected scanner still times out; regression budget closed

**The approved 205-observation sequence at `dc73715` stopped on its first FAF vulnerable input: one incomplete attempt, no completed report, 204 unstarted observations closed and zero remaining. Phase 22 remains incomplete.**

The user's exact `approved` decision is retained in [authorization](../v57-credential-merge/evaluation-authorization.json), bound to proposal `987379ede197b27da159fc0ef11eca6782c0535a66bf8fba061ffe1786e5c03a` delivered at `53d3045`. The frozen scanner is `{a['scanner']['revision']}`, source `{a['scanner']['source_sha256']}`. Input, source archive, original condition, label and effective configuration remain unchanged.

[Validation](validation.json) and [assessment](assessment.json) retain **{a['whole_seconds']:.9f} seconds** whole-input time and cleanup by **{a['whole_including_cleanup_seconds']:.9f} seconds**, within the 15-second allowance, without a remaining process-group kill. The outer sequence took **{a['sequence_seconds']:.9f} seconds**, exited 1 and closed its budget. The harness's narrower interval was **{a['harness_wall_duration_ms']} ms**. Its `incomplete` outcome has `reason: null`: the supervisor's SIGTERM handler raises `SystemExit`, bypassing `except Exception` while the `finally` writer preserves the incomplete record. This is not a completed native exit-3 result.

**No JSON/SARIF report exists. Findings, warnings, surfaces, named detection and fixed/control discrimination are unknown, not zero.** No batch or ordered repeat completed. All other 23 four-repository observations and all 181 Python/TypeScript compatibility observations were unstarted and closed. Resource CPU totals sum concurrent child workers and neither replace wall time nor identify a hotspot. No retry, profile, comparator, target execution or paid call occurred.

The approved equal-marker credential correction and canonical unknown bypass retain their exact engineering results: 4,050 correction cases with 552 intentional marker deltas and 552 derived cache-input deltas, 2,430 complete bypass comparisons against the preserved correction-only reference, two cache-eviction cases and seven unchanged ordered synthetic credential patterns. The deliberate semantic correction is not claimed to preserve every original `a36f696` state. Both older singleton failures remain failed at their actual sources. This new timeout does not establish a speedup or slowdown; it establishes that the candidate did not finish this input within 300 seconds.

[The next diagnostic proposal](diagnostic-proposal.json), SHA-256 `{sha(OUT/'diagnostic-proposal.json')}`, is **unapproved and unexecuted**. It proposes **one sampled rules-only FAF input** at the same frozen scanner, with a **120-second target, 300-second whole maximum and 15-second cleanup allowance**. It reuses the 100Hz CPU-timer sampler per worker, atomic partial snapshots every 15 seconds and a maximum 1,024 stack frames. Zero optimization attempts, uninstrumented observations, retries, comparators, new repositories, resource changes, target executions or paid calls are included.

The latest valid v54 profile measures `a36f696` before the two current changes and cannot establish residual costs at `dc73715`. The proposed sampler preserves the rule set, worker layout and scanner methods. It verifies actual worker/flow paths and the entire source/harness/revision identity before timer setup or target snapshot access. Parent preflight checks an isolated worker before token consumption; every real worker must retain a matching receipt. [Synthetic checks](sampler-selfcheck/packet.json) preserve six Value vectors and scanner methods, validate frame references and restore signal/timer state. A stale `a36f696` root fails before timer or target access; missing approval fails before output or token creation. These checks execute no corpus input.

The sampled input would consume its entire one-use budget even on timeout or interruption. Partial snapshots may lack final/restored-state receipts. Signal delivery, native code, GIL behavior and sampler/snapshot overhead bias attribution; overlapping shares are not additive or guaranteed removable costs. If a report completes, both schemas and its entire ordered comparison with the original `2e0efb2` reference must be validated after only the established 11 volatile exclusions, followed by source assessment of every delta. No optimization or further run follows automatically.

All **four native failures** remain distinct: `17b4784` at 300.002159 seconds, `6e4fd67` at 300.004111, `a36f696` at 300.000481 and this `dc73715` attempt, each with one incomplete and 204 unstarted closed. The partial profiles retain 86,659 / 79,307 / 78,769 samples at their actual first three scanner sources. The invalid v50 stale-root attempt remains unusable and V49-DIAGNOSTIC-PREPARATION unresolved. Both singleton failures and the six older historical closure proposals remain unaccepted.

The original four-repository fresh evaluation remains **24 completed observations, 12 equal pairs and all four gates failed at `2e0efb2`**: FAF actual read unsupported; no-bash one vulnerable hit and two fixed/control false alerts per batch; Lightning actual client-get and Engram named manifest-write unresolved. Later source corrections and evaluations are exposed regression, not clean unseen-source discrimination.

Product, tests, workflows, schemas and lock remain engineering-tested `dc73715`: **2,399 tests / 36 skips locally and in all 12 hosted suites**, **29 normal CI jobs** and docs passed in [34779741236](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34779741236) / [34779741226](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34779741226). Local combined statement/branch coverage is **89.98%**, branch-only **85.86%**. Actual hosted merge `22ad9ab968d838677540932c83ff46b04e23e588` has the complete candidate tree. All 302 engineering files, package source bytes, six identical zero-call production request replays and approved Docker/Git runtime bindings remain retained. This continuation adds outcome, diagnostic-preparation and final docs/package checks, not a new hosted code pass. Prior file/worktree/evidence restoration and selective Docker cleanup remain preserved.

The [audit](audit.json) retains **all 308 prior requirements** and adds six: **314 total, 89 original + 225 added**. Original rows remain 84 passed, two user-deferred, two proposed limitations and one unresolved human acceptance. Added rows have 205 passed, six historical closure proposals and 14 unresolved before supplemental delivery readback. No failed gate or human decision is silently waived.

TS 94 at `2e0efb2`, Python 87 at `8c62567`, and whole 25 development reuse plus 45+45 Linux at `1f3f72f` retain actual passes and the Meta operator erratum. Memory-keeper's original fresh false alerts, DDG's initially unsupported fixed send and wrong TypeScript label despite actual Python configuration, and Lighthouse's original misses remain unchanged. Language subsets are never pooled into new whole batches. The original held-out result stays 10 completed, 10 unsupported and five incomplete, with zero hits among four completed vulnerable inputs out of ten vulnerable inputs total. Same-agent curation/review is not independent human validation, training-data novelty, broad accuracy or runtime safety proof.

Git stays **312/1,040 incomplete**, 728 deferred. Paid benchmark/pilots remain deferred, Phase 21 incomplete and Phase 24/15 unchanged. Historical two paid calls cost $0.071799; this continuation adds zero. Current-source gates, explicit human technical acceptance and accepted closeout remain pending. No merge, ready-state change, release, outreach or Phase 23 is authorized.
'''
with (OUT/'summary.md').open('x') as stream:stream.write(summary)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
body=summary.replace('(../v57-credential-merge/','('+url+'v57-credential-merge/')
for name in ['validation.json','assessment.json','diagnostic-proposal.json','sampler-selfcheck/packet.json','audit.json']:
    body=body.replace('('+name+')','('+url+'v58-credential-regression/'+name+')')
with (OUT/'pr-body.md').open('x') as stream:stream.write(body)
status=f'''## Current v58 credential regression timeout: budget closed

The approved 205-observation sequence at frozen **`dc73715`** stopped on the first
FAF vulnerable input at **{a['whole_seconds']:.6f} seconds** whole-input time.
**One incomplete, zero reports, 204 unstarted closed, zero remaining**; cleanup
passed. Detection, findings, fixed/control discrimination and ordered repeats are
unknown. Current-source four-repository and prior-language gates remain unresolved.
No retry, profile, comparator, target execution or paid call occurred.

`v58-credential-regression/diagnostic-proposal.json` prepares **one sampled FAF
input**, **unapproved and unexecuted**, with a 300-second maximum and 15-second
cleanup allowance. The existing sampler and worker layout remain unchanged;
actual worker/flow/source identities are verified before timer or target access.
Synthetic identity/timer checks and the missing-approval boundary pass.
Earlier `a36f696` samples do not establish residual costs at the corrected source.
No optimization, resource/deadline change or further measurement is authorized.

All **314 requirements (89 original + 225 added)** remain. All four native
timeouts, three partial profiles, invalid stale-root preparation, both singleton
failures and six unaccepted historical closure proposals retain their actual
source bindings. Product and tests remain engineering-tested `dc73715`: **2,399
tests / 36 skips** locally and in all 12 hosted suites, all 29 normal CI jobs and
docs passed. Combined coverage is 89.98%, branch-only 85.86%; six zero-call
production replays and approved runtime/image bindings remain compatible.

**Phase 22 remains incomplete**, pending current-source gates, explicit human
technical acceptance and accepted closeout. Git stays 312/1,040 incomplete;
paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged.
No merge, ready-state change, release, outreach or Phase 23 is authorized.

'''
heading='## Current v57 joint correction: engineering passed, regression pending'
docs=list(read(OLD/'documentation-binding.json')['owning_docs_sha256'])
assert len(docs)==16
for name in docs:
    path=ROOT/name
    text=path.read_text()
    assert text.count(heading)==1,name
    path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{n:sha(ROOT/n) for n in docs}})
print('Preserved 308 prior rows, 314 total; reconciled 16 docs; one diagnostic remains unapproved.')
