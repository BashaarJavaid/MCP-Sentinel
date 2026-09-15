"""Correct inherited restoration prose without changing the verified byte bindings."""
import hashlib,json,shutil
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['compatible-reuse.json','audit.json','summary.md']:shutil.copyfile(OUT/n,OUT/('initial-'+n))
p=OUT/'compatible-reuse.json';r=json.loads(p.read_text())
for n,d in r['engineering_files_sha256'].items():assert sha(ROOT/n)==d,n
r['qualification']='The one-file candidate temporarily changed product source, failed its strict prerequisite, and was restored exactly to tested1948bf9. All302current engineering inputs match the tested source. Existing local/hosted engineering, six zero-call production replays and approved Git runtime/image bindings are compatible after restoration; this is no new candidate test run or capture. Final README-aware packages are separately checked.'
r['prose_correction']={'initial_record_sha256':sha(OUT/'initial-compatible-reuse.json'),'reason':'Inherited no-change-during-attempt wording was incorrect. The hash checks were after exact restoration and were valid; temporary candidate bytes and failure remain preserved.'}
p.write_text(json.dumps(r,indent=2)+'\n')
p=OUT/'audit.json';a=json.loads(p.read_text());a['current_evidence']['compatible-reuse.json']=sha(OUT/'compatible-reuse.json')
for entry in a['current_requirement_interpretations'].values():entry['current_execution_evidence']['compatibility_sha256']=sha(OUT/'compatible-reuse.json')
a['compatibility_prose_correction']={'prior_audit_sha256':sha(OUT/'initial-audit.json'),'corrected_record_sha256':sha(OUT/'compatible-reuse.json'),'no_disposition_change':True};p.write_text(json.dumps(a,indent=2)+'\n')
p=OUT/'summary.md';s=p.read_text();needle='This continuation adds failed-prerequisite/restoration and final docs/package checks, not new hosted code evidence.';assert needle in s;s=s.replace(needle,needle+' The initial compatibility receipt incorrectly inherited no-change-during-attempt prose; its valid post-restoration byte checks and the initial receipt/audit are preserved, with the wording corrected explicitly.');p.write_text(s)
p=OUT/'verify-reuse.py';s=p.read_text().replace('No product/test/workflow/schema/lock change during the failed source-only attempt and exact restoration.','The one-file candidate was temporarily changed, failed, and restored exactly to tested1948bf9.');p.write_text(s)
print('Corrected only inherited compatibility prose;302restored byte bindings reverified and initial records preserved.')
