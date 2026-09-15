"""Retain the stopped outcome and prepare a separately approved diagnostic."""
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = OUT.parents[3]
PREVIOUS = BASE/'v52-merge-fastpath'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

p = read(PREVIOUS/'evaluation-proposal.json')
v = read(OUT/'validation.json')
packet = read(OUT/'raw/packet.json')
assert v['validation_passed'] and not v['execution_gate_passed']
assert len(v['attempts']) == 1 and len(v['unstarted_closed']) == 204
attempt = v['attempts'][0]
assert attempt['state'] == 'incomplete' and not attempt['report_present']
assert attempt['timing']['timed_out'] and attempt['timing']['cleanup_verified']
assert attempt['timing']['elapsed_including_cleanup_seconds'] - attempt['timing']['elapsed_seconds'] < 15
item = p['groups']['faf-read-root']['inputs']['faf-read-root-vulnerable']
results_path = OUT/'raw'/attempt['directory']/'results.json'
results = read(results_path)
assert results['scanner'] == p['scanner']
assert results['manifest_sha256'] == p['groups']['faf-read-root']['manifest_sha256']
assert results['authorization_sha256'] == sha(ROOT/p['groups']['faf-read-root']['source_freeze_approval'])
assert results['model_calls'] == 0 and not results['requests']
assert len(results['outcomes']) == 1 and results['outcomes'][0]['state'] == 'incomplete'
assert results['outcomes'][0]['configuration_sha256'] == item['configuration_sha256']
assert results['outcomes'][0]['reason'] is None
assert not list((OUT/'raw').glob('*/*/report.*'))
assert read(OUT/'owned-work.json')['owned_processes'] == []
assessment = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'scanner': p['scanner'],
    'approval_sha256': sha(PREVIOUS/'evaluation-authorization.json'), 'validation_sha256': sha(OUT/'validation.json'),
    'execution_gate_passed': False, 'source_assessment_complete_for_retained_outputs': True,
    'budget': {'planned': 205, 'attempted': 1, 'completed': 0, 'incomplete': 1, 'unstarted_closed': 204, 'remaining': 0, 'closed': True},
    'input': item['input'], 'attempt': attempt, 'harness_results_sha256': sha(results_path),
    'whole_seconds': attempt['timing']['elapsed_seconds'],
    'whole_including_cleanup_seconds': attempt['timing']['elapsed_including_cleanup_seconds'],
    'harness_wall_duration_ms': results['outcomes'][0]['wall_duration_ms'],
    'sequence_seconds': read(OUT/'execution.json')['timing']['elapsed_seconds'],
    'report_count': 0, 'finding_count': None, 'warning_count': None, 'surface_count': None,
    'named_detection': None, 'negative_discrimination': None, 'ordered_repeat_pairs': 0,
    'source_explanation': 'The whole-input supervisor reached300seconds and sent SIGTERM. Its handler raises SystemExit; measure initializes an incomplete entry with reasonNone and writes results in finally. SystemExit bypasses exceptException, explaining the preserved incomplete/null reason and absence of report files. This is not a completed native exit3 report or zero-finding result. No current retained stack or stage trace establishes the expensive operation. The earlier v51 profile is bound to6e4fd67 before the equal-value fast-path reorder; it cannot establish residual costs at a36f696. The new native timeout does not quantify the effect size of this change. The earlier17b4784 profile and invalid interrupted stale-root attempt remain historical only.',
    'source_bindings': {n: sha(ROOT/n) for n in ['scripts/phase20_measurements.py', 'src/sentinel/static/engine.py', 'src/sentinel/static/workers.py', 'artifacts/phase22/integration/v20-linux-diagnostic-v1/runner.py', 'artifacts/phase22/integration/v43-four-fresh-preparation/runner.py']},
    'resource_interpretation': 'Retained child resource totals include concurrent workers. Their summed CPU exceeds wall time; that is not the elapsed input duration or proof of a particular hotspot. No profile, stack sampling or target execution occurred.',
    'compatibility': 'All181prior-language observations and23remaining four-source observations were unstarted and closed. Current source compatibility and corrected four-source discrimination remain unestablished. Prior TS94/Python87/whole Linux results retain original scanner identities.',
    'original_fresh_four_gates_unchanged': True, 'original_fresh_four_gates_passed': 0,
    'paid_calls': 0, 'profiles': 0, 'retries': 0, 'target_execution': False,
    'technical_acceptance_received': False, 'phase22_complete': False}
assessment['prior_profile'] = {'path': 'artifacts/phase22/integration/v51-faf-bound-sampling/assessment.json', 'sha256': sha(BASE/'v51-faf-bound-sampling/assessment.json'), 'scanner_revision': '6e4fd671a97d92f6297dffc900c4dd9e18faad2c', 'current_residual_cost_established': False}
assessment['fastpath_candidate'] = {'synthetic_validation_sha256': sha(PREVIOUS/'synthetic-validation.json'), 'optimization_budget_closed_sha256': sha(PREVIOUS/'optimization-budget-closed.json'), 'synthetic_equivalence_retained': True, 'native_completion_established': False, 'speedup_established': False}
write('assessment.json', assessment)

write('budget-closed.json', {**assessment['budget'], 'budget_closed': True, 'approval_sha256':sha(PREVIOUS/'evaluation-authorization.json'), 'paid_calls':0})
old_profile=BASE/'v50-faf-allocation-sampling'
proposal=read(old_profile/'diagnostic-proposal.json')
proposal.update(scanner=p['scanner'],lock_sha256=p['lock_sha256'],frozen_checkout=p['frozen_checkout'],input=item,manifest_sha256=p['groups']['faf-read-root']['manifest_sha256'],source_freeze_approval=p['groups']['faf-read-root']['source_freeze_approval'],
 purpose='Determine remaining scanner costs on the same FAF vulnerable input after the approved equal-value fast-path candidate still reached300seconds without a report. Earlier v51 samples measure6e4fd67 before this reorder; the current native outcome has no stack or stage attribution. This proposes one new current-source diagnostic, not another optimization or regression retry.',
 command=['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OUT/'diagnostic.py')],output=str(BASE/'v54-faf-fastpath-sampling'),
 instrumentation='Reuse the previously validated100Hz stdlib CPU-timer worker sampler, same rule set, worker layout and300-second limit. Bind import root to frozena36f696; verify actual worker/flow paths and complete scanner source/harness/revision before starting the timer or reading target snapshots. Parent preflight runs an isolated worker identity check before consuming the token; every real worker retains its identity receipt. No scanner method replacement, locals or source values. Identity checks and sampling overhead remain inside the unchanged limit.',
 interpretation='CPU-timer/GIL/native-code delivery and snapshot overhead bias attribution. Overlapping stack shares are not independent/additive costs or guaranteed savings; this profile cannot establish native speedup or regression success. If a report completes, validate JSON/SARIF and compare the complete ordered report with the original2e0efb2 reference after only11established volatile exclusions; source-assess all changes. This nativea36f696 timeout produced no report baseline. Per-worker receipts must all bind a36f696; absent or mismatched identities invalidate attribution. Earlier v47/v51 partial samples retain17b4784/6e4fd67; the invalid v50 attempt remains unusable.',
 environment='Existing locked local macOS environment and frozena36f696 source; no dependency, resource, parallelism or deadline change and no overlapping owned heavy work.',
 stop='At most one attempted input, including timeout, interruption or worker-identity failure. Fail before consumption on parent preflight mismatch. Preserve partial outputs and close the one-use budget on every attempted outcome. No automatic retry, optimization, resource/deadline change or reopened regression/profile budget.')
files=[PREVIOUS/n for n in ['evaluation-proposal.json','evaluation-authorization.json','execution-consumed.json','evaluate.py','authorization.json','synthetic-validation.json','optimization-budget-closed.json']]
files += [OUT/n for n in ['corrected-sampling-worker.py','diagnostic.py','sampler-selfcheck.py','sampler-selfcheck/packet.json','assessment.json','validation.json','budget-closed.json','raw/packet.json','execution.json','assess-and-prepare.py']]
files += [BASE/n for n in ['v43-four-fresh-preparation/runner.py','v20-linux-diagnostic-v1/runner.py','v51-faf-bound-sampling/assessment.json','v51-faf-bound-sampling/source-assessment.json','v50-faf-allocation-sampling/assessment.json']]
proposal['files_sha256']={str(f.relative_to(ROOT)):sha(f) for f in files}
proposal['sampler_reuse']={'prior_proposal_sha256':sha(old_profile/'diagnostic-proposal.json'),'prior_sampler_sha256':sha(old_profile/'corrected-sampling-worker.py'),'allowed_changes':'Only current frozen root/revision/source identity and output/asset paths. All sampling, snapshot, timer restoration, bounds and identity-before-target logic unchanged. Stale6e4fd67 negative control rejects before timer/target access.'}
assert proposal['bounds']==read(old_profile/'diagnostic-proposal.json')['bounds']
write('diagnostic-proposal.json',proposal)
print('Assessed first-input timeout and204closed observations; prepared one unapproved300-second current-source profile.')
