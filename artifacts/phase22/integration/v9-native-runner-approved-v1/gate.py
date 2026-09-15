import json,sys
from pathlib import Path
from scripts.phase20_corpus import validate,digest
from scripts.phase20_scoring import candidate_identity,score,metrics
run=Path(sys.argv[1]);proposal=Path(sys.argv[2]);packet=json.loads((proposal/'packet.json').read_text())
assert digest((proposal/'condition-assessment.json').read_bytes())==packet['files']['condition-assessment.json']
raw=json.loads((run/'results.json').read_text());assert raw['scanner']==packet['scanner_identity'] and raw['model_calls']==0
items={i.id:i for i in validate().inputs};assessments={a['input_id']:a for a in json.loads((proposal/'condition-assessment.json').read_text())['assessments']};rows=[]
assert len(raw['outcomes'])==45 and {r['input_id'] for r in raw['outcomes']}==items.keys()
for outcome in raw['outcomes']:
 case=outcome['input_id'];path=run/case/'report.json';report=json.loads(path.read_text()) if path.exists() else None;findings=report['findings'] if report else [];a=assessments.get(case)
 same=a is None or candidate_identity(findings)==a['candidate_identity']
 if report:assert digest(path.read_bytes())==outcome['report_sha256']
 rows.append({'input_id':case,'label':items[case].label,'wall_duration_ms':outcome['wall_duration_ms'],'native_duration_ms':report['static_analysis']['duration_ms'] if report else None,'assessment_identity_equal':same,**score(label=items[case].label,state=outcome['state'],findings=findings,assessment=a if same else None)})
passed=all(r['state']=='completed' and r['wall_duration_ms']<=120000 and r['native_duration_ms']<=120000 and r['assessment_identity_equal'] for r in rows) and sum(r['label']=='vulnerable' and r['candidate_detected'] is True for r in rows)==20 and sum(r['false_alarm'] is True for r in rows)==0
result={'source':raw['scanner'],'passed':passed,'deadline_ms':120000,'rows':rows,'metrics':metrics(rows),'scope':'One entire45-input native batch; no pooling across failed attempts or environments.'};(run/'gate.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['metrics'],indent=2));assert passed,'Entire45-input completion/timing/scoring gate failed.'
