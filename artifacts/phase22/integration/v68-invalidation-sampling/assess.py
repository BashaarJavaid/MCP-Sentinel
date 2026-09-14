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
PREP = BASE/'v67-invalidation-regression'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
p = read(PREP/'diagnostic-proposal.json')
v = read(OUT/'validation.json')
assert v['passed'] and 1 <= v['sample_snapshots'] <= 5 and v['samples'] > 0
assert read(OUT/'owned-work.json')['owned_processes'] == []
fixed = Path(p['frozen_checkout'])
metrics, contexts, source_lines, source_hashes = [], {}, {}, {}
for row in read(OUT/'sample-attribution.json')['rows']:
    d = read(OUT/(row['rule']+'-cpu-samples.json'))
    frames = {f['id']: f for f in d['frame_catalog']}
    leaf = Counter()
    callers = Counter()
    registration_sites = Counter()
    literal_serialization = 0
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
        contexts[key] = {'frame': frame, 'source_sha256': source_hashes[filename], 'kind': 'scanner' if filename.startswith(str(fixed/'src')) else 'sampler' if source in {OUT/'corrected-sampling-worker.py', PREP/'corrected-sampling-worker.py', PREP/'diagnostic.py'} else 'dependency/interpreter', 'line_context': {str(i): lines[i-1] for i in range(max(1, frame['line']-2), min(len(lines),frame['line']+2)+1)}}
    for sample in d['stacks']:
        stack = [frames[n] for n in sample['frames']]
        top, count = stack[0], sample['count']
        for frame in stack:
            if frame['filename'].endswith('/typescript_registration_flow.py') and frame['function'] == 'factory_tools':
                registration_sites[frame['line']] += count
        if top['filename'].endswith('/json/encoder.py') and any(frame['filename'].endswith('/typescript_path_flow.py') and frame['function'] == 'expression' and frame['line'] == 1057 for frame in stack):
            literal_serialization += count
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
    metrics.append({k: row[k] for k in ['rule','samples','snapshot_worker_cpu_seconds','final_worker_snapshot','signal_and_timer_state_restored','registration_inclusive_samples','registration_inclusive_percent','merge_inclusive_percent','maximum_observed_depth','sampling_started_cpu_seconds','sampling_ended_cpu_seconds','retained_cpu_interval_seconds']} | {'registration_callsite_samples':dict(registration_sites), 'literal_json_encoder_leaf_samples':literal_serialization, 'literal_json_encoder_leaf_percent':literal_serialization/row['samples']*100, 'leaf_samples': dict(leaf), 'leaf_percent': {k: n/row['samples']*100 for k,n in leaf.items()}, 'json_encoder_scanner_callers': [{'filename': k[0], 'function': k[1], 'line': k[2], 'samples': n} for k,n in callers.most_common()]})
write('frame-contexts.json', contexts)
selected = {
 'src/sentinel/static/workers.py': ['run_flow_rules','_worker'],
 'src/sentinel/static/model.py': ['StaticContext'],
 'src/sentinel/static/typescript_discovery.py': ['TypeScriptProgram'],
 'src/sentinel/static/typescript_registration_flow.py': ['RegistrationFlow','factory_tools'],
 'src/sentinel/static/typescript_path_flow.py': ['TypeScriptPathFlow'],
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
 'source_fact':'At4145d35, run_flow_rules requests completed TypeScript tool discovery in the parent before existing worker dispatch. factory_tools invokes RegistrationFlow.initialize for eligible module trees. RegistrationFlow subclasses the full TypeScriptPathFlow and calls its expression for every visited expression before retaining registration metadata. In the non-null/non-undefined literal branch, every visit unconditionally runs json.dumps(node["L"], sort_keys=True), constructs a fresh Value and updates all literal/condition metadata. Source syntax is immutable within TypeScriptProgram. Existing source_range uses a4096-entry per-program identity cache retaining node/file objects; it does not cache literal serialization.',
 'measured_scope':'Actual per-process sample rows and caller/line attribution are retained. Parent and worker denominators are separate; missing workers do not prove they never launched. This sampled attempt is not a native regression repeat or throughput/completion proof.',
 'reuse_constraints':'A future separately approved pure literal-key serialization cache could retain only the exact json.dumps string for an immutable literal node within its source program, using the existing bounded identity-cache pattern. Retain the node object to prevent id reuse; no cross-program/process-global cache or transported integer identities. Preserve exact JSON options, errors, fresh Value allocation, deadline checks and every subsequent literal/condition/registration state update. Never cache a Value, environment, binding or interpreter result. Cold/warm/eviction and complete state/report equivalence must be checked, including interning-sensitive callers.',
 'remaining_work':'The module traversal, branch merging, registration state, rule-specific security/HTTP flows and all coverage still execute. Repeated literal eligibility/cache hits are uncounted. JSON leaf shares describe only the sampled interval; caching overhead, misses and all remaining work may prevent1800-second completion. No optimization has been implemented.',
 'limits':'Partial CPU snapshots, signal/GIL/native-code delivery, snapshot-thread overhead, generated frames and unprofiled parent/final intervals limit attribution. Inclusive stack shares overlap; neither their sum nor cross-version percentage changes are speedups or wholly removable costs. No new measurement, optimization or scanner mutation occurred during this assessment.',
 'optimization_attempts':0,'source_modified':False,'paid_calls':0,'target_execution':False,
}
source_assessment['current_if_contract'] = 'The v66 private monotone invalidation-domain revision remains unchanged: independent baseline/per-arm copies, first completed arm adoption, later arm update. The original v65 strict alias/shrink failure remains unaccepted. No new contract revision is inferred.'
source_assessment['snapshot_termination'] = 'Only a periodic parent snapshot survives; final_worker_snapshot and signal_and_timer_state_restored are both false. Forced group termination after the deadline is confirmed, but the reason final snapshot/restoration did not complete is unestablished. There are no retained temporary snapshot files. No worker launch history or worker costs are inferred.'
source_assessment['alternative_review'] = 'The largest individual sampled line is the existing later-arm invalidation union (statement685). Reducing it or changing per-arm/environment copies would require further isolation/mutation reasoning and is outside this proposed pure serialization reuse. Removing the initial baseline copy would target only3422 parent leaf samples and does not address the larger retained operations. No alternative was implemented or measured.'
source_assessment['literal_lifetime_obligations'] = 'The existing source_range cache states program syntax immutability and holds node/file objects; program construction parses trees once. HTTP flow deepcopy explicitly preserves the same program/source nodes. The new proposal must separately establish eligibility for generated/synthetic mutable literals, identity-sensitive string consumers, context reconstruction and every expression subclass. Full caller/identity/equivalence proof remains an implementation prerequisite, not a completed optimization proof.'
source_assessment['retained_snapshot_files'] = {str(f.relative_to(OUT)):sha(f) for f in OUT.rglob('*') if f.is_file() and ('cpu-samples' in f.name or f.suffix == '.tmp')}
write('source-assessment.json',source_assessment)
a = {'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':p['scanner'],'proposal_sha256':sha(PREP/'diagnostic-proposal.json'),'approval_sha256':sha(PREP/'diagnostic-authorization.json'),'validation_passed':True,'profile_attempts':1,'valid_partial_current_source_profiles':1,'completed_inputs':v['completed_inputs'],'incomplete_inputs':v['incomplete_inputs'],'timing':v['timing'],'harness_outcome':v['harness_outcome'],'report_count':v['report_count'],'finding_count':None,'warning_count':None,'surface_count':None,'source_assessment_complete_for_retained_outputs':True,'samples':v['samples'],'sample_rows':metrics,'assessment_sha256':{n:sha(OUT/n) for n in ['validation.json','sample-attribution.json','source-assessment.json','frame-source-bindings.json','frame-contexts.json','owned-work.json']},'remaining':0,'budget_closed':True,'optimization_attempts':0,'uninstrumented_observations':0,'retries':0,'comparators':0,'paid_calls':0,'target_execution':False,'all_prior_regression_budgets_remain_closed':True,'invalid_v50_attempt_preserved':True,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'One approved current-source sampled attempt. Each process snapshot retains its actual final/restoration flags; the parent uses legacy worker-named fields. No absent-worker cost is inferred. Counts and all recorded frame locations are assessed; no report/native pass is inferred from profiling. Old 205-observation budget stays closed.'}
write('assessment.json',a)
print(json.dumps({'samples':a['samples'],'metrics':metrics,'source_assessment_complete':True},indent=2))
