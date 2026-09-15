"""Close the failed prerequisite and restore only this attempt's source change."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(OUT/'authorization.json');v=read(OUT/'equivalence.json')
assert not v['passed'] and v['ordinary_comparisons']==256
assert [r['control'] for r in v['controls'] if not r['equivalent']]==['alias','shrink']
p=ROOT/'src/sentinel/static/typescript_path_flow.py';baseline=OUT/'baseline/src/sentinel/static/typescript_path_flow.py'
assert sha(p)==v['candidate_sha256'] and sha(baseline)==v['baseline_sha256']
p.write_bytes(baseline.read_bytes())
for name,digest in a['baseline_files_sha256'].items():assert sha(ROOT/name)==digest,name
assert not subprocess.check_output(['git','diff','HEAD','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml'],cwd=ROOT)
record={'recorded_at':datetime.now(timezone.utc).isoformat(),'restored':True,'source_sha256':sha(p),'baseline_scanner':a['scanner'],'attempts_consumed':1,'remaining':0,'budget_closed':True,'failed_prerequisite':'Adversarial captured-arm alias and shrinking-arm state differ; no exclusion is permitted by the approved proposal. Real-target reachability/impact is unestablished.','candidate_sha256':v['candidate_sha256'],'equivalence_sha256':sha(OUT/'equivalence.json'),'paid_calls':0,'corpus_observations':0,'profiles':0,'technical_acceptance_received':False,'phase22_complete':False}
with (OUT/'restoration.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
with (OUT/'optimization-budget-closed.json').open('x') as f:json.dump({'attempted':1,'passed':0,'failed':1,'remaining':0,'closed':True,'paid_calls':0},f,indent=2);f.write('\n')
print('Failed one-use attempt closed; exact tested1948bf9 source restored. No new source attempt or measurement.')
