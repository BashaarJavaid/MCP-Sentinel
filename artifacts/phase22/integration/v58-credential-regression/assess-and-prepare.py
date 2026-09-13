"""Retain the stopped outcome and prepare a separately approved diagnostic."""
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = OUT.parents[3]
PREVIOUS = BASE/'v57-credential-merge'
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
    'source_explanation': 'The whole-input supervisor reached 300 seconds and sent SIGTERM. Its SystemExit handler bypasses except Exception while the finally writer retains an incomplete result with null reason. No native JSON/SARIF report exists; this is not a completed exit-3 or zero-finding result. No stack or stage trace from this attempt identifies the remaining expensive operation. The latest v54 profile measures a36f696 before the approved credential-join correction and canonical unknown bypass, so it cannot establish residual costs at dc73715. This timeout establishes failure to complete within the cap, not a measured speedup or slowdown.',
    'source_bindings': {n: sha(ROOT/n) for n in ['scripts/phase20_measurements.py', 'src/sentinel/static/engine.py', 'src/sentinel/static/workers.py', 'artifacts/phase22/integration/v20-linux-diagnostic-v1/runner.py', 'artifacts/phase22/integration/v43-four-fresh-preparation/runner.py']},
    'resource_interpretation': 'Retained child resource totals include concurrent workers. Their summed CPU exceeds wall time; that is not the elapsed input duration or proof of a particular hotspot. No profile, stack sampling or target execution occurred.',
    'compatibility': 'All181prior-language observations and23remaining four-source observations were unstarted and closed. Current source compatibility and corrected four-source discrimination remain unestablished. Prior TS94/Python87/whole Linux results retain original scanner identities.',
    'original_fresh_four_gates_unchanged': True, 'original_fresh_four_gates_passed': 0,
    'paid_calls': 0, 'profiles': 0, 'retries': 0, 'target_execution': False,
    'technical_acceptance_received': False, 'phase22_complete': False}
assessment['prior_profile'] = {'path':'artifacts/phase22/integration/v54-faf-fastpath-sampling/assessment.json','sha256':sha(BASE/'v54-faf-fastpath-sampling/assessment.json'),'scanner_revision':'a36f696c504e4e8d1f90de5dc84e8942d06316ca','current_residual_cost_established':False}
assessment['joint_correction'] = {'source_assessment_sha256':sha(PREVIOUS/'source-recovery-assessment.json'),'correction_validation_sha256':sha(PREVIOUS/'correction-validation.json'),'bypass_validation_sha256':sha(PREVIOUS/'synthetic-validation.json'),'engineering_sha256':sha(PREVIOUS/'local-checks.json'),'optimization_budget_closed_sha256':sha(PREVIOUS/'optimization-budget-closed.json'),'approved_semantic_delta_retained':True,'bypass_equivalence_to_correction_only_reference_retained':True,'old_state_equivalence_claimed':False,'native_completion_established':False,'speedup_established':False}
write('assessment.json',assessment)
write('budget-closed.json',{**assessment['budget'],'budget_closed':True,'approval_sha256':sha(PREVIOUS/'evaluation-authorization.json'),'paid_calls':0})
old_profile=BASE/'v53-fastpath-regression'
proposal=read(old_profile/'diagnostic-proposal.json')
proposal.update(scanner=p['scanner'],lock_sha256=p['lock_sha256'],frozen_checkout=p['frozen_checkout'],input=item,manifest_sha256=p['groups']['faf-read-root']['manifest_sha256'],source_freeze_approval=p['groups']['faf-read-root']['source_freeze_approval'],
 purpose='Identify remaining scanner costs on the same FAF vulnerable input after the approved credential-join correction and canonical UNKNOWN_VALUE bypass still reached 300 seconds without a report. Earlier v54 samples measure a36f696 before these two changes. This native attempt has no stack or stage attribution. Propose one current-source diagnostic, with zero optimization attempts or uninstrumented regression observations.',
 command=['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OUT/'diagnostic.py')],output=str(BASE/'v59-faf-credential-sampling'),
 instrumentation='Reuse the validated 100Hz stdlib CPU-timer worker sampler, existing rule set, worker layout and 300-second limit. Bind imports to frozen dc73715 and verify actual worker/flow paths plus complete source/harness/revision before timer setup or target snapshot access. Parent preflight checks an isolated worker before consuming a token; every real worker retains its identity receipt. No scanner method replacement, locals or source values. Identity and sampling overhead remain inside the unchanged limit.',
 interpretation='Signal/GIL/native-code delivery and snapshot overhead bias attribution. Overlapping stack shares are not additive costs or guaranteed savings; this profile does not establish native speedup or regression success. If a report completes, validate JSON/SARIF, compare the entire ordered report with the original 2e0efb2 reference after only the established 11 exclusions, and source-assess every change. The current native dc73715 timeout has no report baseline. Every worker must bind dc73715; absent or mismatched identities invalidate attribution. Earlier profiles retain their actual 17b4784/6e4fd67/a36f696 identities; the stale-root v50 attempt remains unusable.',
 environment='Existing locked local macOS environment and frozen dc73715 source. No dependency, resource, parallelism or deadline change; no overlapping owned heavy work.')
files=[PREVIOUS/n for n in ['evaluation-proposal.json','evaluation-authorization.json','execution-consumed.json','evaluate.py','authorization.json','correction-validation.json','synthetic-validation.json','source-recovery-assessment.json','optimization-budget-closed.json']]
files += [OUT/n for n in ['corrected-sampling-worker.py','diagnostic.py','sampler-selfcheck.py','sampler-selfcheck/packet.json','assessment.json','validation.json','budget-closed.json','raw/packet.json','execution.json','assess-and-prepare.py']]
files += [BASE/n for n in ['v43-four-fresh-preparation/runner.py','v20-linux-diagnostic-v1/runner.py','v54-faf-fastpath-sampling/assessment.json','v54-faf-fastpath-sampling/source-assessment.json','v50-faf-allocation-sampling/assessment.json']]
proposal['files_sha256']={str(f.relative_to(ROOT)):sha(f) for f in files}
proposal['sampler_reuse']={'prior_proposal_sha256':sha(old_profile/'diagnostic-proposal.json'),'prior_sampler_sha256':sha(old_profile/'corrected-sampling-worker.py'),'allowed_changes':'Only frozen root/revision/source identity and output/asset paths. Sampling, snapshot, timer restoration, bounds and identity-before-target logic unchanged. A stale a36f696 control rejects before timer or target access.'}
assert proposal['bounds']==read(old_profile/'diagnostic-proposal.json')['bounds']
write('diagnostic-proposal.json',proposal)
print('Assessed first-input timeout and 204 closed observations; prepared one unapproved 300-second current-source profile.')
