"""Retain public source metadata; no target imports or execution."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

out = Path(__file__).resolve().parent / 'research'
out.mkdir(exist_ok=True)
label, endpoint = sys.argv[1:]
path = out / (label + '.json')
assert not path.exists() and '/' not in label
command = ['gh', 'api', endpoint]
result = subprocess.run(command, capture_output=True, timeout=90)
path.write_bytes(result.stdout)
receipt = {'retrieved_at': datetime.now(timezone.utc).isoformat(), 'command': command, 'exit_code': result.returncode, 'stderr': result.stderr.decode(), 'sha256': hashlib.sha256(result.stdout).hexdigest(), 'target_execution': False}
(out / (label + '-retrieval.json')).write_text(json.dumps(receipt, indent=2) + '\n')
assert result.returncode == 0, receipt
data = json.loads(result.stdout)
if isinstance(data, dict) and 'items' in data:
    print(label, 'total', data['total_count'])
    for item in data['items']:
        print(item.get('repository', {}).get('full_name'), item.get('sha'), item.get('commit', {}).get('message', item.get('title', '')).split('\n')[0])
else:
    print(label, 'retained', len(result.stdout), 'bytes')
