"""Run the existing non-corpus engineering commands at the committed candidate."""
import json,subprocess,sys
from pathlib import Path
out=Path(__file__).resolve().parent;root=out.parents[3];base=out.parent
head=json.loads((out/'candidate-commit.json').read_text())['source']
checks=[
 ('lock',['uv','lock','--check','--offline']),
 ('schema',['python','-m','sentinel.schema','check']),
 ('notices',['python','scripts/generate_third_party_notices.py','--check']),
 ('artifacts',['python','-m','scripts.generate_phase5_artifacts','--check']),
 ('candidate-docs',['python','-m','mkdocs','build','--strict']),
 ('build',['uv','build','--offline','--out-dir',str(out/'distributions')]),
 ('runtime-requirements',['uv','export','--locked','--offline','--no-dev','--no-editable','--no-emit-project','--format','requirements-txt','--output-file',str(out/'runtime-requirements.txt')]),
 ('dependency-audit',['pip-audit','--no-deps','--disable-pip','-r',str(out/'runtime-requirements.txt')]),
]
for label,command in checks:
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==head
 assert not subprocess.check_output(['git','diff','HEAD'],cwd=root)
 assert not (base/('v72-'+label+'.json')).exists()
 subprocess.run([sys.executable,'/private/tmp/phase22-check.py','v72-'+label,*command],cwd=root,check=True)
