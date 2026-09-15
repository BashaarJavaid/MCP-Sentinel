"""Validate retained approved observations without executing target or scanner analysis."""
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

from sentinel.report.validate_json import validate_report_data
from sentinel.report.validate_sarif import validate_sarif_data

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
ASSETS = OUT.parent / 'v27-constructor-fix'
HOSTED = OUT / 'hosted'
RAW = HOSTED / 'artifacts/phase22-lighthouse-regression'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('regression', ASSETS / 'evaluate.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
proposal = runner.approved()
retained = json.loads((HOSTED / 'packet.json').read_text())
assert retained['retention_complete']
for name, digest in retained['files_sha256'].items():
    assert sha(HOSTED / name) == digest, name
packet = json.loads((RAW / 'packet.json').read_text())
assert packet['scanner'] == proposal['scanner']
assert packet['workflow_revision'] == retained['run']['headSha'] == 'b53581dc16136b1b41920671f4c98b9889c4b0fd'
assert packet['workflow_run'] == '34641101185' and packet['workflow_attempt'] == '1'
assert packet['proposal_sha256'] == sha(ASSETS / 'evaluation-proposal.json')
assert packet['approval_sha256'] == sha(ASSETS / 'evaluation-authorization.json')
assert packet['budget_closed'] and packet['model_calls'] == 0 and not packet['target_execution']
for name, digest in packet['files_sha256'].items():
    assert sha(RAW / name) == digest, name
order = [{'batch': b, 'input_id': i} for b in proposal['batch_order'] for i in proposal['corpus']['input_ids']]
assert packet['unstarted'] == order[len(packet['attempts']):]
previous, rows = {}, []
for attempt, expected in zip(packet['attempts'], order):
    assert {k: attempt[k] for k in expected} == expected
    assert attempt['state'] == 'completed'
    runner.prior.completed(attempt['timing'])
    assert attempt['timing']['elapsed_including_cleanup_seconds'] - attempt['timing']['elapsed_seconds'] <= 15
    folder = RAW / attempt['directory']
    result = json.loads((folder / 'results.json').read_text())
    assert result['scanner'] == proposal['scanner'] and result['model_calls'] == 0 and not result['requests']
    assert result['manifest_sha256'] == proposal['corpus']['sha256']
    assert result['authorization_sha256'] == packet['approval_sha256']
    assert len(result['outcomes']) == 1 and result['outcomes'][0]['state'] == 'completed'
    path = folder / attempt['input_id'] / 'report.json'
    report = json.loads(path.read_text())
    validate_report_data(report)
    validate_sarif_data(json.loads(path.with_suffix('.sarif').read_text()))
    assert sha(path) == result['outcomes'][0]['report_sha256']
    assert report['analysisComplete'] and report['executionSuccessful']
    assert runner.condition(report, proposal['witnesses'][attempt['input_id']]) == attempt['condition']
    assert sha(path.parent / 'configuration.json') == json.loads((ROOT / proposal['configuration_path']).read_text())[attempt['input_id']]['sha256']
    canonical = runner.supervisor.clean(report, runner.prior.EXCLUDED)
    if attempt['batch'] == 'rules-repeat':
        assert previous[attempt['input_id']] == canonical and attempt['ordered_repeat_equal']
    else:
        previous[attempt['input_id']] = canonical
    rows.append({**attempt, 'report_sha256': sha(path), 'finding_count': len(report['findings']), 'warnings': len(report['warnings']), 'coverage': report['static_analysis']['coverage']})
if packet['passed']:
    assert len(rows) == 10 and not packet['unstarted'] and all(r['condition']['condition_passed'] for r in rows)
    assert retained['run']['conclusion'] == 'success'
else:
    assert retained['run']['conclusion'] == 'failure' and packet['stop_reason']
with zipfile.ZipFile(HOSTED / 'logs.zip') as archive:
    checkouts = [archive.read(n).decode() for n in archive.namelist() if 'Check out' in n and 'Post' not in n]
    assert any(packet['workflow_revision'] in s for s in checkouts)
    assert any(proposal['scanner']['revision'] in s for s in checkouts)
p = OUT / 'validation.json'
assert not p.exists()
p.write_text(json.dumps({'run': 34641101185, 'scanner': packet['scanner'], 'passed': packet['passed'], 'budget_closed': True, 'remaining': 0, 'unstarted_closed': packet['unstarted'], 'rows': rows, 'source_assessment_pending': True, 'raw_packet_sha256': sha(RAW / 'packet.json'), 'retained_packet_sha256': sha(HOSTED / 'packet.json'), 'validator_sha256': sha(Path(__file__)), 'new_paid_calls': 0}, indent=2) + '\n')
print('Validated', len(rows), 'completed observations; gate:', packet['passed'], '; closed unstarted:', len(packet['unstarted']))
