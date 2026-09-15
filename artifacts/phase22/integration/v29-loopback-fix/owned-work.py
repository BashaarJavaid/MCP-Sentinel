"""Read-only final check for this continuation's processes and owned containers."""
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

rows={}
for line in subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines():
    parts=line.strip().split(None,2)
    if len(parts)==3:
        rows[int(parts[0])]={'parent':int(parts[1]),'command':parts[2]}
ancestors=set();pid=os.getpid()
while pid in rows and pid not in ancestors:
    ancestors.add(pid);pid=rows[pid]['parent']
markers=['phase22-check.py','phase22-v9-capture-production.py','v29-full-suite','v29-loopback-fix/retain-quality.py','v28-lighthouse-regression/retain.py']
owned=[{'pid':pid,**r} for pid,r in rows.items() if pid not in ancestors and any(m in r['command'] for m in markers)]
managed=subprocess.check_output(['docker','ps','-aq','--filter','label=com.securemcp.sentinel=true'],text=True).splitlines()
named=subprocess.check_output(['docker','ps','-aq','--filter','name=sentinel'],text=True).splitlines()
assert not owned and not managed and not named,(owned,managed,named)
p=Path(__file__).with_name('owned-work-final.json');assert not p.exists();p.write_text(json.dumps({'recorded_at':datetime.now(timezone.utc).isoformat(),'owned_processes':owned,'managed_container_ids':managed,'sentinel_named_container_ids':named,'qualification':'Read-only check after local tests, production replay and hosted collectors completed; current process/ancestors excluded. No unrelated work was terminated.'},indent=2)+'\n');print('No remaining owned processes or containers.')
