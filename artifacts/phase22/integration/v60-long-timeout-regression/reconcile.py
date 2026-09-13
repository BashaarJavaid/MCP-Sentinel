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
OLD = BASE/'v59-timeout-policy'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

a = read(OUT/'assessment.json')
assert a['budget'] == {'planned':205,'attempted':1,'completed':0,'incomplete':1,'unstarted_closed':204,'remaining':0,'closed':True}
assert read(BASE/'v60-diagnostic-boundary.json')['exit_code'] == 0
old = read(OLD/'audit.json')
rows = copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
    if row['id'] in {'V59-DELIVERY', 'V59-REGRESSION-DECISION'}:
        row['previous_row'] = copy.deepcopy(row)
        name = 'delivery-verification.json' if row['id']=='V59-DELIVERY' else 'evaluation-authorization.json'
        row.update(disposition='passed', evidence=[str((OLD/name).relative_to(ROOT))], assessment='Verified 24ff6a0 draft delivery or the subsequent exact approved decision. This passes delivery/authorization only; it does not accept the later timeout or Phase 22.')
new = [
    ('V60-AUTH','Bind the exact 205-observation approval to proposal, launcher, scanner and bounds','passed',['../v59-timeout-policy/evaluation-authorization.json','../v59-timeout-policy/execution-preflight.json']),
    ('V60-VALIDATION','Preserve timeout/incomplete output and close 204 unstarted observations with verified cleanup','passed',['validation.json','assessment.json','owned-work.json','compatible-reuse.json']),
    ('V60-ASSESSMENT','Assess every retained output without inventing report contents or current-source compatibility','passed',['assessment.json']),
    ('V60-DIAGNOSTIC-PREPARATION','Prepare one separately gated sampled input with synthetic and missing-approval checks, without execution','passed',['diagnostic-proposal.json','sampler-selfcheck/packet.json','../v60-diagnostic-boundary.json']),
    ('V60-REGRESSION-GATE','Complete current-source four-repository and affected compatibility gates or obtain explicit disposition of this actual failure','unresolved',['assessment.json']),
    ('V60-DELIVERY','Seal the stopped execution and complete audit, then verify delivery of the concrete next decision to the existing draft','unresolved',[]),
]
for identity, requirement, disposition, evidence in new:
    rows.append({'id':identity,'requirement':requirement,'disposition':disposition,'evidence':[str((OUT/n).resolve().relative_to(ROOT)) for n in evidence],'assessment':'One incomplete timed-out input, zero reports, 204 unstarted closed and zero remaining. No current-source discrimination, compatibility, speedup or human acceptance is established.'})
assert len(old['requirements']) == 89 and len(old['additional_scope_requirements']) == 234
assert len(rows) == 240 and len({r['id'] for r in old['requirements']+rows}) == 329
audit = copy.deepcopy(old)
audit['historical_v59_status_fields'] = {k:copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements'} and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(),additional_scope_requirements=rows,additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),prior_audit={'path':str((OLD/'audit.json').relative_to(ROOT)),'sha256':sha(OLD/'audit.json')},regression_approved=True,regression_executed=True,current_regression_approved=True,current_regression_executed=True,current_source_corpus_observations=1,current_source_completed_observations=0,current_source_incomplete_observations=1,unstarted_closed=204,remaining=0,budget_closed=True,execution_gate_passed=False,diagnostic_prepared=True,diagnostic_approved=False,diagnostic_executed=False,current_diagnostic_prepared=True,current_diagnostic_approved=False,current_diagnostic_executed=False,diagnostic_attempts=0,diagnostic_completed_inputs=0,diagnostic_budget_closed=False,diagnostic_remaining=0,valid_current_source_profiles=0,current_budget_interpretation='The approved 205-observation sequence stopped on the first timeout: one incomplete, 204 unstarted closed, zero remaining. Earlier joint source-only correction remains verified and closed. One new sampled input is proposed, unapproved and unexecuted; no old numerical budget is reused.',new_paid_calls=0,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,status='Approved 7bf4c6e regression timed out on its first FAF input. One incomplete, no report, 204 unstarted closed. Current-source detection/compatibility remain unresolved. One 1800-second sampled input is prepared, unapproved and unexecuted; all earlier failures retain their source bindings.')
assert audit['additional_scope_dispositions']=={'passed':219,'unresolved':15,'proposed documented limitation awaiting decision':6}
audit['current_evidence']={n:sha(OUT/n) for n in ['assessment.json','validation.json','diagnostic-proposal.json','sampler-selfcheck/packet.json','owned-work.json']}
for identity in ['R66','R88']:
    audit['current_requirement_interpretations'][identity]='Original 24 fresh observations and all four failed repository gates remain at 2e0efb2. The exposed 7bf4c6e regression timed out on the first FAF input with no report and 204 unstarted closed. Current-source detection/compatibility and human acceptance remain unestablished. No historical failure is relabeled or accepted.'
for prior,current in zip(old['requirements']+old['additional_scope_requirements'],audit['requirements']+rows):
    assert prior==current or current.get('previous_row')==prior
audit['current_timeout_policy_seconds'] = 1800
audit['timeout_policy_retained'] = True
write('audit.json',audit)
write('prior-row-preservation.json',{'prior_audit_sha256':sha(OLD/'audit.json'),'retained_prior_rows':323,'total_rows':329,'updated_rows':['V59-DELIVERY','V59-REGRESSION-DECISION'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})

audit['current_timeout_policy_seconds'] = 1800
audit['timeout_policy_retained'] = True

summary=f'''# Thirty-minute regression timed out; budget closed

**The approved 205-observation sequence at `7bf4c6e` stopped on the first FAF vulnerable input after 30 minutes without a report. One input is incomplete, 204 unstarted observations are closed, and zero budget remains. Phase 22 remains incomplete.**

The exact `approved` decision is retained in [authorization](../v59-timeout-policy/evaluation-authorization.json), bound to proposal `0a07544a9db0396780d686af952ab2057cc78f8df2f6897128c714ac4126d164` delivered at `24ff6a0`. Frozen scanner: `{a['scanner']['revision']}`; source SHA-256: `{a['scanner']['source_sha256']}`. The original source archive, condition, label, effective configuration and observation order remain unchanged.

[Validation](validation.json) and [assessment](assessment.json) retain **{a['whole_seconds']:.9f} seconds** whole-input time, **{a['whole_including_cleanup_seconds']:.9f} seconds** including cleanup and **{a['sequence_seconds']:.9f} seconds** for the outer sequence. Cleanup passed within its separate 15-second allowance, without a remaining process-group kill. The harness interval was {a['harness_wall_duration_ms']} ms. SIGTERM raises `SystemExit`, bypassing `except Exception`; the finally writer preserves an incomplete record with null reason. The outer evaluator separately records its failed completion assertion and exits 1.

**No JSON/SARIF report exists. Findings, warnings, surfaces, detection and fixed/control discrimination are unknown.** No batch or ordered repeat completed. The other 23 four-source observations and all 181 language regression observations were unstarted and closed. CPU totals sum concurrent workers; they do not identify a hotspot. No retry, profile, comparator, target execution, new repository or paid call occurred.

The user-selected **1800-second shared policy remains in place**. The policy is the only scanner change from `dc73715`; its source proof and tests retain the shared deadline and shorter caller limits. Both five-minute and thirty-minute attempts failed without reports. Different stopping ceilings do not establish speedup or slowdown. Extending the deadline alone did not establish completion.

[The next diagnostic proposal](diagnostic-proposal.json), SHA-256 `{sha(OUT/'diagnostic-proposal.json')}`, is **unapproved and unexecuted**: one sampled rules-only FAF input at the same frozen `7bf4c6e`, **1800-second whole-input maximum plus 15-second cleanup**, with 120 seconds as informational target. The existing 100Hz CPU sampler per worker, atomic 15-second partial snapshots, maximum 1024 frames, rule set and worker layout are retained. Zero optimization attempts, uninstrumented observations, retries, comparators, new repositories, resource changes, target executions or paid calls are included. This observes costs over the same 30-minute window that failed; it does not assume the old profile still describes current execution.

Actual worker/flow/source/harness/revision identities are checked before timers or target snapshot access. Parent preflight validates an isolated worker before consuming the separate one-use token. [Synthetic checks](sampler-selfcheck/packet.json) preserve six Value vectors and scanner methods, validate frame references and restore signal/timer state. The old `dc73715` root fails before timer or target access; missing approval fails before output or token creation. These checks execute no corpus input. The earlier v58 five-minute profile proposal remains unapproved and unexecuted, superseded only as the next proposed step.

The one sampled attempt consumes its budget even on timeout or interruption. Partial snapshots may lack final/restored-state receipts. Signal delivery, native code, GIL behavior and sampling/snapshot overhead bias attribution; overlapping stack shares are not additive or guaranteed removable cost. If a report completes, validate JSON/SARIF and its entire ordered comparison against the original `2e0efb2` reference after only the established 11 volatile exclusions, then source-assess every delta. No optimization or further run follows automatically. The prepared occurrence-inventory helper was unused because no report exists; it supplies no measured diagnostic count.

The latest valid v54 profile measures `a36f696` before the approved equal-marker credential correction and canonical unknown bypass. Their retained source-only results remain 4,050 correction cases (552 intentional marker deltas and 552 derived cache-input deltas), 2,430 complete bypass comparisons against the correction-only reference, two cache-eviction cases and seven unchanged ordered synthetic credential patterns. Both earlier singleton failures remain failed. No equivalence to every original `a36f696` state is claimed.

All five native timeout attempts remain distinct: `17b4784` at 300.002159 seconds, `6e4fd67` at 300.004111, `a36f696` at 300.000481, `dc73715` at 300.005621 and the present `7bf4c6e` at {a['whole_seconds']:.6f}; each has one incomplete and 204 unstarted closed. The three valid earlier partial profiles retain 86,659 / 79,307 / 78,769 samples at their actual sources. Invalid v50 stale-root evidence remains unusable and V49-DIAGNOSTIC-PREPARATION unresolved. Six older historical closure proposals and both singleton failures remain unaccepted.

The original fresh four-repository result remains **24 completed observations, 12 equal pairs and all four gates failed at `2e0efb2`**: FAF actual read unsupported; no-bash one vulnerable hit and two fixed/control false alerts per batch; Lightning actual client-get and Engram named manifest-write unresolved. Later corrections and observations are exposed regression, not clean unseen-source discrimination.

[Compatible reuse](compatible-reuse.json) verifies all 302 engineering inputs against actual tested `7bf4c6e`: **2,403 tests / 36 skips locally and in all 12 hosted suites**, all 29 normal jobs and docs passed in [CI 34784085204](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34784085204) / [docs 34784085193](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34784085193). Actual hosted merge `aa28ae250a411ba1773e919ad39fc656de842d8c` is recorded in the original quality packet; authoritative full identity is retained there. Local combined statement/branch coverage is 89.98%, branch-only 85.86%. Six zero-call production replays and 19 approved Git runtime component bindings remain compatible. This continuation adds report validation, source assessment, proposal checks and final docs/package checks, not a new hosted code pass. Prior file/worktree restoration and selective Docker cleanup remain preserved.

The [audit](audit.json) retains **all 323 prior requirements** and adds six: **329 total, 89 original + 240 added**. Original rows remain 84 passed, two user-deferred, two proposed limitations and one unresolved human acceptance. Added rows have 219 passed, six historical closure proposals and 15 unresolved before supplemental draft delivery. All prior rows are preserved, with explicit previous rows for V59 delivery and evaluation approval. No failure or human decision is silently waived.

TS 94 at `2e0efb2`, Python 87 at `8c62567` and whole 25 development reuse plus 45+45 Linux at `1f3f72f` retain their original evidence and Meta operator erratum. Original memory-keeper false alerts, DDG initially unsupported fixed send and wrong TypeScript manifest label despite actual Python configuration, and original Lighthouse misses remain unchanged. Language subsets are never pooled into new whole batches. The original held-out result stays 10 completed, 10 unsupported and five incomplete, with zero hits among four completed vulnerable inputs out of ten vulnerable inputs total. Same-agent curation/review is not independent human validation, training-data novelty, broad accuracy or runtime safety proof.

Git stays **312/1,040 incomplete**, 728 deferred. Paid benchmark/pilots remain deferred, Phase 21 incomplete and Phase 24/15 unchanged. Historical two paid calls cost $0.071799; this continuation adds zero. Current-source gates, explicit human technical acceptance and accepted closeout remain pending. No merge, ready-state change, release, outreach or Phase 23 is authorized.
'''
summary=summary.replace('aa28ae250a411ba1773e919ad39fc656de842d8c','aa28ae250a411ba1773e919ad39fc656de842b8c')
with (OUT/'summary.md').open('x') as stream:stream.write(summary)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v60-long-timeout-regression/'
body=f'''The approved 205-observation evaluation at `7bf4c6e` stopped on its first FAF input after {a['whole_seconds']:.3f} seconds without a report. Cleanup passed; 204 unstarted observations are closed and zero budget remains. The 30-minute shared policy remains in place. Detection and compatibility remain unresolved.

[Review packet]({url}summary.md) · [329-row audit]({url}audit.json) · [next diagnostic proposal]({url}diagnostic-proposal.json)

The next proposal is unapproved and unexecuted: one sampled FAF input, 30-minute maximum plus 15-second cleanup, existing 100Hz sampler/worker layout, no optimization, retries, uninstrumented observations, comparators, target executions or paid calls. Earlier failures and source bindings remain preserved.

Product/tests/workflows remain verified `7bf4c6e`: 2,403 tests / 36 skips locally and in all 12 hosted suites, 29 normal CI jobs and docs passed. This delivery adds evidence and documentation, not a new hosted code pass. Six production replays retain zero-call evidence.

Phase 22 remains incomplete pending current-source gates, explicit human technical acceptance and accepted closeout. Git stays 312/1,040 incomplete; paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged. No merge, ready-state change, release, outreach or Phase 23 is authorized.
'''
with (OUT/'pr-body.md').open('x') as stream:stream.write(body)
status=f'''## Current v60 thirty-minute regression: timed out, budget closed

The approved 205-observation sequence at frozen **`7bf4c6e`** stopped on the first
FAF vulnerable input after **{a['whole_seconds']:.6f} seconds**. **One incomplete,
zero reports, 204 unstarted closed and zero remaining**; cleanup passed. Findings,
detection, fixed/control discrimination and ordered repeats remain unknown.
The approved 1800-second shared policy remains in place; extending the deadline
alone did not establish completion. No retry, profile or paid call occurred.

`v60-long-timeout-regression/diagnostic-proposal.json` prepares **one sampled FAF
input**, **unapproved and unexecuted**, with a 1800-second maximum and 15-second
cleanup allowance. Existing sampler/worker layout, synthetic identity/timer and
missing-approval checks pass. Older `a36f696` samples do not establish current costs.
No optimization, uninstrumented run, comparator or target execution is included.

All **329 requirements (89 original + 240 added)** remain, including five native
timeouts, three valid partial profiles, invalid stale-root preparation, both
singleton failures and six unaccepted historical closure proposals. Product and
tests remain verified `7bf4c6e`: **2,403 tests / 36 skips** locally and in all 12
hosted suites, 29 normal CI jobs and docs passed. Combined coverage is 89.98%,
branch-only 85.86%; six zero-call replays and approved runtime bindings remain.
This continuation adds outcome, preparation and docs/package checks.

**Phase 22 remains incomplete**, pending current-source gates, explicit human
technical acceptance and accepted closeout. Git stays 312/1,040 incomplete;
paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged.
No merge, ready-state change, release, outreach or Phase 23 is authorized.

'''
heading='## Current v59 timeout policy: engineering passed, evaluation pending'
docs=list(read(OLD/'documentation-binding.json')['owning_docs_sha256'])
assert len(docs)==16
for name in docs:
    path=ROOT/name
    text=path.read_text()
    assert text.count(heading)==1,name
    path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{n:sha(ROOT/n) for n in docs}})
print('Preserved 323 prior rows, 329 total; reconciled 16 docs; one diagnostic remains unapproved.')
