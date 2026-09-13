"""Bind unchanged approved supervisor logic to the new, unapproved proposal."""
import hashlib,json
from pathlib import Path
out=Path(__file__).resolve().parent;old=out.parent/'v45-four-source-recovery'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((out/'evaluation-proposal.json').read_text())
assert (out/'evaluate.py').read_bytes()==(old/'evaluate.py').read_bytes()
assert (out/'launch.py').read_text()==(old/'launch.py').read_text().replace('v46-four-source-regression','v58-credential-regression')
assert not (out/'evaluation-authorization.json').exists()
previous=json.loads((old/'launcher-binding.json').read_text())
binding={**previous,'proposal_sha256':sha(out/'evaluation-proposal.json'),'launcher_sha256':sha(out/'launch.py'),'runner_sha256':sha(out/'evaluate.py'),'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(out/'launch.py')],'child_cwd':p['frozen_checkout'],'logic_reuse':{'prior_runner_sha256':sha(old/'evaluate.py'),'runner_byte_identical':True,'launcher_change':'Only new output directory v58-credential-regression; all launch/preflight/deadline/cleanup logic equal.','prior_supervisor_check_sha256':sha(out.parent/'v45-supervisor-boundaries.json')},'qualification':'This binds the new proposal to the existing1150-minute outer supervisor. No scope, source, label, ordering or deadline relaxation. Exact new approval is required before output or launch-token creation.'}
with (out/'launcher-binding.json').open('x') as f:json.dump(binding,f,indent=2);f.write('\n')
print('Bound unchanged runner and supervisor; no evaluation authorized or launched.')
