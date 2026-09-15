"""Source-assess the complete retained18-report delta without extra observations."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];DEST=OUT/'first-three-assessment';OLD=OUT.parent/'v44-four-fresh-evaluation'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inventory=read(DEST/'inventory.json');old=read(OLD/'inventory.json');delta=read(DEST/'report-difference-inventory.json')
current={(r['input_id'],r['batch']):r for r in inventory['rows']};prior={(r['input_id'],r['batch'].removeprefix('rules-')):r for r in old['rows']}
assessed=[];diagnostic_changes=[]
count_paths={'review_activity/static/candidate_count','review_activity/static/unreviewed_count','static_analysis/total_matches','summary/by_severity/Medium','summary/by_status/needs_review','summary/total'}
with gzip.open(DEST/'complete-report-differences.jsonl.gz','rt') as f:
 for line in f:
  item=json.loads(line);key=(item['input_id'],item['batch']);n=current[key];o=prior[key]
  for d in item['changes']:
   path='/'.join(d['path'])
   if path=='findings':
    explanation='Complete ordered raw candidates are source-adjudicated in finding-source-assessment.json. Named no-bash fixed qualifiers now preserve lexical boundaries; Lightning adds named and registry SENT-015 candidates but fails fixed literal-rejection qualification; Engram adds named manifest write and separate import read, with fixed resolved-copy qualifiers. All other candidates retain explicit source judgments. Original findings and failures remain bound to2e0efb2; no vanished finding is silently counted as a fixed pass.'
   elif path in {'warnings','static_analysis/coverage/unresolved_flows'}:
    explanation='Every current occurrence maps to diagnostic-source-assessment.json/source-context-assessment.json. Full ordered before/after arrays are retained here; occurrence-count changes are separately indexed below. No-bash has identical diagnostic multisets but changed warning order, which remains visible. Python removals include newly supported named sinks; other removed warnings alone prove neither safety nor full operation support. New Engram SENT-016 summarizer HTTP/response warnings remain explicit uncertainty outside export scope. Earlier/current repeated reports each agree within their own source; cross-source ordered equality is not claimed.'
   elif path=='static_analysis/rule_outcomes':
    assert len(d['before'])==len(d['after'])
    for a,b in zip(d['before'],d['after'],strict=True):
     assert {k:v for k,v in a.items() if k!='match_count'}=={k:v for k,v in b.items() if k!='match_count'}
     if a['match_count']!=b['match_count']:
      assert b['match_count']==a['match_count']+2
      assert (n['case_id']=='lightning-discover-linklocal' and b['rule_id']=='SENT-015') or (n['case_id']=='engram-export-home' and b['rule_id']=='SENT-012')
    explanation='Only match counts change: Lightning SENT-015 adds the named get and separate registry get; Engram SENT-012 adds the named manifest write and separate markdown import read. Ordered rule IDs, evaluation status, skip reasons and exemption counters are unchanged. SENT-001 absence-of-permissions skip remains visible; no rule coverage is newly inferred.'
   else:
    assert path in count_paths,path
    assert d['after']==d['before']+2
    explanation='Derived raw count increases by two, matching the two individually assessed new Medium/needs_review static candidates. It is not two independent named detections, new model review or a broad accuracy score.'
   assessed.append({'input_id':item['input_id'],'batch':item['batch'],'path':path,'assessment':explanation})
  def diagnostic_key(d):return(d['kind'],d['context'],d['diagnostic']['message'])
  a=Counter(map(diagnostic_key,o['diagnostics']));b=Counter(map(diagnostic_key,n['diagnostics']))
  for direction,counts,context_map in [('removed',a-b,old['contexts']),('added',b-a,inventory['contexts'])]:
   for (kind,context,message),count in counts.items():
    c=context_map[context]
    explanation='Retained source occurrence in '+c['path']+' / '+c.get('scope','module/helper')+'. '
    if direction=='added':
     assert n['case_id']=='engram-export-home' and c['path']=='src/engram/summarizer.py' and c['line'] in {37,42,43} and message.startswith('SENT-016')
     explanation+='Summarizer HTTP post/response status/JSON/string processing is now reported unresolved by SENT-016. This is a separate memory summarization route, not the selected export manifest write; no model or network operation ran. Keep credential and response uncertainty visible.'
    elif 'client.get' in message and c['path'].endswith('tools/discover_api.py') and c['line'] in {126,132} and message.startswith('SENT-015'):
     explanation+='The selected SENT-015 HTTPX get is now present with caller flow in findings. This supports sink recognition only; Lightning fixed link-local qualification still fails. Other rules may retain unresolved receiver diagnostics.'
    elif 'manifest_path.write_text' in message and message.startswith('SENT-012'):
     explanation+='The selected SENT-012 manifest write is now present with caller flow and fixed resolved-copy qualifier. Broader containment at use and runtime behavior remain unestablished.'
    else:
     explanation+='This exact warning/flow occurrence disappeared relative to the original scanner. Preserve its old source and historical assessment; removal alone does not prove the call resolved, became safe, ceased executing, or improved coverage. Current source contexts/findings assess remaining behavior; do not substitute this removal for a named gate.'
    diagnostic_changes.append({'input_id':item['input_id'],'batch':item['batch'],'direction':direction,'kind':kind,'context':context,'source':c,'message':message,'occurrence_count':count,'assessment':explanation})
assert len(assessed)==sum(delta['changed_paths'].values())
result={'complete_source_assessment_for18':True,'complete_ordered_reconstruction_passed':delta['complete_ordered_reconstruction_passed'],'differences_sha256':delta['differences_sha256'],'inventory_sha256':sha(DEST/'report-difference-inventory.json'),'assessed_changed_paths':assessed,'diagnostic_occurrence_changes':diagnostic_changes,'unassessed_changes':0,'unchanged':'Every non-excluded field not listed in the complete reconstruction is equal, including ordered surface metadata, scope/exclusions, target, schema, stage identity and execution-success fields. Only the11prospectively established volatile fields are excluded.','qualification':'Same-agent complete retained-source/report assessment. No fresh source claim, single-change causal attribution, current earlier-language compatibility, broad safety, accepted limitation or human technical acceptance.'}
with (DEST/'report-difference-assessment.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
assessment=read(DEST/'assessment.json');assert assessment['complete_report_difference_assessment_pending']
assessment['complete_report_difference_assessment_pending']=False
assessment['evidence_sha256']['report-difference-assessment.json']=sha(DEST/'report-difference-assessment.json')
with (DEST/'assessment-with-differences.json').open('x') as f:json.dump(assessment,f,indent=2);f.write('\n')
print('All18complete report differences assessed;',len(assessed),'changed paths;',sum(x['occurrence_count'] for x in diagnostic_changes),'diagnostic occurrence deltas retained; activeFAF untouched.')
