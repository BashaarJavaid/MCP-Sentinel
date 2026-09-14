"""Prepare a complete current acceptance audit only after both approved gates finish."""
import copy,hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];PRIOR=BASE/'v72-prototype-property-correction'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT))
def write(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
old=read(PRIOR/'audit.json');four=read(BASE/'v73-corrected-four-results/final-assessment/assessment.json');languages=read(BASE/'v75-prior-language-results/final-assessment/assessment.json')
assert four['all_four_narrow_gates_passed'] and four['completed']==24 and four['entire_ordered_pairs_equal']==12
assert languages['all_narrow_conditions_passed'] and languages['completed']==181 and languages['entire_ordered_pairs_equal']==83 and languages['source_assessment_complete']
assert read(BASE/'v75-prior-language-results/completion-verification.json')['passed']
assert read(PRIOR/'delivery-verification.json')['passed']
assert len(old['requirements'])==89 and len(old['additional_scope_requirements'])==318
rows=copy.deepcopy(old['additional_scope_requirements']);originals=copy.deepcopy(old['requirements'])
current_evidence=[BASE/'v73-corrected-four-results/final-assessment/assessment.json',BASE/'v75-prior-language-results/final-assessment/assessment.json',BASE/'v75-prior-language-results/completion-verification.json']
current_ids={'V45-REGRESSION','V45-ASSESSMENT','V48-REGRESSION','V52-REGRESSION','V70-PRIOR-LANGUAGES','V72-CURRENT-REGRESSION'}
limits={
 'R66':'Original held-out10complete/10unsupported/5incomplete;0hits among4completed vulnerable of10total. Exposed corrections do not establish unseen-source accuracy.',
 'R88':'Original source-selection/fresh failures remain; later corrections are exposed and same-agent source-reviewed. DDG first-frozen f85a90f detection and prospective output discrimination passed, but build_request/send fixed-path support was absent. V35 a50e9b7 completed87/36pairs yet qualified0of6DDGnegative sends and failed Meta image fixed/control qualification; V38 and currentV75 exposed corrections do not retroactively pass those support failures.',
 'V14-RETENTION':'Failed/reverted optimization; no5%paired gain or current speedup established.',
 'V21-SEQUENCE':'Original62/115stopped,53unstartedclosed; exact98refresh and whole25reuse later establish their actual1f3f72f whole-batch results. Current subsets are no new whole45+45Linux runs.',
 'V21-FRESH-PROPOSAL':'Reusedv4preparation failed novelty; later independently prepared sources do not retroactively makev4fresh.',
 'V25-EXPOSED-REGRESSION':'6db3858Lighthouse vulnerable miss;1/10attempted,9closed. Laterf85a90f exposed pass and current qualification do not erase the miss.',
 'V27-REGRESSION':'4a2359dLighthouse fixed qualification failed after2vulnerablehits;3/10attempted,7closed. Later exposed passes retain the failure.',
 'V39-EVALUATION':'8c62567fresh memory-keeper negative failure:1vulnerablehit/2matchingnegativealerts perbatch. Later2e0efb2andcurrentcec0322exposed passes are distinct.',
 'V44-FOUR-GATE':'Original2e0efb2four-repository24/24,12pairs,all4gatesfailed. Currentcec0322all4narrowexposed passes do not make the original results fresh successes.',
 'V49-DIAGNOSTIC-PREPARATION':'InvalidV50stale-root preparation/attempt imported17b4784instead of6e4fd67. Six valid partial profiles retain separate process/source/interval limits; no speedup or removable fraction.',
 'V55-EQUIVALENCE':'Reverted broad-singleton synthetic environment-equivalence failure; structural flow equality does not remove identity-sensitive environment delta. Real-target reachability unestablished.',
 'V56-EQUIVALENCE':'Reverted canonical-singleton eviction failure. Separately approvedV57equal-marker correction and bypass do not retroactively pass the original strict failure.',
 'V65-EQUIVALENCE':'Strict captured-arm alias/shrinking failure after256ordinary passes. ApprovedV66prospective private/monotone domain excludes only its two named injected callbacks; original strict failure remains.',
 'V70-FOUR-GATE':'4145d35no-bash/Engram narrow passes; Lightning fixed/safe qualification and FAF detection/support failures. Currentcec0322supersedes current detection evidence only.',
 'V68-OPT-DECISION':'Explicitly propose leaving original4145d35literal-serialization performance proposal unopened, unimplemented and unapproved; no performance attempt included.'}
for n in [46,49,53,58,60,63,67]:limits[f'V{n}-REGRESSION-GATE']='Historical source-bound native timeout:1incomplete/0reports/204unstartedclosed of205;zero remaining. Current uncapped FAF observations are distinct approved runs. No retrospective timeout pass or reopened budget.'
for row in originals+rows:
 identity=row['id']
 if identity in current_ids or identity in limits or identity=='V72-DELIVERY':
  before=copy.deepcopy(row);row['previous_row']=before
  if identity in current_ids:
   row.update(disposition='passed',assessment='Current-source requirement established by separately approvedV73four24andV75prior-language181, with95wholeorderedpairs, actual caller/guard/sink support and full source assessment. Original source-bound failed/stopped attempts remain historical; ordinaryFAF1800completion remains a proposed limitation.',evidence=list(dict.fromkeys(row.get('evidence',[])+[rel(p) for p in current_evidence])))
  elif identity=='V72-DELIVERY':row.update(disposition='passed',assessment='Actual5263cb2existing-draft delivery verified by supplementalV72receipt; sealed pending previous row preserved.',evidence=[rel(PRIOR/'delivery-verification.json')])
  else:row.update(disposition='proposed documented limitation awaiting decision',assessment=limits[identity]+' Explicit human acceptance remains required.',evidence=list(dict.fromkeys(row.get('evidence',[])+[rel(p) for p in current_evidence]+[rel(OUT/'acceptance-limits.md')])))
new=[
 ('V73-AUTH','Bind exact approved corrected24-observation scope, intake, source and sole token','passed',['v73-corrected-regression-intake.json','v72-prototype-property-correction/evaluation-authorization.json','v72-prototype-property-correction/execution-consumed.json']),
 ('V73-EXECUTION','Complete24static observations,12entire ordered pairs, zero-paid budget closure and cleanup','passed',['v73-corrected-four-results/execution.json','v73-corrected-four-results/completion-verification.json']),
 ('V73-FOUR-GATES','Establish all4current-source narrow vulnerable/fixed/safe gates','passed',['v73-corrected-four-results/final-assessment/assessment.json']),
 ('V73-ASSESSMENT','Source-assess all794findings/87808diagnostics/282surfaces/6781contexts and complete ordered differences','passed',['v73-corrected-four-results/final-assessment/assessment.json']),
 ('V73-TIMING','Retain all6uncapped FAF durations and unchanged normal1800policy without claiming speedup','passed',['v73-corrected-four-results/execution.json','v73-corrected-four-results/final-assessment/assessment.json']),
 ('V74-PREPARATION','Bind unchanged181-observation compatibility scope, source, runtime, normal limits and tested approval boundaries','passed',['v74-prior-language-preparation/evaluation-proposal.json','v74-prior-language-preparation/preparation-verification.json','v74-prior-language-preparation/runner-boundaries.json']),
 ('V75-AUTH','Bind exact V74approval, source/runtime preflight and sole181-observation token','passed',['v74-prior-language-preparation/evaluation-authorization.json','v74-prior-language-preparation/execution-preflight.json','v74-prior-language-preparation/execution-consumed.json']),
 ('V75-EXECUTION','Complete181static observations/83ordered pairs with normal1800/Semgrep10/cleanup15/four-worker limits and closed budget','passed',['v75-prior-language-results/execution.json','v75-prior-language-results/final-assessment/validation.json','v75-prior-language-results/completion-verification.json']),
 ('V75-COMPATIBILITY','Establish94TypeScript/87Python narrow compatibility; retain DDGqualification and2Metaoperator errata','passed',['v75-prior-language-results/final-assessment/assessment.json']),
 ('V75-ASSESSMENT','Assess every changed finding, warning, unresolved flow, surface and full ordered report difference against actual source','passed',['v75-prior-language-results/final-assessment/assessment.json','v75-prior-language-results/final-assessment/difference-inventory.json']),
 ('V76-ENGINEERING-REUSE','Bind unchanged testedcec0322engineering, sixzero-callproduction requests and19runtimecomponents','passed',['v72-prototype-property-correction/local-checks.json','v72-prototype-property-correction/compatibility.json','v75-prior-language-results/completion-verification.json']),
 ('V76-FAF-DEADLINE','Obtain explicit practical disposition of ordinary1800-second FAF completion remaining unestablished','proposed documented limitation awaiting decision',['v73-corrected-four-results/final-assessment/assessment.json']),
 ('V76-FAILURE-RETENTION','Preserve all407previous rows, historical failures, approvals and original/corrected continuation helpers','passed',['v76-technical-acceptance/prior-row-preservation.json','v76-technical-acceptance/check-failure-assessment.json']),
 ('V76-REVIEW-DELIVERY','Complete affected docs/packages, seal evidence and verify review-packet delivery to existing OPEN DRAFT PR37','unresolved',[]),
 ('V76-ACCEPTED-CLOSEOUT','Record explicit technical acceptance then deliver and verify actual accepted closeout without merge/release','unresolved',[])]
for identity,requirement,disposition,paths in new:
 rows.append({'id':identity,'requirement':requirement,'disposition':disposition,'evidence':[rel(BASE/p) for p in paths],'assessment':('Current source-bound evidence as linked; no target execution or paid call.' if disposition=='passed' else 'Explicit human decision and/or subsequent verified delivery remain required; Phase22incomplete.')})
assert len({r['id'] for r in originals+rows})==407+len(new)
p=copy.deepcopy(old);p['historical_v72_status_fields']={k:copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements','current_requirement_interpretations'} and not k.startswith('historical_')}
p.update(recorded_at=datetime.now(timezone.utc).isoformat(),requirements=originals,additional_scope_requirements=rows,dispositions=dict(Counter(r['disposition'] for r in originals)),additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),prior_audit={'path':rel(PRIOR/'audit.json'),'sha256':sha(PRIOR/'audit.json')},regression_approved=True,regression_executed=True,current_regression_approved=True,current_regression_executed=True,proposed_native_observations=0,current_source_corpus_observations=205,current_source_completed_observations=205,current_source_incomplete_observations=0,execution_gate_passed=True,current_four_repository_gate_passed=True,current_four_repository_gates_passed=4,current_earlier_language_compatibility_established=True,budget_closed=True,remaining=0,unstarted_closed=0,acceptance_packet_ready=True,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,status='All current-source narrow detection/compatibility gates pass under their exact approved policies; explicit human acceptance of the delivered packet and recorded historical/practical limitations, then verified accepted closeout, remain. No speedup or normal-policy FAF completion established.')
p['current_budget_interpretation']='Two separately approved closed budgets:V73uncapped24/24andV75normal181/181,95wholeorderedpairs;zero remaining/retries/profiles/paid calls. No old budget reopened.'
p['current_source_input_accounting']={'total_attempted_inputs':205,'native_attempts_total':205,'unique_input_records':110,'completed':205,'sampled_attempts_total':0,'authorized_remaining':0,'four_repository_uncapped_observations':24,'normal_policy_prior_language_observations':181,'whole_ordered_pairs_equal':95,'qualification':'Separate approvals and policies; no new whole45+45Linux batch or fresh-source pass.'}
p['experimental_timeout_policy'].update(approved=True,executed=True,budget_closed=True,remaining=0)
p['current_evidence']={rel(path):sha(path) for path in current_evidence}
condition_ids={'R18':'atlassian-auth','R19':'atlassian-ssrf','R20':'atlassian-upload','R21':'excel-boundary','R22':'filesystem-prefix','R23':'git-arguments','R24':'git-repository','R25':'git-staging','R26':'kubernetes-shell','R27':'mobile-output','R28':'Mastra','R29':'calculator metadata','R31':'dbt selector','R33':'Meta image URL','R35':'Meta operator fallback including2approvederrata','R87':'fetchmcp','R89':'SearXNG'}
for row in originals+rows:
 identity=row['id'];entry=copy.deepcopy(old.get('current_requirement_interpretations',{}).get(identity,{}));entry['previous_interpretation']=copy.deepcopy(entry)
 basis='The exact original requirement and its source/test/evidence bindings remain above. Product,tests,harness,lock and all303engineering inputs match testedcec0322; actual2450/36local and12hosted suites,29normal jobs/docs,6production request replays and19runtimebindings remain source-bound. This docs/evidence continuation adds no hosted code pass.'
 if identity in condition_ids:basis='Current V75 source-assessed '+condition_ids[identity]+' observations establish the same narrow condition under unchanged source/prerequisites; full ordered deltas and unrelated uncertainty remain. '+basis
 elif identity in {'R63','R64','R65','V21-SEQUENCE'}:basis='Retain actual1f3f72fwhole25development reuse and whole45+45Linux evidence at original sources. Current94TS/87Python compatibility is separately approved and cannot be pooled into a new wholeLinux batch. '+basis
 elif identity=='R67':basis='All new/changed unrelated candidates are separately source-assessed; calculator adds2outside-metadata candidates per report and14Git repository-copy occurrences retain initial-check/physical-use qualifications, without independent confirmed exploit/false-positive judgments. Complete raw denominators and uncertainty retained. '+basis
 elif identity in limits:basis=limits[identity]+' This is a proposed explicit limitation, not an accepted waiver or retrospective pass.'
 elif identity in current_ids:basis=row['assessment']
 elif identity in {'R77','R78'}:basis='Actual user deferral persists:396-request paid benchmark and external pilots are deferred and nonblocking for revisedPhase22; no paid observation added.'
 elif identity in {'R84','V43-ACCEPTANCE-CLOSEOUT','V76-ACCEPTED-CLOSEOUT'}:basis='Separate explicit human technical acceptance of the delivered proposal and subsequent verified accepted-closeout delivery remain required. Evaluation approvals do not satisfy them; pilots remain explicitly deferred.'
 elif identity.startswith(('V73-','V74-','V75-','V76-')):basis=row['assessment']+' '+row['requirement']
 entry.update(requirement=row['requirement'],current_disposition=row['disposition'],current_execution_interpretation=basis,current_execution_evidence={rel(path):sha(path) for path in current_evidence})
 p['current_requirement_interpretations'][identity]=entry
assert len(p['current_requirement_interpretations'])==len(originals)+len(rows)
write('audit.json',p)
write('prior-row-preservation.json',{'prior_audit_sha256':sha(PRIOR/'audit.json'),'retained_prior_rows':407,'total_rows':len(originals)+len(rows),'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']},'changed_rows':[r['id'] for before,r in zip(old['requirements']+old['additional_scope_requirements'],originals+rows,strict=False) if before!=r],'previous_rows_preserved':all(before==after or before==after.get('previous_row') for before,after in zip(old['requirements']+old['additional_scope_requirements'],originals+rows))})
print('Prepared complete audit:',len(originals)+len(rows),'rows; explicit technical acceptance and accepted closeout remain pending.')
