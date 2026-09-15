"""Preserve every requirement and reconcile only the completed uncapped experiment."""
import copy
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = OUT.parents[3]
PREV = BASE / 'v68-invalidation-sampling'
PREP = BASE / 'v69-uncapped-four-repository'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, value):
    with (OUT / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')

a = read(OUT / 'final-assessment/assessment.json')
old = read(PREV / 'audit.json')
correction = read(PREV / 'audit-current-status.json')
assert a['completed'] == 24 and a['source_assessment_complete'] and a['budget_closed']
assert a['entire_ordered_pairs_equal'] == 12 and not a['complete_report_difference_assessment_pending']
assert a['repository_gates_passed'] == 2 and not a['technical_acceptance_received']
assert correction['audit_sha256'] == sha(PREV / 'audit.json')
delivery = read(PREV / 'delivery-verification.json')
assert delivery['passed']
assert read(BASE / 'v70-compatible-reuse.json')['exit_code'] == 0
rows = copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
    if row['id'] == 'V68-DELIVERY':
        row['previous_row'] = copy.deepcopy(row)
        row.update(disposition='passed', evidence=[str((PREV / 'delivery-verification.json').relative_to(ROOT))], assessment='Actual 8f4c448 draft delivery verified; supplemental v68 audit-status correction remains explicit. This delivery was not Phase 22 technical acceptance.')
new = [
    ('V69-AUTH', 'Bind the explicit uncapped four-repository choice to one 24-observation scope, unchanged source and zero paid calls', 'passed', [PREP / 'intake.json', PREP / 'evaluation-authorization.json', PREP / 'execution-consumed.json']),
    ('V69-PREPARATION', 'Verify launcher-only uncapped behavior, finite cleanup, identity, missing-approval boundaries and unchanged ordinary policy', 'passed', [PREP / 'evaluation-proposal.json', PREP / 'execution-preflight.json', BASE / 'v69-synthetic-equivalence.json', BASE / 'v69-boundaries.json', BASE / 'v69-preparation-corrected.json', BASE / 'v69-approval-boundary-corrected.json']),
    ('V70-EXECUTION', 'Complete the sole approved 24 observations, packaged reports, 12 entire ordered pairs and verified closed-budget cleanup', 'passed', [OUT / 'execution.json', OUT / 'final-assessment/validation.json']),
    ('V70-TIMING', 'Record actual uncapped whole-input times without claiming normal-policy completion, native speedup or a revised shipped deadline', 'passed', [OUT / 'final-assessment/assessment.json', PREP / 'uncapped.py']),
    ('V70-SOURCE-ASSESSMENT', 'Assess every current finding, diagnostic, surface, context and complete ordered reference difference, preserving corrections and support limits', 'passed', [OUT / 'final-assessment/assessment.json', OUT / 'final-assessment/report-difference-assessment.json', OUT / 'first21-assessment/assessment-binding-check.json']),
    ('V70-FOUR-GATE', 'Establish all four current-source repository gates with actual named vulnerable detection and supported fixed/control discrimination', 'unresolved', [OUT / 'final-assessment/assessment.json']),
    ('V70-PRIOR-LANGUAGES', 'Establish necessary current-source compatibility for the earlier Python/TypeScript schedules under separate exact approval', 'unresolved', [PREP / 'evaluation-proposal.json', OUT / 'compatible-reuse.json']),
    ('V70-DELIVERY', 'Preserve all prior requirements, complete affected checks, seal the experiment and verify existing draft delivery', 'unresolved', []),
]
for identity, requirement, disposition, evidence in new:
    rows.append({'id': identity, 'requirement': requirement, 'disposition': disposition, 'evidence': [str(p.relative_to(ROOT)) for p in evidence], 'assessment': 'The 24-observation uncapped experiment completes with 12 entire ordered pairs. No-bash and Engram pass only their frozen narrow qualifiers; Lightning negative qualification and FAF named detection/support fail. Normal 1800-second policy and the 181 unexecuted earlier-language observations remain separate. No new optimization, profile, retry, target execution or paid call; no limitation or technical acceptance inferred.'})
assert len(old['requirements']) == 89 and len(old['additional_scope_requirements']) == 302 and len(rows) == 310
for before, after in zip(old['additional_scope_requirements'], rows):
    assert before == after or after.get('previous_row') == before
audit = copy.deepcopy(old)
audit['historical_v68_status_fields'] = {k: copy.deepcopy(v) for k, v in old.items() if k not in {'requirements', 'additional_scope_requirements'} and not k.startswith('historical_')}
audit.update(copy.deepcopy(correction['effective_current_status']))
audit['v68_status_correction'] = {'path': str((PREV / 'audit-current-status.json').relative_to(ROOT)), 'sha256': sha(PREV / 'audit-current-status.json'), 'applied_before_current_update': True}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(), additional_scope_requirements=rows, additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)), prior_audit={'path': str((PREV / 'audit.json').relative_to(ROOT)), 'sha256': sha(PREV / 'audit.json')}, proposed_native_observations=24, current_source_corpus_observations=25, current_source_completed_observations=24, current_source_incomplete_observations=1, unstarted_closed=0, remaining=0, budget_closed=True, execution_gate_passed=True, current_four_repository_gate_passed=False, current_four_repository_gates_passed=2, current_earlier_language_compatibility_established=False, current_diagnostic_prepared=False, current_diagnostic_approved=False, current_diagnostic_executed=False, current_optimization_approved=False, current_optimization_attempts=0, optimization_approved=False, optimization_attempts=0, optimization_synthetic_verified=False, optimization_budget_closed=False, acceptance_packet_ready=False, technical_acceptance_requested=False, technical_acceptance_received=False, phase22_complete=False, status='All 24 uncapped observations and 12 entire ordered pairs completed at 4145d35. Two narrow exposed gates pass; Lightning qualification and FAF detection/support fail. Measured FAF completions exceed the retained normal 1800-second policy. Earlier-language compatibility and technical acceptance remain unresolved.')
audit['current_source_input_accounting'] = {'prior_default_policy_native_regression': {'attempts': 1, 'complete': 0, 'incomplete': 1, 'unstarted_closed': 204, 'remaining': 0, 'budget_closed': True}, 'prior_sampled_diagnostic': {'attempts': 1, 'complete': 0, 'incomplete': 1, 'valid_partial_snapshots': 1, 'samples': 148001, 'remaining': 0, 'budget_closed': True}, 'uncapped_four_repository_experiment': {'attempts': 24, 'complete': 24, 'incomplete': 0, 'unstarted_closed': 0, 'remaining': 0, 'budget_closed': True, 'ordered_pairs': 12}, 'total_attempted_inputs': 26, 'native_attempts_total': 25, 'sampled_attempts_total': 1, 'qualification': 'Distinct one-use approvals at the same scanner; earlier timeout and profile remain unchanged. Unstarted 204 from the old sequence are closed, not permission for the separate unapproved 181 earlier-language observations.'}
audit['current_budget_interpretation'] = 'Only the user-selected 24-observation experiment ran in this continuation, once and without time caps. Its budget is closed with zero remaining. Shipped 1800-second default is unchanged. Pending literal serialization optimization remains unapproved/unopened, with zero attempts; no historical budget reopens.'
audit['experimental_timeout_policy'] = {'whole_input_limit_seconds': None, 'outer_sequence_limit_seconds': None, 'semgrep_rule_timeout_seconds': 0, 'finite_cleanup_preserved': True, 'normal_product_deadline_seconds': 1800, 'proposal_sha256': sha(PREP / 'evaluation-proposal.json')}
for row in audit['requirements'] + rows:
    entry = copy.deepcopy(old.get('current_requirement_interpretations', {}).get(row['id'], {}))
    entry.update(requirement=row['requirement'], historical_disposition=row['disposition'], current_execution_interpretation='Unchanged 4145d35 engineering remains verified. The separate uncapped four-repository experiment now supplies 24 complete reports and two narrow passes, with Lightning and FAF failures source-assessed. This neither completes earlier-language compatibility nor changes any historical measurement, approved limitation, or required human decision.', current_execution_evidence={'assessment_sha256': sha(OUT / 'final-assessment/assessment.json'), 'compatibility_sha256': sha(OUT / 'compatible-reuse.json')})
    audit['current_requirement_interpretations'][row['id']] = entry
assert len(audit['current_requirement_interpretations']) == 399
assert audit['additional_scope_dispositions'] == {'passed': 283, 'unresolved': 21, 'proposed documented limitation awaiting decision': 6}, audit['additional_scope_dispositions']
audit['current_evidence'] = {str(p.relative_to(OUT)): sha(p) for p in [OUT / 'execution.json', OUT / 'final-assessment/validation.json', OUT / 'final-assessment/assessment.json', OUT / 'compatible-reuse.json']}
write('audit.json', audit)
write('prior-row-preservation.json', {'prior_audit_sha256': sha(PREV / 'audit.json'), 'prior_status_correction_sha256': sha(PREV / 'audit-current-status.json'), 'retained_prior_rows': 391, 'total_rows': 399, 'updated_rows': ['V68-DELIVERY'], 'rows': {r['id']: hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest() for r in old['requirements'] + old['additional_scope_requirements']}})
faf = next(c for c in a['cases'] if c['case_id'] == 'faf-read-root')
status = f'''## Current v70 uncapped experiment: complete run, two failed gates

The user-approved **24-observation uncapped four-repository experiment** at
**`4145d35`** completed, with **all 12 entire ordered report pairs equal**,
verified cleanup and zero remaining budget. The 18 non-FAF observations took
6.28–10.72 seconds each. FAF took **{min(faf['timings_seconds']):.6f}–{max(faf['timings_seconds']):.6f}
seconds** per input. **{a['beyond1800']} observations exceeded the ordinary
1,800-second policy**, which remains unchanged; no speedup is established.

**No-bash and Engram pass their narrow exposed conditions**, retaining the exact
lexical/physical and initial-home/reconstructed-use qualifiers. **Lightning
fails fixed/safe qualification; FAF misses the vulnerable read and leaves both
negative paths unsupported.** All 260 findings, 52,492 diagnostic occurrences,
282 surfaces, 4,963 source contexts and full ordered reference differences are
source-assessed. The original fresh failures remain source-bound and unchanged.

The pending v68 literal-serialization optimization remains **unapproved and
unimplemented**. No source tuning, profile, retry, comparator, target execution
or paid call ran during this experiment. The earlier Python/TypeScript schedule's
**181 observations are outside this approval**; current compatibility is pending.

All **399 requirements (89 original + 310 added)** and all historical failures
remain, including the explicit v68 audit-status correction. Unchanged engineering
retains **2,419 tests / 36 skips** locally and in all 12 hosted suites, 29 normal
jobs and docs passed; combined coverage 90.08%, branch-only 85.92%. Six zero-call
production replays and approved runtime bindings remain. This is no new hosted
code pass, broad accuracy result, accepted limitation or independent validation.

**Phase 22 remains incomplete**, pending the failed current-source gates,
earlier-language compatibility, explicit human technical acceptance and accepted
closeout. Git stays 312/1,040 incomplete with 728 deferred; paid benchmark/pilots
are deferred, Phase 21 is incomplete, and Phase 24/15 are unchanged. No merge,
ready-state change, release, outreach or Phase 23 is authorized.

'''
heading = '## Current v68 invalidation profile: source-only decision pending'
docs = list(read(PREV / 'documentation-binding.json')['owning_docs_sha256'])
assert len(docs) == 16
for name in docs:
    path = ROOT / name
    text = path.read_text()
    assert text.count(heading) == 1, name
    path.write_text(text.replace(heading, status + heading.replace('Current', 'Historical', 1), 1))
write('owning-docs.json', {'sha256': {n: sha(ROOT / n) for n in docs}})
with (OUT / 'status.md').open('x') as f:
    f.write(status)
print('Preserved 391 prior requirements, 399 total; reconciled 16 owning docs. Two failed gates and separate technical acceptance remain unresolved.')
