"""Validate retained approved observations without invoking the scanner."""
import hashlib
import importlib.util
import json
import os
import sys
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
ASSETS = OUT.parent/'v57-credential-merge'
RAW = OUT/'raw'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
proposal = read(ASSETS/'evaluation-proposal.json')
os.chdir(proposal['frozen_checkout'])
sys.path[:0] = [str(Path.cwd()/'src'), str(Path.cwd())]
from sentinel.report.validate_json import validate_report_data
from sentinel.report.validate_sarif import validate_sarif_data
spec = importlib.util.spec_from_file_location('approved_runner', ASSETS/'evaluate.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
assert runner.approved() == proposal
packet = read(RAW/'packet.json')
execution = read(OUT/'execution.json')
launch = read(OUT/'launch.json')
consumed = read(ASSETS/'execution-consumed.json')
assert packet['budget_closed'] and packet['remaining_observation_budget'] == 0
assert packet['scanner'] == proposal['scanner']
assert packet['runner_revision'] == '53d3045b3927ffe3163f4016b98f563b2ed87096'
for key, path in [('proposal_sha256', ASSETS/'evaluation-proposal.json'), ('approval_sha256', ASSETS/'evaluation-authorization.json')]:
    assert packet[key] == launch[key] == consumed[key] == sha(path)
assert launch['launcher_binding_sha256'] == sha(ASSETS/'launcher-binding.json')
assert consumed['budget_consumed'] and consumed['output'] == str(RAW)
assert packet['model_calls'] == 0 and not packet['target_execution']
assert launch['command'] == proposal['prepared_command'] and launch['cwd'] == proposal['frozen_checkout']
timing = execution['timing']
assert timing['cleanup_verified']
assert launch['sequence_limit_seconds'] == 69000
for name, digest in packet['files_sha256'].items():
    assert sha(RAW/name) == digest, name
assert packet['unstarted'] == proposal['order'][len(packet['attempts']):]
rows = []
previous = {}
pairs = 0
for attempt, expected in zip(packet['attempts'], proposal['order']):
    assert all(attempt[k] == value for k, value in expected.items())
    row = dict(attempt)
    group = proposal['groups'][attempt['group']]
    item = group['inputs'][attempt['input_id']]
    row.update({key: item['input'][key] for key in ['label', 'snapshot', 'tree_sha256', 'repository', 'language']})
    folder = RAW/attempt['directory']
    path = folder/attempt['input_id']/'report.json'
    row['report_present'] = path.is_file()
    if path.is_file():
        report = read(path)
        validate_report_data(report)
        validate_sarif_data(read(path.with_suffix('.sarif')))
        row.update(report_sha256=sha(path), sarif_sha256=sha(path.with_suffix('.sarif')),
                   finding_count=len(report['findings']), warning_count=len(report['warnings']),
                   coverage=report['static_analysis']['coverage'], rule_outcomes=report['static_analysis']['rule_outcomes'],
                   analysis_complete=report['analysisComplete'], execution_successful=report['executionSuccessful'])
    if attempt['state'] == 'completed':
        runner.prior.completed(attempt['timing'])
        assert report['analysisComplete'] and report['executionSuccessful']
        assert report['static_analysis']['duration_ms'] <= 300000
        result = read(folder/'results.json')
        assert result['scanner'] == proposal['scanner'] and result['manifest_sha256'] == group['manifest_sha256']
        assert result['model_calls'] == 0 and not result['requests']
        assert len(result['outcomes']) == 1 and result['outcomes'][0]['state'] == 'completed'
        assert result['outcomes'][0]['report_sha256'] == sha(path)
        assert sha(path.parent/'configuration.json') == item['configuration_sha256']
        if group['source_freeze_approval']:
            assert result['authorization_sha256'] == sha(Path.cwd()/group['source_freeze_approval'])
        canonical = runner.supervisor.clean(report, runner.prior.EXCLUDED)
        if attempt['batch'] == 'repeat':
            equal = previous[(attempt['group'], attempt['input_id'])] == canonical
            assert equal == attempt['ordered_repeat_equal']
            pairs += equal
        else:
            previous[(attempt['group'], attempt['input_id'])] = canonical
        row['reference_sha256'] = sha(ROOT/item['reference_report'])
        row['entire_reference_equal'] = canonical == runner.supervisor.clean(read(ROOT/item['reference_report']), runner.prior.EXCLUDED)
    rows.append(row)
if packet['passed']:
    assert timing['returncode'] == 0 and not timing['timed_out'] and not timing['remaining_group_killed']
    assert len(rows) == 205 and all(r['state'] == 'completed' for r in rows) and pairs == 95
else:
    assert timing['returncode'] != 0 and packet.get('stop_reason')
result = {'validation_passed': True, 'execution_gate_passed': packet['passed'], 'stop_reason': packet.get('stop_reason'),
          'scanner': proposal['scanner'], 'raw_packet_sha256': sha(RAW/'packet.json'), 'execution_sha256': sha(OUT/'execution.json'),
          'validator_sha256': sha(Path(__file__)), 'attempts': rows, 'repeat_pairs_equal': pairs,
          'states': dict(Counter(r['state'] for r in rows)), 'unstarted_closed': packet['unstarted'],
          'remaining': 0, 'budget_closed': True, 'source_assessment_pending': True, 'paid_calls': 0}
with (OUT/'validation.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(f'Validated {len(rows)} attempts and {pairs} equal ordered pairs; execution gate {packet["passed"]}.')
