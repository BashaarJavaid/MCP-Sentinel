"""Retain every prior requirement while recording the approved longer timeout."""
import copy
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = Path.cwd()
OLD = BASE/'v58-credential-regression'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value):
    with (OUT/name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')

local = read(OUT/'local-checks.json')
quality = read(BASE/'v59-candidate-quality-audit/packet.json')
proposal = read(OUT/'evaluation-proposal.json')
freeze = read(OUT/'freeze.json')
assert local['states'] == {'passed': 2403, 'skipped': 36}
assert len(quality['quality']) == 12 and proposal['scanner'] == freeze['scanner']
assert read(OUT/'timeout-confirmation.json')['maximum_seconds'] == 1800
assert not (OUT/'evaluation-authorization.json').exists()
assert not (BASE/'v60-long-timeout-regression').exists()
assert not (BASE/'v59-faf-credential-sampling').exists()
old = read(OLD/'audit.json')
rows = copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
    if row['id'] == 'V58-DELIVERY':
        row['previous_row'] = copy.deepcopy(row)
        assert read(OLD/'delivery-verification.json')['passed']
        row.update(disposition='passed', evidence=[str((OLD/'delivery-verification.json').relative_to(ROOT))], assessment='Exact draft delivery b168738 verified. This closes delivery only, not the failed regression or human technical acceptance.')
new = [
    ('V59-AUTH', 'Bind the prospective timing-policy revision and explicit 30-minute preference', 'passed', ['authorization.json', 'timeout-confirmation.json']),
    ('V59-SOURCE', 'Prove the single shared deadline change and preserve detector, cleanup and source contracts', 'passed', ['source-proof.json', 'source-checkpoint.json']),
    ('V59-ENGINEERING', 'Complete actual-source local and hosted engineering including deadline boundary tests and packages', 'passed', ['local-checks.json', '../v59-candidate-quality-audit/packet.json']),
    ('V59-CAPTURES', 'Verify six zero-call production replays and approved runtime/image compatibility', 'passed', ['compatibility.json', 'demo-validation.json', '../v59-production-capture-revalidation/packet.json']),
    ('V59-FREEZE', 'Freeze verified source and validate all unchanged exposed inputs and configurations', 'passed', ['freeze.json', 'frozen-source-validation.json']),
    ('V59-REGRESSION-PREPARATION', 'Prepare the exact 205-observation longer-timeout proposal and verified supervisor', 'passed', ['evaluation-proposal.json', 'scoring-rubric.json', 'runner-boundaries.json', 'launcher-binding.json']),
    ('V59-REGRESSION-DECISION', 'Obtain separate exact numerical approval before current-source corpus execution', 'unresolved', ['evaluation-proposal.json']),
    ('V59-CHECK-RETENTION', 'Retain actual check outcomes and preserve all prior failed measurements and closed budgets', 'passed', ['check-failure-assessment.json']),
    ('V59-DELIVERY', 'Seal evidence and verify reconciled documentation delivery to the existing draft', 'unresolved', []),
]
for identity, requirement, disposition, evidence in new:
    rows.append({'id': identity, 'requirement': requirement, 'disposition': disposition,
                 'evidence': [str((OUT/name).resolve().relative_to(ROOT)) for name in evidence],
                 'assessment': 'The approved timeout policy is prospective. Engineering/source prerequisites pass; new numerical evaluation and Phase 22 acceptance remain separate. Earlier failed gates retain their original outcomes.'})
audit = copy.deepcopy(old)
audit['historical_v58_status_fields'] = {k: copy.deepcopy(v) for k, v in old.items() if k not in {'requirements', 'additional_scope_requirements'} and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(), source=freeze['scanner']['revision'], scanner_identity=freeze['scanner'], candidate_scanner=freeze['scanner'], hosted_quality='v59-candidate-quality-audit/packet.json', additional_scope_requirements=rows, additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)), prior_audit={'path': str((OLD/'audit.json').relative_to(ROOT)), 'sha256': sha(OLD/'audit.json')}, engineering_passed=True, regression_prepared=True, regression_approved=False, regression_executed=False, current_regression_prepared=True, current_regression_approved=False, current_regression_executed=False, proposed_native_observations=205, current_source_corpus_observations=0, current_source_completed_observations=0, current_source_incomplete_observations=0, unstarted_closed=0, remaining=0, budget_closed=True, execution_gate_passed=None, diagnostic_prepared=False, diagnostic_approved=False, diagnostic_executed=False, current_diagnostic_prepared=False, current_diagnostic_approved=False, current_diagnostic_executed=False, diagnostic_budget_closed=True, diagnostic_attempts=0, diagnostic_remaining=0, valid_current_source_profiles=0, optimization_prepared=False, optimization_approved=False, optimization_attempts=0, optimization_synthetic_verified=False, current_optimization_prepared=False, current_optimization_approved=False, current_optimization_attempts=0, optimization_budget_closed=True, optimization_remaining=0, timeout_policy_revision_approved=True, maximum_input_seconds=1800, target_seconds=120, target_is_informational=True, candidate_retained_in_product=True, current_budget_interpretation='Approved timeout-policy source change and engineering are complete. No current-source corpus/profile budget has been approved or consumed. The proposed 205 observations are new permission, not a reopened remainder. The pending v58 diagnostic is superseded as next step, preserved unapproved and unexecuted.', acceptance_packet_ready=False, technical_acceptance_requested=False, technical_acceptance_received=False, phase22_complete=False, new_paid_calls=0, status='Verified 30-minute shared static deadline at 7bf4c6e, with 2403 tests / 36 skips locally and all 12 hosted suites. Detector logic is unchanged from dc73715. A 205-observation exposed regression is prepared, unapproved and unexecuted. All earlier failures and closed budgets remain preserved; Phase 22 incomplete.')
audit['current_evidence'] = {name: sha(OUT/name) for name in ['authorization.json', 'timeout-confirmation.json', 'source-proof.json', 'local-checks.json', 'freeze.json', 'evaluation-proposal.json', 'runner-boundaries.json', 'launcher-binding.json', 'check-failure-assessment.json']}
assert len(old['requirements']) == 89 and len(rows) == 234
assert audit['additional_scope_dispositions'] == {'passed': 213, 'unresolved': 15, 'proposed documented limitation awaiting decision': 6}
for previous, current in zip(old['requirements']+old['additional_scope_requirements'], audit['requirements']+rows):
    assert previous == current or current.get('previous_row') == previous
save('audit.json', audit)
save('prior-row-preservation.json', {'retained_prior_rows': 314, 'total_rows': 323, 'prior_audit_sha256': sha(OLD/'audit.json'), 'updated_rows': ['V58-DELIVERY'], 'rows': {r['id']: hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
summary = f'''# Thirty-minute static deadline verified; evaluation approval pending

The user's `yes do that.` instruction authorized a longer finite timeout policy, followed by the explicit **30 minutes** preference. The shared static limit is now **1,800 seconds** at scanner `{proposal['scanner']['revision']}`; 120 seconds remains an informational target. Completion within the new ceiling is required. Earlier five-minute failures remain failed at their actual limits. **Phase 22 is incomplete.**

[Source proof](source-proof.json) establishes one product AST literal change: `STATIC_TIMEOUT_SECONDS` changes from 300 to 1800. The orchestrator starts this shared deadline before TypeScript discovery; engine, workers, parser and report assembly use its remaining time, and an earlier caller deadline still wins. Existing Semgrep sublimits, model/dynamic limits and cleanup behavior are unchanged. No detector, suppression, source configuration or worker-count change occurs. Boundary tests use mocked time and retain deadline/cleanup failure checks.

[Local engineering](local-checks.json) and all 12 Linux/macOS/Windows × Python 3.10–3.13 suites pass **2,403 tests / 36 skips**; 248 focused tests pass. All 29 normal jobs pass in [CI 34784085204](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34784085204), and [docs 34784085193](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34784085193) pass. Local combined statement/branch coverage is **{local['coverage_totals']['percent_covered']:.2f}%**, branch-only **{local['coverage_totals']['percent_branches_covered']:.2f}%**. Hosted merge `aa28ae250a411ba1773e919ad39fc656de842b8c` has the complete candidate tree `128ac9f09c4463680a0ca8fbec201df028bd41d1`. Four optional Phase 22 corpus jobs are skipped. Normal CI's historical reproductions remain pinned to `8824014`, not current-source corpus observations.

Ruff, format, strict mypy, lock, schemas, notices, dependency audit, offline artifacts, docs, wheel/sdist member checks, installed-wheel platform checks and Docker/isolation checks pass. Six production requests regenerate and checked-replay with unchanged fingerprints/full request hashes and **zero live model calls**. The authorized scanner-owned Docker fixture completes 20/20 attempts with 14 findings. All 19 Git runtime component hashes and the approved image remain unchanged; no Git campaign runs. [Check assessment](check-failure-assessment.json) retains actual verification outcomes. Earlier restored files and selective Docker cleanup remain preserved.

The [frozen source](freeze.json) has source SHA-256 `{proposal['scanner']['source_sha256']}`, harness `{proposal['scanner']['harness_sha256']}` and unchanged lock `{proposal['lock_sha256']}`. No corpus input has run at this scanner.

[The exact evaluation proposal](evaluation-proposal.json), SHA-256 `{sha(OUT/'evaluation-proposal.json')}`, is **unapproved and unexecuted**: one serial local macOS sequence, **205 exposed native observations** over 110 unique records and 95 entire ordered pairs. It retains 24 original four-repository observations, 94 TypeScript and 87 Python observations. Fifteen Python development records run once. Sources, configurations, labels, prerequisites, named-condition/negative-support gates and the established 11 volatile exclusions are unchanged. All 110 source records are validated without executing them.

Each input has a 120-second informational target, **30-minute native/whole ceiling** and 15-second cleanup limit. The outer sequence cap is **6,275 minutes (104 hours 35 minutes)**, with a 6,274-minute internal stop: 205 × 30 minutes plus the prior 125-minute reserve. **This is a worst-case cap, not a runtime estimate or a required wait.** Each completed scan returns immediately. Infrastructure, execution, timeout, identity/schema, cleanup or ordered-repeat failures close every unused observation. Detection/negative-support failures remain collected results for source assessment. There are zero retries, profiles, comparators, new repositories, target executions, hosted evaluation dispatches or paid calls.

[Runner boundary checks](runner-boundaries.json) verify the precise deadline-only change, eight synthetic deadline cases and existing condition/process-supervisor controls. The historical 300-second helper remains intact. The launcher requires a new exact proposal/runner/scanner/bounds authorization before creating output or a launch token. The prior v58 sampled-input proposal remains unapproved and unexecuted, superseded only as the next planned action.

All four first-input native timeouts remain preserved: `17b4784` at 300.002159 seconds, `6e4fd67` at 300.004111, `a36f696` at 300.000481 and `dc73715` at 300.005621. Each had one incomplete, no report and 204 unstarted closed. No-report findings, diagnostics and detection are unknown, not zero. The 86,659 / 79,307 / 78,769 partial profiles retain their actual sources; the stale-root v50 attempt remains unusable. Both singleton equivalence failures remain unresolved and reproduced; the later explicitly authorized credential correction is separately verified. The timing revision establishes neither a speedup nor current-source detection compatibility.

The original four-repository fresh result stays **24 completed / 12 equal pairs, all four gates failed at `2e0efb2`**: FAF actual read unsupported; no-bash vulnerable detection plus two fixed/control false alerts per batch; Lightning actual get and Engram named manifest write unresolved. Later corrections and this proposed execution are exposed regression. TS 94 at `2e0efb2`, Python 87 at `8c62567`, and whole 25 development reuse plus 45+45 Linux at `1f3f72f` retain their actual evidence and Meta operator erratum. Language subsets never become a new whole historical/development run.

Original memory-keeper false alerts, DDG's unsupported fixed send and erroneous TypeScript manifest label despite actual Python configuration, Lighthouse misses, and held-out 10 completed / 10 unsupported / five incomplete with zero hits among four completed vulnerable inputs out of ten vulnerable total remain unchanged. Same-agent curation/review is not independent human validation, training-data novelty, broad accuracy or runtime safety proof.

The [audit](audit.json) preserves all **314 prior rows**, adding nine for **323 total (89 original + 234 added)**. Original rows remain 84 passed, two user-deferred, two proposed limitations and one human acceptance pending. Added rows are 213 passed, six unaccepted historical closure proposals and 15 unresolved before supplemental delivery verification. No failed gate is silently waived or relabeled as a historical pass.

Git remains **312/1,040 incomplete**, with 728 deferred. Paid benchmark/pilots remain deferred; Phase 21 incomplete and Phase 24/15 unchanged. Historical two paid calls cost $0.071799; this continuation adds zero. New evaluation approval, actual results/source assessment, explicit human technical acceptance and accepted closeout remain. No merge, ready-state change, release, outreach or Phase 23 is authorized.
'''
with (OUT/'summary.md').open('x') as f: f.write(summary)
url = 'https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v59-timeout-policy/'
body = f'''The shared static deadline is now 30 minutes, as requested. The prior five-minute limit stopped the first FAF input before a report could be assessed. Detector logic is unchanged; earlier failures remain preserved.

At `7bf4c6e`, local and all 12 hosted suites pass 2,403 tests / 36 skips; all 29 normal jobs and docs pass. Six production requests replay with zero paid calls. [Full source and engineering assessment]({url}summary.md).

[The frozen proposal]({url}evaluation-proposal.json) awaits exact approval: 205 exposed observations, 30 minutes per input, a 104h35m worst-case sequence cap, no retries/profiles/comparators/target execution/paid calls. This cap is not a runtime estimate. The original four fresh gates remain failed; no current-source corpus run has started.

[All 323 requirements]({url}audit.json) are retained. Phase 22 remains incomplete pending evaluation, source assessment, explicit human technical acceptance and accepted closeout. Git campaigns and paid benchmark/pilots remain deferred. This PR remains draft; no merge, ready-state change, release, outreach or Phase 23 is authorized.
'''
with (OUT/'pr-body.md').open('x') as f: f.write(body)
status = f'''## Current v59 timeout policy: engineering passed, evaluation pending

The user confirmed **30 minutes per input**. The shared static deadline is now
1,800 seconds at **`7bf4c6e`**, source `{proposal['scanner']['source_sha256']}`;
120 seconds remains informational. Source proof establishes one product AST
literal change; detector logic and cleanup are unchanged from `dc73715`.
Local and all 12 hosted suites pass **2,403 tests / 36 skips**; all 29 normal jobs
and docs pass in 34784085204 / 34784085193. Six production requests replay with
zero paid calls. Actual engineering and runtime bindings are retained.

`v59-timeout-policy/evaluation-proposal.json` is **unapproved and unexecuted**:
205 exposed observations, 110 input records, 95 ordered pairs; 30-minute input
ceiling, 15-second cleanup and 6,275-minute outer cap. This is a worst-case cap,
not a duration estimate. All original conditions, support requirements and
11 volatile exclusions remain. No retry, profile, comparator, new repository,
target execution or paid call. The pending v58 diagnostic is preserved unexecuted.

All four earlier native timeouts, partial/invalid profiles, singleton failures
and original fresh failures remain source-bound and unaccepted. No speedup,
current-source compatibility or new unseen-source discrimination is established.
The audit retains **323 rows (89 original + 234 added)**, including all 314 prior
rows and six unaccepted historical closure proposals. **Phase 22 is incomplete**:
actual regression, source assessment, explicit human acceptance and closeout remain.
Git stays 312/1,040 incomplete; paid benchmark/pilots deferred, Phase 21 incomplete
and Phase 24/15 unchanged. No merge, ready-state, release, outreach or Phase 23.

'''
heading = '## Current v58 credential regression timeout: budget closed'
docs = list(read(OLD/'documentation-binding.json')['owning_docs_sha256'])
for name in docs:
    path = ROOT/name
    text = path.read_text()
    assert text.count(heading) == 1, name
    path.write_text(text.replace(heading, status+heading.replace('Current', 'Historical', 1), 1))
policy = ROOT/'docs/phase22-timeout-policy.md'
text = policy.read_text()
text = text.replace('completed results at a longer supported limit. The initial implementation uses\n**1,800 seconds (30 minutes)** uniformly for deterministic static analysis.', 'completed results at a longer supported limit, then explicitly confirmed the\n**30-minute** preference. The implementation uses **1,800 seconds** uniformly\nfor deterministic static analysis.', 1)
policy.write_text(text)
save('owning-docs.json', {'sha256': {name: sha(ROOT/name) for name in docs}})
save('budget-closed.json', {'closed': True, 'source_policy_work_complete': True, 'scanner': proposal['scanner'], 'corpus_observations': 0, 'profiles': 0, 'paid_calls': 0, 'remaining_approved_observations': 0, 'proposed_not_approved_observations': 205, 'qualification': 'Policy implementation/engineering complete. No numerical budget authorized or consumed; all earlier remainders remain closed.'})
print('Retained all 314 prior rows; 323 total. Exact 205-observation proposal remains unapproved.')
