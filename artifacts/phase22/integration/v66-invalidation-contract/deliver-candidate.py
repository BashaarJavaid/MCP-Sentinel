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
assert pr['head']['sha'] == 'f5f1faa706969d4581cc32eb040fdf28884287c8'
assert pr['draft'] and pr['state'] == 'open' and pr['base']['ref'] == 'phase22/description-poisoning'
assert pr['body'] == (OUT.parent / 'v65-if-invalidation-accumulator/pr-body-delivery.md').read_text()
with (OUT / 'candidate-pre-pr37.json').open('x') as f:
    json.dump({k:pr[k] for k in ('state','draft','title','body','head','base')}, f, indent=2)
body = f'''Candidate `{head}` reuses the first completed TypeScript If arm's private invalidation set after an explicit mutation-domain contract revision. Each arm still starts from its own original-baseline copy; every guard, statement and conservative union executes. The shared 1800-second deadline remains unchanged.

The source proof covers all shipped writers/readers, seven flow classes, control-flow entry points and the HTTP deep-copy path. The candidate passes 256 ordinary synthetic comparisons, 766 complete production-flow comparisons across 263 tests, 157 tests with complete ordered discovery/warning/option comparisons, six complete baseline-versus-candidate Python/TypeScript/mixed serial/parallel results, and five mutation/export guard rejection controls. Ruff, format and whole-scope strict typing pass. Full local and hosted engineering are in progress.

The earlier strict-equivalence attempt remains failed. Only its two exact injected scanner callbacks (clear the private set; export a completed arm alias) are prospectively outside the explicitly approved domain. Their complete original deltas remain retained, with no other failure excluded. Verification-helper callback-copy and import-root errors and corrections are preserved. No native speedup, 1800-second completion or current-source corpus compatibility is established.

All 365 prior requirements and original failed gates remain. No corpus observation, profile, retry, comparator, target execution or paid call occurred. Current-source regression requires a separately approved tested-source proposal. Phase 22 remains incomplete pending actual gates, explicit human technical acceptance and accepted closeout. Git stays 312/1,040 incomplete with 728 deferred; paid benchmark/pilots deferred, Phase 21 incomplete, Phase 24/15 unchanged. This PR remains OPEN DRAFT with its existing base; no merge, ready-state change, release, outreach or Phase 23.
'''
metadata = {'title':'Phase 22: invalidation contract revised; engineering in progress','body':body}
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
