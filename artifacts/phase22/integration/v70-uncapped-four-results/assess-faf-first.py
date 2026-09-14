"""Assess the completed FAF vulnerable report without adding an observation."""
import hashlib
import json
import tarfile
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];DEST=OUT/'first-faf-assessment';OLD=OUT.parent/'v44-four-fresh-evaluation';PREP=OUT.parent/'v69-uncapped-four-repository'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
 with (DEST/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')

inv=read(DEST/'inventory-source-corrected.json');initial=read(DEST/'inventory.json');validation=read(DEST/'validation.json');old=read(OLD/'inventory.json');assert validation['passed'] and len(inv['rows'])==1
row=inv['rows'][0];v=validation['observations'][0];assert row['input_id']==v['input_id']=='faf-read-root-vulnerable' and not row['findings'];assert len(row['diagnostics'])==2332 and len(row['surfaces'])==2
changed=[k for k,c in inv['contexts'].items() if c!=initial['contexts'][k]];assert len(changed)==1
assert inv['contexts'][changed[0]]['occurrence_lines']==[27]
write('source-index-correction.json',{'initial_failed_check':'v70-faf-first-inventory','initial_failure':'Conceptual dynamic-tool-description diagnostic had no literal description occurrence in cli-detector.ts; helper incorrectly required one. No report/input execution failed.','first_correction':'Keep the whole verified file with explicit file-only location precision; do not invent a source line.','subsequent_mapping_error':'The relative module specifier began with a dot; splitting at the first dot produced an empty base and falsely matched every source line. The intermediate check missed that semantic indexing error.','corrected_context':changed[0],'original_mapping':initial['contexts'][changed[0]],'corrected_mapping':inv['contexts'][changed[0]],'initial_inventory_sha256':sha(DEST/'inventory.json'),'corrected_inventory_sha256':sha(DEST/'inventory-source-corrected.json'),'helper_checks':['v70-faf-first-inventory-corrected','v70-faf-first-source-inventory'],'source_only':True,'new_observations':0,'qualification':'Initial helpers/checks remain preserved. This is assessment tooling correction, not a scanner retry, altered source/report or waived gate.'})
contexts={}
for key,c in inv['contexts'].items():
 p=c['path'];prior=old['contexts'].get(key)
 if prior is not None:assert c==prior
 if p.startswith('tests/') or '.test.' in p or '/test-' in p:
  role='Retained upstream test/harness source, mocks and assertions. Source data only; never imported or executed. Its unresolved framework/global/module bindings do not establish production reachability.'
 elif p in {'src/server.ts','src/index.ts','src/cli.ts'}:
  role='FAF package entry or SDK server construction/registration. The current report discovers two unnamed registration surfaces bound to the same server handler; only the cli surface lists examined rules. server.ts94 still leaves this.toolHandler.callTool unresolved. Raw request, SDK escape, transport, logging and error limitations remain; source startup reachability does not prove named faf_read analysis.'
 elif p=='src/handlers/tools.ts':
  role='FAF tool listing/dispatch. FafToolHandler constructor uses private engineAdapter parameter-property syntax at28; current TypeScriptPathFlow.class_members rejects constructor parameter attributes. Source callTool faf_read arm694-701 delegates to fileHandlers.faf_read, but the class and actual server delegation remain unsupported in this report. No named sink is detected.'
 elif p=='src/handlers/fileHandler.ts' or p=='src/utils/safe-path.ts':
  role='FAF file read/confinement implementation. The vulnerable source normalizes and denies selected system prefixes but permits the frozen absolute outside regular file. Its actual fs.readFile127 receives the requested path after validation/size prerequisites. No caller-bound finding establishes this sink in the completed report; zero findings fail detection rather than prove safety.'
 elif p=='src/handlers/engine-adapter.ts':
  role='FAF engine/CLI adapter: working-directory environment, CLI discovery, command dispatch, local implementation fallback and error handling. Indexed argument aliases and global/environment states remain unresolved. These broader command routes are not substitutes for the named fileHandlers.faf_read sink, nor evidence of target execution or measured native stage cost.'
 elif p=='src/utils/cli-detector.ts':
  role='CLI location/version detection from operator environment, platform candidates, glob expansion and bounded source loops. Indexed aliases, control flow and dynamic metadata remain unresolved. The conceptual dynamic-description warning supplies only this file, with no literal description token; the full verified source is retained without invented line attribution.'
 elif p=='src/handlers/championship-tools.ts':
  role='Separate championship tool listing/dispatch and project scoring/context operations. Their environment, command, indexed-value and control-flow limitations remain. They do not count as the selected faf_read sink or independently prove runtime tool registration.'
 elif p.startswith('src/faf-core/commands/'):
  role='FAF core command '+Path(p).stem+' handles project/context configuration, rendering or updates. Its retained loops, indexed arrays, dynamic field assignments and global/error bindings are source limitations outside the frozen initial read condition; no command or target mutation ran.'
 elif p.startswith('src/faf-core/parsers/'):
  role='FAF format/metadata parser '+Path(p).stem+'. Parsing, indexed values, loop exits, formatting and any GitHub-related environment/network bindings remain unresolved as recorded. These are separate source routes, not a named read hit, resolved external operation or authorized target request.'
 elif p.startswith('src/faf-core/engines/') or p.startswith('src/faf-core/generators/'):
  role='FAF analysis/generation helper '+Path(p).stem+' processes project files, dependencies, formats and generated context. Retain unknown state, indexed aliases, dynamic fields and loop/control limitations; source inspection does not execute it or certify runtime output.'
 else:
  role='FAF source helper '+p+' provides platform/filesystem/configuration/formatting or related support. Each indexed occurrence retains its exact unresolved binding or control-flow limitation and separate source prerequisites; no inferred safety, exploit or named-condition substitution.'
 contexts[key]={'source':c,'assessment':role,'prior_identical_source_context':prior is not None,'disposition':'Retain exact source-bound uncertainty. Statement/binding indexing is not resolution, execution or a broad safety claim.'}
assert len(contexts)==1490 and sum(c['prior_identical_source_context'] for c in contexts.values())==1171
write('source-context-assessment.json',{'contexts':contexts,'count':1490,'prior_identical_contexts':1171,'new_contexts':319,'unassessed':0,'qualification':'Same-agent source review; conceptual diagnostic stays file-only and relative import maps to its actual literal line27.'})
write('finding-source-assessment.json',{'rows':[],'count':0,'unassessed':0,'qualification':'Actual completed report has zero findings; named vulnerable detection fails. This is not a missing-report zero or proof of safety.'})
diagnostics=[{'input_id':row['input_id'],'batch':row['batch'],'report_sha256':row['report_sha256'],**d,'assessment_context':d['context'],'disposition':'Retain exact warning/unresolved operation and source role; no inferred safety or suppression.'} for d in row['diagnostics']]
assert all(d['context'] in contexts for d in diagnostics)
write('diagnostic-source-assessment.json',{'rows':diagnostics,'count':2332,'by_kind':dict(Counter(d['kind'] for d in diagnostics)),'unmapped':0,'context_packet_sha256':sha(DEST/'source-context-assessment.json')})
surfaces=[]
for s in row['surfaces']:
 value=s['surface'];assert value['status']=='unresolved' and value['name'] is None and value['handler']['path']=='src/server.ts' and value['handler']['range']['start_line']==91
 surfaces.append({**s,'assessment':'Unnamed ambiguous-dispatch surface at '+value['location']['path']+'. It binds server.ts91-110, whose callTool delegation at94 remains unresolved. The cli location lists five examined rule IDs; the index location lists none. Preserve each exact entry and reason; identical handler source does not justify inventing per-entry coverage, a named tool, or a detected sink.'})
write('surface-source-assessment.json',{'rows':surfaces,'count':2,'unassessed':0,'total_possible_surfaces':'unknown','workspace':row['coverage']['workspace']})
archive=OUT.parent/'v43-four-fresh-preparation/research/source-archives/faf-vulnerable.tar.gz';anchors={}
with tarfile.open(archive) as t:
 for path,ranges in {'src/handlers/tools.ts':[(27,28),(690,701)],'src/server.ts':[(53,59),(86,110)],'src/handlers/fileHandler.ts':[(82,131)]}.items():
  member=next(m for m in t if m.isfile() and m.name.endswith('/'+path));data=t.extractfile(member).read();lines=data.decode().splitlines();assert hashlib.sha256(data).hexdigest()==inv['source_files'][row['snapshot']][path]
  anchors[path]={'source_sha256':hashlib.sha256(data).hexdigest(),'ranges':{f'{a}-{b}':'\n'.join(f'{i+1}: {lines[i]}' for i in range(a-1,b)) for a,b in ranges}}
source=ROOT/'src/sentinel/static/typescript_path_flow.py';lines=source.read_text().splitlines();anchors[str(source.relative_to(ROOT))]={'source_sha256':sha(source),'ranges':{'807-869':'\n'.join(f'{i+1}: {lines[i]}' for i in range(806,869))}}
write('named-source-diagnosis.json',{'archive_sha256':sha(archive),'anchors':anchors,'finding':'Constructor parameter properties are explicitly excluded by class_members. FafToolHandler uses constructor(private engineAdapter: FafEngineAdapter), and the actual completed report emits its class-unsupported warning plus unresolved this.toolHandler.callTool. Source delegates the named faf_read arm to actual fs.readFile, which is absent from findings.','qualification':'Source-visible supported explanation for this missed route, not a new trace/profile or proof that a parameter-property correction alone completes discovery, detection, fixed guards or compatibility. Other unsupported classes/members/control flow remain. No source optimization/correction or target execution performed.'})
write('assessment.json',{'scanner':validation['scanner'],'proposal_sha256':sha(PREP/'evaluation-proposal.json'),'approval_sha256':sha(PREP/'evaluation-authorization.json'),'validation_sha256':sha(DEST/'validation.json'),'input_id':row['input_id'],'completed':1,'whole_seconds':v['timing']['elapsed_seconds'],'native_seconds':v['native_seconds'],'cleanup_verified':True,'within_normal_1800_policy':False,'uncapped_execution_gate_passed':True,'source_assessment_complete_for_this_report':True,'complete_report_difference_assessment_pending':True,'vulnerable_hit':False,'named_sink_support_established':False,'vulnerable_detection_gate_passed':False,'fixed_and_safe_pending':True,'repeat_pending':True,'finding_count':0,'warning_count':1548,'unresolved_flow_count':784,'diagnostic_count':2332,'surface_count':2,'source_context_count':1490,'four_repository_sequence_complete':False,'budget_closed':False,'new_inputs':0,'paid_calls':0,'target_execution':False,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'First current-source native FAF report completes under experimental uncapped policy in2283.81718seconds but fails named vulnerable detection. One actual observation within the still-active24-observation sequence; no retry/new batch and no historical timeout or first-frozen gate is rewritten. Remaining five FAF observations continue.','evidence_sha256':{n:sha(DEST/n) for n in ['inventory-source-corrected.json','source-index-correction.json','source-context-assessment.json','finding-source-assessment.json','diagnostic-source-assessment.json','surface-source-assessment.json','named-source-diagnosis.json']}})
print('First FAF report source-assessed:2283.81718seconds,zero findings,2332diagnostics,2unresolved surfaces; named detection fails. Remaining sequence untouched.')
