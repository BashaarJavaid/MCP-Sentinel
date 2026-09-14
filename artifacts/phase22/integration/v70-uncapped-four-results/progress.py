"""Read-only progress/process inventory; no scanner instrumentation or extra input."""
import json,subprocess
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent
p=json.loads((out/'raw/packet.json').read_text());launch=json.loads((out/'launch.json').read_text())
rows={}
for line in subprocess.check_output(['ps','-axo','pid=,ppid=,etime=,time=,%cpu=,rss=,command='],text=True).splitlines():
 f=line.strip().split(None,6)
 if len(f)==7:rows[int(f[0])]={'ppid':int(f[1]),'elapsed':f[2],'cpu_time':f[3],'cpu_percent':float(f[4]),'rss_kib':int(f[5]),'command':f[6]}
owned={launch['pid']}
while True:
 added={pid for pid,r in rows.items() if r['ppid'] in owned}-owned
 if not added:break
 owned|=added
record={'recorded_at':datetime.now(timezone.utc).isoformat(),'completed':sum(r['state']=='completed' for r in p['attempts']),'attempted':len(p['attempts']),'closed':p.get('budget_closed',False),'active_input':next((r['input_id'] for r in reversed(p['attempts']) if r['state']=='attempted'),None),'processes':[{'pid':pid,**rows[pid]} for pid in sorted(owned) if pid in rows],'qualification':'Passive owned-process progress inventory only. CPU totals/RSS are not stack profiling, native speedup or stage attribution.'}
with (out/'progress.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
print(json.dumps(record))
