"""Bind the deliberate credential-join correction and separately equivalent bypass."""
import hashlib,json,subprocess,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=Path.cwd();BASE=OUT.parent
sys.path.insert(0,str(ROOT))
from scripts.phase20_measurements import scanner_identity
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
head=read(OUT/'candidate-commit.json')['source']
assert head=='dc7371513a065457af566f4b589b9ed147130d64'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
assert not subprocess.check_output(['git','diff','HEAD'])
old=(OUT/'baseline-sent016.py').read_text()
expected=old.replace('            if all(branch.get(name, empty) is first for branch in branches[1:]):','            if all(\n                (other := branch.get(name, empty)) is first or other == first\n                for branch in branches[1:]\n            ):',1)
assert (ROOT/'src/sentinel/static/rules/sent016.py').read_text()==expected
expected=(OUT/'baseline-path-flow.py').read_text().replace('    return _combine(tuple(values), key)','    if len(values) == 1 and values[0] is UNKNOWN_VALUE and not key:\n        return UNKNOWN_VALUE\n    return _combine(tuple(values), key)',1)
assert (ROOT/'src/sentinel/static/path_flow.py').read_text()==expected
c=read(OUT/'correction-validation.json');v=read(OUT/'synthetic-validation.json');r=read(OUT/'synthetic-reports.json')
assert c['passed'] and c['cases']==4050 and len(c['intended_marker_deltas'])==len(c['downstream_guard_cache_deltas'])==552
assert v['passed'] and v['semantic_cases']==2430 and len(v['cache_eviction_cases'])==2
assert r['passed'] and len(r['cases'])==7
assert [x['expected_matches'] for x in r['cases']]==[1,1,0,1,1,0,0]
assert all(x['entire_ordered_rule_state_equal'] for x in r['cases'])
scanner=scanner_identity();assert scanner['revision']==head
packet={'scanner':head,'scanner_identity':scanner,'attempts':1,'authorization_sha256':sha(OUT/'authorization.json'),'exact_two_approved_product_edits':True,'baseline_files_sha256':{name:sha(OUT/name) for name in ['baseline-path-flow.py','baseline-sent016.py']},'candidate_files_sha256':{name:sha(ROOT/name) for name in ['src/sentinel/static/path_flow.py','src/sentinel/static/rules/sent016.py']},'correction_validation_sha256':sha(OUT/'correction-validation.json'),'synthetic_validation_sha256':sha(OUT/'synthetic-validation.json'),'synthetic_reports_sha256':sha(OUT/'synthetic-reports.json'),
    'approved_semantic_delta':'CredentialFlow.merge retains the first Value when all present/defaulted marker Values are completely equal, independently of cache interning. Across4050cases,552changed marker records are exactly this branch: formerly reset uncontained fields or stripped source-free safety metadata now retain the equal first marker. These are deliberately changed a36f696 internal states, not hidden equivalence exclusions. Every other environment entry and pre-consumer flow field agrees.',
    'downstream_assessment':'552derived credential_guard_cache input tuples change because they include those exact marker Values. The cached guard facts and conditioned credential outputs agree. Only contained HTTP-source markers contribute absent-caller facts, and only contained selected markers establish operator opt-in. The correction does not create guard facts from uncontained markers. Seven existing synthetic HTTP credential patterns preserve all ordered matches/captures, warnings, visits, exemptions and skip_reason, with four detections and three negatives.',
    'bypass_proof':'The correction-only source was preserved before editing combine. Against it,2430complete Value/Python/TypeScript environment and structural flow cases plus two saturated-cache eviction cases agree with no exclusions. Canonical UNKNOWN_VALUE with one input and empty key avoids tuple/cache dispatch; nine ineligible controls retain dispatch. No other _combine/LRU/source bytes change. Immutable empty-value interning may differ without changing state semantics under the corrected join.',
    'retained_failures':'Both broad and canonical singleton failures reproduce using their original candidate and a36f696 credential source. Their budgets remain closed and failed rows are not accepted or relabeled. Real-target reachability of the adversarial contained-false marker remains unestablished. Original fresh-source failures, all three native timeouts, partial and invalid profiles remain unchanged.',
    'helper_failure_assessment':'First bypass checker seeded self-referential TypeScript record members and recursed in the unchanged correction-only reference before candidate comparison. Replaced only the synthetic leaf-member topology, preserving first helper/log. First full-rule comparison helper lacked the repository root in sys.path and failed before source analysis; corrected the import root and retained the initial helper/log. Initial Ruff/format errors concerned a90-character test parameter line; formatting only tests fixed them. No further product correction, observation, profile or paid call occurred.',
    'scope_limit':'No current-source corpus result, real-target impact, fresh generalization or native speedup is established. Canonical unknown frequency is unmeasured and300-second completion is not promised. Both languages still require separately approved exposed regression after all engineering and freeze.',
    'corpus_observations':0,'profiles':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False}
with (OUT/'source-recovery-assessment.json').open('x') as stream:json.dump(packet,stream,indent=2);stream.write('\n')
print(json.dumps(scanner))
print('Exact source correction/bypass bound to4050correction cases,2430equivalence cases,two evictions and seven full ordered synthetic rule comparisons.')
