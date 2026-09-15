"""Freeze two upstream source pairs and six records; never scan or execute them."""
import difflib, hashlib, importlib.util, json, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path('/private/tmp/mcp-phase22-options'); OUT=Path(__file__).resolve().parent
BASE=ROOT/'artifacts/phase22/corpus-unseen-v1'
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from scripts import phase20_measurements as h
from scripts.phase20_corpus import archive_files, digest, materialize, tree_digest
spec=importlib.util.spec_from_file_location('unseen_corpus',OUT/'corpus.py'); corpus=importlib.util.module_from_spec(spec);spec.loader.exec_module(corpus)
read=lambda p:json.loads(p.read_text())
ref=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
 return ref(p)
freeze=read(OUT/'scope-and-precuration-freeze.json');actual=h.scanner_identity()
assert all(actual[k]==freeze['scanner'][k] for k in ['source_sha256','harness_sha256'])
comparison=read(OUT/'novelty-comparison.json');assert not comparison['name_matches'] and not comparison['archive_read_failures']
for overlaps in comparison['overlaps'].values():
 assert all(n=='tests/__init__.py' and d['sha256']==digest(b'') for n,d in overlaps.items())
assert not BASE.exists()
cases=[
 {'id':'taskwarrior-shell','archive_label':'taskwarrior','repository':'awwaiid/mcp-server-taskwarrior','language':'typescript','rule_id':'SENT-002','tool':'mark_task_done','argument':'identifier','scan_root':'.','licenses':['LICENSE'],
  'condition':'An MCP mark_task_done caller controls identifier. A schema-valid string such as 1; printf PHASE22_INERT; # crosses from a task identifier into shell command syntax in execSync. The upstream fixed execFileSync passes the entire identifier as one argv element without a shell. The witness is documentation only and is never executed.',
  'safe_value':'1',
  'flow':'index.ts imports SDK Server and CallToolRequestSchema, registers mark_task_done via ListToolsRequestSchema, and dispatches request.params through switch(name). markTaskDoneRequest only requires z.string(); safeParse failure throws. Vulnerable line146 interpolates parsed.data.identifier into child_process.execSync. Fixed lines151–154 use execFileSync(task,[identifier,done]) with shell absent. The same parsed field reaches the fixed invocation.',
  'prerequisites':['Operator starts the upstream stdio server with the declared SDK and a local configured task binary. The declared package omits a direct zod dependency; a compatible zod must be present for its source import. No installation/startup is performed.','Caller reaches the registered mark_task_done route with a string identifier; no unrecorded outer authorization or sanitizer.','POSIX shell interpretation for the vulnerable witness. Fixed subprocess creation uses Node shell=false default; no malicious replacement task binary or executable search path.'],
  'limits':['Named shell interpretation only; no claim about Taskwarrior option/filter semantics, authorization, stable task IDs, other tools, or Windows batch execution.','GitHub current repository language says JavaScript; both selected complete archives contain index.ts and tsconfig.json and no JavaScript source. Actual evaluated language is TypeScript.','Fixed/safe records share the full fixed tree; the static scanner is not specialized to the illustrative safe value.'],
  'evidence_files':['index.ts','package.json','tsconfig.json','README.md','LICENSE'],
  'witnesses':{'vulnerable':{'path':'index.ts','sink_line':146},'fixed':{'path':'index.ts','sink_line':151}},
  'license_assessment':'Both archives retain the complete MIT license. Repository API identity is non-fork; name matches absent from the pre-curation inventory.'},
 {'id':'proxmox-upload-root','archive_label':'proxmox','repository':'nick-holmquist/proxmox-mcp','language':'python','rule_id':'SENT-012','tool':'pve_storage_upload','argument':'file_path','scan_root':'.','licenses':['README.md','pyproject.toml'],
  'condition':'An MCP pve_storage_upload caller must not open /srv/proxmox-outside/fixture.iso outside operator PROXMOX_MCP_UPLOAD_DIR=/srv/proxmox-upload. Vulnerable upload_to_storage checks isfile then opens the original caller path. Fixed _resolve_upload_path requires a nonempty operator directory, resolves directory and caller path, rejects commonpath mismatch, returns the checked path, and upload_to_storage opens that returned value.',
  'safe_value':'/srv/proxmox-upload/fixture.iso',
  'flow':'server.py _MODULES/_build_dispatch_table derives tool ownership from get_tools; @server.call_tool dispatches the exact name to storage.handle_tool. tools/storage.py declares pve_storage_upload and forwards arguments[file_path] to imported singleton client.upload_to_storage. client=ProxmoxClient() is initialized with _api=None. Vulnerable client.py line436 open(file_path,rb); fixed helper415–437 returns resolved and method457–464 consumes it. API property/network upload occurs after opening; the named local read boundary does not require claiming successful remote exfiltration.',
  'prerequisites':['Stable nonempty operator PROXMOX_MCP_UPLOAD_DIR=/srv/proxmox-upload; operator environment and dotenv inputs are not caller controlled.','Caller supplies node, storage, file_path and valid optional content. The outside witness is an existing ordinary readable regular file; the safe file is inside the existing allowed root.','Upstream Python stdio SDK server and declared dependencies/configuration are available in the source scenario. No target import/startup or credentials are supplied during evaluation.','No symlink replacement, filesystem race, mount change or custom filesystem hooks between resolution/isfile/open. Correct Proxmox configuration is additionally required for a successful upload, which is outside this static read condition.'],
  'limits':['Initial resolved filesystem containment only; no race/physical-use, downstream Proxmox authorization, successful exfiltration, API/DNS/TLS or other tool safety claim.','Module-table dispatch and imported singleton/helper support remain to be established in actual scanner output and source assessment; no-alert unsupported code fails discrimination.','Fixed/safe share complete source/configuration; safe caller value is an illustrative source prerequisite, not a specialization of static analysis.'],
  'evidence_files':['src/proxmox_mcp/server.py','src/proxmox_mcp/tools/storage.py','src/proxmox_mcp/client.py','src/proxmox_mcp/__init__.py','pyproject.toml','README.md','.env.example'],
  'witnesses':{'vulnerable':{'path':'src/proxmox_mcp/client.py','sink_line':436},'fixed':{'path':'src/proxmox_mcp/client.py','sink_line':464}},
  'license_assessment':'Both full archives declare MIT in README and pyproject.toml, including the MIT classifier. Neither contains a standalone license/full grant text; GitHub license metadata is null. All actual declarations are preserved; no absent grant text is fabricated. This qualification follows the retained no-bash declaration-only precedent.'}
]
novelty=save(BASE/'novelty.json',{'passed':True,'precuration_freeze':ref(OUT/'scope-and-precuration-freeze.json'),'comparison':ref(OUT/'novelty-comparison.json'),'recorded_source_files':len(comparison['text_files_sha256']),'distinct_archives':comparison['distinct_archives_read'],'identities':comparison['identities_and_fork_parent_checked'],'assessment':'No candidate identity/name match and no substantive file overlap; only empty Proxmox tests/__init__.py. Both API identities are non-forks. Complete source review shows standard SDK scaffolding, not copied prior condition implementations. No claim against arbitrarily transformed copies.','limits':comparison['limits'],'observations':0,'paid_calls':0})
manifest={'version':1,'status':'proposed_pending_user_freeze','freeze_approved':False,'methodology':'Two distinct repository cases, three unchanged source records each, proposed twice. Artifact-local schema reuses existing Input/Snapshot, source/hash/license validation, exact frozen approval and production measure. It replaces only the old fixed 50-input/5-rule population requirement for this exact six-input packet. All prior manifests remain untouched. No mutations or extra historical records are needed.','snapshots':[],'pairs':[],'inputs':[],'packet':[novelty],'repository_aliases':{}}
for case in cases:
 label=case['archive_label'];repo=read(OUT/f'research/{label}-repo.json');fix=read(OUT/f'research/{label}-fix.json');parent=read(OUT/f'research/{label}-parent.json')
 assert repo['full_name']==case['repository'] and repo['fork'] is False
 assert fix['parents'][0]['sha']==parent['sha']
 trees={}
 for version,commit in [('vulnerable',parent),('fixed',fix)]:
  archive=OUT/f'research/source-archives/{label}-{version}.tar.gz';receipt=read(archive.with_suffix('.json'));files=archive_files(archive.read_bytes(),strip_root=True)
  assert receipt['revision']==commit['sha'] and receipt['sha256']==digest(archive.read_bytes()) and receipt['tree_sha256']==tree_digest(files)
  assert {n:digest(b) for n,b in files.items()}==receipt['files_sha256']
  assert all(n in files for n in case['licenses'])
  if label=='taskwarrior':assert b'MIT License' in files['LICENSE'] and b'"license": "MIT"' in files['package.json']
  else:assert b'license = "MIT"' in files['pyproject.toml'] and '## License\n\nMIT' in files['README.md'].decode()
  trees[version]=files
  manifest['snapshots'].append({'repository':case['repository'],'revision':commit['sha'],'url':receipt['url'],'archive':ref(archive),'licenses':case['licenses'],'files':receipt['files_sha256']})
  case[version+'_revision']=commit['sha'];case[version+'_git_tree']=commit['commit']['tree']['sha']
 directory=BASE/case['id'];directory.mkdir(parents=True)
 a,b=trees['vulnerable'],trees['fixed'];changed=sorted(n for n in a.keys()|b.keys() if a.get(n)!=b.get(n));case['all_changed_files']=changed
 (directory/'full-pair.diff').write_text(''.join(''.join(difflib.unified_diff(a.get(n,b'').decode(errors='replace').splitlines(True),b.get(n,b'').decode(errors='replace').splitlines(True),fromfile='vulnerable/'+n,tofile='fixed/'+n)) for n in changed))
 case['actual_detector_support']='Unmeasured: require source-bound discovery/caller/guard/value/sink support after execution. Native output has no positive per-sink guard trace. A generic rule/line match is only a candidate; full source assessment decides the named condition.'
 review=save(directory/'condition-review.json',case)
 provenance=save(directory/'provenance.json',{'repository':ref(OUT/f'research/{label}-repo.json'),'fix':ref(OUT/f'research/{label}-fix.json'),'parent':ref(OUT/f'research/{label}-parent.json'),'first_parent_verified':True,'archives':[ref(OUT/f'research/source-archives/{label}-{v}.tar.json') for v in trees],'license_qualification':case['license_assessment'],'novelty':novelty,'reviewer':'Same agent, source-only after pre-curation freeze; not independent human review.'})
 manifest['packet'] += [review,provenance,ref(directory/'full-pair.diff')]
 manifest['pairs'].append({'id':case['id'],'rule_id':case['rule_id'],'fix_origin':'upstream','provenance':[review,provenance,novelty],'review':case['flow']})
 manifest['repository_aliases'][case['repository'].casefold()]=case['repository']
 for version in ['vulnerable','fixed','safe']:
  source_version='fixed' if version=='safe' else version;files=trees[source_version]
  item={'id':case['id']+'-'+version,'family':case['id'],'repository':case['repository'],'language':case['language'],'split':'held_out','variant':'safe_control' if version=='safe' else 'original','label':version,'snapshot':case[source_version+'_revision'],'scan_root':case['scan_root'],'condition':case['condition']+(' Safe caller value: '+case['safe_value'] if version=='safe' else ''),'prerequisites':case['prerequisites']+(['Use illustrative safe value '+case['safe_value']] if version=='safe' else []),'static_applicability':case['actual_detector_support'],'runtime_applicability':'unsupported','runtime_reason':'Zero target execution authorized; static source-only evaluation.','runtime_configuration':None,'evidence':[{'path':n,'start_line':1,'end_line':len(files[n].splitlines()),'sha256':digest(files[n]),'role':'Complete source context; condition-review.json distinguishes caller, guard, sink and prerequisites.'} for n in case['evidence_files'] if files.get(n)],'matching':'Require '+case['rule_id']+' on the named '+case['tool']+' caller '+case['argument']+' at the actual scored sink with the specified boundary violation; unrelated rule/line overlap is insufficient.','tree_sha256':tree_digest(files)}
  manifest['inputs'].append(item)
manifest_ref=save(BASE/'manifest.json',manifest);m=corpus.validate(BASE/'manifest.json');configs={}
for item in m.inputs:
 with tempfile.TemporaryDirectory(prefix='phase22-unseen-source-only-') as tmp:
  target=materialize(item,next(s for s in m.snapshots if s.revision==item.snapshot),Path(tmp).resolve()/'source',m.packet)
  config=h.load_configuration(target,environ={},static_only=True,cli_overrides={'rules_only':True,'ignore_paths':['.phase20/**'],'max_findings_per_scan':500},llm_cli_overrides={'model':h.LLM.model,'reasoning_effort':'medium','retries':0,'max_concurrency':1,'cache_enabled':False})
  payload={'scanner':config.scanner.model_dump(mode='json'),'target':config.target.model_dump(mode='json') if config.target else None,'static_only':config.static_only,'language':config.language.value}
  assert payload['language']==item.language and config.scanner.scanner.rules_only
  configs[item.id]={'configuration':payload,'sha256':digest((json.dumps(payload,indent=2,sort_keys=True)+'\n').encode())}
config_ref=save(BASE/'configurations.json',configs)
save(OUT/'cases.json',cases)
save(BASE/'checkpoint-cec0322.json',{'status':'prepared_not_approved_not_executed','recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':freeze['scanner'],'manifest':manifest_ref,'configurations':config_ref,'novelty':novelty,'cases':ref(OUT/'cases.json'),'input_order':[i.id for i in m.inputs],'repository_count':2,'input_count':6,'proposed_observations':12,'mutations':0,'observations':0,'paid_calls':0,'target_execution':False})
print('Six source-only records validated: two repositories; zero scans, target executions or paid calls.')
