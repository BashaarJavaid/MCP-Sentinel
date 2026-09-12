"""Bind unchanged runtime evidence and preserve prior source-specific results."""
import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd(); b=r/'artifacts/phase22/integration'; o=b/'v29-loopback-fix'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((b/'v5-git-runtime-reuse/packet.json').read_text())
for name,digest in old['unchanged_runtime_component_files'].items(): assert sha(r/name)==digest,name
image=subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',old['approved_image']],text=True).strip()
assert image==old['approved_image']
assert not subprocess.check_output(['docker','ps','-a','--filter','label=com.securemcp.sentinel=true','--format','{{json .}}'],text=True).strip()
replay=json.loads((b/'v29-production-capture-revalidation/packet.json').read_text())
assert replay['source']=='439c3fe658d30ebbc6cf6e21296261a38a6a3e92' and replay['model_calls']==0
assert len(replay['requests'])==6 and all(x['accepted'] for x in replay['requests'])
prior=json.loads((b/'v19-final-production-capture-revalidation/packet.json').read_text())
assert [(x['fingerprint'],x['request_sha256']) for x in replay['requests']]==[(x['fingerprint'],x['request_sha256']) for x in prior['requests']]
for name,digest in json.loads((o/'protected-files.json').read_text()).items(): assert sha(r/name)==digest,name
for worktree in ['/Users/bashaarjavaid/Projects/MCP-Sentinel','/private/tmp/mcp-phase22-frozen-1f3f72f']:
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=worktree)
changed=subprocess.check_output(['git','diff','--name-only','1f3f72f','f85a90f','--','src'],text=True).splitlines()
assert changed==['src/sentinel/static/engine.py','src/sentinel/static/rules/sent015.py','src/sentinel/static/typescript_discovery.py','src/sentinel/static/typescript_path_flow.py','src/sentinel/static/typescript_registration_flow.py']
refs=['v28-lighthouse-regression/assessment.json','v25-lighthouse-fix/audit.json','v24-fresh-v5/assessment.json','v24-fresh-v5/warning-source-assessment.json','v24-fresh-v5/audit.json','v22-refresh-disposition-corrected.json','v13-exposed-assessment/packet.json','v13-searxng-assessment/packet.json','v5-git-runtime-reuse/packet.json','v19-final-production-capture-revalidation/packet.json','v29-production-capture-revalidation/packet.json']
seals={}
for n in range(1,56):
 p=json.loads((b/f'evidence-v{n}.json').read_text()); assert sha(b/p['archive'])==p['sha256'];seals[p['archive']]=p['sha256']
out={'source':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'corrected_scanner':'f85a90f9ba2d1c43019e8505b977d57f3476a9c9','changed_product_files':changed,'runtime_components':old['unchanged_runtime_component_files'],'runtime_reference_sha256':sha(b/'v5-git-runtime-reuse/packet.json'),'approved_image':image,'git_limits':'13 retained campaigns,1040 planned/312 tested/728 remaining, all incomplete. Byte-identical runtime/catalog/config/report components and existing source rows support reuse; no new Git target execution or complete coverage claim.','production_replay':'Six actual requests regenerated and accepted with exact prior fingerprints/request hashes. Owned Docker demo is separate from corpus evaluation; no Lighthouse target execution.','prior_results_sha256':{n:sha(b/n) for n in refs},'prior_seals_sha256':seals,'exposed_regressions':'Prior2ac39aa results remain passed at their measured source. Changed TypeScript discovery/flow is not byte-compatible; no automatic current-source reuse or corpus timing claim. Proposed Lighthouse check is separate and unapproved.','historical_timing':'Approved whole25 reuse plus45+45 timing/condition results remain passed at1f3f72f. Product changes are not new current-source timing measurements.','current_source_corpus_observations':0,'prior_scanner_regression_observations_this_continuation':3,'new_paid_calls':0,'sentinel_containers':[],'main_and_frozen_worktrees_clean':True,'phase22_complete':False}
p=o/'compatibility.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('Verified six requests, runtime/image bindings, protected files and55 prior seals.')
