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
assert pr['head']['sha'] == '637a25cbb5f5bc6fcf8b3a7b30b4274aa8ea44fb'
assert pr['draft'] and pr['state'] == 'open' and pr['base']['ref'] == 'phase22/description-poisoning'
assert pr['body'] == (OUT.parent / 'v61-faf-long-timeout-sampling/pr-body-delivery.md').read_text()
with (OUT / 'candidate-pre-pr37.json').open('x') as f:
    json.dump({k:pr[k] for k in ('state','draft','title','body','head','base')}, f, indent=2)
body = f'''Candidate `{head}` reuses completed TypeScript MCP tool discovery across the existing rule workers and parent coverage. Ordered warning effects are applied at the original `tools()` consumption point; returned symbols and parsed files/trees travel in the same private IPC graph, and identity indexes are rebuilt. Every rule-specific detector and HTTP analysis still runs. The shared 1800-second deadline is unchanged.

The user approved one source-only attempt. All 272 affected tests, 125 additional complete discovery comparisons, producer AST equivalence, Ruff/format and strict source typing pass. Focused checks include full rule states, warning/cache effects, source aliases across pickle, incomplete/empty discovery, expired deadlines and Python/TypeScript/mixed-workspace serial/parallel output. Worker checks prove one producer while all four detectors execute. Full local and hosted engineering are in progress; no native speedup or FAF completion is established.

No new corpus observation, profile, retry, comparator, target execution or paid call is authorized or has occurred. The earlier 30-minute native timeout and sampled timeout remain closed with no reports. All original four-repository fresh failures, historical outcomes, failed singleton attempts, invalid stale-root preparation and all 335 requirements remain preserved. See the [preceding complete audit](https://github.com/BashaarJavaid/MCP-Sentinel/blob/637a25c/artifacts/phase22/integration/v61-faf-long-timeout-sampling/audit.json) and [current authorization](https://github.com/BashaarJavaid/MCP-Sentinel/blob/{head}/artifacts/phase22/integration/v62-shared-tool-discovery/authorization.json).

Phase 22 remains incomplete. Current-source evaluation requires a separately approved tested-source proposal; explicit human technical acceptance and accepted closeout follow. Git stays 312/1,040 incomplete with 728 deferred; paid benchmark/pilots remain deferred, Phase 21 incomplete and Phase 24/15 unchanged. The PR remains OPEN DRAFT; no merge, ready-state change, release, outreach or Phase 23.
'''
metadata = {'title':'Phase 22: shared discovery reuse; engineering verification in progress','body':body}
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
