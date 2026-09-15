"""Validate the retained single profile and attribute samples without rerunning."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = OUT.parents[3]
PREP = BASE/'v46-four-source-regression'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

p = read(PREP/'diagnostic-proposal.json')
approval = read(PREP/'diagnostic-authorization.json')
assert approval['approved'] and approval['proposal_sha256'] == sha(PREP/'diagnostic-proposal.json')
assert approval['scanner'] == p['scanner'] and approval['bounds'] == p['bounds']
for name, digest in p['files_sha256'].items():
    assert sha(ROOT/name) == digest, name
assert sha(OUT/'sampling-worker.py') == sha(PREP/'sampling-worker.py')
attempt = read(OUT/'attempt.json')
execution = read(OUT/'execution.json')
assert attempt['proposal_sha256'] == sha(PREP/'diagnostic-proposal.json')
assert attempt['approval_sha256'] == sha(PREP/'diagnostic-authorization.json')
assert attempt['scanner'] == p['scanner'] and attempt['total_input_executions'] == 1
assert execution['budget_closed'] and execution['remaining'] == 0
assert read(OUT/'budget-closed.json')['budget_closed']
timing = execution['timing']
assert timing['cleanup_verified'] and not timing['remaining_group_killed']
assert timing['elapsed_including_cleanup_seconds'] - timing['elapsed_seconds'] <= 15
results = read(OUT/'measurement/results.json')
assert results['scanner'] == p['scanner'] and results['manifest_sha256'] == p['manifest_sha256']
assert results['authorization_sha256'] == sha(Path(p['frozen_checkout'])/p['source_freeze_approval'])
assert results['model_calls'] == 0 and not results['requests']
assert len(results['outcomes']) == 1
outcome = results['outcomes'][0]
assert outcome['input_id'] == 'faf-read-root-vulnerable' and outcome['configuration_sha256'] == p['input']['configuration_sha256']
assert outcome['state'] == 'incomplete' and timing['timed_out']
assert not list((OUT/'measurement').glob('*/report.*'))
files = {}
rows = []
for path in sorted(OUT.glob('SENT-*-cpu-samples.json')):
    d = read(path)
    frames = {f['id']: f for f in d['frame_catalog']}
    assert len(frames) == len(d['frame_catalog'])
    assert sum(s['count'] for s in d['stacks']) == d['samples'] > 0
    assert d['requested_hz'] == 100 and d['maximum_recorded_stack_frames'] == 1024
    assert not d['scanner_methods_modified'] and not d['source_values_or_locals_recorded']
    leaf, inclusive, constructors = Counter(), Counter(), Counter()
    merge = allocation = discovery = 0
    for f in frames.values():
        if f['filename'] in files:
            continue
        if f['filename'].startswith('<'):
            files[f['filename']] = {'kind': 'generated/interpreter frame', 'source_bytes_available': False}
        else:
            source = Path(f['filename'])
            assert source.is_file(), source
            files[str(source)] = {'sha256': sha(source), 'kind': 'scanner/sampler/dependency source'}
    for s in d['stacks']:
        assert s['count'] > 0 and s['frames'] and set(s['frames']) <= set(frames)
        stack = [frames[n] for n in s['frames']]
        key = lambda f: (f['filename'], f['function'], f['line'])
        leaf[key(stack[0])] += s['count']
        for k in {(f['filename'], f['function']) for f in stack}:
            inclusive[k] += s['count']
        merge += s['count'] if any(f['filename'].endswith('/typescript_path_flow.py') and f['function'] == 'merge' for f in stack) else 0
        discovery += s['count'] if any(f['filename'].endswith('/typescript_registration_flow.py') and f['function'] == 'factory_tools' for f in stack) else 0
        if len(stack) > 1 and stack[0]['filename'] == '<string>' and stack[0]['function'] == '__init__':
            constructors[key(stack[1])] += s['count']
            if stack[1]['filename'].endswith('/typescript_path_flow.py') and stack[1]['function'] == 'merge' and stack[1]['line'] == 307:
                allocation += s['count']
    assert not d['events'].get('truncated_stacks', 0)
    rows.append({'rule': d['rule'], 'profile_sha256': sha(path), 'samples': d['samples'], 'snapshot_worker_cpu_seconds': d['worker_cpu_seconds'],
        'final_worker_snapshot': d['final_worker_snapshot'], 'signal_and_timer_state_restored': d['signal_and_timer_state_restored'],
        'events': d['events'], 'registration_inclusive_samples': discovery, 'registration_inclusive_percent': discovery/d['samples']*100,
        'merge_inclusive_samples': merge, 'merge_inclusive_percent': merge/d['samples']*100,
        'merge_fallback_constructor_leaf_samples': allocation, 'merge_fallback_constructor_leaf_percent': allocation/d['samples']*100,
        'maximum_observed_depth': max(len(s['frames']) for s in d['stacks']),
        'leaf_frames': [{'filename': k[0], 'function': k[1], 'line': k[2], 'count': count} for k, count in leaf.most_common()],
        'inclusive_functions': [{'filename': k[0], 'function': k[1], 'count': count} for k, count in inclusive.most_common()],
        'generated_constructor_callers': [{'filename': k[0], 'function': k[1], 'line': k[2], 'count': count} for k, count in constructors.most_common()]})
assert {r['rule'] for r in rows} == {'SENT-012', 'SENT-014', 'SENT-015', 'SENT-016'}
write('frame-source-bindings.json', files)
write('sample-attribution.json', {'rows': rows, 'source_binding_sha256': sha(OUT/'frame-source-bindings.json'),
    'qualification': 'Leaf counts partition each worker snapshot. Inclusive function counts overlap and are never summed as independent costs. Percentages are sample shares, not exact CPU fractions or achievable speedups.'})
source = Path(p['frozen_checkout'])/'src/sentinel/static/typescript_path_flow.py'
lines = source.read_text().splitlines()
assert 'Value(key=root)' in lines[306]
write('source-assessment.json', {'path': str(source), 'sha256': sha(source), 'lines': {str(n): lines[n-1] for n in range(302, 340)},
    'measured_path': 'All four workers enter TypeScriptProgram.tools -> factory_tools -> RegistrationFlow.initialize -> shared expression/function/statement traversal. Branch merge is a substantial inclusive sample concentration; generated Value.__init__ directly called at merge line307 is a separately counted leaf concentration.',
    'source_fact': 'For every record-state name with a known root, merge constructs Value(key=root) before dictionary get, even when every branch already contains the name and none of those gets consumes the fallback. The frozen dataclass is immutable. Skipping construction only when all branches contain the name can preserve all selected values, branch order, guard handling and missing-record defaults. Samples contain no locals and do not measure how many of these allocations were unused.',
    'proposed_boundary': 'A single source-only optimization of this fallback construction is justified for investigation; measured samples alone establish neither a guaranteed speedup nor completion within300seconds. Do not alter traversal breadth, guard/value semantics, source labels, warnings or timeout policy.',
    'other_source': {'src/sentinel/static/path_flow.py': sha(Path(p['frozen_checkout'])/'src/sentinel/static/path_flow.py'), 'src/sentinel/static/typescript_registration_flow.py': sha(Path(p['frozen_checkout'])/'src/sentinel/static/typescript_registration_flow.py')},
    'optimization_attempts': 0, 'source_modified': False, 'target_execution': False})
assessment = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'scanner': p['scanner'], 'proposal_sha256': sha(PREP/'diagnostic-proposal.json'),
    'approval_sha256': sha(PREP/'diagnostic-authorization.json'), 'validation_passed': True, 'profile_attempts': 1, 'completed_inputs': 0, 'incomplete_inputs': 1,
    'timing': timing, 'harness_outcome': outcome, 'report_count': 0, 'finding_count': None, 'warning_count': None, 'surface_count': None,
    'source_assessment_complete_for_retained_outputs': True, 'sample_rows': [{k: v for k, v in r.items() if k not in ['leaf_frames', 'inclusive_functions', 'generated_constructor_callers']} for r in rows],
    'assessment_sha256': {n: sha(OUT/n) for n in ['sample-attribution.json', 'source-assessment.json', 'frame-source-bindings.json']},
    'remaining': 0, 'budget_closed': True, 'optimization_attempts': 0, 'uninstrumented_observations': 0, 'retries': 0, 'comparators': 0, 'paid_calls': 0,
    'target_execution': False, 'original_regression204remain_closed': True, 'technical_acceptance_received': False, 'phase22_complete': False,
    'qualification': 'One partial instrumented input, not a native timing/condition or fresh pass. Mandatory cleanup may kill workers before final snapshots; prior periodic files retain only their covered intervals. Timer/GIL/native-code delivery, snapshot overhead and unsampled parent stages limit attribution. No observed samples are claimed wholly removable.'}
write('assessment.json', assessment)
print(json.dumps({'timing': timing, 'workers': assessment['sample_rows'], 'budget_closed': True}, indent=2))
