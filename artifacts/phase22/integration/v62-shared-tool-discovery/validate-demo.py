"""Validate the retained owned-fixture report; no scanner or target execution."""
import hashlib
import json
from pathlib import Path
from sentinel.report.validate_json import validate_report_data
from sentinel.report.validate_sarif import validate_sarif_data

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
raw = BASE/'v62-production-capture-revalidation/demo'
report = json.loads((raw/'report.json').read_text())
validate_report_data(report)
validate_sarif_data(json.loads((raw/'report.sarif').read_text()))
campaign = report['dynamic_analysis']['coverage']['campaign']
assert report['analysisComplete'] and report['executionSuccessful']
assert campaign['planned_attempts'] == campaign['started_attempts'] == campaign['tested_attempts'] == 20
assert campaign['remaining_eligible_attempts'] == 0
assert len(report['findings']) == 14
packet = {'native_and_sarif_valid': True, 'campaign': campaign, 'findings': 14,
          'files_sha256': {n: hashlib.sha256((raw/n).read_bytes()).hexdigest() for n in ['report.json', 'report.sarif']},
          'qualification': 'Read-only validation of the already completed authorized scanner-fixture Docker replay. No additional target execution, corpus observation or paid call.'}
with (OUT/'demo-validation.json').open('x') as stream:
    json.dump(packet, stream, indent=2)
    stream.write('\n')
print('Native/SARIF schemas and20/20 owned-fixture attempt invariants pass.')
