"""Validate frozen corpus bytes and stage old source-freeze receipts; never scan."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path('/private/tmp/mcp-phase22-options');OUT=Path(__file__).resolve().parent
p=json.loads((OUT/'evaluation-proposal.json').read_text());fixed=Path(p['frozen_checkout'])
sys.path[:0]=[str(fixed),str(fixed/'src')]
from scripts.phase20_corpus import validate
from scripts.phase22_corpus import frozen
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows={};staged={}
for group,g in p['groups'].items():
 assert sha(fixed/g['manifest'])==g['manifest_sha256']
 if g['source_freeze_approval']:
  src=ROOT/g['source_freeze_approval'];dest=fixed/g['source_freeze_approval']
  assert sha(src)==p['files_sha256'][g['source_freeze_approval']]
  if dest.exists():assert not dest.is_symlink() and sha(dest)==sha(src)
  else:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);staged[g['source_freeze_approval']]=sha(dest)
 m=validate(path=fixed/g['manifest'],root=fixed) if group.endswith('historical') else frozen(root=fixed,approval_path=fixed/g['source_freeze_approval'])
 selected=[i for i in m.inputs if i.id in g['input_ids']]
 assert [i.id for i in selected]==g['input_ids']
 for i in selected:
  x=g['inputs'][i.id];assert i.model_dump(mode='json')==x['input'];assert sha(ROOT/x['configuration'])==x['configuration_sha256']
 rows[group]={'selected':len(selected),'whole_manifest_validated':len(m.inputs),'source_freeze_receipt':g['source_freeze_approval']}
assert not subprocess.check_output(['git','diff','HEAD'],cwd=fixed)
assert not subprocess.check_output(['git','status','--porcelain'],cwd=fixed)
record={'scanner':p['scanner'],'groups':rows,'source_receipts_staged':staged,'tracked_and_untracked_clean':True,'ignored_source_receipts_hash_bound':True,'new_corpus_observations':0,'paid_calls':0,'configuration_basis':'Frozen manifests and complete source archives validated; same configuration implementation and exact retained effective configuration hashes. Source-freeze receipts are provenance; only a new exact evaluation receipt may authorize these205 observations.'}
with (OUT/'frozen-source-validation.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print('All110 selected input records and their whole manifests validate; zero observations.')
