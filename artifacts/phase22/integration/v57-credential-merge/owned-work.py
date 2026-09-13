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
markers=['v58-', 'v57-', 'v56-', 'v55-', 'v54-', 'v52-', 'v53-', 'v51-', 'v50-', 'v49-', 'v48-', 'v47-', 'v45-', 'v46-', 'v43-', 'v44-', 'mcp-phase22-four-fresh-', 'v42-', 'v41-', 'v41-path-guard-recovery/', 'v40-fresh-v7/', 'v39-fresh-v7/', 'v38-guard-regression/', 'v37-ddg-trace/', 'v36-guard-recovery/','v35-ddg-regression/','phase22-check.py','v34-fixed-coverage-proposal/','v34-fixed-coverage-final/','v34-import-binding/','v32-fresh-v6/runner.py']
owned=[{'pid':pid,**r} for pid,r in rows.items() if pid not in ancestors and any(m in r['command'] for m in markers)]
managed=subprocess.check_output(['docker','ps','-aq','--filter','label=com.securemcp.sentinel=true'],text=True).splitlines()
named=subprocess.check_output(['docker','ps','-aq','--filter','name=sentinel'],text=True).splitlines()
assert not owned and not managed and not named,(owned,managed,named)
p=Path(__file__).with_name('owned-work.json');assert not p.exists();p.write_text(json.dumps({'recorded_at':datetime.now(timezone.utc).isoformat(),'owned_processes':owned,'managed_container_ids':managed,'sentinel_named_container_ids':named,'qualification':'Read-only check after the approved joint correction and canonical bypass completed engineering. Its one-use source-only budget is closed; no corpus, profile, retry or paid call. All prior native budgets remain closed. Current process/ancestors excluded. No unrelated work was terminated.'},indent=2)+'\n');print('No remaining owned processes or containers.')
