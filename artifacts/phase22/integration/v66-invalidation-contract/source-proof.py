"""Bind the exact reapplication and all otherwise unchanged engineering inputs."""
import ast,hashlib,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
head=read(OUT/'candidate-commit.json')['source'];assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
assert not subprocess.check_output(['git','diff','HEAD'])
a=read(OUT/'authorization.json');old=read(OUT.parent/'v62-shared-tool-discovery/local-checks.json')['candidate_engineering_files_sha256']
current={name:sha(ROOT/name) for name in old};current['tests/test_typescript_invalidation_contract.py']=sha(ROOT/'tests/test_typescript_invalidation_contract.py')
changed={n for n in current if current[n]!=old.get(n)}
assert changed=={'CHANGELOG.md','src/sentinel/static/typescript_path_flow.py','tests/test_typescript_invalidation_contract.py'},changed
assert current['src/sentinel/static/typescript_path_flow.py']==read(OUT.parent/'v65-if-invalidation-accumulator/optimization-proposal.json')['failed_candidate_sha256']
for n,d in a['baseline_files_sha256'].items():assert sha(OUT/'baseline'/n)==d
for n,d in a['user_files_sha256'].items():assert sha(ROOT/n)==d
p=ROOT/'src/sentinel/static/typescript_path_flow.py';s=p.read_text()
s=s.replace('            invalidated: set[str] | None = None','            invalidated = initial_invalidated.copy()',1).replace('''                if invalidated is None:
                    invalidated = self.invalidated_objects
                else:
                    invalidated.update(self.invalidated_objects)
            self.invalidated_objects = (
                initial_invalidated.copy() if invalidated is None else invalidated
            )''','''                invalidated.update(self.invalidated_objects)
            self.invalidated_objects = invalidated''',1)
assert s.encode()==(OUT/'baseline/src/sentinel/static/typescript_path_flow.py').read_bytes()
packet={'passed':True,'candidate':head,'baseline_scanner':a['scanner'],'authorization_sha256':sha(OUT/'authorization.json'),'changed_engineering_files':sorted(changed),'candidate_engineering_files_sha256':current,'exact_prior_candidate_reapplied':True,'inverse_patch_restores_complete_baseline':True,'production_domain_proof_sha256':sha(OUT/'production-domain-proof.json'),'original_strict_failure_retained':True,'prospective_contract_revision':a['prospective_contract_revision'],'static_timeout_seconds':1800,'speedup_established':False,'current_source_corpus_compatibility_established':False,'corpus_observations':0,'profiles':0,'paid_calls':0,'technical_acceptance_received':False}
(OUT/'source-proof.json').write_text(json.dumps(packet,indent=2)+'\n')
print('Exact prior candidate reapplied; inverse patch restores baseline. 303 engineering inputs bound.')
