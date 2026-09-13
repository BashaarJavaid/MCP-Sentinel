"""Bind the explained prospective contract revision to the user's continue instruction."""
import datetime,hashlib,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent;OLD=OUT.parent/'v56-canonical-unknown'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proposal=OLD/'optimization-proposal.json'
assert sha(proposal)=='12eea305c03328d6872587a051c090daf6f2d1bb83e1d0a622e3c3a92af92921'
p=json.loads(proposal.read_text())
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert head=='9b2585d3a6cc7e1a3584eff1d9dcbf16a41cffbc'
assert not subprocess.check_output(['git','diff','HEAD'])
binding=json.loads((OLD/'documentation-binding.json').read_text())
for name,digest in binding['user_files_sha256'].items():assert sha(Path(name))==digest,name
for name,destination in [('src/sentinel/static/path_flow.py','baseline-path-flow.py'),('src/sentinel/static/rules/sent016.py','baseline-sent016.py')]:
    source=Path(name);assert sha(source)==p['target_source_sha256'][name]
    with (OUT/destination).open('xb') as stream:stream.write(source.read_bytes())
record={'decision':'continue','interpretation':'After the exact revised-contract/joint-attempt proposal was delivered at9b2585d and explained in response to what is the problem?, the user instructed continue. This authorizes that described joint source-only correction and bypass with its prospective marker-join contract, not corpus/profile/paid execution or Phase22 acceptance.','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'proposal':str(proposal),'proposal_sha256':sha(proposal),'starting_delivery':head,'source_sha256':p['target_source_sha256'],'bounds':p['bounds'],'prospective_contract':p['prospective_contract'],'user_files_sha256':binding['user_files_sha256'],'technical_acceptance_received':False,'phase22_complete':False}
with (OUT/'authorization.json').open('x') as stream:json.dump(record,stream,indent=2);stream.write('\n')
print('One explained joint source-only attempt authorized; both exact source baselines preserved.')
