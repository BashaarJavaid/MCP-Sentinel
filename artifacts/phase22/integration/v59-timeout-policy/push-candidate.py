"""Deliver the authorized candidate to the existing draft for ordinary CI only."""
import hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=Path.cwd();BASE=OUT.parent
read=lambda p:json.loads(p.read_text())
run=lambda args:subprocess.check_output(args,text=True,stderr=subprocess.STDOUT,timeout=180)
def save(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
head=read(OUT/'candidate-commit.json')['source'];old='b168738236d9f0b637fa8764f1ad0f3bbcae50d8'
assert run(['git','rev-parse','HEAD']).strip()==head and not run(['git','diff','HEAD'])
p=json.loads(run(['gh','pr','view','37','--json','state,isDraft,headRefName,headRefOid,baseRefName,title,body']))
assert p['state']=='OPEN' and p['isDraft'] and p['headRefOid']==old and p['headRefName']=='phase22/integration' and p['baseRefName']=='phase22/description-poisoning'
assert p['body']==(BASE/'v58-credential-regression/pr-body-delivery.md').read_text()
save('candidate-pre-pr37.json',p)
title='Phase 22: longer static deadline; engineering verification in progress'
body=f'''# Thirty-minute static deadline: engineering in progress

Candidate `{head}` changes the shared deterministic static deadline from 300 to 1,800 seconds. The user accepted a longer supported limit to prioritize completed, correct results. The 120-second target is informational; shorter caller deadlines and incomplete-on-expiry behavior remain enforced. Workers, rule selection, detector logic, schemas and cleanup are unchanged. This revises the timing policy; it does not claim a speedup or relabel any earlier failure.

Source proof shows exactly one changed product AST literal. Focused static/worker/deadline regressions and whole-scope Ruff/format/strict mypy pass. Existing tests now cover completion beyond 300 seconds, the new maximum, shorter caller deadlines and late report assembly. Full local and hosted verification are in progress. No new corpus observation, profile or paid call has run.

All four native timeouts, three partial profiles, invalid stale-root preparation, both singleton failures, original four fresh failures, prior Python/TypeScript and whole Linux evidence, and unaccepted historical closure proposals remain preserved. The unexecuted v58 sampled diagnostic is superseded as the next step by this user-directed policy revision; it has not been approved or executed.

Phase 22 remains incomplete. The exact new frozen-source regression, its results, explicit human technical acceptance and accepted closeout remain separate. Git stays 312/1,040 incomplete; paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged. PR stays OPEN DRAFT; no merge, ready-state change, release, outreach or Phase 23. Main and all eight protected user documents remain preserved.

The preceding complete audit and failure evidence remain in [v58](https://github.com/BashaarJavaid/MCP-Sentinel/blob/{old}/artifacts/phase22/integration/v58-credential-regression/summary.md). The final engineering packet and exact evaluation proposal will follow verification.
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
