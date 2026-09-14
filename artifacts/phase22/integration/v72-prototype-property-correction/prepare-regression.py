"""Prepare one new, unapproved corrected four-repository regression after engineering."""
import copy,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;base=out.parent;root=out.parents[3]
old=base/'v69-uncapped-four-repository';previous=base/'v70-uncapped-four-results'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=read(out/'freeze.json');local=read(out/'local-checks.json');quality=read(base/'v72-candidate-quality-audit/packet.json')
assert freeze['scanner']['revision']==local['candidate']==quality['source']
assert read(out/'boundary-checks.json')['passed'] and read(out/'synthetic-equivalence.json')['passed']
assert len(read(out/'synthetic-equivalence.json')['comparisons'])==10
assert not (out/'evaluation-authorization.json').exists() and not (out/'execution-consumed.json').exists()
assert not (base/'v73-corrected-four-results').exists()
p=copy.deepcopy(read(old/'evaluation-proposal.json'))
p.update(status='prospective_exposed_correctness_regression_not_approved',recorded_at=datetime.now(timezone.utc).isoformat(),scanner=freeze['scanner'],frozen_checkout=freeze['frozen_checkout'],purpose='Evaluate the ordinary approved-contract constructor parameter-property and initial URL guard corrections at the engineering-tested candidate. Preserve the user preference to do four repositories first. This is a NEW proposal for24uncapped observations, not use of the completed V70 budget.',runner=str((out/'evaluate.py').relative_to(root)),prepared_command=['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(out/'launch.py')],prepared_command_cwd=str(root),launch_precondition='Fresh explicit user approval of this exact source/proposal,24observations and uncapped experimental stopping policy; passing final engineering/freeze/policy/missing-approval checks, unused token, protected state and no conflicting owned work. The previous24observations are closed and supply no renewed permission.',scope_justification='The last24observations completed and exposed two source-established correctness gaps. Both corrections now pass independent scanner-owned and full engineering checks; actual corrected-source results remain unknown. Preserve four-repository-first order:18non-FAF observations followed by6FAF,12inputs twice. All181prior-language observations remain excluded and unapproved; necessary current-source Python/TypeScript compatibility is still a later gate.',following_checkpoint='Source-assess all findings, diagnostics, surfaces and complete ordered differences against original first-frozen and immediately preceding exposed reports. Retain any failure and close all unused observations. Prepare further required compatibility or ordinary correctness work based on actual evidence; no automatic retry, optimization, new measurement budget or technical acceptance.',technical_acceptance_received=False,phase22_complete=False)
p['retained_timeout_policy']['scope']='Proposed reuse of the verified V69 experiment-only deadline overrides and infinity-to-None subprocess-wait adapter, bound to the new candidate. The normal product source remains1800seconds; finite cleanup and existing worker/resource limits remain unchanged.'
p['retained_timeout_policy']['qualification']='A prior-source FAF input took2212.22–2341.48seconds in the completed uncapped experiment. That is historical local timing, not an estimate or ceiling for this expanded correctness candidate. Completion here would establish experimental uncapped behavior only, not normal1800-second completion or speedup.'
p['not_authorized']=['the pending v68 literal-serialization performance optimization','the181prior-language observations','any input beyond these24 or automatic retry/profile/comparator/new repository','product/default deadline change','worker/resource increase or new execution environment','target tests/build/install/endpoints','paid calls','merge/ready/release/outreach/Phase23']
p['original_source_bindings']['immediately_preceding_exposed']='4145d35:24complete/12equal pairs; no-bash and Engram narrow passes, FAF vulnerable miss/unsupported negatives and Lightning negative-qualifier failure. Immutable source/report assessment retained in V70.'
p['prior_exposed_assessment']={'path':str((previous/'final-assessment/assessment.json').relative_to(root)),'sha256':sha(previous/'final-assessment/assessment.json'),'source':read(previous/'final-assessment/assessment.json').get('scanner'),'delivery_sha256':sha(previous/'delivery-verification.json')}
p['current_engineering']={'local_sha256':sha(out/'local-checks.json'),'hosted_audit_sha256':sha(base/'v72-candidate-quality-audit/packet.json'),'freeze_sha256':sha(out/'freeze.json'),'source_assessment_sha256':sha(out/'source-assessment.json')}
p.pop('source_unchanged_proof_sha256',None)
p['files_sha256']={n:d for n,d in p['files_sha256'].items() if not n.startswith(('artifacts/phase22/integration/v66-invalidation-contract/','artifacts/phase22/integration/v69-uncapped-four-repository/'))}
rubric=copy.deepcopy(read(old/'scoring-rubric.json'))
rubric['status']='prospective_corrected_four_repository_regression_not_approved'
rubric['prior_scope_interpretation']='Nested earlier-language rubrics remain required historical conditions but their181observations are excluded. This NEW proposal has24observations on12inputs and12entire ordered pairs; neither earlier approval nor synthetic success authorizes execution.'
rubric['uncapped_experiment_amendment']['prior_rubric_sha256']=sha(old/'scoring-rubric.json')
rubric['previous_exposed_result']={'source':'4145d3559c5300a5003ca8e3368c8da49fb51f91','assessment_sha256':sha(previous/'final-assessment/assessment.json'),'interpretation':'Two narrow passes and two failed support/qualification gates are preserved. Every corrected finding, diagnostic, surface and whole-report difference requires actual source assessment. Quiet unsupported negatives still fail.'}
assert len(p['order'])==p['bounds']['native_observations']==24
assert len({r['input_id'] for r in p['order']})==p['bounds']['distinct_inputs']==12
assert p['bounds']['ordered_repeat_pairs']==12 and p['bounds']['paid_calls']==0
assert [r for r in p['order'] if r['group']=='faf-read-root']==p['order'][-6:]
assert len(p['volatile_exclusions'])==11
with (out/'scoring-rubric.json').open('x') as f:json.dump(rubric,f,indent=2);f.write('\n')
paths=[out/n for n in ['uncapped.py','evaluate.py','launch.py','intake.json','boundary-checks.json','synthetic-equivalence.json','scoring-rubric.json','local-checks.json','freeze.json','source-assessment.json']]+[base/'v72-candidate-quality-audit/packet.json',previous/'final-assessment/assessment.json',previous/'delivery-verification.json']
for path in paths:p['files_sha256'][str(path.relative_to(root))]=sha(path)
p['runtime_policy_sha256']=sha(out/'uncapped.py');p['intake_sha256']=sha(out/'intake.json')
for n,d in p['files_sha256'].items():assert sha(root/n)==d,n
assert not subprocess.check_output(['git','diff',freeze['scanner']['revision'],'--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md'])
with (out/'evaluation-proposal.json').open('x') as f:json.dump(p,f,indent=2);f.write('\n')
binding={'proposal_sha256':sha(out/'evaluation-proposal.json'),'launcher_sha256':sha(out/'launch.py'),'runner_sha256':sha(out/'evaluate.py'),'policy_sha256':sha(out/'uncapped.py'),'command':p['prepared_command'],'scope':'New separately approved24-observation corrected-source proposal. The same-process launcher retains existing per-input process groups and finite cleanup; no automatic wall timer. Missing approval must fail before token, output or target input access.','approved':False,'executed':False,'new_paid_calls':0}
with (out/'launcher-binding.json').open('x') as f:json.dump(binding,f,indent=2);f.write('\n')
print('Prepared unapproved24-observation corrected-source proposal',binding['proposal_sha256'])
