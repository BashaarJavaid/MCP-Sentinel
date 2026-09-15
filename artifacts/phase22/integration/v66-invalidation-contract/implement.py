"""Consume the approved single attempt and apply only the If accumulator change."""
import ast, hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
a=read(OUT/'authorization.json');assert a['decision']=='approved'
assert read(OUT/'owned-initial.json')['owned_processes']==[]
assert read(OUT/'production-domain-proof.json')['passed']
p=ROOT/'src/sentinel/static/typescript_path_flow.py';baseline=OUT/'baseline/src/sentinel/static/typescript_path_flow.py'
assert sha(p)==sha(baseline)==a['baseline_files_sha256']['src/sentinel/static/typescript_path_flow.py']
uses={}
for path in sorted((ROOT/'src').rglob('*.py')):
 text=path.read_text()
 if 'invalidated_objects' in text:
  tree=ast.parse(text)
  uses[str(path.relative_to(ROOT))]={'sha256':sha(path),'occurrences':[{'line':n.lineno,'source':ast.get_source_segment(text,n)} for n in ast.walk(tree) if isinstance(n,ast.Attribute) and n.attr=='invalidated_objects']}
record={'recorded_at':datetime.now(timezone.utc).isoformat(),'approval_sha256':sha(OUT/'authorization.json'),'proposal_sha256':a['proposal_sha256'],'attempts_consumed':1,'remaining_attempts':0,'bounds':a['bounds'],'source_uses':uses,'production_domain_proof_sha256':sha(OUT/'production-domain-proof.json'),'source_assessment':'Current production writers initialize sets, add/update invalidations and restore/union per-arm baselines. No production removal or raw branch-set export is found in these attribute occurrences. The explicit approved revision classifies only the two retained injected controls outside this production domain; the old failure remains.','paid_calls':0}
with (OUT/'optimization-consumed.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
s=p.read_text();s=s.replace('            invalidated = initial_invalidated.copy()','            invalidated: set[str] | None = None',1)
old='''                invalidated.update(self.invalidated_objects)
            self.invalidated_objects = invalidated'''
new='''                if invalidated is None:
                    invalidated = self.invalidated_objects
                else:
                    invalidated.update(self.invalidated_objects)
            self.invalidated_objects = (
                initial_invalidated.copy() if invalidated is None else invalidated
            )'''
assert s.count(old)==1;s=s.replace(old,new,1);ast.parse(s);p.write_text(s)
(OUT/'candidate-typescript-path-flow.py').write_text(s)
(OUT/'candidate.patch').write_bytes(subprocess.check_output(['git','diff','--','src/sentinel/static/typescript_path_flow.py'],cwd=ROOT))
print('Applied one approved If accumulator attempt; equivalence is not yet established.')

assert sha(p)==read(OUT.parent/'v65-if-invalidation-accumulator/optimization-proposal.json')['failed_candidate_sha256']
