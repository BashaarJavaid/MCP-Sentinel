"""Bind every added FAF diagnostic and retain the complete ordered report delta."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent;DEST=OUT/'first-faf-assessment';OLD=OUT.parent/'v44-four-fresh-evaluation'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
current=read(DEST/'inventory-source-corrected.json');old=read(OLD/'inventory.json');row=current['rows'][0]
previous=next(r for r in old['rows'] if r['input_id']==row['input_id'] and r['batch']=='rules-first')
key=lambda d:(d['kind'],d['context'],d['diagnostic']['message'])
a=Counter(map(key,previous['diagnostics']));b=Counter(map(key,row['diagnostics']));assert not a-b
added=b-a;assert sum(added.values())==1089
contexts=read(DEST/'source-context-assessment.json')['contexts'];changes=[]
for (kind,context,message),count in added.items():
 assert context in contexts
 changes.append({'kind':kind,'context':context,'message':message,'occurrence_count':count,'assessment_context':context,'assessment':'Additional explicit uncertainty from the current scanner, retained at its actual source statement/binding/file. See the current source-context judgment. It is not a detected vulnerability or proof of target execution. Prior diagnostic occurrences remain unchanged in count; ordering remains in the complete delta.'})
delta=read(DEST/'report-difference-inventory.json');assert delta['complete_ordered_reconstruction_passed']
assert set(delta['changed_paths'])=={'static_analysis/coverage/surfaces','static_analysis/coverage/unresolved_flows','warnings'}
with gzip.open(DEST/'complete-report-differences.jsonl.gz','rt') as f:
 items=[json.loads(line) for line in f]
assert len(items)==1 and len(items[0]['changes'])==3
result={'complete_source_assessment_for_this_report':True,'complete_ordered_reconstruction_passed':True,'differences_sha256':delta['differences_sha256'],'changed_fields':{'static_analysis/coverage/surfaces':'Zero original surfaces become two unresolved, unnamed startup registrations at cli.ts18 and index.ts15, both pointing to server.ts91-110. Only the first lists five examined rules. Actual this.toolHandler.callTool remains unresolved; source class parameter-property rejection blocks the named read route. No named metadata/sink coverage or detection pass is inferred.','warnings':'All original diagnostic occurrence counts remain;377 warning occurrences are added. Every current warning is mapped and assessed, including the file-only conceptual dynamic-description warning. Full array order is retained.','static_analysis/coverage/unresolved_flows':'712 unresolved-flow occurrences are added; prior counts remain. Additional rule-tagged unsupported operations and source bindings are explicitly assessed. They do not imply target execution or a supported named read.'},'added_diagnostic_occurrences':changes,'added_occurrence_count':1089,'removed_occurrence_count':0,'unassessed_changes':0,'unchanged':'All other non-excluded report fields are equal, including empty findings, zero match counters and ordered rule outcomes. Only the11established volatile fields are excluded.','qualification':'Comparison is between original2e0efb2 and retained4145d35 source with an experimental uncapped policy. It establishes no single-change causal attribution or speedup. Original fresh miss and all source-bound timeouts remain; current vulnerable detection also fails.'}
with (DEST/'report-difference-assessment.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
assessment=read(DEST/'assessment.json');assert assessment['complete_report_difference_assessment_pending'];assessment['complete_report_difference_assessment_pending']=False;assessment['evidence_sha256']['report-difference-assessment.json']=sha(DEST/'report-difference-assessment.json')
with (DEST/'assessment-with-differences.json').open('x') as f:json.dump(assessment,f,indent=2);f.write('\n')
print('Complete first FAF delta assessed:3changed fields,1089added diagnostic occurrences,0removed; zero findings unchanged and named detection still fails.')
