"""Preserve every prior requirement and the failed one-attempt disposition."""
import copy
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = Path.cwd()
OLD = BASE / 'v54-faf-fastpath-sampling'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
old = read(OLD/'audit.json')
rows = copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
    if row['id'] in {'V54-DELIVERY', 'V54-OPT-DECISION'}:
        row['previous_row'] = copy.deepcopy(row)
        row.update(disposition='passed', evidence=[str((OLD/'delivery-verification.json' if row['id']=='V54-DELIVERY' else OUT/'authorization.json').relative_to(ROOT))], assessment='Verified029bef1 draft delivery or exact subsequent approved. decision; neither accepts any historical failure.')
new = [
    ('V55-AUTH', 'Bind the one source-only singleton attempt to the exact approved proposal and baseline', 'passed', ['authorization.json']),
    ('V55-EQUIVALENCE', 'Preserve complete Value and flow semantics, including cache interning and identity-sensitive callers', 'unresolved', ['identity-validation.json', 'assessment.json', 'optimization-budget-closed.json']),
    ('V55-ASSESSMENT', 'Assess the failed prerequisite and initial verification-helper comparison defect without claiming real-target reachability', 'passed', ['assessment.json', 'check-identity.py', 'assess-failure.py']),
    ('V55-RESTORATION', 'Close the single failed attempt and restore exact tested product source, preserving the candidate', 'passed', ['optimization-budget-closed.json', 'candidate-path-flow.py', 'candidate.patch', 'assessment.json']),
    ('V55-NARROW-PREPARATION', 'Prepare a separate bounded canonical UNKNOWN_VALUE-only proposal without implementing it', 'passed', ['optimization-proposal.json']),
    ('V55-NARROW-DECISION', 'Obtain a separate decision before the newly narrowed source-only optimization attempt', 'unresolved', ['optimization-proposal.json']),
    ('V55-DELIVERY', 'Verify final docs/package, seal and exact existing draft delivery with all prior requirements retained', 'unresolved', []),
]
for identity, requirement, disposition, evidence in new:
    rows.append({'id': identity, 'requirement': requirement, 'disposition': disposition, 'evidence': [str((OUT/n).relative_to(ROOT)) for n in evidence], 'assessment': 'One broad singleton attempt failed its synthetic environment equivalence prerequisite and was reverted. No real-target regression or runtime reachability is claimed. A narrower canonical-empty-value proposal is unapproved; no stopped budget is reopened.'})
audit = copy.deepcopy(old)
audit['historical_v54_status_fields'] = {k: copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements'} and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(), additional_scope_requirements=rows, additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)), prior_audit={'path':str((OLD/'audit.json').relative_to(ROOT)), 'sha256':sha(OLD/'audit.json')}, current_optimization_prepared=True, current_optimization_approved=True, current_optimization_attempts=1, optimization_prepared=True, optimization_approved=True, optimization_attempts=1, optimization_synthetic_verified=False, optimization_budget_closed=True, optimization_remaining=0, candidate_retained_in_product=False, next_optimization_prepared=True, next_optimization_approved=False, next_optimization_attempts=0, acceptance_packet_ready=False, technical_acceptance_requested=False, technical_acceptance_received=False, phase22_complete=False, new_paid_calls=0, status='Broad singleton bypass failed synthetic environment identity equivalence and was reverted; one attempt closed. Whole-flow check defect separately corrected. Real-target reachability unestablished. Product remains tested a36f696. Canonical UNKNOWN_VALUE-only proposal is unapproved and unstarted.')
audit['current_evidence'] = {n:sha(OUT/n) for n in ['authorization.json','assessment.json','identity-validation.json','optimization-budget-closed.json','optimization-proposal.json','owned-work.json']}
assert len(old['requirements']) == 89 and len(rows) == 201
for prior, current in zip(old['requirements']+old['additional_scope_requirements'], audit['requirements']+rows):
    assert prior == current or current.get('previous_row') == prior
assert audit['additional_scope_dispositions'] == {'passed':182, 'unresolved':13, 'proposed_documented_limitation':6}, audit['additional_scope_dispositions']
save('audit.json', audit)
save('prior-row-preservation.json', {'retained_prior_rows':283, 'total_rows':290, 'prior_audit_sha256':sha(OLD/'audit.json'), 'updated_rows':['V54-DELIVERY','V54-OPT-DECISION'], 'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
summary = f'''# Singleton optimization failed its prerequisite; candidate reverted

**The approved broad singleton cache bypass failed its required synthetic environment equivalence check. One attempt consumed, zero remaining. Product source is restored exactly to tested `a36f696`; Phase 22 remains incomplete.**

The user's `approved.` decision binds [authorization](authorization.json) to the proposal SHA-256 `94c740f84b0e3478ad75124b426ed9e914ff8789f076733dba21e5df6c0f9a81`, delivered at `029bef1`. The candidate added only the proposed singleton/key/safety guard to shared `path_flow.combine`. Its [source](candidate-path-flow.py), [patch](candidate.patch), exact baseline, failed check and [closed budget](optimization-budget-closed.json) are retained. No alternative implementation, corpus observation, profile, retry, comparator, target execution or paid call occurred.

The existing `_combine` LRU uses `Value` equality, so a warm cache can return the same object for distinct equal inputs. Direct singleton return preserves their separate identities. `CredentialFlow.merge` compares absence/opt-in markers using `is`. In the retained adversarial internal case, two equal tainted markers have `contained=False`: baseline interning retains their fields, while the bypass makes them distinct and the merge substitutes `UNKNOWN_VALUE`. The environment therefore differs. For the contained-true case, both environments agree.

This is **a synthetic internal-state counterexample, not an observed target finding change**. Source guard constructors set these markers contained-true; later merges can reset them to `UNKNOWN_VALUE`. No path establishing the adversarial nonempty tainted contained-false marker from a complete target program has been demonstrated. That limit does not permit silently narrowing the approved complete-state prerequisite after it fails. The approved stop rule closes the attempt; it does not authorize patching the credential merge or trying another optimization.

The initial helper also incorrectly compared `vars(flow)` containing separately constructed helper objects. Its full-flow false flags were verification defects. [Assessment](assessment.json) structurally compares all fields, including RegistrationFlow and HTTPContext backreferences: both cases have equal full flow state, and only the contained-false environment differs. Both input environments remain unchanged by merge. The original helper, failed receipt and corrected assessment are preserved separately; the independent environment failure is not erased. No candidate rerun against a corpus or real target occurred.

The prerequisite failed before the broader synthetic matrix or affected/full local/hosted engineering. Those checks were not run for the rejected candidate, and no engineering pass is claimed for it. The exact product rollback restores the existing tested source; final docs/package/source checks verify this delivery separately.

The [new proposal](optimization-proposal.json), SHA-256 `{sha(OUT/'optimization-proposal.json')}`, requests **one separate source-only attempt** limited to `len(values) == 1`, `values[0] is UNKNOWN_VALUE`, and an empty requested key. Every other input would retain the original cache dispatch. The module's canonical `UNKNOWN_VALUE` is exactly frozen `Value()` with all default/empty fields. The failed tainted marker is ineligible. Empty-value cache interning and every identity-sensitive caller must still be verified; no semantic or performance pass is assumed. This proposal is **unapproved and unimplemented**.

Required checks preserve the failed case, use structural full-state comparisons across Python and TypeScript, cover cold/warm caches, equal-but-distinct empty Values, mixed identities, all metadata/guard/key states, null/missing/undefined and empty/one/two/many inputs, and count eligible versus fallback cache dispatch. Stop on the first verified equivalence or avoided-work failure. If those prerequisites pass, complete local/hosted engineering and source-bound zero-call compatibility before freezing and separately proposing regression. Bounds remain **zero corpus observations, profiles, retries, comparators, new repositories, target executions, runtime campaigns or paid calls**.

The current profile's combine/cache-call leaf share was 7.40–7.64%, but canonical unknown frequency was not captured. It is not a removable-cost estimate or a promised speedup. The narrower proposal does not guarantee completion within 300 seconds.

All three native timeouts remain separate and unchanged: `17b4784` at 300.002159 seconds, `6e4fd67` at 300.004111 seconds and `a36f696` at 300.000481 seconds, each one incomplete and 204 unstarted closed. The current `a36f696` profile timed out at 300.007176 seconds with four verified worker identities, 78,769 partial samples and successful cleanup. Earlier partial profiles retain 86,659 samples at `17b4784` and 79,307 at `6e4fd67`. The interrupted stale-root v50 attempt remains invalid; V49-DIAGNOSTIC-PREPARATION remains unresolved. No old budget is reopened.

The original four-repository fresh result remains 24 complete observations, 12 equal report pairs and all four gates failed at `2e0efb2`: FAF actual read unsupported; no-bash one vulnerable hit plus two fixed/control false alerts per batch; Lightning actual client-get and Engram named manifest-write unresolved. Later corrections are exposed regressions, never clean unseen-source discrimination.

Restored product, tests, workflows, schemas and lock retain engineering-tested `a36f696`: **2,386 tests / 36 skips locally and in all 12 hosted suites**, all 29 normal CI jobs and docs passed in [34767417083](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34767417083) / [34767417081](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34767417081). Local combined coverage is 89.98%, branch-only 85.85%. All 302 engineering files, package members, six unchanged zero-call production requests and approved Docker/Git runtime bindings retain their source. This rejected-candidate continuation adds no hosted code pass. Earlier file/worktree/evidence restoration and selective Docker cleanup remain preserved.

The [audit](audit.json) retains **all 283 prior rows** and adds seven: **290 total, 89 original plus 201 added**. Original dispositions remain 84 passed, two user-deferred, two proposed documented limitations and one pending human acceptance. Added rows have 182 passed, six historical closure proposals and 13 unresolved before supplemental delivery verification. The failed equivalence row remains unresolved, not accepted or relabeled as a historical pass.

TS94 at `2e0efb2`, Python87 at `8c62567`, and whole 25 development reuse plus 45+45 Linux at `1f3f72f` retain their actual passes and Meta operator erratum. Partial language subsets are never pooled into a new whole batch. Original memory-keeper false alerts, DDG's initially unsupported fixed send and incorrect TypeScript label despite Python execution, Lighthouse misses, and the original held-out 10 complete / 10 unsupported / five incomplete with zero hits among four completed vulnerable inputs out of ten vulnerable total remain unchanged. Same-agent review is not independent human validation, training-data novelty, broad accuracy or runtime proof.

Git stays **312/1,040 incomplete**, 728 deferred; paid benchmark and pilots remain deferred, Phase 21 incomplete and Phase 24/15 unchanged. Historical two paid calls cost $0.071799; this continuation adds zero. Human technical acceptance and accepted closeout are pending. No merge, ready-state change, release, outreach or Phase 23 is authorized.
'''
with (OUT/'summary.md').open('x') as stream: stream.write(summary)
url = 'https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v55-singleton-combine/'
body = summary
for name in ['authorization.json','candidate-path-flow.py','candidate.patch','optimization-budget-closed.json','assessment.json','optimization-proposal.json','audit.json']:
    body = body.replace('('+name+')', '('+url+name+')')
with (OUT/'pr-body.md').open('x') as stream: stream.write(body)
status = '''## Current v55 singleton attempt: equivalence failure retained

The approved broad singleton cache bypass failed its synthetic environment
equivalence prerequisite and was reverted. A warm cache interns equal Values;
direct return changes identity-sensitive credential-marker merging for a tainted
contained-false internal state. Real-target reachability of that state is not
established. Initial whole-flow comparison flags were a helper-object comparison
defect; structural reassessment preserves equal full flow state and confirms the
independent environment delta. All evidence remains visible. **One failed attempt
consumed, zero remaining; product restored exactly to tested `a36f696`.**

`v55-singleton-combine/optimization-proposal.json` prepares one **unapproved,
unimplemented** attempt restricted to the canonical `UNKNOWN_VALUE` singleton
and empty requested key. Every other input must retain cache dispatch. Complete
state and interning checks remain required; eligibility frequency and speedup
are unknown. No corpus/profile/retry, target execution or paid call is authorized.

All three native timeouts, partial profiles, invalid stale-root attempt and
original fresh failures remain source-bound. The audit retains **290 rows
(89 original + 201 added)**, including six unaccepted historical closure proposals
and the new unresolved equivalence failure. Restored `a36f696` retains 2,386 tests /
36 skips in local and all 12 hosted suites, 29 normal CI jobs and docs passed;
combined coverage 89.98%, branch-only 85.85%. This is no new hosted code pass.
**Phase 22 remains incomplete.** Git remains 312/1,040 incomplete; paid benchmark
and pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged. No merge,
ready-state change, release, outreach or Phase 23 is authorized.

'''
docs = list(read(OLD/'documentation-binding.json')['owning_docs_sha256'])
heading = '## Current v54 sampled timeout: source-only decision pending'
for name in docs:
    path = ROOT/name
    text = path.read_text()
    assert text.count(heading) == 1, name
    path.write_text(text.replace(heading, status+heading.replace('Current','Historical',1),1))
save('owning-docs.json', {'sha256':{name:sha(ROOT/name) for name in docs}})
print('Preserved283 prior rows;290 total; candidate reverted, narrowed proposal unapproved.')
