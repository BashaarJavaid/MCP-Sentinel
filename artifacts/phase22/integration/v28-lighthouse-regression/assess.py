"""Adjudicate every retained finding/diagnostic against frozen source, without scans."""
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from scripts.phase22_corpus import frozen, input_files

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
ASSETS = OUT.parent / 'v27-constructor-fix'
RAW = OUT / 'hosted/artifacts/phase22-lighthouse-regression'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
validation = json.loads((OUT / 'validation.json').read_text())
assert not validation['passed'] and len(validation['rows']) == 3
proposal = json.loads((ASSETS / 'evaluation-proposal.json').read_text())
manifest = frozen(approval_path=ASSETS / 'evaluation-authorization.json')
# Each group describes the actual source operation, not a blanket dismissal.
groups = [
 (['Server', 'Server.prototype.setRequestHandler.call'], 'The imported SDK method is saved and forwarded through the upstream prototype compatibility wrapper. Binding warnings remain on some analysis paths; the current SENT-015 report follows a source-bound handler to the sink. Neither recognition nor this warning proves runtime SDK compatibility.'),
 (['this.server', 'this.server.setRequestHandler', 'this.setupToolHandlers', 'this.handleRunAudit', 'this.handleGetPerformanceScore', 'request.params.name', 'run'], 'Class construction installs ListTools/CallTool handlers; the switch delegates to run_audit or the performance helper, then module startup connects stdio. The report retains two unresolved dispatch surfaces with unknown total. Source-supported sink detection does not establish complete named-tool enumeration.'),
 (['Array', 'Array.isArray', 'args.categories.every'], 'Array/schema compatibility and optional category-string checks are argument/schema operations, not destination validation. Unresolved builtin binding remains visible.'),
 (['JSON', 'JSON.parse', 'JSON.stringify', 'Object', 'Object.entries', 'category', 'category.title', 'category.score', 'category.description', 'key'], 'Audit category scores/metrics are assembled and serialized; the performance helper parses that response. These output operations occur after the request and do not reject its destination.'),
 (['console', 'console.error', 'err', 'error', 'error.message'], 'SDK compatibility catch, startup logging and tool error reporting use these values. No execution, exfiltration or successful error recovery is inferred.'),
 (['process', 'process.env', 'process.on', 'process.exit', 'this.server.close', 'this.server.connect', 'chrome.kill'], 'Source configures the Chrome environment and stdio/SIGINT/browser lifecycle. Environment values are not the caller URL; target lifecycle is unexecuted. These warnings do not establish destination rejection.'),
 (['URL', 'url', 'hostname', 'parsed.protocol', 'hostname.toLowerCase', 'includes'], 'Fixed validation parses the caller URL, restricts HTTP(S), and checks known metadata hostnames before the IP branch. Source review establishes the canonical numeric label separately; hostname/DNS and broader protection are not proven by this diagnostic.'),
 (['ip.startsWith', 'ip.split', 'parseInt', 'range.mask'], 'Fixed range iteration includes null-mask 169.254 rejection and a separate computed 172 mask. The loopback helper admits ::1 and 127.*, neither of which is canonical 169.254.169.254. The measured report lacks the required narrow qualification despite this source guard.'),
 (['dynamic tool description'], 'The source lists literal descriptions in a low-level ListTools handler; the scanner still reports description/dispatch uncertainty for this wrapper context. Do not infer missing source metadata or fully examined descriptions.'),
]
reviews = {key: text for keys, text in groups for key in keys}
patterns = {'Server.prototype.setRequestHandler.call': 'originalSetRequestHandler.call(', 'includes': 'BLOCKED_HOSTNAMES.includes(', 'dynamic tool description': 'description:', 'run': 'server.run()'}
flow_review = {
 'unresolved call to Array.isArray': reviews['Array'],
 'unresolved call to lighthouse': 'The imported Lighthouse call consumes the caller URL. SENT-015 recognizes this sink; other rule flow engines retain an unresolved-call warning. This is not proof of target execution or a separate named vulnerability.',
 'unresolved call to Object.entries': reviews['Object'],
 'computed or prototype member assignment': 'This location assigns a computed score/metric key in the formatted response after the request. Conservative mutation uncertainty is retained; it is not an additional destination bypass.',
 'unresolved call to JSON.stringify': reviews['JSON'],
 'unresolved call to JSON.parse': reviews['JSON'],
 'SDK instance escapes to an unresolved call': 'The exact source location is await this.server.connect(transport). The scanner conservatively reports receiver escape at startup while retaining discovered handler candidates. No runtime startup success, receiver integrity or complete dispatch coverage is inferred.',
 'unresolved call to hostname.toLowerCase': reviews['hostname'],
 'unresolved call to BLOCKED_HOSTNAMES.includes': reviews['includes'],
 'unresolved call to net.isIP': 'Fixed source branches on ordinary net.isIP before explicit loopback/range classification. Some rule engines leave that call unresolved. The narrow label is established from the source branch, not from a runtime IP check.',
 'unresolved call to range.mask': reviews['range.mask'],
 'unresolved call to ip.split': reviews['ip.split'],
 'unresolved call to parseInt': reviews['parseInt'],
 'unresolved call to dns.resolve4': 'DNS resolution occurs only after the IP-literal branch returns or rejects. It is outside the canonical literal label, and DNS failure is explicitly allowed to return. Broader hostname/redirect/IPv6 protection remains unestablished.',
 'unsupported control flow': 'The source continue skips permitted loopback DNS answers. This unresolved DNS loop is separate from the initial literal IP branch; no complete DNS/address-set protection is claimed.',
}
rows, outcomes = [], []
for attempt in validation['rows']:
    item = next(i for i in manifest.inputs if i.id == attempt['input_id'])
    snapshot = next(s for s in manifest.snapshots if s.revision == item.snapshot)
    source = input_files(item, snapshot, ROOT)['src/index.ts']
    digest = hashlib.sha256(source).hexdigest()
    assert digest == proposal['witnesses'][item.id]['source_sha256']
    lines = source.decode().splitlines()
    report_path = RAW / attempt['directory'] / item.id / 'report.json'
    report = json.loads(report_path.read_text())
    def add(kind, index, diagnostic, locations, assessment):
        assert locations and all(1 <= n <= len(lines) for n in locations)
        rows.append({'input_id': item.id, 'batch': attempt['batch'], 'kind': kind, 'index': index, 'diagnostic': diagnostic, 'source_path': 'src/index.ts', 'source_sha256': digest, 'source_lines': [{'line': n, 'text': lines[n-1]} for n in locations], 'assessment': assessment, 'runtime_proof': False})
    assert len(report['findings']) == 1
    finding = report['findings'][0]
    sink = proposal['witnesses'][item.id]['sink_line']
    assert finding['rule_id'] == 'SENT-015' and finding['location']['range']['start_line'] == sink
    assert finding['evidence']['snippet'] in lines[sink-1]
    locations = sorted({sink, *(l['range']['start_line'] for l in finding['evidence']['flow_locations'])})
    fixed = item.id.endswith('-fixed')
    if fixed:
        locations = sorted({*locations, 64, 72, 75, 81, 82, 83, 114, 115, 116, 117, 292})
    add('finding', 0, finding, locations, 'The fixed source rejects the canonical initial 169.254.169.254 literal before Chrome/Lighthouse. The report retains a broad SSRF candidate but omits the mandatory narrow link-local qualification. This fails the approved fixed-input condition; it is not proof of an upstream literal bypass. Synthetic analysis reproduces lost qualification on the ::1 loopback return.' if fixed else 'The registered CallTool handler forwards run_audit arguments to the local audit method; the supplied URL reaches Lighthouse with no initial link-local rejection. This condition-matched static finding is a vulnerable hit. The two variants share one vulnerability and are correlated, not independent successes.')
    for index, warning in enumerate(report['warnings']):
        if warning['code'] == 'static_binding_unresolved':
            binding = warning['message'].split("binding '", 1)[1][:-1]
            pattern = patterns.get(binding, binding)
            locations = [n for n, line in enumerate(lines, 1) if pattern in line]
            add('warning', index, warning, locations, reviews[binding])
        else:
            match = re.fullmatch(r'SENT-\d+ at src/index.ts:(\d+): (.*); protection is not established', warning['message'])
            assert match
            add('warning', index, warning, [int(match[1])], flow_review[match[2]])
    coverage = report['static_analysis']['coverage']
    assert coverage['total_possible_surfaces'] is None and len(coverage['surfaces']) == 2
    for index, flow in enumerate(coverage['unresolved_flows']):
        match = re.fullmatch(r'SENT-\d+ at src/index.ts:(\d+): (.*); protection is not established', flow['message'])
        assert match and flow['location']['range']['start_line'] == int(match[1])
        add('unresolved_flow', index, flow, [int(match[1])], flow_review[match[2]])
    for index, surface in enumerate(coverage['surfaces']):
        assert surface['status'] == 'unresolved' and surface['name'] is None
        add('surface', index, surface, [surface['handler']['range']['start_line'], surface['location']['range']['start_line']], reviews['request.params.name'])
    outcomes.append({'input_id': item.id, 'condition_passed': attempt['condition']['condition_passed'], 'sink_candidates': 1, 'qualified_candidates': 0, 'whole_input_seconds': attempt['timing']['elapsed_seconds'], 'native_seconds': attempt['native_seconds'], 'timing_class': attempt['timing_class'], 'warnings': len(report['warnings']), 'unresolved_flows': len(coverage['unresolved_flows']), 'surfaces': 2, 'report_sha256': sha(report_path)})
counts = dict(Counter(r['kind'] for r in rows))
assert counts == {'finding': 3, 'warning': 261, 'unresolved_flow': 164, 'surface': 6}
def write(name, data):
    path = OUT / name
    assert not path.exists()
    path.write_text(json.dumps(data, indent=2) + '\n')
write('source-assessment.json', {'rows': rows, 'counts': counts, 'unassessed': 0, 'source_only': True})
write('assessment.json', {'recorded_at': datetime.now(timezone.utc).isoformat(), 'run': 34641101185, 'workflow': 'b53581dc16136b1b41920671f4c98b9889c4b0fd', 'scanner': proposal['scanner'], 'condition_gate_passed': False, 'source_assessment_complete': True, 'budget': {'dispatches_consumed': 1, 'native_attempted': 3, 'native_completed': 3, 'native_unstarted_closed': 7, 'remaining': 0, 'closed': True, 'retries': 0, 'comparators': 0, 'profiles': 0, 'paid_calls': 0, 'target_execution': False}, 'outcomes': outcomes, 'observed_vulnerable_condition_hits': 2, 'observed_vulnerable_inputs': 2, 'fixed_inputs_observed': 1, 'fixed_condition_failures': 1, 'control_inputs_observed': 0, 'ordered_repeats_observed': 0, 'complete_five_input_batches': 0, 'within_120_second_target': 3, 'extended_time': 0, 'cleanup_verified': True, 'source_assessment_counts': counts, 'product_implication': 'Vulnerable detection is restored on both correlated variants, but fixed-source qualification fails. No complete discrimination/repeat gate or fresh generalization is claimed. All seven unstarted observations are closed. The existing fix-it instruction authorizes a minimal source correction and synthetic/engineering checks; another corpus run needs a new exact approval.', 'first_frozen_result': 'Original1f3f72f remains15 complete and0/2 hits per native batch/comparator. Previous6db3858 stopped after one completed vulnerable miss; nine unstarted closed. Neither failure is replaced.', 'references_sha256': {n: sha(OUT/n) for n in ['validation.json','source-assessment.json','binding.json','dispatch-consumed.json','hosted/packet.json']}, 'technical_acceptance_received': False, 'phase22_complete': False})
print('Source-assessed', counts, 'with zero unassessed entries; stopped budget closed.')
