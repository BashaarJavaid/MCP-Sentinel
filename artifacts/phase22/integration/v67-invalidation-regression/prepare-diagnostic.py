"""Bind the existing sampler to one unapproved current-source diagnostic."""
import ast,copy,hashlib,json
from pathlib import Path
out=Path(__file__).resolve().parent;base=out.parent;root=out.parents[3];assets=base/'v66-invalidation-contract';old=base/'v63-shared-discovery-regression'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=read(assets/'evaluation-proposal.json');a=read(out/'assessment.json')
assert a['budget']=={'planned':205,'attempted':1,'completed':0,'incomplete':1,'unstarted_closed':204,'remaining':0,'closed':True}
assert read(out/'parent-sampler-selfcheck/packet.json')['passed'] and read(out/'sampler-selfcheck/packet.json')['wrong_root_rejected_before_execution']
functions=['sample','snapshot','snapshots','start','finish']
for n in functions:
 trees=[ast.parse((directory/'corrected-sampling-worker.py').read_text()) for directory in [old,out]]
 nodes=[next(x for x in t.body if isinstance(x,ast.FunctionDef) and x.name==n) for t in trees]
 assert ast.dump(nodes[0],include_attributes=False)==ast.dump(nodes[1],include_attributes=False)
proposal=copy.deepcopy(read(old/'diagnostic-proposal.json'))
proposal.update(scanner=p['scanner'],lock_sha256=p['lock_sha256'],frozen_checkout=p['frozen_checkout'],input=p['groups']['faf-read-root']['inputs']['faf-read-root-vulnerable'],manifest_sha256=p['groups']['faf-read-root']['manifest_sha256'],source_freeze_approval=p['groups']['faf-read-root']['source_freeze_approval'],purpose='Identify remaining scanner costs after the approved invalidation-accumulator change still timed out on the first FAF input. The1948bf9 parent profile predates this change and does not establish current residual costs. One sampled input only; no optimization or uninstrumented retry.',command=['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(out/'diagnostic.py')],output=str(base/'v68-invalidation-sampling'))
proposal['environment']=proposal['environment'].replace('frozen1948bf9','frozen4145d35')
proposal['sampler_reuse']={'prior_proposal_sha256':sha(old/'diagnostic-proposal.json'),'prior_sampler_sha256':sha(old/'corrected-sampling-worker.py'),'sampling_functions_ast_identical':functions,'allowed_changes':'Only frozen root/source identity and diagnostic/regression/output path bindings. Actual parent wrapper, existing worker entry wrapper, cadence, stack cap, snapshot interval and signal restoration remain unchanged. Stale parent rejects before target access and stale worker rejects before timer/snapshot access. No scanner method changes.','synthetic_parent_sha256':sha(out/'parent-sampler-selfcheck/packet.json'),'synthetic_worker_sha256':sha(out/'sampler-selfcheck/packet.json')}
proposal['prior_partial_profile']={'path':str((base/'v64-shared-discovery-sampling/assessment.json').relative_to(root)),'sha256':sha(base/'v64-shared-discovery-sampling/assessment.json'),'scanner_revision':'1948bf942babce155b701f5b22ed941eb16d99d0','current_residual_cost_established':False,'retained_outcome':'148764 parent samples, no worker snapshot/report, timeout and verified cleanup. Final parent snapshot restored timer before later forced teardown; cause of later teardown delay unestablished.'}
files=[assets/n for n in ['evaluation-proposal.json','evaluation-authorization.json','execution-consumed.json','evaluate.py','authorization.json','source-proof.json','freeze.json','local-checks.json','discovery-equivalence.json']]
files += [out/n for n in ['corrected-sampling-worker.py','diagnostic.py','sampler-selfcheck.py','sampler-selfcheck/packet.json','parent-sampler-selfcheck.py','parent-sampler-selfcheck/packet.json','assessment.json','validation.json','budget-closed.json','raw/packet.json','execution.json','prepare-diagnostic.py']]
files += [base/n for n in ['v43-four-fresh-preparation/runner.py','v20-linux-diagnostic-v1/runner.py','v64-shared-discovery-sampling/assessment.json','v50-faf-allocation-sampling/assessment.json']]
proposal['files_sha256']={str(f.relative_to(root)):sha(f) for f in files}
assert not (out/'diagnostic-authorization.json').exists() and not (base/'v68-invalidation-sampling').exists()
with (out/'diagnostic-proposal.json').open('x') as f:json.dump(proposal,f,indent=2);f.write('\n')
print('Prepared one unapproved1800-second parent/worker profile; zero profile executions, retries or paid calls.')
