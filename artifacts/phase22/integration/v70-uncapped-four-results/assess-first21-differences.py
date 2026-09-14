"""Reuse hash-bound completed delta judgments and assess the two FAF negatives."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent;DEST=OUT/'first21-assessment';ROOT=OUT.parents[3]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def deltas(p):
 with gzip.open(p/'complete-report-differences.jsonl.gz','rt') as f:return {(r['input_id'],r['batch']):r for r in map(json.loads,f)}

three=OUT/'first-three-assessment';faf=OUT/'first-faf-assessment';previous={**deltas(three),**deltas(faf)};current=deltas(DEST)
assert len(previous)==19 and len(current)==21 and all(current[k]==v for k,v in previous.items())
inv=read(DEST/'inventory.json');old=read(OUT.parent/'v44-four-fresh-evaluation/inventory.json');prior={(r['input_id'],r['batch'].removeprefix('rules-')):r for r in old['rows']};indexed={(r['input_id'],r['batch']):r for r in inv['rows']}
judgments=[];occurrences=[]
for key,item in current.items():
 if key in previous:
  packet=three if key[0]!='faf-read-root-vulnerable' else faf
  judgments.append({'input_id':key[0],'batch':key[1],'complete_delta_equal_to_previous':True,'source_assessment':str((packet/'report-difference-assessment.json').relative_to(ROOT)),'source_assessment_sha256':sha(packet/'report-difference-assessment.json')})
  continue
 assert key in {('faf-read-root-fixed','first'),('faf-read-root-safe','first')}
 assert {tuple(d['path']) for d in item['changes']}=={('warnings',),('static_analysis','coverage','unresolved_flows'),('static_analysis','coverage','surfaces')}
 row=indexed[key];before=prior[key];identity=lambda d:(d['kind'],d['context'],d['diagnostic']['message'])
 a=Counter(map(identity,before['diagnostics']));b=Counter(map(identity,row['diagnostics']));assert not a-b
 added=b-a;assert sum(added.values())==1098
 for (kind,context,message),count in added.items():
  assert context in inv['contexts']
  occurrences.append({'input_id':key[0],'batch':key[1],'kind':kind,'context':context,'message':message,'occurrence_count':count,'assessment':'Added explicit uncertainty at the exact fixed-source context in source-context-assessment.json. No original diagnostic count disappears. Current class/handler delegation remains unsupported; no guard/value/sink support or safe-negative conclusion follows from zero findings.'})
 judgments.append({'input_id':key[0],'batch':key[1],'changed_fields':{'warnings':'Added source-bound warnings retained in full order; exact occurrence deltas below. Existing warning counts remain.','static_analysis/coverage/unresolved_flows':'Added unresolved rule/source flows retained. They do not establish target execution or resolved guard/sink support.','static_analysis/coverage/surfaces':'Zero original surfaces become the same two unnamed ambiguous-dispatch surfaces seen on the vulnerable input. cli.ts18 lists five examined rules; index.ts15 lists none. Both bind server.ts91-110, where toolHandler.callTool remains unresolved. The source-fixed home/root confinement is not a scanner-supported named path.'},'all_other_nonvolatile_fields_equal':True,'added_diagnostic_occurrences':1098,'removed_diagnostic_occurrences':0,'source_assessment':'faf-fixed-source-assessment.json','source_assessment_sha256':sha(DEST/'faf-fixed-source-assessment.json'),'conclusion':'Empty findings remain empty, but the actual fixed/safe read is unsupported. Both negative support gates fail under the unchanged rubric.'})
assert len(judgments)==21
result={'complete_source_assessment_for21':True,'complete_ordered_reconstruction_passed':read(DEST/'report-difference-inventory.json')['complete_ordered_reconstruction_passed'],'differences_sha256':sha(DEST/'complete-report-differences.jsonl.gz'),'rows':judgments,'new_negative_diagnostic_occurrences':occurrences,'unassessed_changes':0,'qualification':'All complete ordered changes are either exactly equal to a prior hash-bound current assessment or independently assessed here. Only the11approved volatile exclusions apply. No current-source earlier-language compatibility, fresh result, accepted limitation or human technical acceptance is inferred.'}
with (DEST/'report-difference-assessment.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
a=read(DEST/'assessment.json');assert a['complete_report_difference_assessment_pending'];a['complete_report_difference_assessment_pending']=False
for name in ['report-difference-assessment.json','assessment-binding-check.json']:a['evidence_sha256'][name]=sha(DEST/name)
with (DEST/'assessment-with-differences.json').open('x') as f:json.dump(a,f,indent=2);f.write('\n')
print('All21complete ordered differences assessed. All12distinct inputs source-reviewed; only three FAF repeats remain.')
