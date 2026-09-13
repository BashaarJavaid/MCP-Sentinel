"""Retain the stopped outcome and prepare a separately approved diagnostic."""
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = OUT.parents[3]
PREVIOUS = BASE/'v48-merge-allocation'
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
    'source_explanation': 'The whole-input supervisor reached300seconds and sent SIGTERM. Its handler raises SystemExit; measure initializes an incomplete entry with reasonNone and writes results in finally. SystemExit bypasses exceptException, explaining the preserved incomplete/null reason and absence of report files. This is not a completed native exit3 report or zero-finding result. No current retained stack or stage trace establishes the expensive operation. The earlier v47 profile is bound to 17b4784 before the allocation predicate; it cannot establish residual costs at 6e4fd67. The new native timeout does not measure the effect size of the allocation change.',
    'source_bindings': {n: sha(ROOT/n) for n in ['scripts/phase20_measurements.py', 'src/sentinel/static/engine.py', 'src/sentinel/static/workers.py', 'artifacts/phase22/integration/v20-linux-diagnostic-v1/runner.py', 'artifacts/phase22/integration/v43-four-fresh-preparation/runner.py']},
    'resource_interpretation': 'Retained child resource totals include concurrent workers. Their summed CPU exceeds wall time; that is not the elapsed input duration or proof of a particular hotspot. No profile, stack sampling or target execution occurred.',
    'compatibility': 'All181prior-language observations and23remaining four-source observations were unstarted and closed. Current source compatibility and corrected four-source discrimination remain unestablished. Prior TS94/Python87/whole Linux results retain original scanner identities.',
    'original_fresh_four_gates_unchanged': True, 'original_fresh_four_gates_passed': 0,
    'paid_calls': 0, 'profiles': 0, 'retries': 0, 'target_execution': False,
    'technical_acceptance_received': False, 'phase22_complete': False}
assessment['prior_profile'] = {'path': 'artifacts/phase22/integration/v47-faf-sampling/assessment.json', 'sha256': sha(BASE/'v47-faf-sampling/assessment.json'), 'scanner_revision': '17b4784363f35096a13d33913e98967b24cbad14', 'current_residual_cost_established': False}
assessment['allocation_candidate'] = {'synthetic_validation_sha256': sha(PREVIOUS/'synthetic-validation.json'), 'optimization_budget_closed_sha256': sha(PREVIOUS/'optimization-budget-closed.json'), 'synthetic_equivalence_retained': True, 'native_completion_established': False, 'speedup_established': False}
write('assessment.json', assessment)
files = [PREVIOUS/'evaluation-proposal.json', PREVIOUS/'evaluation-authorization.json', PREVIOUS/'execution-consumed.json', PREVIOUS/'evaluate.py',
         OUT/'sampling-worker.py', OUT/'diagnostic.py', OUT/'sampler-selfcheck.py', OUT/'sampler-selfcheck/packet.json',
         OUT/'assessment.json', OUT/'validation.json', OUT/'raw/packet.json', OUT/'execution.json',
         BASE/'v43-four-fresh-preparation/runner.py', BASE/'v20-linux-diagnostic-v1/runner.py', BASE/'v47-faf-sampling/assessment.json', PREVIOUS/'synthetic-validation.json', PREVIOUS/'optimization-budget-closed.json']
proposal = {'status': 'prepared_not_approved_not_executed', 'scanner': p['scanner'], 'lock_sha256': p['lock_sha256'], 'frozen_checkout': p['frozen_checkout'],
    'input': item, 'manifest_sha256': p['groups']['faf-read-root']['manifest_sha256'], 'source_freeze_approval': p['groups']['faf-read-root']['source_freeze_approval'],
    'purpose': 'Locate residual scanner costs on the same FAF vulnerable input at 6e4fd67 after the approved allocation predicate still timed out. The v47 profile measured 17b4784 before that change; current native output has no stage or stack trace. Reuse the same bounded sampler to obtain current-source attribution before proposing any further optimization. No second optimization is authorized.',
    'command': ['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python', '-I', str(OUT/'diagnostic.py')],
    'initial_cwd': str(ROOT), 'output': str(BASE/'v50-faf-allocation-sampling'),
    'bounds': {'total_input_executions': 1, 'sampled_profiles': 1, 'uninstrumented_observations': 0, 'whole_input_maximum_seconds': 300,
               'normal_target_seconds': 120, 'cleanup_maximum_seconds': 15, 'cpu_timer_hz_per_worker': 100,
               'periodic_snapshot_seconds': 15, 'maximum_stack_frames': 1024, 'optimization_attempts': 0, 'retries': 0,
               'comparators': 0, 'paid_calls': 0, 'hosted_dispatches': 0, 'target_execution': False},
    'instrumentation': 'Reuse the previously validated stdlib ITIMER_PROF worker sampler at100Hz. Replace only the scanner-owned worker entry-point path with a wrapper calling the unchanged workers._worker. Capture filename/function/line/frame counts, never locals or source values. Same rule set, configuration, process layout and internal300-second deadline. No parent sampling or target execution; absence of worker samples leaves parent/stage attribution unresolved.',
    'partial_output': 'Retain atomic15-second snapshots even if workers are killed by the unchanged timeout cleanup. A killed worker may lack a final/restored-state snapshot; report that fact. Do not weaken cleanup, extend deadlines or claim a complete profile interval.',
    'interpretation': 'CPU-timer/GIL/native-code delivery and snapshot overhead bias sampling. Overlapping stacks are not additive independent costs or guaranteed removable work. The instrumented result is diagnostic, not a native timing/regression/fresh gate pass. If a report completes, validate it and compare ordered content to the original2e0efb2 reference with only the11 established volatile exclusions; source-assess every change. The stopped6e4fd67 attempt produced no report baseline.',
    'stop': 'One attempted input only, including timeout/incomplete/interruption. Fail closed before source execution on identity, approval or synthetic sampler mismatch. Preserve all partial output and close the one-use budget; no automatic optimization, rerun or reopening of the closed204 observations.',
    'environment': 'Existing locked local macOS environment; frozen6e4fd67 source; no dependency/resource/runner upgrade and no overlapping owned heavy work.',
    'files_sha256': {str(f.relative_to(ROOT)): sha(f) for f in files},
    'technical_acceptance_received': False, 'phase22_complete': False}
write('diagnostic-proposal.json', proposal)
print('Assessed one incomplete timeout and204closed observations; prepared one unapproved300-second worker profile, zero executions.')
