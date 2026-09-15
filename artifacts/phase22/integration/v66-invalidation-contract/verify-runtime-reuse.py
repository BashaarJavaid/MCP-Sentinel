"""Bind retained runtime and six current zero-call production requests."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((BASE/'v5-git-runtime-reuse/packet.json').read_text())
for n,d in old['unchanged_runtime_component_files'].items():assert sha(ROOT/n)==d,n
image=subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',old['approved_image']],text=True).strip();assert image==old['approved_image']
replay=json.loads((BASE/'v66-production-capture-revalidation/packet.json').read_text());prior=json.loads((BASE/'v19-final-production-capture-revalidation/packet.json').read_text())
assert replay['source']=='4145d3559c5300a5003ca8e3368c8da49fb51f91' and replay['model_calls']==0
assert len(replay['requests'])==6 and all(x['accepted'] for x in replay['requests'])
assert [(x['fingerprint'],x['request_sha256']) for x in replay['requests']]==[(x['fingerprint'],x['request_sha256']) for x in prior['requests']]
protected=json.loads((BASE/'shared-discovery-intake-20260914/intake.json').read_text())['user_files_sha256']
for n,d in protected.items():assert sha(ROOT/n)==d,n
assert not subprocess.check_output(['git','diff','HEAD','--','src','tests','scripts','schemas','uv.lock','pyproject.toml','action.yml','.github','Makefile'])
assert len(protected)==9
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==replay['source']
p={'scanner':'4145d3559c5300a5003ca8e3368c8da49fb51f91','production_source':replay['source'],'runtime_component_files_sha256':old['unchanged_runtime_component_files'],'runtime_reference_sha256':sha(BASE/'v5-git-runtime-reuse/packet.json'),'approved_image':image,'production_replay_sha256':sha(BASE/'v66-production-capture-revalidation/packet.json'),'six_exact_fingerprints_and_full_requests_unchanged':True,'user_files_sha256':protected,'git_limits':'13 campaigns,312/1040 tested and728 remaining; all incomplete. User deferred completing this coverage. No new Git campaign or target execution.','corpus_observations':0,'paid_calls':0,'owned_demo':'Ordinary production request construction uses the authorized Sentinel-controlled Docker fixture; all model calls forbidden and existing cassettes replayed. This is separate from corpus target execution.','phase22_complete':False}
path=OUT/'compatibility.json';assert not path.exists();path.write_text(json.dumps(p,indent=2)+'\n');print('Verified19 runtime component hashes, approved image and6 identical production requests; zero paid calls.')
