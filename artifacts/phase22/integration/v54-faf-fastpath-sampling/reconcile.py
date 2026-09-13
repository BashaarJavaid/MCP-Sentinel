"""Retain the full audit and source-bound sampled result without accepting failures."""
import copy,hashlib,json,os
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];OLD=BASE/'v53-fastpath-regression'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
    with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
a=read(OUT/'assessment.json');old=read(OLD/'audit.json');rows=copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
    if row['id']=='V53-DELIVERY':
        row['previous_row']=copy.deepcopy(row);row.update(disposition='passed',evidence=['artifacts/phase22/integration/v53-fastpath-regression/delivery-verification.json'],assessment='Actual c337211 head/base/draft/title/body readback passed; this delivery does not accept any native or fresh failure.')
new=[('V54-AUTH','Bind the exact corrected single-profile approval to delivered proposal and frozen scanner','passed',['../v53-fastpath-regression/diagnostic-authorization.json','../v53-fastpath-regression/diagnostic-preflight.json']),('V54-PROFILE-VALIDATION','Validate current-source worker identities, all retained partial samples, output and closed budget','passed',['validation.json','owned-work.json']),('V54-SOURCE-ASSESSMENT','Source-assess all retained frame/stack attribution and state sampling limitations','passed',['assessment.json','source-assessment.json','frame-source-bindings.json','sample-attribution.json']),('V54-OPT-PREPARATION','Prepare one bounded source-only singleton cache-bypass optimization proposal with zero implementation or new measurement','passed',['optimization-proposal.json']),('V54-OPT-DECISION','Obtain a separate decision before another source-only optimization attempt','unresolved',['optimization-proposal.json']),('V54-DELIVERY','Seal partial diagnostic, reconcile every prior row and verify existing draft delivery','unresolved',[])]
for identity,requirement,disposition,evidence in new:rows.append({'id':identity,'requirement':requirement,'disposition':disposition,'evidence':[str((OUT/n).resolve().relative_to(ROOT)) for n in evidence],'assessment':'One current-source sampled timeout with four valid partial worker snapshots; no report/native pass. Source-only optimization remains unapproved; all old budgets and failures preserved.'})
assert len(old['requirements'])==89 and len(rows)==194 and len({r['id'] for r in old['requirements']+rows})==283
audit=copy.deepcopy(old);audit['historical_v53_status_fields']={k:copy.deepcopy(v) for k,v in old.items() if k not in ['requirements','additional_scope_requirements'] and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(),additional_scope_requirements=rows,additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),prior_audit={'path':str((OLD/'audit.json').relative_to(ROOT)),'sha256':sha(OLD/'audit.json')},diagnostic_approved=True,diagnostic_executed=True,diagnostic_attempts=1,diagnostic_completed_inputs=0,diagnostic_budget_closed=True,diagnostic_remaining=0,valid_current_source_profiles=1,current_diagnostic_approved=True,current_diagnostic_executed=True,optimization_prepared=True,optimization_approved=False,optimization_attempts=0,optimization_synthetic_verified=False,current_optimization_prepared=True,current_optimization_approved=False,current_optimization_attempts=0,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,new_paid_calls=0,status='Corrected current-source single profile timed out at300seconds with4verified worker identities and78769retained partial samples; budget closed. Registration traversal dominates; shared value-combine entry/cache dispatch remains a leaf concentration. One source-only eligible singleton bypass is unapproved/unstarted. No native completion, detection/compatibility or acceptance follows.')
audit['current_evidence']={n:sha(OUT/n) for n in ['assessment.json','validation.json','source-assessment.json','sample-attribution.json','optimization-proposal.json','owned-work.json']}
assert len(old['additional_scope_requirements'])==188
for prior,current in zip(old['requirements']+old['additional_scope_requirements'],audit['requirements']+rows):
    assert prior==current or current.get('previous_row')==prior
write('audit.json',audit)
write('prior-row-preservation.json',{'prior_audit_sha256':sha(OLD/'audit.json'),'retained_prior_rows':277,'updated_rows':['V53-DELIVERY'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})

table='\n'.join(f"| {r['rule']} | {r['samples']:,} | {r['merge_inclusive_percent']:.2f}% | {r['leaf_percent']['combine_cache_call_leaf']:.2f}% | {r['leaf_percent']['merge_equal_predicate_leaf']:.2f}% |" for r in a['sample_rows'])
summary=f"""# Current fast-path profile assessed; source-only decision pending

**The approved single FAF profile at `a36f696` retained four verified worker identities and 78,769 partial samples, then timed out. One incomplete input, no report, zero remaining budget. Phase 22 remains incomplete.**

The exact `approved` decision binds the [diagnostic authorization](../v53-fastpath-regression/diagnostic-authorization.json) to proposal `9d3d83da8e6c3295dd98c9462a3bf9809bd8dbf9da442f27cc698ca7ce90f925`, delivered at `c337211`. [Validation](validation.json) establishes worker/flow imports and complete scanner revision/source/harness identity before timer setup or target snapshot access. The whole input reached **{a['timing']['elapsed_seconds']:.9f} seconds**; cleanup finished by **{a['timing']['elapsed_including_cleanup_seconds']:.9f} seconds**, within 15 seconds and without a remaining group kill. No owned process or container remains. The harness retained `incomplete`, `reason: null` and **{a['harness_outcome']['wall_duration_ms']:,} ms** within its narrower interval.

No JSON/SARIF report exists. Findings, warnings, surfaces, named vulnerable detection, fixed/control discrimination and ordered repeats remain unknown, not zero. This profile does not reopen any of the three closed native regression budgets or establish a native timing, fresh-source, corrected-discrimination or compatibility pass.

[Full sample attribution](sample-attribution.json) and [source assessment](source-assessment.json) validate all retained counts, stacks, frame references and source hashes. Each row describes one worker's last periodic snapshot:

| Worker | Samples | Merge inclusive | Combine cache-call leaf | Equal-value predicate leaf |
| --- | ---: | ---: | ---: | ---: |
{table}

All four snapshots lack final/restored-state records after mandatory cleanup. Their retained CPU intervals differ. TypeScript registration/factory traversal covers roughly **99.6%** of each partial snapshot. Merge is **33.09–33.73% inclusive**; shared `combine` entry/cache dispatch is **7.40–7.64% leaf share**. Inclusive shares overlap and cannot be added as independent costs. Prior normalized sample shares at `17b4784` or `6e4fd67` do not measure an absolute speedup. Signal/GIL/native-code delivery, snapshot-thread overhead, unsampled parent stages and unretained final intervals limit attribution.

[Caller attribution](stack-caller-attribution.json) also retains source-range bookkeeping, branch-state updates, TypeScript literal JSON serialization and hashed-key construction. JSON encoder samples have scanner callers; they are not simply dismissed as profiler-output overhead. No locals, singleton frequency, argument lengths or cache-hit rates were recorded.

The shared `combine` function converts every input list into a tuple and enters the existing 4,096-entry LRU before `_combine` checks unchanged values. For **exactly one Value**, no effective key override, and no required source-free safety stripping, the existing implementation returns that value unchanged. This identifies a narrow source-level opportunity. The [exact proposal](optimization-proposal.json), SHA-256 `{sha(OUT/'optimization-proposal.json')}`, requests **one source-only attempt** to recognize only that case before tuple/cache dispatch in `src/sentinel/static/path_flow.py:combine`. It is **unapproved and unstarted**.

Preserve `_combine`, its cache and every other path. No new cache, dependency, multi-value shortcut, traversal pruning, resource/deadline change or source-label change is proposed. Required verification covers the complete Value and Python/TypeScript flow state, cold/warm caches, equal-but-distinct values, key overrides, absent/null/undefined markers, source-free guards and all path/URL/credential/option/record/array metadata. Trace all shared callers and any identity-sensitive behavior: cached interning and direct-input identity may differ, but no identity-dependent semantic change is permitted. Synthetic accounting must show eligible calls avoid cache entry while fallback cases remain unchanged. A failed equivalence or avoided-work check closes the attempt without another target.

The profile does **not** establish how often this case occurs or how much total work it could remove. No 300-second completion or percentage speedup is promised. If separately approved and successful, complete affected/full local and hosted engineering, static/package/schema/lock checks, zero-call production/runtime compatibility and freeze. Any subsequent native/compatibility execution needs a separate exact proposal. Bounds for this source-only proposal are **zero corpus observations, profiles, retries, comparators, new repositories, target executions, runtime campaigns or paid calls**.

The first cleanup verification ran while the report-attribution helper was still active and correctly failed on those two helper PIDs; no container remained. After attribution finished, the unchanged check passed under a new label. Both receipts remain retained. This was verification ordering, not another profile or a cleanup failure in the measured input.

All three native timeouts remain separate: `17b4784` at 300.002159 seconds, `6e4fd67` at 300.004111 seconds and `a36f696` at 300.000481 seconds, each one incomplete with 204 unstarted closed. Previous partial profiles retain 86,659 samples at `17b4784` and 79,307 at `6e4fd67`; this profile is separately bound to `a36f696`. The invalid interrupted v50 stale-root attempt remains unusable, and V49-DIAGNOSTIC-PREPARATION remains unresolved. No failed measurement becomes a pass or accepted limitation.

The original four-source fresh result stays **24 complete observations, 12 equal pairs and all four gates failed at `2e0efb2`**: FAF actual read unsupported; no-bash one vulnerable hit plus two fixed/control false alerts per batch; Lightning client-get and Engram named manifest-write unresolved. Later corrections on these exposed sources cannot establish clean unseen-source discrimination.

Product, tests, workflows, schemas and lock retain tested **`a36f696`: 2,386 tests / 36 skips locally and in all 12 hosted suites**. All 29 normal CI jobs and docs passed in [34767417083](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34767417083) / [34767417081](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34767417081); local combined statement/branch coverage is89.98%, branch-only85.85%. All302 engineering files, package source members, six identical zero-call production requests and approved Docker/Git image/runtime bindings retain that source. This continuation adds evidence/source assessment and final docs/package checks, not a new hosted code pass. Earlier file/evidence/worktree restoration and selective Docker cleanup remain preserved.

The [audit](audit.json) retains all **277 prior requirements** and adds six: **283 total, 89 original + 194 added**. Original dispositions remain84passed, two user-deferred, two proposed documented limitations and one pending human acceptance. Added rows have176passed, six historical closure proposals and12unresolved before the separate delivery readback. Corrected corpus gates and explicit human technical acceptance remain unresolved.

TS94 at `2e0efb2`, Python87 at `8c62567` and whole25 development reuse plus45+45 Linux at `1f3f72f` retain their actual passes and Meta operator erratum; language subsets are never pooled into a new whole batch. Original memory-keeper false alerts, DDG's initially unsupported fixed send and incorrect TypeScript metadata despite Python execution, Lighthouse misses, and the original held-out10complete/10unsupported/5incomplete with zero hits among four completed vulnerable inputs out of ten vulnerable total remain unchanged. Same-agent review is not independent human validation, training-data novelty, broad accuracy or runtime safety proof.

Git remains **312/1,040 incomplete**,728deferred; paid benchmark and pilots stay deferred, Phase21 incomplete and Phase24/15 unchanged. Historical two paid calls cost $0.071799; this continuation adds zero. Explicit human technical acceptance and verified accepted closeout remain pending. No merge, ready-state change, release, outreach or Phase23 is authorized.
"""
for left,right in [('is89.98','is 89.98'),('branch-only85.85','branch-only 85.85'),('All302','All 302'),('remain84passed','remain 84 passed'),('have176passed','have 176 passed'),('and12unresolved','and 12 unresolved'),('whole25','whole 25'),('plus45+45','plus 45+45'),('held-out10complete/10unsupported/5incomplete','held-out 10 complete/10 unsupported/5 incomplete'),('**,728deferred','**, 728 deferred'),('Phase21','Phase 21'),('Phase24/15','Phase 24/15'),('Phase23','Phase 23')]:summary=summary.replace(left,right)
with (OUT/'summary.md').open('x') as f:f.write(summary)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
body=summary.replace('(../v53-fastpath-regression/','('+url+'v53-fastpath-regression/')
for n in ['validation.json','sample-attribution.json','source-assessment.json','stack-caller-attribution.json','optimization-proposal.json','audit.json']:body=body.replace('('+n+')','('+url+'v54-faf-fastpath-sampling/'+n+')')
with (OUT/'pr-body.md').open('x') as f:f.write(body)
heading='## Current v53 fast-path regression timeout: budget closed'
status=f"""## Current v54 sampled timeout: source-only decision pending

The approved single profile at frozen **`a36f696`** retains **four verified worker
identities and 78,769 partial samples**. Whole input **{a['timing']['elapsed_seconds']:.6f} seconds**;
cleanup passed, no report exists and the one-use budget is closed. Registration
traversal dominates; merge is33.09–33.73% inclusive and shared combine/cache call
is7.40–7.64% leaf sample share. These overlapping partial shares establish no
native speedup, removable-cost fraction or300-second completion.

`v54-faf-fastpath-sampling/optimization-proposal.json` proposes **one unapproved
source-only singleton fast path** before the existing value-combination cache.
Only an unchanged sole Value with no key override or required safety stripping
could bypass the tuple/cache call. All other paths, cache and complete flow state
must remain compatible, including cold/warm and identity-sensitive controls.
No implementation, corpus/profile/retry, new cache, resource/deadline change or
paid call is authorized. Eligible-case prevalence remains unmeasured.

All three native timeouts/204closed remainders, prior partial profiles, invalid
stale-worker preparation and original fresh failures remain unchanged. The audit
retains **283 requirements (89 original + 194 added)** and six unaccepted historical
closure proposals. Product retains tested `a36f696`: 2,386 tests /36skips locally
and in all12hosted suites,29normal CI jobs anddocs passed; combined coverage89.98%,
branch-only85.85%, six unchanged zero-call production requests and runtime bindings.
**Phase 22 remains incomplete.** Git stays312/1,040 incomplete with728deferred;
paid benchmark/pilots deferred, Phase21 incomplete and Phase24/15 unchanged.
No merge, ready-state change, release, outreach or Phase23 is authorized.

"""
for left,right in [('is33.09','is 33.09'),('is7.40','is 7.40'),('or300','or 300'),('/204closed','/204 closed'),('/36skips','/ 36 skips'),('all12hosted','all 12 hosted'),(',29normal',', 29 normal'),('anddocs','and docs'),('coverage89.98','coverage 89.98'),('branch-only85.85','branch-only 85.85'),('stays312','stays 312'),('with728deferred','with 728 deferred'),('Phase21','Phase 21'),('Phase24/15','Phase 24/15'),('Phase23','Phase 23')]:status=status.replace(left,right)
docs=list(read(OLD/'documentation-binding.json')['owning_docs_sha256']);assert len(docs)==16
for name in docs:
 path=ROOT/name;text=path.read_text();assert text.count(heading)==1,name
 path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{n:sha(ROOT/n) for n in docs}})
print('Preserved277prior rows;283total; reconciled16docs; singleton proposal unapproved and unstarted.')
