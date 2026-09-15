"""Prepare the next exact scope; this does not authorize any corpus observation."""
import hashlib,json
from pathlib import Path
from scripts.phase20_measurements import scanner_identity
ROOT=Path.cwd();BASE=ROOT/'artifacts/phase22/integration';OUT=BASE/'v29-loopback-fix';OLD=BASE/'v27-constructor-fix'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
scanner=scanner_identity();assert scanner['revision']=='f85a90f9ba2d1c43019e8505b977d57f3476a9c9'
(OUT/'evaluate.py').write_bytes((OLD/'evaluate.py').read_bytes())
p=ROOT/'.github/workflows/ci.yml';s=p.read_text();assert s.count('4a2359d5b67719b1129c7a63eafc17e6d85cedf3')==1;s=s.replace('4a2359d5b67719b1129c7a63eafc17e6d85cedf3',scanner['revision']).replace('v27-constructor-fix/evaluate.py','v29-loopback-fix/evaluate.py');p.write_text(s)
proposal=json.loads((OLD/'evaluation-proposal.json').read_text());proposal['scanner']=scanner
proposal['purpose']='Verify the narrow URL qualification across IPv6 loopback returns after4a2359d detected both vulnerable inputs but failed qualification of the first fixed input. This is a new exposed regression scope; previous stopped budgets and original fresh misses remain unchanged.'
proposal['runner']='artifacts/phase22/integration/v29-loopback-fix/evaluate.py'
proposal['files_sha256'].update({str(p.relative_to(ROOT)):sha(p) for p in [OUT/'evaluate.py',OUT/'correction.json',BASE/'v28-lighthouse-regression/assessment.json',ROOT/'.github/workflows/ci.yml']})
proposal['previous_closed_regression']={'run':34641101185,'scanner':'4a2359d5b67719b1129c7a63eafc17e6d85cedf3','proposal_sha256':sha(OLD/'evaluation-proposal.json'),'assessment_path':'artifacts/phase22/integration/v28-lighthouse-regression/assessment.json','assessment_sha256':sha(BASE/'v28-lighthouse-regression/assessment.json'),'completed':3,'vulnerable_hits':2,'fixed_condition_failures':1,'unstarted_closed':7,'remaining':0}
assert not (OUT/'evaluation-proposal.json').exists();(OUT/'evaluation-proposal.json').write_text(json.dumps(proposal,indent=2)+'\n')
print(scanner,sha(OUT/'evaluation-proposal.json'))
