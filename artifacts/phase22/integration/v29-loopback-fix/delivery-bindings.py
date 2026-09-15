"""Bind the final reviewable docs and sealed correction evidence before delivery."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
r=Path.cwd();b=r/'artifacts/phase22/integration';o=b/'v29-loopback-fix';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quality='439c3fe658d30ebbc6cf6e21296261a38a6a3e92';scanner='f85a90f9ba2d1c43019e8505b977d57f3476a9c9'
inputs=['src','tests','scripts','schemas','pyproject.toml','uv.lock','action.yml','.github','Makefile','LICENSE','README.md','CHANGELOG.md']
assert not subprocess.check_output(['git','diff',quality,'--',*inputs])
assert json.loads((b/'v29-final-docs.json').read_text())['exit_code']==0
assert json.loads((b/'v29-quality/packet.json').read_text())['engineering_passed']
audit=json.loads((o/'audit.json').read_text());assert audit['dispositions']=={'passed':82,'explicitly user-deferred':2,'unresolved':5}
for name,digest in audit['current_source_and_test_files'].items():assert sha(r/name)==digest,name
protected=json.loads((o/'protected-files.json').read_text())
for name,digest in protected.items():assert sha(r/name)==digest,name
assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())==set(protected)
for cwd in ['/Users/bashaarjavaid/Projects/MCP-Sentinel','/private/tmp/mcp-phase22-frozen-1f3f72f','/private/tmp/mcp-phase22-frozen-6db3858']:
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=cwd)
seal=json.loads((b/'evidence-v56.json').read_text());assert sha(b/seal['archive'])==seal['sha256']
assert not (o/'evaluation-authorization.json').exists()
names=['AGENTS.md','ROADMAP.md','ARCHITECTURE.md','README.md','docs/rules.md','docs/phase22-technical.md','docs/phase22-implementation-status.md','docs/phase22-ssrf-follow-up.md','docs/phase22-timeout-policy.md','docs/phase22-corpus-review.md','artifacts/phase22/integration/README.md','artifacts/phase22/integration/requirements.md','artifacts/phase22/integration/progress.md']
refs=['audit.json','summary.md','pr-body.md','evaluation-proposal.json','local-checks.json','local-source-binding.json','compatibility.json','source-compatibility-scope.json']
p={'recorded_at':datetime.now(timezone.utc).isoformat(),'tested_workflow':quality,'verified_corrected_scanner':scanner,'first_frozen_corpus_scanner':'1f3f72f0f25c597b53c9f833e2e4bec99728d328','byte_identical_quality_inputs':inputs,'owning_docs_sha256':{n:sha(r/n) for n in names},'review_packet_sha256':{n:sha(o/n) for n in refs},'evidence_seal':{'path':'artifacts/phase22/integration/evidence-v56.tar.gz','sha256':seal['sha256']},'user_files_sha256':protected,'main_and_frozen_worktrees_clean':True,'ordinary_ci':{'ci':34642059839,'docs':34642059977,'normal_jobs_passed':29,'optional_jobs_skipped':4,'matrix_suites':12,'tests_per_suite':2242,'skips_per_suite':36},'current_source_corpus_observations':0,'prior_scanner_regression_observations_this_continuation':3,'new_paid_calls':0,'evaluation_approved':False,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'This post-seal binding and final delivery receipt are supplemental; they are not claimed inside the archive or a commit that predates them. Final remote delivery is verified after push.'}
path=o/'documentation-binding.json';assert not path.exists();path.write_text(json.dumps(p,indent=2)+'\n');print('Bound',len(names),'owning docs and exact unchanged quality/package inputs.')
