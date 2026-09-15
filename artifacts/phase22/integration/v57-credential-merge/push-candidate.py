"""Deliver the authorized candidate to the existing draft for ordinary CI only."""
import hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=Path.cwd();BASE=OUT.parent
read=lambda p:json.loads(p.read_text())
run=lambda args:subprocess.check_output(args,text=True,stderr=subprocess.STDOUT,timeout=180)
def save(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
head=read(OUT/'candidate-commit.json')['source'];old='9b2585d3a6cc7e1a3584eff1d9dcbf16a41cffbc'
assert run(['git','rev-parse','HEAD']).strip()==head and not run(['git','diff','HEAD'])
p=json.loads(run(['gh','pr','view','37','--json','state,isDraft,headRefName,headRefOid,baseRefName,title,body']))
assert p['state']=='OPEN' and p['isDraft'] and p['headRefOid']==old and p['headRefName']=='phase22/integration' and p['baseRefName']=='phase22/description-poisoning'
assert p['body']==(BASE/'v56-canonical-unknown/pr-body-delivery.md').read_text()
save('candidate-pre-pr37.json',p)
title='Phase 22: credential merge corrected; engineering verification in progress'
body=f'''# Credential merge correction and canonical bypass: engineering in progress

Approved candidate `{head}` makes equal immutable credential markers join consistently regardless of cache interning, then bypasses cache dispatch only for the canonical `UNKNOWN_VALUE` singleton without a key override. This deliberately revises the named marker-join behavior; it is not claimed to preserve every original `a36f696` internal state.

The correction passes 4,050 structural cases with 552 explicitly retained marker deltas and 552 derived cache-input deltas; credential guard results agree. All 480 correction-stage credential/flow regressions pass. The bypass passes 2,430 complete Python/TypeScript state comparisons against the correction-only reference and two saturated-cache eviction cases. Affected tests, Ruff/format and strict mypy passed; full local and hosted engineering are in progress. The initial synthetic fixture recursion failure and test-format failures remain retained with their corrections.

Both older singleton failures reproduce against their original sources. All three native timeouts, partial/invalid profiles, original four fresh failures, prior TS/Python and whole-batch evidence, six historical closure proposals and original held-out limitations remain unchanged. No new corpus observation, profile or paid call is authorized or executed. No speedup or 300-second completion is established.

Phase 22 remains incomplete. Exact regression approval, actual results, explicit human technical acceptance and accepted closeout remain pending. Git stays312/1,040 incomplete; pilots/paid benchmark deferred, Phase21 incomplete and Phase24/15 unchanged. PR remains OPEN DRAFT; no merge, ready-state, release, outreach or Phase23. Main worktree and all eight protected user documents are preserved.

The complete preceding evidence and limitations remain in [v56](https://github.com/BashaarJavaid/MCP-Sentinel/blob/{old}/artifacts/phase22/integration/v56-canonical-unknown/summary.md). Final engineering evidence and the complete updated audit will follow after verification.
'''
with (OUT/'candidate-pr-body.md').open('x') as stream:stream.write(body)
save('candidate-metadata-update.json',{'title':title,'body':body})
print(run(['git','push','https://github.com/BashaarJavaid/MCP-Sentinel.git','HEAD:refs/heads/phase22/integration']),flush=True)
print(run(['gh','api','--method','PATCH','repos/BashaarJavaid/MCP-Sentinel/pulls/37','--input',str(OUT/'candidate-metadata-update.json'),'--jq','{number,state,draft,title,head:.head.sha}']),flush=True)
for _ in range(12):
    p=json.loads(run(['gh','pr','view','37','--json','state,isDraft,headRefOid,baseRefName,title,body']))
    if p['headRefOid']==head and p['title']==title and p['body']==body:break
    time.sleep(5)
else:raise AssertionError('Candidate pushed; readback stale. Recheck read-only before any new mutation.')
assert p['state']=='OPEN' and p['isDraft'] and p['baseRefName']=='phase22/description-poisoning'
save('candidate-delivery.json',{'passed':True,'head':head,'recorded_at':datetime.now(timezone.utc).isoformat(),'pr':p,'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'engineering':'in progress','corpus_observations':0,'profiles':0,'paid_calls':0,'phase22_complete':False})
print('Candidate exact draft readback verified; normal PR engineering workflows may run.')
