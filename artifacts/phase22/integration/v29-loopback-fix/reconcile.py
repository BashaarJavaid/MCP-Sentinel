"""Reconcile all original and added requirements with actual completed evidence."""
import copy
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path.cwd();BASE=ROOT/'artifacts/phase22/integration';OUT=BASE/'v29-loopback-fix'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((BASE/'v27-constructor-fix/audit.json').read_text());p=copy.deepcopy(old)
quality=json.loads((BASE/'v29-quality-audit/packet.json').read_text())
assert len(quality['quality'])==12 and all(q['passed']==2242 and q['skipped']==36 for q in quality['quality'])
assert json.loads((BASE/'v29-full-suite.json').read_text())['exit_code']==0
assert json.loads((OUT/'local-source-binding.json').read_text())['current_product_tests_packages_equal_corrected_commit']
proposal=json.loads((OUT/'evaluation-proposal.json').read_text())
assert not proposal['approval_received'] and not (OUT/'evaluation-authorization.json').exists()
counts=defaultdict(Counter)
for c in ET.parse(BASE/'v29-full-suite-junit.xml').iter('testcase'):
 state='skipped' if c.find('skipped') is not None else 'failed' if c.find('failure') is not None or c.find('error') is not None else 'passed'
 counts[c.attrib['classname'].replace('.','/')+'.py'][state]+=1
assert sum(c['passed'] for c in counts.values())==2242 and sum(c['skipped'] for c in counts.values())==36 and not any(c['failed'] for c in counts.values())
refs=['v29-quality/packet.json','v29-quality-audit/packet.json','v29-full-suite.json','v29-full-suite-junit.xml','v29-full-suite-coverage.json','v29-production-capture-revalidation/packet.json','v29-loopback-fix/compatibility.json','v29-loopback-fix/local-source-binding.json','v29-loopback-fix/local-checks.json','v29-loopback-fix/correction.json','v29-loopback-fix/check-failure-assessment.json','v29-loopback-fix/evaluation-proposal.json','v29-loopback-fix/source-compatibility-scope.json','v28-lighthouse-regression/assessment.json','v28-lighthouse-regression/source-assessment.json','v28-lighthouse-regression/retained-source-deltas.json','v27-constructor-fix/evaluation-authorization.json']
common='The4a2359d approved regression detected both correlated vulnerable variants, then failed fixed-input qualification;3 completed,7 unstarted closed. Currentf85a90f passes engineering at439c3fe but has no corpus observation. Historical results retain actual measured sources. No new limitation or final technical acceptance is inferred.'
for row in p['requirements']:
 prior=next(r for r in old['requirements'] if r['id']==row['id'])
 row['prior_requirement_record_sha256']=hashlib.sha256(json.dumps(prior,sort_keys=True).encode()).hexdigest()
 row['historical_assessment']={'audit':'v27-constructor-fix/audit.json','text':row['assessment']}
 row['evidence'].extend('artifacts/phase22/integration/'+n for n in refs)
 row['interpretation']=common
 if row['id'] in {'R66','R88'}:
  row['assessment']='Original fresh1f3f72f remains15 completed with0/2 hits per native batch and comparator. The approved4a2359d exposed run detects2/2 correlated vulnerable inputs, but its first fixed input lacks required narrow qualification. Three complete,seven closed unstarted,no control/repeat/full-batch pass. All3 findings,261 warnings,164 flow occurrences and6 unresolved surfaces are source-assessed. Minimalf85a90f correction passes engineering; exact new regression is unapproved. Fresh outcome disposition and generalization limitations remain unresolved.'
 elif row['id'] in {'R71','R72','R73','R74'}:
  row['assessment']='Currentf85a90f local and all12 hosted suites pass2242 tests/36 skips with branch coverage above80%;29 normal jobs/docs at439c3fe pass. Exact package blobs,lock/schema/notices/artifacts,Ruff/format/strictmypy,wheel/Docker/isolation/hooks and six zero-call production replays pass. This is engineering evidence,not a corrected corpus pass.'
 elif row['id'] in {'R62','R83'}:
  row['assessment']='Owning docs and audit preserve all first frozen failures, the stopped4a2359d fixed-condition failure and closed seven-input remainder, verified narrow loopback correction and exact unapproved proposal. Earlier timing/exposed passes remain source-bound; current compatibility/fresh disposition/human acceptance remain open. Phase22 incomplete and later-phase/paid/pilot dispositions unchanged.'
 elif row['id'] in {'R44','R70','R75','R76'}:
  row['assessment']+=' At439c3fe, whose scanner bytes equalf85a90f, all six requests replay with unchanged fingerprints/request hashes and zero paid calls. Git runtime/image remain unchanged and campaigns incomplete312/1040.'
for row in p['additional_scope_requirements']:
 if row['id']=='V27-REGRESSION':
  row['assessment']='Exact new approved run34641101185 at4a2359d completed two vulnerable hits then failed first fixed qualification. Three observations consumed,seven unstarted closed,no remaining budget. This remains a closed historical failed gate.'
  row.setdefault('evidence',[]).append('artifacts/phase22/integration/v28-lighthouse-regression/assessment.json')
for i,text,status in [
 ('V28-AUTH','Record actual approved decision and consume exactly one bounded dispatch','passed'),
 ('V28-DISPOSITION','Retain three completed observations,close seven unstarted,and assess all findings/diagnostics/coverage','passed'),
 ('V29-CORRECTION','Preserve narrow IPv4 link-local exclusion across IPv6 loopback equality returns without broad safety claims','passed'),
 ('V29-ENGINEERING','Verify minimal correction and six regressions locally and in the supported hosted matrix','passed'),
 ('V29-PROPOSAL','Prepare exact next bounded regression without executing it','passed'),
 ('V29-REGRESSION','Obtain exact new approval and demonstrate complete Lighthouse discrimination and ordered-repeat gate','unresolved')]:
 p['additional_scope_requirements'].append({'id':i,'requirement':text,'disposition':status,'evidence':['artifacts/phase22/integration/'+n for n in refs]})
p.update(recorded_at=datetime.now(timezone.utc).isoformat(),source='439c3fe658d30ebbc6cf6e21296261a38a6a3e92',scanner_identity=proposal['scanner'],workflow_tested_source='439c3fe658d30ebbc6cf6e21296261a38a6a3e92',current_tests_by_file=dict(counts),current_source_corpus_runs=0,latest_measured_scanner=json.loads((BASE/'v28-lighthouse-regression/assessment.json').read_text())['scanner'],prior_scanner_regression_observations_this_continuation=3,new_paid_calls=0,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,current_exposed_evaluation_approved=False,current_exposed_evaluation_executed=False,status=common,prior_audit={'path':'v27-constructor-fix/audit.json','sha256':sha(BASE/'v27-constructor-fix/audit.json')},owning_document_binding='Final v29 documentation/delivery bindings are supplemental to this pre-seal audit.',per_file_test_counts_basis='Actual completed v29 JUnit; exact product/test sources bound to committedf85a90f.')
p['historical_source_and_test_file_bindings']={'source':old['source'],'files':old['current_source_and_test_files'],'earlier':old['historical_source_and_test_file_bindings']}
p['current_source_and_test_files']={n:sha(ROOT/n) for n in old['current_source_and_test_files']}
p['references_sha256'].update({n:sha(BASE/n) for n in refs})
p['dispositions']=dict(Counter(r['disposition'] for r in p['requirements']))
p['additional_scope_dispositions']=dict(Counter(r['disposition'] for r in p['additional_scope_requirements']))
assert len(p['requirements'])==89 and len(p['additional_scope_requirements'])==78
assert p['dispositions']=={'passed':82,'explicitly user-deferred':2,'unresolved':5}
assert p['additional_scope_dispositions']=={'passed':71,'unresolved':7}
path=OUT/'audit.json';assert not path.exists();path.write_text(json.dumps(p,indent=2)+'\n');print(p['dispositions'],p['additional_scope_dispositions'])
