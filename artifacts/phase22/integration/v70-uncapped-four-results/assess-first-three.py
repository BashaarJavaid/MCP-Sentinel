"""Assess immutable completed reports; never read or change the active FAF input."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
DEST = OUT / 'first-three-assessment'
OLD = OUT.parent / 'v44-four-fresh-evaluation'
PREP = OUT.parent / 'v69-uncapped-four-repository'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (DEST / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')

inventory = read(DEST / 'inventory.json')
validation = read(DEST / 'validation.json')
prior_inventory = read(OLD / 'inventory.json')
prior_findings = read(OLD / 'finding-source-assessment.json')
assert validation['passed'] and len(inventory['rows']) == 18
contexts = inventory['contexts']
prior_by_key = {(r['context'], r['finding']['rule_id']): r for r in prior_findings['rows']}
sdk = read(OLD / 'sdk-validation-source.json')
assert sha(Path(sdk['source_path'])) == sdk['source_sha256']
write('sdk-validation-source.json', sdk)

# Reassess current support instead of inheriting the original missed-sink claims.
context_rows = {}
for key, c in contexts.items():
    p, group = c['path'], c['case_id']
    scope = c.get('scope', 'module/import/helper binding')
    if key in prior_inventory['contexts']:
        assert c == prior_inventory['contexts'][key]
    if p.startswith('tests/') or '.test.' in p or '/test-' in p:
        role = 'Retained upstream test source, mocks or fixtures; read only, never executed.'
    elif group == 'no-bash-write-prefix':
        if p == 'src/security.ts':
            role = 'Shared path/network validation. Vulnerable raw normalizedRoot prefix admits the frozen sibling; fixed root-plus-separator or exact-root check rejects it. Returned safe and absolutePath feed the checked write helper. Current fixed named write accurately carries lexical-boundary/physical-gap qualification.'
        elif p == 'src/fileSystem.ts':
            role = 'Filesystem listing/read/write/trash helper. Only overwrite writeFileSync at139 vulnerable/140 fixed is the named sink. Fixed checked absolutePath retains the lexical boundary; physical symlink containment is not established. Metadata, append, read and trash candidates remain separate.'
        elif p == 'src/index.ts':
            role = 'Official SDK CallToolRequestSchema dispatcher, Zod arguments, operator root and executeTool forwarding. Source and finding flow bind write_file; the report still exposes one unnamed unresolved surface, so complete named metadata discovery is not established.'
        else:
            role = 'No-bash source helper for audit, Git, approval, network or project scripts. Its configuration, external effects and prerequisites are separate from the frozen overwrite condition.'
    elif group == 'lightning-discover-linklocal':
        if p.endswith('tools/discover_api.py'):
            role = 'Lightning manifest/registry discovery in '+scope+'. The selected nonempty URL takes the available HTTPX branch through _fetch_and_format_manifest and _fetch_manifest to _try_fetch/client.get. Current findings establish this named sink but omit the fixed initial literal link-local rejection qualification. The separate registry route uses operator environment/base URL and query/category; it is outside the selected direct-URL condition.'
        elif p.endswith('tools/_ssrf_guard.py'):
            role = 'Initial URL/IP guard in '+scope+'. urlsplit hostname becomes ip_address; is_blocked_ip includes is_link_local/is_private and causes SsrfError, caught with terminal return before client construction. This proves the selected fixed initial literal rejection in source. The current unqualified named finding fails to recognize it. DNS lookup, rebinding, redirects, other destinations and deployment safety are not certified.'
        elif p.endswith('server.py'):
            role = 'Lightning official SDK schema listing/dispatch/service initialization in '+scope+'. All26 listed tools including discover_api are recognized. Default compatible SDK schema validation precedes handler dispatch; wallet-exempt discover_api and frozen available HTTPX prerequisites bind the selected route. This is not runtime execution or proof that every downstream operation is supported.'
        else:
            role = 'Lightning '+scope+' in '+p+' implements separate wallet/payment/budget/agent/API/configuration or response handling. Its unresolved calls remain limitations, not measured extra conditions or runtime proof.'
    else:
        assert group == 'engram-export-home'
        if p.endswith('server.py') and (scope == 'memory_export_all' or c.get('binding') == 'launch state'):
            role = 'Engram export/launch source. Function-local Path and named manifest_path.write_text are now recognized. Fixed resolved.relative_to(home) rejects the outside caller path before _get_engine and export; the later original Path reconstruction is explicitly qualified as unestablished at use. Stable home/cwd/environment and ordinary-file prerequisites support only the frozen initial-boundary discrimination. Unconfigured launch fallback remains visible.'
        elif p.endswith('markdown_io.py'):
            role = 'Engram '+scope+' implements markdown/export/snapshot or import parsing. These helper reads, directories and files are separate from the named server manifest write. Fixed export home-guard qualification applies only to the reviewed export route; other callers are not globally safe.'
        else:
            role = 'Engram '+scope+' in '+p+' implements other memory/database/embedding/search/summarization behavior. Healthy PostgreSQL, permissions, valid data and NullEmbedder remain frozen prerequisites; no database, model or target operation ran.'
    context_rows[key] = {'source': c, 'assessment': role, 'prior_identical_source_context': key in prior_inventory['contexts'], 'disposition': 'Retain each exact unresolved operation and occurrence; indexing does not resolve a warning or prove safety. Findings are adjudicated separately.'}

findings, diagnostics, surfaces, rows = [], [], [], []
for inv, v in zip(inventory['rows'], validation['observations'], strict=True):
    assert inv['input_id'] == v['input_id'] and inv['batch'] == v['batch'] and inv['report_sha256'] == v['report_sha256']
    group, vulnerable = inv['case_id'], inv['label'] == 'vulnerable'
    named, matched = [], []
    for fr in inv['findings']:
        f, c = fr['finding'], contexts[fr['context']]
        p, line, rule = c['path'], c['line'], f['rule_id']
        is_named = (group == 'no-bash-write-prefix' and p == 'src/fileSystem.ts' and line in {139,140} and rule == 'SENT-012') or (group == 'lightning-discover-linklocal' and p.endswith('tools/discover_api.py') and line in {126,132} and rule == 'SENT-015') or (group == 'engram-export-home' and p == 'src/engram/server.py' and line in {1081,1095} and rule == 'SENT-012')
        condition_match = is_named and (vulnerable or group == 'lightning-discover-linklocal')
        old = prior_by_key.get((fr['context'], rule))
        if is_named:
            named.append(f['dedup_key'])
            if condition_match:
                matched.append(f['dedup_key'])
            if group == 'no-bash-write-prefix':
                assert 'writeFileSync(validation.absolutePath' in f['evidence']['snippet']
                if vulnerable:
                    assert 'normalized root-prefix' in f['description']
                    explanation = old['assessment']
                else:
                    assert 'lexical directory boundary' in f['description'] and 'symlinks' in f['description']
                    explanation = 'Supported named negative under the prospectively bound qualifier rubric. security.ts16-27 resolves the requested path and rejects unless root-plus-separator or exact root; fileSystem.ts120-123 checks safe and140 writes the returned checked absolutePath. The frozen outside sibling is rejected and safe path is inside. The report accurately limits residual uncertainty to physical/symlink containment, which is excluded by the frozen ordinary-file prerequisites. Retain this broader raw candidate; it does not allege the scored sibling-prefix bypass. Named metadata remains unresolved separately.'
            elif group == 'lightning-discover-linklocal':
                assert 'client.get(url)' in f['evidence']['snippet'] and f['description'] == 'A caller URL reaches an outbound request without enforced scheme and destination restrictions.'
                if vulnerable:
                    explanation = 'Named vulnerable candidate hit: recognized discover_api caller URL, available HTTPX branch, _fetch_and_format_manifest/_fetch_manifest and _try_fetch at126 now bind actual client.get. The selected literal URL ends in .json and is tried directly without initial private/link-local rejection. Wallet, optional dependency and service assumptions remain as frozen; no network request or exploit ran.'
                else:
                    explanation = 'Named fixed/safe false alert under the unchanged scoring rubric. discover_api.py483 awaits validate_url_allowed before AsyncClient490. _ssrf_guard.py141-166 parses the literal and raises on is_blocked_ip, whose111-121 predicate includes link-local/private; caught SsrfError returns at484-488. The selected169.254.169.254 initial URL cannot reach client.get132, and93.184.216.34 is the safe control. The finding carries the actual caller/sink route and guard source locations but no scheme/link-local/private-literal qualification; missing qualification fails discrimination. Do not relabel this as an unrelated redirect/DNS concern or infer broad SSRF safety.'
            else:
                assert 'manifest_path.write_text' in f['evidence']['snippet']
                if vulnerable:
                    assert f['description'].startswith('Caller-controlled paths')
                    explanation = 'Named vulnerable candidate hit at actual server.py1081 manifest_path.write_text with memory_export_all caller output_path and function-local Path. No initial home boundary rejects the frozen outside directory. Healthy PostgreSQL/NullEmbedder, export helpers, writable filesystem and no-race prerequisites remain; unrelated helper findings are not counted as extra hits.'
                else:
                    assert 'resolved copy' in f['description'] and 'equivalence and containment' in f['description']
                    explanation = 'Supported narrow initial-boundary negative under the prospectively bound resolved-copy rubric. server.py1069 resolves Path(output_path),1070 resolves home,1072 relative_to rejects outside via ValueError return before engine/export. Later1086 reconstructs original Path and1095 writes the named manifest. Stable home/cwd/environment and ordinary-file prerequisites establish the selected outside rejection and inside control; the scanner explicitly leaves reconstructed-path equivalence/containment at use unestablished. Retain the raw qualified candidate and that limitation; this is not full fixed-path or runtime safety.'
        elif group == 'lightning-discover-linklocal' and rule == 'SENT-015':
            assert p.endswith('tools/discover_api.py') and line in {337,369}
            explanation = 'Unmatched registry-request candidate at _search_registry/client.get(request_url). The base derives from operator L402_REGISTRY_URL/LIGHTNING_ENABLE_API_URL or the fixed public default; caller query/category are encoded query values. The frozen direct-URL route has query/category absent and never takes this branch. Its generic caller-URL wording does not prove destination control here; preserve the overbroad candidate with operator configuration prerequisites, no extra named hit or new network test.'
        elif group == 'engram-export-home':
            assert rule == 'SENT-012' and p == 'src/engram/markdown_io.py'
            operation = {146:'dump_memories output mkdir',156:'per-memory markdown write',223:'snapshot output mkdir',286:'parse_claudemd_memories input read',385:'dump_all_projects export mkdir',409:'create_export_readme mkdir',435:'README write'}[line]
            explanation = 'Unmatched helper candidate: '+operation+'. The selected sink is server.py manifest_path.write_text, now independently detected. Export-route fixed home guard is preserved where the raw report gives resolved-copy qualification; shared other caller routes and import/snapshot paths are not declared safe. Healthy database, permissions, source data and no-race prerequisites remain. No target read/write occurred.'
        else:
            assert old is not None, (group,p,line,rule)
            explanation = old['assessment']
            if group == 'no-bash-write-prefix' and line in {129,130} and rule == 'SENT-012':
                explanation = 'Unmatched parent-directory mkdir, executed in the overwrite branch even when the parent already exists. Its recursive call then has no new directory to create under the frozen parent-exists prerequisite. This corrects the historical assessment wording that the branch was not taken. Source uses dirname of the validated path; fixed source rejects the outside caller before this operation. It is not the selected writeFileSync sink.'
            if group == 'no-bash-write-prefix' and not vulnerable and rule == 'SENT-012':
                explanation += ' Current raw qualifier, if present, accurately records the lexical guard and physical-gap uncertainty; preserve it rather than inheriting a historical generic missing-boundary claim.'
        findings.append({'batch': inv['batch'], 'input_id': inv['input_id'], 'report_sha256': inv['report_sha256'], **fr, 'named_sink': is_named, 'matches_condition': condition_match, 'assessment': explanation, 'prior_assessment_reference': {'file': str((OLD/'finding-source-assessment.json').relative_to(ROOT)), 'context': fr['context'], 'rule_id': rule} if old else None, 'disposition': 'named vulnerable hit' if condition_match and vulnerable else 'named negative false alert' if condition_match else 'supported qualified named negative' if is_named else 'source-assessed unmatched finding'})
    assert len(named) == 1
    for d in inv['diagnostics']:
        assert d['context'] in context_rows
        diagnostics.append({'batch':inv['batch'],'input_id':inv['input_id'],'report_sha256':inv['report_sha256'],**d,'assessment_context':d['context'],'disposition':'Retain exact unresolved operation with source role; no inferred safety, suppression or exploit.'})
    for s in inv['surfaces']:
        surface = s['surface']
        if group == 'no-bash-write-prefix':
            assert surface['name'] is None and surface['status'] == 'unresolved'
            explanation = 'Official SDK dispatcher remains unnamed/unresolved in surface metadata; source and finding flow independently bind the selected write_file route. Complete named handler/metadata coverage is not established.'
        else:
            assert surface['name'] and surface['status'] == 'recognized'
            explanation = 'Exact source-listed '+surface['name']+' registration/handler is recognized. Examined rule IDs record attempted analysis, not full downstream coverage. The selected '+('discover_api sink is now detected but fixed initial literal guard qualification fails.' if group == 'lightning-discover-linklocal' else 'memory_export_all manifest write is now detected with fixed resolved-copy qualifier; launch-state fallback and reconstructed-use limitations remain.')
        surfaces.append({'batch':inv['batch'],'input_id':inv['input_id'],'report_sha256':inv['report_sha256'],**s,'assessment':explanation})
    assert inv['coverage']['workspace'] is None
    rows.append({**v,'case_id':group,'label':inv['label'],'snapshot':inv['snapshot'],'named_candidate_keys':named,'matching_keys':matched,'named_vulnerable_hit':bool(matched) if vulnerable else None,'named_negative_false_alert':bool(matched) if not vulnerable else None,'supported_qualified_negative':not vulnerable and not matched,'coverage':inv['coverage']})

assert len(findings) == 260 and len(diagnostics) == 38388 and len(surfaces) == 270 and len(context_rows) == 1970
write('source-context-assessment.json', {'contexts':context_rows,'count':1970,'unassessed':0,'prior_identical_contexts':1959,'new_contexts':11,'qualification':'Same-agent source assessment of retained bytes, not independent human validation or target execution.'})
write('finding-source-assessment.json', {'rows':findings,'count':260,'unassessed':0})
write('diagnostic-source-assessment.json', {'rows':diagnostics,'count':38388,'by_kind':dict(Counter(d['kind'] for d in diagnostics)),'unmapped':0,'context_packet_sha256':sha(DEST/'source-context-assessment.json')})
write('surface-source-assessment.json', {'rows':surfaces,'count':270,'unassessed':0,'total_possible_surfaces':'unknown; no coverage percentage inferred','workspace':'null in all18 reports; no new workspace coverage'})
cases = []
for group in ('no-bash-write-prefix','lightning-discover-linklocal','engram-export-home'):
    selected = [r for r in rows if r['case_id'] == group]
    batches = {b:{'completed':3,'vulnerable_hits':sum(bool(r['matching_keys']) for r in selected if r['batch']==b and r['label']=='vulnerable'),'matching_negative_alerts':sum(len(r['matching_keys']) for r in selected if r['batch']==b and r['label']!='vulnerable'),'supported_qualified_negatives':sum(r['supported_qualified_negative'] for r in selected if r['batch']==b)} for b in ('first','repeat')}
    passed = all(v['vulnerable_hits']==1 and v['matching_negative_alerts']==0 and v['supported_qualified_negatives']==2 for v in batches.values())
    cases.append({'case_id':group,'batches':batches,'completed':6,'ordered_report_pairs_equal':3,'actual_named_sink_supported':True,'fixed_guard_qualification_established':group!='lightning-discover-linklocal','narrow_repository_gate_passed':passed,'full_runtime_safety_established':False,'timings_seconds':[r['timing']['elapsed_seconds'] for r in selected]})
assert sum(c['narrow_repository_gate_passed'] for c in cases)==2
write('assessment.json', {'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':validation['scanner'],'proposal_sha256':sha(PREP/'evaluation-proposal.json'),'approval_sha256':sha(PREP/'evaluation-authorization.json'),'rubric_sha256':sha(PREP/'scoring-rubric.json'),'validation_sha256':sha(DEST/'validation.json'),'source_assessment_complete_for_completed18':True,'complete_report_difference_assessment_pending':True,'four_repository_sequence_complete':False,'FAF_pending':True,'budget_closed':False,'execution_gate_passed_for_completed18':True,'repository_gates_passed':2,'repository_gates_assessed':3,'repository_gates_required':4,'cases':cases,'rows':rows,'finding_count':260,'diagnostic_count':38388,'surface_count':270,'source_context_count':1970,'entire_ordered_report_pairs_equal':9,'max_whole_seconds':max(r['timing']['elapsed_seconds'] for r in rows),'paid_calls':0,'new_inputs':0,'target_execution':False,'limitation_accepted':False,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Partial assessment of already completed immutable outputs within the one active24-observation experiment; not a new batch, fresh result, full regression or closed budget. All original first-frozen failures remain. Two narrow exposed gates pass with the exact prospective qualifiers; Lightning negative discrimination fails. Earlier181 language observations are outside current authorization and current-source compatibility remains pending.','historical_assessment_erratum':'v44 no-bash parent-mkdir wording incorrectly said the branch is not taken when the parent exists. The overwrite branch does invoke recursive mkdir; no new directory is needed under that prerequisite. Original raw source/report and failed named gates are unchanged.','evidence_sha256':{n:sha(DEST/n) for n in ['inventory.json','source-context-assessment.json','finding-source-assessment.json','diagnostic-source-assessment.json','surface-source-assessment.json','sdk-validation-source.json']}})
print('18 completed reports assessed:2 narrow exposed gates pass,Lightning discrimination fails;FAF and complete differences pending. All260 findings/38388 diagnostics/270 surfaces retained.')
