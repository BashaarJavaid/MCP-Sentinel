"""Bind the hosted synthetic merge tree to the exact tested candidate."""
import json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent;head='dc7371513a065457af566f4b589b9ed147130d64'
def api(path):return json.loads(subprocess.check_output(['gh','api','repos/BashaarJavaid/MCP-Sentinel/'+path],text=True))
p=api('pulls/37');assert p['head']['sha']==head and p['draft'] and p['state']=='open' and p['base']['ref']=='phase22/description-poisoning'
merge=p['merge_commit_sha'];commit=api('git/commits/'+merge);candidate=api('git/commits/'+head)
assert commit['tree']['sha']==candidate['tree']['sha'];assert head in [x['sha'] for x in commit['parents']]
with (OUT/'checkout-binding.json').open('x') as f:json.dump({'head':head,'synthetic_merge':merge,'tree':commit['tree']['sha'],'parents':[x['sha'] for x in commit['parents']],'complete_tree_equal_to_head':True,'pr_base':p['base']['ref'],'draft':True},f,indent=2);f.write('\n')
print('Hosted merge',merge,'has complete tree equal to',head)
