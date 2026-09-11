"""Compare already retained canonical reports; no detector execution."""
import hashlib
import importlib.util
import json
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('runner',BASE/'v27-constructor-fix/evaluate.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
raw=OUT/'hosted/artifacts/phase22-lighthouse-regression'
prior=BASE/'v24-fresh-v5/hosted/artifacts/phase22-fresh-v5'
packet=json.loads((raw/'packet.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for a in packet['attempts']:
 p=raw/a['directory']/a['input_id']/'report.json';old=prior/a['directory']/a['input_id']/'report.json'
 x,y=[m.supervisor.clean(json.loads(path.read_text()),m.prior.EXCLUDED) for path in [old,p]]
 def differences(x,y,pointer=''):
  if isinstance(x,dict) and isinstance(y,dict):
   return [v for key in sorted(x.keys()|y.keys()) for v in differences(x.get(key),y.get(key),pointer+'/'+key)]
  return [] if x==y else [{'pointer':pointer,'before':x,'after':y}]
 deltas=differences(x,y)
 assert {d['pointer'] for d in deltas} <= {'/findings','/warnings','/static_analysis/coverage/surfaces','/static_analysis/coverage/unresolved_flows','/review_activity/static/candidate_count','/review_activity/static/unreviewed_count','/static_analysis/rule_outcomes','/static_analysis/total_matches','/summary/by_severity/Medium','/summary/by_status/needs_review','/summary/total'}
 rows.append({'input_id':a['input_id'],'before_sha256':sha(old),'after_sha256':sha(p),'deltas':deltas,'assessment':'The constructor correction exposes the handler/sink path: one SENT-015 finding, two unresolved dispatch surfaces and additional rule-specific flow/binding diagnostics. The added finding also changes rule match counts, total/Medium/needs_review summaries and unreviewed candidate accounting from zero to one; no review call occurs. All current occurrences are individually source-assessed in source-assessment.json. Former class-rejection and old binding diagnostics remain in original reports; the new report does not establish complete dispatch or runtime protection.'})
path=OUT/'retained-source-deltas.json';assert not path.exists();path.write_text(json.dumps({'baseline_scanner':'1f3f72f','candidate_scanner':'4a2359d','volatile_exclusions':sorted(m.prior.EXCLUDED),'rows':rows,'new_scans':0,'new_paid_calls':0},indent=2)+'\n');print([(r['input_id'],[d['pointer'] for d in r['deltas']]) for r in rows])
