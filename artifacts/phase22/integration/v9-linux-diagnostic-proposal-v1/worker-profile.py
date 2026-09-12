import collections,cProfile,json,marshal,pstats,sys,threading,time
from pathlib import Path
sys.path.insert(0,ROOT_SOURCE)
from sentinel.static import workers,path_flow
out=Path(OUTPUT);rule=sys.argv[-1];counts=collections.Counter();original=path_flow.combine
prof=cProfile.Profile()
def counted(values,key=''):
 counts[(len(values),bool(key))]+=1
 return original(values,key)
path_flow.combine=counted
stop=threading.Event()
def snapshot():
 prof.snapshot_stats()
 with (out/(rule+'.prof')).open('wb') as stream:marshal.dump(prof.stats,stream)
 (out/(rule+'-timing-partial.json')).write_text(json.dumps({'wall':time.monotonic()-start,'cpu':time.process_time()-cpu,'partial':True}))
 (out/(rule+'-counts.json')).write_text(json.dumps({str(k):v for k,v in counts.copy().items()},indent=2))
def snapshots():
 while not stop.wait(20):snapshot()
start=time.monotonic();cpu=time.process_time();thread=threading.Thread(target=snapshots,daemon=True);thread.start();prof.enable()
try:workers._worker()
finally:
 prof.disable();stop.set();thread.join();snapshot()
 (out/(rule+'-timing.json')).write_text(json.dumps({'wall':time.monotonic()-start,'cpu':time.process_time()-cpu}))
