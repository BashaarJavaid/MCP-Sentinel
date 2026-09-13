"""Assess retained profile frames and source-established repeated discovery only."""
import ast
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = OUT.parents[3]
PREP = BASE/'v60-long-timeout-regression'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
p = read(PREP/'diagnostic-proposal.json')
v = read(OUT/'validation.json')
assert v['passed'] and v['sample_snapshots'] == 4 and v['samples'] > 0
assert read(OUT/'owned-work.json')['owned_processes'] == []
fixed = Path(p['frozen_checkout'])
metrics, contexts, source_lines, source_hashes = [], {}, {}, {}
for row in read(OUT/'sample-attribution.json')['rows']:
    d = read(OUT/(row['rule']+'-cpu-samples.json'))
    frames = {f['id']: f for f in d['frame_catalog']}
    leaf = Counter()
    callers = Counter()
    for frame in frames.values():
        filename = frame['filename']
        key = f"{filename}:{frame['first_line']}:{frame['function']}:{frame['line']}"
        if key in contexts:
            continue
        if filename.startswith('<'):
            contexts[key] = {'frame': frame, 'kind': 'generated/interpreter code; no retained source file'}
            continue
        source = Path(filename)
        if filename not in source_lines:
            source_lines[filename] = source.read_text().splitlines()
            source_hashes[filename] = sha(source)
        lines = source_lines[filename]
        assert 1 <= frame['line'] <= len(lines), frame
        contexts[key] = {'frame': frame, 'source_sha256': source_hashes[filename], 'kind': 'scanner' if filename.startswith(str(fixed/'src')) else 'sampler' if source == OUT/'corrected-sampling-worker.py' else 'dependency/interpreter', 'line_context': {str(i): lines[i-1] for i in range(max(1, frame['line']-2), min(len(lines),frame['line']+2)+1)}}
    for sample in d['stacks']:
        stack = [frames[n] for n in sample['frames']]
        top, count = stack[0], sample['count']
        if top['filename'].endswith('/path_flow.py') and top['function'] == 'combine':
            leaf['combine_entry'] += count
        if top['filename'].endswith('/typescript_path_flow.py') and top['function'] == '<genexpr>' and top['line'] == 318:
            leaf['merge_equal_predicate'] += count
        if top['filename'].endswith('/json/encoder.py'):
            leaf['json_encoder'] += count
            caller = next((f for f in stack if f['filename'].startswith(str(fixed/'src'))), None)
            if caller:
                callers[(caller['filename'], caller['function'], caller['line'])] += count
            else:
                leaf['json_encoder_without_scanner_caller'] += count
    metrics.append({k: row[k] for k in ['rule','samples','snapshot_worker_cpu_seconds','final_worker_snapshot','signal_and_timer_state_restored','registration_inclusive_samples','registration_inclusive_percent','merge_inclusive_percent','maximum_observed_depth']} | {'leaf_samples': dict(leaf), 'leaf_percent': {k: n/row['samples']*100 for k,n in leaf.items()}, 'json_encoder_scanner_callers': [{'filename': k[0], 'function': k[1], 'line': k[2], 'samples': n} for k,n in callers.most_common()]})
write('frame-contexts.json', contexts)
selected = {
 'src/sentinel/static/workers.py': ['run_flow_rules','_worker'],
 'src/sentinel/static/model.py': ['StaticContext'],
 'src/sentinel/static/typescript_discovery.py': ['TypeScriptProgram'],
 'src/sentinel/static/typescript_registration_flow.py': ['RegistrationFlow','factory_tools'],
 'src/sentinel/static/typescript_path_flow.py': ['analyze'],
 'src/sentinel/static/typescript_modules.py': ['TypeScriptModules'],
}
source_context = {}
for name, symbols in selected.items():
    source = fixed/name
    text = source.read_text()
    tree = ast.parse(text)
    source_context[name] = {'sha256': sha(source), 'definitions': [{'name': node.name,'line':node.lineno,'end_line':node.end_lineno,'source':ast.get_source_segment(text,node)} for node in tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in symbols]}
tool_calls = {}
for source in sorted((fixed/'src/sentinel/static').rglob('*.py')):
    text = source.read_text()
    tree = ast.parse(text)
    calls = [n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='tools']
    if calls:
        tool_calls[str(source.relative_to(fixed))] = {'sha256':sha(source),'calls':[{'line':n.lineno,'expression':ast.get_source_segment(text,n)} for n in calls]}
source_assessment = {
 'scanner':p['scanner'], 'source_context':source_context, 'all_static_tools_call_sites':tool_calls,
 'frame_contexts_sha256':sha(OUT/'frame-contexts.json'), 'sample_metrics':metrics,
 'source_fact':'run_flow_rules already parses TypeScript once and sends trees in private scanner-owned pickle IPC, then each of four workers creates a fresh StaticContext/TypeScriptProgram. Each flow detector calls tools(), which includes the same factory_tools traversal before rule-specific analysis. The parent coverage inventory later calls tools() again. Source syntax is immutable within a program; identity-keyed class/location indexes are rebuilt in workers. The current tools method has no retained result cache.',
 'measured_scope':'The current verified worker samples include factory_tools stacks. The exact shares and leaf/caller counts are retained per worker above; no parent-stage profile or completed later rule-specific traversal is inferred.',
 'reuse_constraints':'A future source-only attempt could retain completed tool bindings within the source program and pass them alongside the SAME parsed tree/file graph through existing private IPC. Preserve node/file alias identities, all ordered bindings, factory/SDK registrations and ordered warning behavior. Replay discovery warnings at the original tools() point rather than moving them earlier in worker-visible reports. Respect module option-cache warning effects and repeated-call deduplication. Rebuild identity-keyed indexes; never transport stale id() keys or use a global/cross-input cache. Empty completed discovery differs from missing discovery. An incomplete/failed discovery must never become a cached success.',
 'remaining_work':'Rule-specific security flow, HTTP discovery and coverage interpretation must still execute fully. They may remain expensive; this profile has not measured their complete future cost. Earlier source-only optimizations and every native/profile failure remain unchanged.',
 'limits':'Partial CPU snapshots, signal/GIL/native-code delivery, snapshot-thread overhead, generated frames and unprofiled parent/final intervals limit attribution. Inclusive stack shares overlap; neither their sum nor cross-version percentage changes are speedups or wholly removable costs. No new measurement, optimization or scanner mutation occurred during this assessment.',
 'optimization_attempts':0,'source_modified':False,'paid_calls':0,'target_execution':False,
}
write('source-assessment.json',source_assessment)
a = {'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':p['scanner'],'proposal_sha256':sha(PREP/'diagnostic-proposal.json'),'approval_sha256':sha(PREP/'diagnostic-authorization.json'),'validation_passed':True,'profile_attempts':1,'valid_partial_current_source_profiles':1,'completed_inputs':v['completed_inputs'],'incomplete_inputs':v['incomplete_inputs'],'timing':v['timing'],'harness_outcome':v['harness_outcome'],'report_count':v['report_count'],'finding_count':None,'warning_count':None,'surface_count':None,'source_assessment_complete_for_retained_outputs':True,'samples':v['samples'],'sample_rows':metrics,'assessment_sha256':{n:sha(OUT/n) for n in ['validation.json','sample-attribution.json','source-assessment.json','frame-source-bindings.json','frame-contexts.json','owned-work.json']},'remaining':0,'budget_closed':True,'optimization_attempts':0,'uninstrumented_observations':0,'retries':0,'comparators':0,'paid_calls':0,'target_execution':False,'all_prior_regression_budgets_remain_closed':True,'invalid_v50_attempt_preserved':True,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'One approved current-source sampled attempt. Each worker snapshot retains its actual final/restoration flags. Counts and all recorded frame locations are assessed; no report/native pass is inferred from profiling. Old 205-observation budget stays closed.'}
write('assessment.json',a)
print(json.dumps({'samples':a['samples'],'metrics':metrics,'source_assessment_complete':True},indent=2))
