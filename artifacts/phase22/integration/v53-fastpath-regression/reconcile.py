"""Preserve all requirements and publish the actual stopped execution status."""
import copy
import hashlib
import json
import os
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = OUT.parents[3]
OLD = BASE/'v52-merge-fastpath'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

a = read(OUT/'assessment.json')
assert a['budget'] == {'planned': 205, 'attempted': 1, 'completed': 0, 'incomplete': 1, 'unstarted_closed': 204, 'remaining': 0, 'closed': True}
old = read(OLD/'audit.json')
rows = copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
    if row['id'] == 'V52-DELIVERY':
        row['previous_row'] = copy.deepcopy(row)
        row['disposition'] = 'passed'
        row['evidence'] = ['artifacts/phase22/integration/v52-merge-fastpath/delivery-verification.json']
        row['assessment'] = 'Actual43b9a85draft delivery readback passed; this does not accept the later execution failure.'
new = [
    ('V53-AUTH', 'Bind the exact205-observation approval to proposal, launcher, scanner and bounds', 'passed', ['../v52-merge-fastpath/evaluation-authorization.json', '../v52-merge-fastpath/execution-preflight.json']),
    ('V53-STOP', 'Preserve timeout/incomplete output and close all204unstarted observations with verified cleanup', 'passed', ['validation.json', 'assessment.json', 'owned-work.json']),
    ('V53-ASSESSMENT', 'Assess every available outcome without inventing report contents or corrected-scanner compatibility', 'passed', ['assessment.json']),
    ('V53-DIAGNOSTIC-PREPARATION', 'Prepare a separately gated single bounded sampled input with synthetic validation and zero execution', 'passed', ['diagnostic-proposal.json', 'sampler-selfcheck/packet.json', '../v53-diagnostic-boundary.json']),
    ('V53-REGRESSION-GATE', 'Complete current-source four-repository and affected compatibility gates or obtain an explicit disposition of actual failure', 'unresolved', ['assessment.json']),
    ('V53-DELIVERY', 'Seal stopped execution, reconcile every prior row and verify existing draft delivery of the concrete next decision', 'unresolved', []),
]
for identity, requirement, disposition, evidence in new:
    rows.append({'id': identity, 'requirement': requirement, 'disposition': disposition,
                 'evidence': [str((OUT/n).resolve().relative_to(ROOT)) for n in evidence],
                 'assessment': 'One incomplete timed-out observation, no reports,204closed unstarted,zero remaining. No corrected-source discrimination/compatibility or human acceptance is claimed.'})
assert len(old['requirements']) == 89 and len(rows) == 188
assert len({r['id'] for r in old['requirements']+rows}) == 277
audit = copy.deepcopy(old)
audit['historical_v52_status_fields'] = {k: copy.deepcopy(value) for k,value in old.items() if k not in ['requirements','additional_scope_requirements'] and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(), additional_scope_requirements=rows,
             additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),
             prior_audit={'path': str((OLD/'audit.json').relative_to(ROOT)), 'sha256': sha(OLD/'audit.json')},
             regression_approved=True, regression_executed=True, current_regression_approved=True, current_regression_executed=True, current_source_corpus_observations=1,
             current_source_completed_observations=0, current_source_incomplete_observations=1,
             unstarted_closed=204, remaining=0, budget_closed=True,
             execution_gate_passed=False, diagnostic_prepared=True, diagnostic_approved=False,
             diagnostic_executed=False, current_diagnostic_prepared=True,current_diagnostic_approved=False,current_diagnostic_executed=False,diagnostic_attempts=0, diagnostic_completed_inputs=0, diagnostic_budget_closed=False, diagnostic_remaining=0, new_paid_calls=0, acceptance_packet_ready=False,
             technical_acceptance_requested=False, technical_acceptance_received=False, phase22_complete=False,
             status='Approved205-observation sequence stopped on first FAF vulnerable timeout;1incomplete,0complete,204unstarted closed. All corrected-source detection/compatibility gates remain unresolved. One300-second diagnostic is prepared,unapproved and unexecuted.')
audit['current_evidence'] = {n: sha(OUT/n) for n in ['assessment.json', 'validation.json', 'diagnostic-proposal.json', 'sampler-selfcheck/packet.json', 'owned-work.json']}
for identity in ['R66', 'R88']:
    audit['current_requirement_interpretations'][identity] = 'Original24first-frozen observations and all4failed fresh gates remain at2e0efb2. Approved correcteda36f696regression stopped on first FAF timeout,with no completed report and204unstarted closed. Current-source detection/compatibility remains unestablished. No historical closure or new failure is accepted.'
assert len(old['additional_scope_requirements'])==182
for prior,current in zip(old['requirements']+old['additional_scope_requirements'],audit['requirements']+rows):
    assert prior==current or current.get('previous_row')==prior
write('audit.json', audit)
write('prior-row-preservation.json', {'prior_audit_sha256': sha(OLD/'audit.json'), 'retained_prior_rows': 271, 'updated_rows': ['V52-DELIVERY'],
     'rows': {r['id']: hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})

summary=f"""# FAF timeout at the fast-path candidate; regression budget closed

**The approved 205-observation sequence at `a36f696` stopped on its first input: one incomplete attempt, no completed reports, 204 unstarted observations closed and zero remaining. Phase 22 remains incomplete.**

The exact user decision `approve` binds the [authorization](../v52-merge-fastpath/evaluation-authorization.json) to proposal `d7dbe81c25e0ea4ef5ad60608a1f78ed11408db8853eb8abe55e33e90d89b913` delivered at `43b9a85`. The sole input was `faf-read-root-vulnerable` from Wolfe-Jam/faf-mcp at the original frozen source/configuration. Its [whole-input duration](assessment.json) was **{a['whole_seconds']:.9f} seconds**; cleanup completed by **{a['whole_including_cleanup_seconds']:.9f} seconds**, within the 15-second allowance, with no remaining process-group kill. The outer sequence took **{a['sequence_seconds']:.9f} seconds**, exited 1 and closed its budget. All owned processes and containers were absent afterward.

The retained harness result is `incomplete`, `reason: null`, with **{a['harness_wall_duration_ms']} ms** measured inside its narrower interval. The SIGTERM handler raises `SystemExit`; this bypasses `except Exception` but still runs the harness's `finally` writer, explaining that record. **No native JSON/SARIF report exists. Findings, warnings, surfaces, named detection and negative discrimination are unknown, not zero.** There is no completed batch, ordered pair or native exit-3 report. Resource CPU totals sum concurrent child workers and cannot identify a hotspot or replace whole-input elapsed time.

[Validation](validation.json) and [source assessment](assessment.json) bind every retained file, scanner/configuration/approval identity, actual timeout and all 204 closed observations. The other 23 four-source observations and all 181 prior-language observations did not start. Corrected FAF, no-bash, Lightning and Engram discrimination and prior Python/TypeScript compatibility remain unestablished. This timeout establishes failure to finish within 300 seconds; it does not quantify a speedup or slowdown. The 10,944 synthetic equivalence checks and eight avoided-fallback cases remain engineering evidence only. The one source-only optimization budget stays closed.

The [next diagnostic proposal](diagnostic-proposal.json), SHA-256 `{sha(OUT/'diagnostic-proposal.json')}`, is **unapproved and unexecuted**. It proposes **one sampled rules-only input**, the same FAF vulnerable case at frozen `{a['scanner']['revision']}`, source `{a['scanner']['source_sha256']}`, unchanged harness and lock. Bounds: **120-second target, 300-second whole maximum, 15-second cleanup**, existing local macOS environment, 100Hz CPU timer per worker, 15-second atomic partial snapshots and at most 1,024 stack frames. **Zero optimization attempts, uninstrumented observations, retries, comparators, new repositories, target execution or paid calls.** No observation budget is reopened.

Earlier valid v51 samples measured `6e4fd67` before the fast-path reorder; they cannot establish the remaining cost at `a36f696`. The proposed sampler preserves the existing worker layout, rule/configuration and scanner methods. Before timer setup or target snapshot access it checks actual worker/flow paths plus complete scanner source/harness/revision. Parent preflight checks the isolated worker before consuming a token, and every real worker must retain a matching identity receipt. [Synthetic checks](sampler-selfcheck/packet.json) preserve six value vectors and scanner method identities, validate samples/frame references and restore signal/timer state. A stale `6e4fd67` root fails before sampling; missing approval fails before output or token creation. No target corpus was executed by these checks.

A sampled timeout would consume the entire one-use diagnostic budget. Killed workers may have only partial snapshots without final/restored-state receipts; signal/GIL/native-code delays and instrumentation overhead limit attribution. Overlapping shares are not guaranteed removable costs or native performance results. If a report completes, validate both schemas, compare the entire ordered report with the source-bound `2e0efb2` reference after only the 11 established volatile exclusions, and assess every delta. No optimization or further run follows automatically.

All three native failures remain separate: `17b4784` at 300.002159 seconds, `6e4fd67` at 300.004111 seconds and this `a36f696` timeout, each one incomplete with 204 unstarted closed. Earlier sampled timeouts retain their original identities: 86,659 partial samples at `17b4784`, and 79,307 partial samples with four verified worker identities at `6e4fd67`. The invalid interrupted v50 stale-root attempt has no usable profile/report and remains unresolved in V49-DIAGNOSTIC-PREPARATION. Its later corrected profile does not erase that error. No historical measurement becomes a pass or an accepted limitation.

The original four-source fresh result remains **24 completed observations, 12 equal ordered pairs and all four gates failed at `2e0efb2`**: FAF actual read unsupported; no-bash one vulnerable hit plus two fixed/control false alerts per batch; Lightning client-get and Engram named manifest-write paths unresolved. Later corrections on these exposed sources cannot establish clean unseen-source discrimination.

Product, tests, workflows, schema and lock remain engineering-tested `a36f696`: **2,386 tests / 36 skips** locally and in all 12 hosted suites, local combined statement/branch coverage **89.98%**, branch-only **85.85%**, all **29 normal CI jobs** and docs passed in [34767417083](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34767417083) / [34767417081](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34767417081). Actual hosted merge `6623f48bb9a5f36a9d48342f50c9e9d408d0e9bd` has the complete candidate tree. All 302 engineering files, package source bytes, six identical zero-call production requests and approved Docker/Git image/runtime bindings remain retained. This continuation adds report, diagnostic-preparation and final docs/package validation, not a new hosted code pass. Previous exact file/worktree restoration and selective Docker cleanup remain preserved.

The [audit](audit.json) preserves all **271 prior requirements** and adds six: **277 total, 89 original + 188 added**. Original dispositions remain 84 passed, two user-deferred, two proposed limitations and one unresolved human acceptance. Added rows have 171 passed, six historical closure proposals and 11 unresolved before the separate delivery readback. Corrected detection/compatibility gates, failure dispositions and explicit human technical acceptance remain open.

Memory-keeper's original fresh false alerts, DDG's initially unsupported fixed send and incorrect TypeScript manifest label despite actual Python configuration, Lighthouse's original misses and all prior failures remain source-bound. TS94 at `2e0efb2`, Python87 at `8c62567` and whole 25 development reuse plus 45+45 Linux at `1f3f72f` retain their actual passes and Meta operator erratum. Language subsets are never pooled into a new whole batch. The original held-out result stays 10 completed, 10 unsupported and five incomplete, with zero hits among four completed vulnerable inputs out of ten vulnerable total. Same-agent curation/review is not independent human validation, training-data novelty, broad accuracy or runtime safety proof.

Git campaigns remain **312/1,040 incomplete**, 728 deferred. Paid benchmark and pilots stay deferred; Phase 21 remains incomplete and Phase 24/15 gates unchanged. Historical paid calls remain two costing $0.071799; this continuation adds zero. No merge, ready-state change, release, outreach or Phase 23 is authorized. The next exact diagnostic decision, further justified technical work, explicit human acceptance and verified accepted closeout remain separate checkpoints.
"""
with (OUT/'summary.md').open('x') as f:f.write(summary)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
body=summary.replace('(../v52-merge-fastpath/','('+url+'v52-merge-fastpath/')
for n in ['assessment.json','validation.json','diagnostic-proposal.json','sampler-selfcheck/packet.json','audit.json']:body=body.replace('('+n+')','('+url+'v53-fastpath-regression/'+n+')')
with (OUT/'pr-body.md').open('x') as f:f.write(body)
heading='## Current v52 equal-value fast path: regression approval pending'
status=f"""## Current v53 fast-path regression timeout: budget closed

The approved 205-observation sequence at frozen **`a36f696`** stopped on its first
FAF vulnerable input at **{a['whole_seconds']:.6f} seconds** whole-input time.
**One incomplete, zero reports, 204 unstarted closed, zero remaining**; cleanup
passed. Findings, guards, negative discrimination and ordered repeats are unknown.
Corrected four-source and prior-language compatibility gates remain unestablished.
No retry, profile, target execution or paid call occurred. All earlier failures
and original fresh outcomes remain preserved with their actual scanner identities.

The next **single 300-second sampled FAF input** is prepared, **unapproved and
unexecuted** in `v53-fastpath-regression/diagnostic-proposal.json`. It retains the
existing CPU-timer sampler, source/configuration and worker layout, with verified
actual worker/flow/scanner identities before timer or target snapshot access.
The stale-root synthetic control and missing-approval boundary pass. Earlier
`6e4fd67` samples cannot establish remaining costs after the current reorder.
No further optimization, retry, resource/deadline change or paid call is authorized.

All **277 requirements (89 original + 188 added)** remain, including six unaccepted
historical closure proposals and the unresolved invalid stale-worker preparation.
Product/tests/workflows remain `a36f696`: 2,386 tests / 36 skips locally and in all
12 hosted suites; 29 normal CI jobs and docs passed, combined coverage 89.98% and
branch-only 85.85%. Six zero-call production requests and runtime bindings persist.
**Phase 22 remains incomplete.** Git stays 312/1,040 incomplete with 728 deferred;
paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged.
No merge, ready-state change, release, outreach or Phase 23 is authorized.

"""
docs=list(read(OLD/'documentation-binding.json')['owning_docs_sha256']);assert len(docs)==16
for n in docs:
 path=ROOT/n;text=path.read_text();assert text.count(heading)==1,n
 path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{n:sha(ROOT/n) for n in docs}})
print('Preserved271prior rows;277total; reconciled16docs; current-source diagnostic remains unapproved.')
