"""Validate the retained single profile and attribute samples without rerunning."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = OUT.parents[3]
PREP = BASE/'v67-invalidation-regression'
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
assert sha(OUT/'corrected-sampling-worker.py') == sha(PREP/'corrected-sampling-worker.py')
identities = {}
for path in sorted(OUT.glob('*-worker-identity.json')):
    identity = read(path)
    assert identity['scanner'] == p['scanner'] and identity['verified_before_timer_and_target_snapshot']
    assert identity['imports'] == {n: str(Path(p['frozen_checkout'])/('src/sentinel/static/'+n+'.py')) for n in ['workers','typescript_path_flow','typescript_discovery']}
    identities[path.name.removesuffix('-worker-identity.json')] = {'sha256': sha(path), **identity}
assert 'parent' in identities and identities['parent']['role'] == 'parent'
assert set(identities) <= {'parent','SENT-012','SENT-014','SENT-015','SENT-016'}
attempt = read(OUT/'attempt.json')
execution = read(OUT/'execution.json')
assert attempt['proposal_sha256'] == sha(PREP/'diagnostic-proposal.json')
assert attempt['approval_sha256'] == sha(PREP/'diagnostic-authorization.json')
assert attempt['scanner'] == p['scanner'] and attempt['total_input_executions'] == 1
token = read(PREP/'diagnostic-consumed.json')
assert token == {'proposal_sha256':sha(PREP/'diagnostic-proposal.json'),'approval_sha256':sha(PREP/'diagnostic-authorization.json'),'output':str(OUT),'attempts_consumed':1}
assert read(PREP/'diagnostic-preflight.json')['passed']
assert execution['budget_closed'] and execution['remaining'] == 0
assert read(OUT/'budget-closed.json')['budget_closed']
timing = execution['timing']
assert timing['cleanup_verified']
assert timing['elapsed_including_cleanup_seconds'] - timing['elapsed_seconds'] <= 15
results = read(OUT/'measurement/results.json')
assert results['scanner'] == p['scanner'] and results['manifest_sha256'] == p['manifest_sha256']
assert results['authorization_sha256'] == sha(Path(p['frozen_checkout'])/p['source_freeze_approval'])
assert results['model_calls'] == 0 and not results['requests']
assert len(results['outcomes']) == 1
outcome = results['outcomes'][0]
assert outcome['input_id'] == 'faf-read-root-vulnerable' and outcome['configuration_sha256'] == p['input']['configuration_sha256']
assert sha(OUT/'measurement'/outcome['input_id']/'configuration.json') == p['input']['configuration_sha256']
assert outcome['state'] == 'incomplete' and timing['timed_out'], 'Completed or differently failed input requires full report/output assessment before using this timeout validator.'
assert not list((OUT/'measurement').glob('*/report.*'))
files = {}
rows = []
for path in sorted(OUT.glob('*-cpu-samples.json')):
    d = read(path)
    assert path.name == d['rule']+'-cpu-samples.json' and d['rule'] in identities
    frames = {f['id']: f for f in d['frame_catalog']}
    assert len(frames) == len(d['frame_catalog'])
    assert sum(s['count'] for s in d['stacks']) == d['samples'] > 0
    assert all(isinstance(f['id'], int) for f in d['frame_catalog'])
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
            if stack[1]['filename'].endswith('/typescript_path_flow.py') and stack[1]['function'] == 'merge' and stack[1]['line'] == 329:
                allocation += s['count']
    assert d['worker_cpu_seconds'] >= d['sampling_started_cpu_seconds'] >= 0
    if d['final_worker_snapshot']:
        assert d['signal_and_timer_state_restored'] and d['sampling_ended_cpu_seconds'] is not None
    assert not d['events'].get('truncated_stacks', 0)
    rows.append({'rule': d['rule'], 'profile_sha256': sha(path), 'samples': d['samples'], 'snapshot_worker_cpu_seconds': d['worker_cpu_seconds'],
        'final_worker_snapshot': d['final_worker_snapshot'], 'signal_and_timer_state_restored': d['signal_and_timer_state_restored'],
        'sampling_started_cpu_seconds':d['sampling_started_cpu_seconds'], 'sampling_ended_cpu_seconds':d['sampling_ended_cpu_seconds'], 'retained_cpu_interval_seconds':d['worker_cpu_seconds']-d['sampling_started_cpu_seconds'], 'events': d['events'], 'registration_inclusive_samples': discovery, 'registration_inclusive_percent': discovery/d['samples']*100,
        'merge_inclusive_samples': merge, 'merge_inclusive_percent': merge/d['samples']*100,
        'merge_fallback_constructor_leaf_samples': allocation, 'merge_fallback_constructor_leaf_percent': allocation/d['samples']*100,
        'maximum_observed_depth': max(len(s['frames']) for s in d['stacks']),
        'leaf_frames': [{'filename': k[0], 'function': k[1], 'line': k[2], 'count': count} for k, count in leaf.most_common()],
        'inclusive_functions': [{'filename': k[0], 'function': k[1], 'count': count} for k, count in inclusive.most_common()],
        'generated_constructor_callers': [{'filename': k[0], 'function': k[1], 'line': k[2], 'count': count} for k, count in constructors.most_common()]})
assert {r['rule'] for r in rows} <= set(identities)
assert 'parent' in {r['rule'] for r in rows}
assert len(rows) <= 5
write('frame-source-bindings.json', files)
write('sample-attribution.json', {'rows': rows, 'source_binding_sha256': sha(OUT/'frame-source-bindings.json'),
    'qualification': 'Parent and worker denominators are separate. Legacy worker_cpu_seconds/final_worker_snapshot fields refer to the sampled process, including parent. Leaf counts partition each process snapshot. Inclusive function counts overlap and are never summed as independent costs. Percentages are sample shares, not exact CPU fractions or achievable speedups.'})
write('validation.json', {'passed':True,'scanner':p['scanner'],'process_identities':identities,'worker_identities':{k:v for k,v in identities.items() if k != 'parent'},'parent_identity':identities['parent'],'worker_coverage_qualification':'Actual identities and snapshots only. Missing workers do not prove dispatch never occurred; no worker cost is inferred from parent samples.','timing':timing,'harness_outcome':outcome,'profile_attempts':1,'completed_inputs':0,'incomplete_inputs':1,'report_count':0,'sample_snapshots':len(rows),'samples':sum(r['samples'] for r in rows),'budget_closed':True,'remaining':0,'paid_calls':0,'source_assessment_pending':True,'raw_sha256':{str(f.relative_to(OUT)):sha(f) for f in sorted(OUT.rglob('*')) if f.is_file() and (f.name.endswith('-cpu-samples.json') or f.name.endswith('-worker-identity.json') or f.name in ['execution.json','budget-closed.json','attempt.json','results.json','configuration.json','observation.log','corrected-sampling-worker.py'] or f.suffix == '.tmp')}})
print(json.dumps([{'rule':r['rule'],'samples':r['samples'],'merge_percent':r['merge_inclusive_percent'],'constructor_percent':r['merge_fallback_constructor_leaf_percent'],'leaf_top':r['leaf_frames'][:12]} for r in rows],indent=2))
