"""Consolidate completed source judgments and assess the two FAF negatives."""
import copy
import hashlib
import json
import tarfile
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];DEST=OUT/'first21-assessment';THREE=OUT/'first-three-assessment';FAF=OUT/'first-faf-assessment';OLD=OUT.parent/'v44-four-fresh-evaluation';PREP=OUT.parent/'v69-uncapped-four-repository'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
 with (DEST/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')

inv=read(DEST/'inventory.json');validation=read(DEST/'validation.json');three=read(THREE/'assessment-with-differences.json');faf=read(FAF/'assessment-with-differences.json');old=read(OLD/'inventory.json')
assert validation['passed'] and validation['completed']==21 and not three['complete_report_difference_assessment_pending'] and not faf['complete_report_difference_assessment_pending']
contexts={**read(THREE/'source-context-assessment.json')['contexts'],**read(FAF/'source-context-assessment.json')['contexts']}
assert len(contexts)==3460 and all(v['source']==inv['contexts'][k] for k,v in contexts.items())
vulnerable_contexts=read(FAF/'source-context-assessment.json')['contexts']
by_location={(v['source']['path'],v['source'].get('line'),v['source'].get('binding')):(k,v) for k,v in vulnerable_contexts.items()}
reused=0;reassessed=0
for key,c in inv['contexts'].items():
 if key in contexts:continue
 assert c['case_id']=='faf-read-root' and c['snapshot']==inv['rows'][-1]['snapshot']
 prior=by_location.get((c['path'],c.get('line'),c.get('binding')))
 if prior and {k:v for k,v in c.items() if k!='snapshot'}=={k:v for k,v in prior[1]['source'].items() if k!='snapshot'}:
  entry=copy.deepcopy(prior[1]);entry['source']=c;entry['reused_judgment']={'source':str((FAF/'source-context-assessment.json').relative_to(ROOT)),'sha256':sha(FAF/'source-context-assessment.json'),'context':prior[0],'all_context_fields_equal_except_revision':True};reused+=1
 else:
  p=c['path'];reassessed+=1
  if p=='src/handlers/tools.ts':
   role='Fixed FAF listing/dispatch source. Constructor(private engineAdapter: FafEngineAdapter) at29 remains outside the current constructor-attribute contract; the report retains class rejection at28 and unresolved server.ts94 delegation. Its faf_read switch arm delegates to fileHandlers.faf_read; other private methods, argument handling, scoring, project updates and commands remain separate unresolved source routes. No named read support is established.'
  elif p=='src/handlers/fileHandler.ts':
   role='Fixed FAF file handler/PathValidator. handleFafRead extracts rawPath, assigns filePath=confineFileOp(rawPath) at106, returns on PathConfinementError or rethrows before the read, checks size, then passes filePath to actual fs.readFile131 inside Promise.race. Under frozen ordinary-file/operator-root prerequisites the outside path is rejected and the inside control is within the root. The current report has no caller-bound read finding or guard qualification and leaves handler delegation unresolved; these quiet negatives fail supported-path discrimination. Other class/binding/size/timer limitations remain explicit; no read was executed.'
  elif p=='src/utils/safe-path.ts':
   role='Fixed confinement helper. Operator FAF_ALLOWED_ROOTS is stable/nonempty in the frozen condition; fileOpRoots uses it, confineFileOp disables the separate .faf-extension restriction, confinePath canonicalizes roots/path and withinRoots checks exact root or root-plus-separator. Outside rejection throws before returning resolved to the actual read. The ordinary existing-file prerequisite makes the successful canonicalization branch source-relevant; generic loop termination, symlink races, other roots/deployments and custom Error support are not inferred. This source guard is not established as supported by the current named scanner path.'
  else:
   assert p=='tests/security-path-confinement.test.ts',p
   role='New fixed upstream path-confinement test source with handler.callTool/textOf helpers. Read-only source evidence, never executed; target tests do not replace the actual scanner detection/negative-support gate.'
  entry={'source':c,'assessment':role,'disposition':'Retain exact source uncertainty; no target execution, safe-negative inference from silence, or unrelated-condition substitution.'}
 entry['prior_identical_source_context']=key in old['contexts'] and c==old['contexts'][key]
 contexts[key]=entry
assert len(contexts)==4963 and reused==1351 and reassessed==152
write('source-context-assessment.json',{'contexts':contexts,'count':4963,'unassessed':0,'reused_fixed_contexts_identical_except_revision':1351,'fixed_contexts_reassessed':152,'qualification':'Same-agent source review. Existing first18/firstFAF judgments retain their hashes; fixed revision uses exact source bytes, not assumed line equivalence. File-only conceptual and exact module-literal indexing corrections remain.'})

findings=read(THREE/'finding-source-assessment.json')['rows'];assert len(findings)==260 and all(not r['findings'] for r in inv['rows'][18:])
write('finding-source-assessment.json',{'rows':findings,'count':260,'unassessed':0,'faf_zero_finding_reports':[{'input_id':r['input_id'],'report_sha256':r['report_sha256'],'qualification':'Completed empty finding list; vulnerable miss or unsupported negative, never proof of safety.'} for r in inv['rows'][18:]]})
diagnostics=[];surfaces=[];rows=[]
old_surfaces=read(THREE/'surface-source-assessment.json')['rows'];first_surfaces=read(FAF/'surface-source-assessment.json')['rows']
for i,(r,v) in enumerate(zip(inv['rows'],validation['observations'],strict=True)):
 assert r['input_id']==v['input_id'] and r['batch']==v['batch'] and r['report_sha256']==v['report_sha256']
 for d in r['diagnostics']:
  assert d['context'] in contexts
  diagnostics.append({'input_id':r['input_id'],'batch':r['batch'],'report_sha256':r['report_sha256'],**d,'assessment_context':d['context'],'disposition':'Exact unresolved operation retained with source role; no inferred safety, suppression or executed behavior.'})
 for s in r['surfaces']:
  if i<18:
   candidates=[x for x in old_surfaces if x['input_id']==r['input_id'] and x['batch']==r['batch'] and x['index']==s['index']];assert len(candidates)==1 and candidates[0]['surface']==s['surface'];explanation=candidates[0]['assessment']
  else:
   original=first_surfaces[s['index']];assert original['surface']==s['surface'];explanation=original['assessment']+' The fixed/safe source guard, where present, does not resolve this current ambiguous dispatch or establish the named read.'
  surfaces.append({'input_id':r['input_id'],'batch':r['batch'],'report_sha256':r['report_sha256'],**s,'assessment':explanation})
 if i<18:
  previous=three['rows'][i];assert previous['report_sha256']==r['report_sha256'];rows.append(previous)
 else:
  assert r['case_id']=='faf-read-root' and r['batch']=='first' and not r['findings']
  rows.append({**v,'case_id':r['case_id'],'label':r['label'],'snapshot':r['snapshot'],'named_candidate_keys':[],'matching_keys':[],'named_vulnerable_hit':False if r['label']=='vulnerable' else None,'named_negative_false_alert':False if r['label']!='vulnerable' else None,'supported_qualified_negative':False,'actual_named_sink_supported':False,'fixed_source_guard_present':r['label']!='vulnerable','scanner_guard_recognition_established':False,'condition_passed':False,'coverage':r['coverage'],'assessment':'Actual named vulnerable read is missed.' if r['label']=='vulnerable' else 'Quiet negative remains unsupported at the actual read. Source-bound fixed rejection exists under the original prerequisites, but no current caller/guard/value/sink support or accurate qualifier is established.'})
assert len(diagnostics)==45440 and len(surfaces)==276
write('diagnostic-source-assessment.json',{'rows':diagnostics,'count':45440,'by_kind':dict(Counter(d['kind'] for d in diagnostics)),'unmapped':0,'context_packet_sha256':sha(DEST/'source-context-assessment.json')})
write('surface-source-assessment.json',{'rows':surfaces,'count':276,'unassessed':0,'total_possible_surfaces':'unknown; no percentage inferred','workspace':'null in every report; no expanded workspace claim'})

archive=OUT.parent/'v43-four-fresh-preparation/research/source-archives/faf-fixed.tar.gz';anchors={}
with tarfile.open(archive) as t:
 for path,ranges in {'src/handlers/tools.ts':[(28,29),(695,702)],'src/handlers/fileHandler.ts':[(96,131)],'src/utils/safe-path.ts':[(61,75),(83,125),(142,179)]}.items():
  member=next(m for m in t if m.isfile() and m.name.endswith('/'+path));data=t.extractfile(member).read();lines=data.decode().splitlines();assert hashlib.sha256(data).hexdigest()==inv['source_files'][rows[-1]['snapshot']][path]
  anchors[path]={'source_sha256':hashlib.sha256(data).hexdigest(),'ranges':{f'{a}-{b}':'\n'.join(f'{i+1}: {lines[i]}' for i in range(a-1,b)) for a,b in ranges}}
write('faf-fixed-source-assessment.json',{'archive_sha256':sha(archive),'anchors':anchors,'source_review_path':'artifacts/phase22/corpus-four-fresh-v2/faf-read-root/condition-review.json','source_review_sha256':sha(ROOT/'artifacts/phase22/corpus-four-fresh-v2/faf-read-root/condition-review.json'),'conclusion':'Source confines the selected ordinary file paths before the actual read; current scanner path/guard/value/sink support is unestablished because tool-handler delegation remains unresolved. Zero fixed/safe findings therefore fail the required support gate.','source_execution':False,'full_runtime_safety_established':False,'limitation_accepted':False})
cases=copy.deepcopy(three['cases']);cases.append({'case_id':'faf-read-root','batches':{'first':{'completed':3,'vulnerable_hits':0,'matching_negative_alerts':0,'supported_qualified_negatives':0,'unsupported_negatives':2},'repeat':{'completed':0,'pending':3}},'completed':3,'planned':6,'ordered_report_pairs_equal':0,'actual_named_sink_supported':False,'fixed_guard_qualification_established':False,'narrow_repository_gate_passed':False,'full_runtime_safety_established':False,'timings_seconds':[r['timing']['elapsed_seconds'] for r in rows[-3:]],'qualification':'First batch fails detection and negative support; repeat reports remain pending within the active scope.'})
write('assessment.json',{'scanner':validation['scanner'],'proposal_sha256':sha(PREP/'evaluation-proposal.json'),'approval_sha256':sha(PREP/'evaluation-authorization.json'),'rubric_sha256':sha(PREP/'scoring-rubric.json'),'validation_sha256':sha(DEST/'validation.json'),'completed':21,'distinct_inputs_completed':12,'entire_ordered_pairs_equal':9,'source_assessment_complete_for_completed21':True,'complete_report_difference_assessment_pending':True,'four_repository_sequence_complete':False,'FAF_repeats_pending':3,'budget_closed':False,'execution_gate_passed_for_completed21':True,'repository_gates_passed':2,'repository_gates_required':4,'repository_gates_with_observed_failed_prerequisites':['lightning-discover-linklocal','faf-read-root'],'cases':cases,'rows':rows,'finding_count':260,'diagnostic_count':45440,'surface_count':276,'source_context_count':4963,'within120':18,'beyond1800':3,'max_whole_seconds':max(r['timing']['elapsed_seconds'] for r in rows),'new_inputs':0,'paid_calls':0,'target_execution':False,'limitation_accepted':False,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'All12distinct inputs have now completed in this one active24-observation experiment. Two narrow exposed repository gates pass with exact prospective qualifiers; Lightning negative discrimination and FAF vulnerable/negative support fail. Only three FAF repeats remain. All original first-frozen failures, normal1800-second policy failures and earlier-language compatibility requirements persist. No automatic correction or source tuning during the sequence.','evidence_sha256':{n:sha(DEST/n) for n in ['inventory.json','source-context-assessment.json','finding-source-assessment.json','diagnostic-source-assessment.json','surface-source-assessment.json','faf-fixed-source-assessment.json']},'reused_assessments_sha256':{str((p/'assessment-with-differences.json').relative_to(ROOT)):sha(p/'assessment-with-differences.json') for p in (THREE,FAF)}})
print('All21completed outputs source-assessed:260findings/45440diagnostics/276surfaces/4963contexts. Two narrow gates pass;Lightning andFAF fail. Three FAF repeats remain active.')
