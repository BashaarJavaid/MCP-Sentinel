import hashlib,json,os,platform,resource,sys,time
from pathlib import Path
root=Path.cwd();sys.path[:0]=[str(root/'src'),str(root)]
from scripts.phase20_measurements import measure,scanner_identity
from scripts.phase22_corpus import frozen
from sentinel.static import workers
from sentinel.llm.semantic_reviewer import OpenAITransport
async def forbidden(*args,**kwargs):raise AssertionError('Model calls forbidden')
OpenAITransport.create=forbidden
for key in list(os.environ):
 if key.startswith(('OPENAI_','SENTINEL_')):os.environ.pop(key)
proposal_root=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=False)
proposal=json.loads((proposal_root/'packet.json').read_text())
approval=json.loads((proposal_root/'authorization.json').read_text())
assert approval['approved'] is True and approval['proposal_sha256']==hashlib.sha256((proposal_root/'packet.json').read_bytes()).hexdigest()
for name,expected in proposal['files_sha256'].items():assert hashlib.sha256((proposal_root/name).read_bytes()).hexdigest()==expected,name
identity=scanner_identity();assert identity==proposal['scanner']
assert hashlib.sha256((root/'uv.lock').read_bytes()).hexdigest()==proposal['lock_sha256']
manifest=frozen();ids=proposal['input_ids'];selected=[i for i in manifest.inputs if i.id in ids];assert len(selected)==2
original_worker=workers.WORKER
packet={'scanner':identity,'approval':approval,'python':sys.version,'platform':platform.platform(),'cpu_count':os.cpu_count(),'loadavg_before':os.getloadavg(),'meminfo':Path('/proc/meminfo').read_text(),'workflow_run':os.environ['GITHUB_RUN_ID'],'model_calls':0,'target_execution':False,'runs':[],'limits':'Four native runs and two instrumented diagnostic runs on the same immutable scanner. Profiles do not substitute for native timing gates. No full batch or retry.'}
(out/'environment.json').write_text(json.dumps(packet,indent=2)+'\n')
for mode in ['native','profile']:
 for item in selected:
  for ordinal in range(2 if mode=='native' else 1):
   label=f'{mode}-{item.id}-{ordinal+1}'
   if mode=='profile':
    profile_dir=out/(label+'-workers');profile_dir.mkdir()
    shim=profile_dir/'worker-profile.py'
    shim.write_text((proposal_root/'worker-profile.py').read_text().replace('ROOT_SOURCE',repr(str(root/'src'))).replace('OUTPUT',repr(str(profile_dir))))
    workers.WORKER=shim
   else:workers.WORKER=original_worker
   before=time.monotonic();resource_before=tuple(resource.getrusage(resource.RUSAGE_CHILDREN))
   print('START',label,flush=True)
   result=measure(manifest.model_copy(update={'inputs':[item]}),'rules',out/label)
   row={'label':label,'mode':mode,'wall_seconds':time.monotonic()-before,'child_resource_before':resource_before,'child_resource_after':tuple(resource.getrusage(resource.RUSAGE_CHILDREN)),'outcomes':result['outcomes']}
   packet['runs'].append(row);(out/'packet.json').write_text(json.dumps(packet,indent=2)+'\n');print(json.dumps(row),flush=True)
workers.WORKER=original_worker
assert scanner_identity()==identity and len(packet['runs'])==6
packet['loadavg_after']=os.getloadavg();(out/'packet.json').write_text(json.dumps(packet,indent=2)+'\n')
