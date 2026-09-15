"""Bind the single approved predicate change, synthetic evidence and prior failures."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path
out=Path(__file__).resolve().parent
root=Path.cwd()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=(out/'baseline-typescript-path-flow.py').read_text()
current=(root/'src/sentinel/static/typescript_path_flow.py').read_text()
before='if name.startswith("#record:") and root in self.objects'
after='if name.startswith("#record:")\n                and root in self.objects\n                and any(name not in branch for branch in branches)'
assert old.count(before)==1 and current==old.replace(before,after)
assert ast.dump(ast.parse(current.replace(after,before)))==ast.dump(ast.parse(old))
validation=json.loads((out/'synthetic-validation.json').read_text())
assert validation['passed'] and validation['semantic_cases']==10944
assert validation['candidate_source_sha256']==sha(root/'src/sentinel/static/typescript_path_flow.py')
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert source=='6e4fd671a97d92f6297dffc900c4dd9e18faad2c'
packet={'scanner':source,'attempts':1,'authorization_sha256':sha(out/'authorization.json'),'baseline_source_sha256':sha(out/'baseline-typescript-path-flow.py'),'candidate_source_sha256':sha(root/'src/sentinel/static/typescript_path_flow.py'),'entire_file_change_exactly_approved_predicate':True,'synthetic_validation_sha256':sha(out/'synthetic-validation.json'),'proof':'If every branch has the name, every get returns that branch value; its default is unobserved. Otherwise the exact previous Value(key=root) is still constructed for known records. Other names keep UNKNOWN_VALUE. Empty branches/name unions, branch order, equality/identity reuse, guards and combined metadata code are unchanged. Dictionary membership reads scanner-owned plain dictionaries and mutates no state.','synthetic_scope':'10,944 baseline/candidate cases compare environment and every flow attribute, including RuleRunState and untouched inputs. Cases vary empty/one/two/three/eight branches, missing positions, equal/unequal values, registered/unregistered record roots, guard names, source-free and sourced protection, record/array/path/URL metadata. Separate accounting preserves needed fallback allocations and avoids four all-present allocations.','allocation_limits':'The membership predicate itself has cost. Synthetic allocation counts and the earlier incomplete sampled snapshots do not establish a native speedup or completion within 300 seconds. No analysis shortcut, deadline, resource, cache, rule or target change.','historical_bindings':{'v44':'24 first-frozen complete, four failed fresh gates at2e0efb2','v46':'1 incomplete native attempt,204 unstarted closed at17b4784','v47':'1 incomplete sampled attempt at17b4784,four partial snapshots,budget closed'},'next_gate':'Full engineering, frozen candidate, then separately approved current-source native regression and source assessment. Python87 remains needed because the previous shared Python correction at17b4784 has not received corpus validation.','corpus_observations':0,'profiles':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False}
with (out/'source-recovery-assessment.json').open('x') as stream:json.dump(packet,stream,indent=2);stream.write('\n')
print('Verified exact one-predicate source change and10,944 equal synthetic cases; no native performance claim.')
