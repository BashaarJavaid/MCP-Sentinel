"""Deliver the authorized candidate to the same draft for ordinary engineering."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
run = lambda *args: subprocess.check_output(args, cwd=ROOT, text=True)
head = json.loads((OUT / 'candidate-commit.json').read_text())['source']
assert run('git', 'rev-parse', 'HEAD').strip() == head
assert not run('git', 'diff', 'HEAD')
pr = json.loads(run('gh', 'api', 'repos/BashaarJavaid/MCP-Sentinel/pulls/37'))
assert pr['head']['sha'] == '42d6c7c007b43f8e96ca0056817e9e7673033159'
assert pr['draft'] and pr['state'] == 'open' and pr['base']['ref'] == 'phase22/description-poisoning'
assert pr['body'] == (OUT.parent / 'v71-four-source-correctness/candidate-pr-body.md').read_text()
with (OUT / 'candidate-pre-pr37.json').open('x') as f:
    json.dump({k:pr[k] for k in ('state','draft','title','body','head','base')}, f, indent=2)
body = f'''Candidate `{head}` retains the ordinary TypeScript constructor parameter-property and Python derived URL guard corrections, with one additional conservative boundary: `__proto__` parameter properties are rejected consistently with existing prototype-mutation handling. The first candidate 42d6c7c failed this independent synthetic control; its local suite was interrupted after 1,408 passes/36 skips and CI 34845266890 was cancelled. Those are preserved partial results, not complete engineering passes.

All 224 focused class, URL, discovery and worker checks now pass, including the prototype rejection control, exact parameter defaults/receivers, cold/warm nonempty discovery, pickle source identity and ordered serial/parallel state. Ruff, format and whole-scope strict mypy pass. New full local and hosted engineering and zero-call production revalidation are in progress at this exact corrected candidate. No current-source corpus result or speedup is established.

The completed uncapped 24-observation experiment at 4145d35 remains immutable:12 entire ordered pairs agree, cleanup passes, and its budget is closed. FAF took 2,212.22–2,341.48 seconds per input and failed named detection/support; Lightning failed fixed/safe qualification. No-bash and Engram passed only their narrow exposed conditions. Earlier original fresh failures remain unchanged. The normal 1,800-second shared deadline remains in place.

All 399 existing requirements remain; the correction and failed-boundary evidence will be reconciled in the final packet. The next proposal will preserve four-repository-first scope with 24 observations under a separately approved experiment-only uncapped policy; 181 prior-language observations remain outside it. No new corpus input, profile, retry, comparator, target execution or paid call occurred. The pending V68 performance optimization remains unapproved/unimplemented.

Phase 22 remains incomplete pending actual current-source gates, explicit human technical acceptance and accepted closeout. Git stays 312/1,040 incomplete with 728 deferred; paid benchmark/pilots deferred, Phase 21 incomplete, Phase 24/15 unchanged. This PR stays OPEN DRAFT with its existing base; no merge, ready-state change, release, outreach or Phase 23.
'''
metadata = {'title':'Phase 22: prototype boundary corrected; full engineering in progress','body':body}
with (OUT / 'candidate-metadata-update.json').open('x') as f:
    json.dump(metadata, f, indent=2)
with (OUT / 'candidate-pr-body.md').open('x') as f:
    f.write(body)
print(run('git','push','https://github.com/BashaarJavaid/MCP-Sentinel.git','HEAD:refs/heads/phase22/integration'))
response = json.loads(run('gh','api','--method','PATCH','repos/BashaarJavaid/MCP-Sentinel/pulls/37','--input',str(OUT/'candidate-metadata-update.json')))
with (OUT / 'candidate-patch-response.json').open('x') as f:
    json.dump({k:response[k] for k in ('state','draft','title','body','head','base')},f,indent=2)
pr = json.loads(run('gh','api','repos/BashaarJavaid/MCP-Sentinel/pulls/37'))
remote = json.loads(run('gh','api','repos/BashaarJavaid/MCP-Sentinel/git/ref/heads/phase22/integration'))
verified = pr['head']['sha'] == remote['object']['sha'] == head and pr['title'] == metadata['title'] and pr['body'] == body and pr['draft'] and pr['state'] == 'open' and pr['base']['ref'] == 'phase22/description-poisoning'
with (OUT / 'candidate-delivery.json').open('x') as f:
    json.dump({'passed':verified,'head':head,'recorded_at':datetime.now(timezone.utc).isoformat(),'pr':{k:pr[k] for k in ('state','draft','title','body')},'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'paid_calls':0,'engineering':'pending'},f,indent=2)
assert verified, 'Readback stale: resolve by reads, never repeat this writer.'
print('Candidate draft delivery verified.')
