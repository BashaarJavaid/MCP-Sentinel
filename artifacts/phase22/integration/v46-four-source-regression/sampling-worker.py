"""100Hz CPU-time stack samples in scanner-owned workers; no method replacement."""
import collections,json,signal,sys,threading,time
from pathlib import Path
root=Path('/private/tmp/mcp-phase22-frozen-17b4784');sys.path[:0]=[str(root/'src'),str(root)]
from sentinel.static import workers
out=Path(__file__).resolve().parent;rule=sys.argv[-1];frames={};stacks=collections.Counter();events=collections.Counter();busy=False;stop=threading.Event();started_cpu=None;ended_cpu=None;restored=False
INTERVAL=0.01;MAX_FRAMES=1024

def sample(signum,frame):
 global busy
 if busy:events['reentrant_skipped']+=1;return
 busy=True
 try:
  events['signals']+=1;ids=[]
  while frame is not None and len(ids)<MAX_FRAMES:
   code=frame.f_code;key=(code.co_filename,code.co_name,code.co_firstlineno,frame.f_lineno)
   index=frames.get(key)
   if index is None:index=len(frames);frames[key]=index
   ids.append(index);frame=frame.f_back
  if frame is not None:events['truncated_stacks']+=1
  if ids:stacks[tuple(ids)]+=1
  else:events['empty_frames']+=1
 finally:busy=False

def snapshot(final=False):
 # Copy stacks first: subsequent catalog entries can be extra, never missing.
 saved_stacks=dict(stacks);catalog=dict(frames);saved_events=dict(events)
 data={'rule':rule,'timer':'ITIMER_PROF','requested_interval_seconds':INTERVAL,'requested_hz':1/INTERVAL,'samples':sum(saved_stacks.values()),'events':saved_events,'frame_catalog':[{'id':index,'filename':key[0],'function':key[1],'first_line':key[2],'line':key[3]} for key,index in sorted(catalog.items(),key=lambda item:item[1])],'stacks':[{'frames':list(key),'count':count} for key,count in saved_stacks.items()],'stack_order':'leaf_to_root','maximum_recorded_stack_frames':MAX_FRAMES,'worker_cpu_seconds':time.process_time(),'sampling_started_cpu_seconds':started_cpu,'sampling_ended_cpu_seconds':ended_cpu,'signal_and_timer_state_restored':restored,'final_worker_snapshot':final,'scanner_methods_modified':False,'source_values_or_locals_recorded':False,'limitations':'Statistical CPU-timer samples are delivered to Python main-thread frames. Native-code and GIL/signal-delivery delays can bias attribution; snapshot-thread CPU can be charged to the interrupted main frame. Recursive/caller stacks overlap. Snapshot CPU and sampler CPU are included; no sampled share is an exact or wholly removable cost.'}
 path=out/(rule+'-cpu-samples.json');tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(path)

def snapshots():
 while not stop.wait(15):snapshot()

def start():
 global started_cpu
 assert threading.current_thread() is threading.main_thread()
 previous=(signal.getsignal(signal.SIGPROF),signal.getitimer(signal.ITIMER_PROF))
 assert previous[1]==(0.0,0.0),'Pre-existing CPU timer: stop before source execution'
 assert signal.SIGPROF not in signal.pthread_sigmask(signal.SIG_BLOCK,[]),'CPU sample signal is blocked'
 signal.signal(signal.SIGPROF,sample);started_cpu=time.process_time();signal.setitimer(signal.ITIMER_PROF,INTERVAL,INTERVAL)
 return previous

def finish(previous):
 global ended_cpu,restored
 # Snapshot thread is joined first by the caller; only the main worker remains.
 mask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGPROF})
 signal.setitimer(signal.ITIMER_PROF,0)
 while signal.SIGPROF in signal.sigpending():signal.sigwait({signal.SIGPROF})
 ended_cpu=time.process_time();signal.signal(signal.SIGPROF,previous[0]);signal.setitimer(signal.ITIMER_PROF,*previous[1]);signal.pthread_sigmask(signal.SIG_SETMASK,mask)
 restored=signal.getsignal(signal.SIGPROF)==previous[0] and signal.getitimer(signal.ITIMER_PROF)==previous[1]
 assert restored

if __name__=='__main__':
 previous=start();thread=threading.Thread(target=snapshots,daemon=True);thread.start()
 try:workers._worker()
 finally:stop.set();thread.join();finish(previous);snapshot(True)
