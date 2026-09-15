"""Bind final owning documents after evidence sealing, before draft delivery."""
import hashlib
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path.cwd();BASE=ROOT/'artifacts/phase22/integration';OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quality='439c3fe658d30ebbc6cf6e21296261a38a6a3e92'
inputs=['src','tests','scripts','schemas','pyproject.toml','uv.lock','action.yml','.github','Makefile','LICENSE','README.md','CHANGELOG.md']
assert not subprocess.check_output(['git','diff',quality,'--',*inputs])
assert json.loads((BASE/'v30-final-docs.json').read_text())['exit_code']==0
assert json.loads((OUT/'owned-work-final.json').read_text())['owned_processes']==[]
audit=json.loads((OUT/'audit.json').read_text());assert audit['current_exposed_gate_passed']
protected=json.loads((BASE/'v29-loopback-fix/protected-files.json').read_text())
for n,d in protected.items():assert sha(ROOT/n)==d,n
assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())==set(protected)
worktrees={}
for folder,expected in [('/Users/bashaarjavaid/Projects/MCP-Sentinel','4cd57593b2585b9ee05c0f175930e6a0d76d362a'),('/private/tmp/mcp-phase22-frozen-1f3f72f','1f3f72f0f25c597b53c9f833e2e4bec99728d328'),('/private/tmp/mcp-phase22-frozen-6db3858','6db3858f1368033642354ab5ebb53aef76315a16'),('/private/tmp/mcp-phase22-frozen-f85a90f','f85a90f9ba2d1c43019e8505b977d57f3476a9c9')]:
 actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=folder,text=True).strip();assert actual==expected
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=folder)
 worktrees[folder]=actual
subprocess.run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'],check=True)
names=['AGENTS.md','ROADMAP.md','ARCHITECTURE.md','README.md','docs/rules.md','docs/phase22-technical.md','docs/phase22-implementation-status.md','docs/phase22-ssrf-follow-up.md','docs/phase22-timeout-policy.md','docs/phase22-corpus-review.md','artifacts/phase22/integration/README.md','artifacts/phase22/integration/requirements.md','artifacts/phase22/integration/progress.md']
deltas={}
for n,d in audit['current_source_and_test_files'].items():
 if sha(ROOT/n)!=d:
  assert n in names,n
  deltas[n]={'audit_sha256':d,'final_sha256':sha(ROOT/n)}
seal=json.loads((BASE/'evidence-v57.json').read_text());assert sha(BASE/seal['archive'])==seal['sha256']
proposal=BASE/'v30-compatibility-proposal/evaluation-proposal.json'
assert not proposal.with_name('evaluation-authorization.json').exists()
refs=['audit.json','assessment.json','source-assessment.json','summary.md','pr-body.md','validation.json','retained-source-deltas.json']
p={'recorded_at':datetime.now(timezone.utc).isoformat(),'tested_workflow':quality,'scanner':audit['scanner_identity'],'evaluation_workflow':'75142f053ab5017ebd0a7f0953994ee9f7c14dd8','evaluation_run':34648036083,'evaluation_observations':10,'evaluation_passed':True,'byte_identical_quality_inputs':inputs,'owning_docs_sha256':{n:sha(ROOT/n) for n in names},'review_packet_sha256':{n:sha(OUT/n) for n in refs},'post_audit_document_deltas':deltas,'evidence_seal':{'path':str(BASE/seal['archive']),'sha256':seal['sha256']},'user_files_sha256':protected,'clean_worktrees':worktrees,'next_proposal_sha256':sha(proposal),'next_proposal_approved':False,'new_paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Supplemental post-seal document binding. Final remote delivery is verified after push; this record does not claim its future commit or inclusion inside seal57.'}
path=OUT/'documentation-binding.json';assert not path.exists();path.write_text(json.dumps(p,indent=2)+'\n');print('Final13 owning docs bound;quality inputs unchanged;protected worktrees clean.')
