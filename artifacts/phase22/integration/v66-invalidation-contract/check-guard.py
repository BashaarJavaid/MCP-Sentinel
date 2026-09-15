"""Reject private-set removals/exports, including local aliases and reflection."""
import importlib.util,json,shutil,tempfile
from pathlib import Path
import sentinel
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
spec=importlib.util.spec_from_file_location('guard',ROOT/'tests/test_typescript_invalidation_contract.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.test_private_invalidation_mutations_do_not_remove_or_export()
mutations=['self.invalidated_objects.clear()','self.escaped = self.invalidated_objects','invalidated.clear()','self.escaped = invalidated','getattr(self, "invalidated_objects").clear()']
old=sentinel.__file__;results=[]
with tempfile.TemporaryDirectory(prefix='v66-contract-guard-') as d:
 root=Path(d)/'sentinel';shutil.copytree(ROOT/'src/sentinel',root,ignore=shutil.ignore_patterns('__pycache__'))
 sentinel.__file__=str(root/'__init__.py');path=root/'static/typescript_path_flow.py';source=path.read_text()
 try:
  for mutation in mutations:
   path.write_text(source.replace('                    invalidated = self.invalidated_objects','                    invalidated = self.invalidated_objects\n                    '+mutation,1))
   try:m.test_private_invalidation_mutations_do_not_remove_or_export()
   except AssertionError:results.append({'mutation':mutation,'rejected':True})
   else:raise AssertionError(('guard missed mutation',mutation))
 finally:sentinel.__file__=old
(OUT/'guard-validation.json').write_text(json.dumps({'passed':True,'controls':results,'candidate_passes':True,'corpus_observations':0,'paid_calls':0},indent=2)+'\n')
print('Candidate accepted; all five removal/export/reflection mutations rejected.')
