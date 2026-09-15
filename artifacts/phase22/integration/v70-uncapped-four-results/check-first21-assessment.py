"""Independently verify every consolidated source/row binding and the fixed revision."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent;DEST=OUT/'first21-assessment'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inv=read(DEST/'inventory.json');a=read(DEST/'assessment.json');contexts=read(DEST/'source-context-assessment.json')['contexts'];validation=read(DEST/'validation.json')
assert len(inv['rows'])==len(a['rows'])==len(validation['observations'])==21
assert set(contexts)==set(inv['contexts']) and all(contexts[k]['source']==v for k,v in inv['contexts'].items())
prior=set(read(OUT/'first-three-assessment/inventory.json')['contexts'])|set(read(OUT/'first-faf-assessment/inventory-source-corrected.json')['contexts'])
fixed={k:v for k,v in inv['contexts'].items() if k not in prior}
assert len(fixed)==1503 and {c['snapshot'] for c in fixed.values()}=={inv['rows'][-1]['snapshot']}
assert inv['rows'][-2]['snapshot']==inv['rows'][-1]['snapshot']!=inv['rows'][-3]['snapshot']
for r,v,assessed in zip(inv['rows'],validation['observations'],a['rows'],strict=True):
 assert r['input_id']==v['input_id']==assessed['input_id'] and r['report_sha256']==v['report_sha256']==assessed['report_sha256']
 assert r['snapshot']==assessed['snapshot'] and r['label']==assessed['label'] and r['batch']==v['batch']==assessed['batch']
 for item in r['findings']+r['diagnostics']+r['surfaces']:
  assert contexts[item['context']]['source']['snapshot']==r['snapshot']
assert len(read(DEST/'finding-source-assessment.json')['rows'])==sum(len(r['findings']) for r in inv['rows'])==260
assert len(read(DEST/'diagnostic-source-assessment.json')['rows'])==sum(len(r['diagnostics']) for r in inv['rows'])==45440
assert len(read(DEST/'surface-source-assessment.json')['rows'])==sum(len(r['surfaces']) for r in inv['rows'])==276
initial=OUT/'assess-first21-initial.py';corrected=OUT/'assess-first21.py'
bad="assert c['case_id']=='faf-read-root' and c['snapshot']!=faf['input_id']";good="assert c['case_id']=='faf-read-root' and c['snapshot']==inv['rows'][-1]['snapshot']"
assert initial.read_text().replace(bad,good)==corrected.read_text()
result={'passed':True,'source_contexts_bound':4963,'fixed_contexts_exact_revision_verified':1503,'rows_bound':21,'new_inputs':0,'paid_calls':0,'initial_helper_sha256':sha(initial),'corrected_helper_sha256':sha(corrected),'assessment_sha256':sha(DEST/'assessment.json'),'correction':'The original helper compared a snapshot hash with an input ID, a vacuous assertion. Its other inventory/archive/row checks passed and actual source bindings were correct. Preserve that executed helper and receipt; the corrected assertion now uses the actual fixed snapshot, independently verified here for all1503fixed contexts. Existing assessment outputs are unchanged; no scan/retry occurred.','qualification':'Artifact source-binding verification only. The active three FAF repeats and eventual complete sequence checks remain separate.'}
with (DEST/'assessment-binding-check.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print('All4963source contexts and21report rows bound; all1503fixed contexts independently match the correct fixed revision. Initial vacuous assertion preserved/corrected; no report changes.')
