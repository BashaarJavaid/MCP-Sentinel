"""Index retained report changes and four-source occurrences for source assessment only."""
import ast
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
ASSETS = OUT.parent/'v62-shared-tool-discovery'
read = lambda p: json.loads(p.read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
p = read(ASSETS/'evaluation-proposal.json')
v = read(OUT/'validation.json')
assert v['validation_passed'] and v['budget_closed']
fixed = Path(p['frozen_checkout'])
sys.path[:0] = [str(fixed/'src'), str(fixed)]
from scripts.phase20_corpus import validate
from scripts.phase22_corpus import frozen, input_files

manifests, cache, contexts = {}, {}, {}
rows, findings, diagnostics, surfaces, other, unlocated = [], [], [], [], [], []
four = {'faf-read-root', 'no-bash-write-prefix', 'lightning-discover-linklocal', 'engram-export-home'}
def files_for(group, input_id):
    key = (group, input_id)
    if key not in cache:
        g = p['groups'][group]
        if group not in manifests:
            manifests[group] = validate(path=fixed/g['manifest'], root=fixed) if group.endswith('historical') else frozen(root=fixed, approval_path=fixed/g['source_freeze_approval'])
        m = manifests[group]
        item = next(i for i in m.inputs if i.id == input_id)
        snapshot = next(s for s in m.snapshots if s.revision == item.snapshot)
        files = input_files(item, snapshot, fixed)
        prefix = '' if item.scan_root == '.' else item.scan_root+'/'
        cache[key] = {n[len(prefix):]: b for n, b in files.items() if n.startswith(prefix)}
    return cache[key]
def context(files, path, line=None, binding=None):
    if path not in files:
        return None
    data = files[path]
    lines = data.decode().splitlines()
    key = sha(json.dumps([path, sha(data), line, binding]).encode())
    if key in contexts:
        return key
    c = {'path': path, 'source_sha256': sha(data)}
    if line is not None:
        if not 0 < line <= len(lines):
            return None
        c.update(line=line, statement=lines[line-1], excerpt=[f'{n+1}: {lines[n]}' for n in range(max(0, line-5), min(len(lines), line+5))])
        if path.endswith('.py'):
            try:
                tree = ast.parse(data)
            except SyntaxError:
                c['scope_parse_status'] = 'unsupported; raw source remains bound'
            else:
                scopes = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.lineno <= line <= n.end_lineno]
                node = min(scopes, key=lambda n: n.end_lineno-n.lineno) if scopes else None
                c['scope'] = node.name if node else 'module'
                if node:
                    c['enclosing_source'] = '\n'.join(f'{n}: {lines[n-1]}' for n in range(node.lineno, node.end_lineno+1))
    else:
        base = binding.split('.')[0]
        markers = {'tools/list metadata': 'ListToolsRequestSchema', 'dynamic tool description': 'description', 'launch state': 'mcp.run'}
        base = markers.get(binding, base)
        occurrence = [n+1 for n, text in enumerate(lines) if re.search(r'(?<![\w$])'+re.escape(base)+r'(?![\w$])', text)]
        if not occurrence:
            return None
        c.update(binding=binding, base_identifier=base, occurrence_lines=occurrence,
                 excerpt=[f'{n+1}: {lines[n]}' for n in range(max(0, occurrence[0]-3), min(len(lines), occurrence[0]+3))])
    contexts[key] = c
    return key

def diagnostic_context(files, d):
    message = d['message']
    located = re.fullmatch(r'(SENT-\d+) at (.+):(\d+): (.+)', message)
    binding = re.fullmatch(r"(.+): cannot resolve TypeScript binding '(.+)'", message)
    launch = re.fullmatch(r'(.+): unresolved launch state; analyzing the unconfigured handler as well', message)
    if located:
        return context(files, located[2], int(located[3]))
    if binding:
        return context(files, binding[1], binding=binding[2])
    if launch:
        return context(files, launch[1], binding='launch state')
    return None

def clean(value):
    if isinstance(value, dict):
        return {k: clean(x) for k, x in value.items() if k not in p['volatile_exclusions']}
    if isinstance(value, list):
        return [clean(x) for x in value]
    return value

def occurrences(before, after, all_current):
    # Counter matching preserves duplicate multiplicity; retained indices preserve ordering.
    encode = lambda x: json.dumps(clean(x), sort_keys=True)
    remaining_old = Counter(map(encode, before))
    for index, value in enumerate(after):
        key = encode(value)
        same = remaining_old[key] > 0
        if same:
            remaining_old[key] -= 1
        if all_current or not same:
            yield 'current' if all_current else 'added', index, value
    remaining_new = Counter(map(encode, after))
    for index, value in enumerate(before):
        key = encode(value)
        if remaining_new[key]:
            remaining_new[key] -= 1
        else:
            yield 'removed', index, value

for attempt in v['attempts']:
    if not attempt['report_present']:
        continue
    group, input_id = attempt['group'], attempt['input_id']
    item = p['groups'][group]['inputs'][input_id]
    path = OUT/'raw'/attempt['directory']/input_id/'report.json'
    report, reference = read(path), read(ROOT/item['reference_report'])
    common = {k: attempt[k] for k in ['group', 'batch', 'input_id', 'state', 'report_sha256', 'reference_sha256']}
    common.update(reference_report=item['reference_report'], snapshot=item['input']['snapshot'], tree_sha256=item['input']['tree_sha256'], actual_language=p['groups'][group]['actual_language'])
    all_current = group in four
    files = files_for(group, input_id) if all_current or not attempt['entire_reference_equal'] else None
    for direction, index, finding in occurrences(reference['findings'], report['findings'], all_current):
        loc = finding['location']
        ctx = context(files, loc['path'], loc['range']['start_line'])
        flow = [context(files, x['path'], x['range']['start_line']) for x in finding['evidence'].get('flow_locations', []) if x.get('kind') == 'file']
        row = {**common, 'direction': direction, 'index': index, 'finding': finding, 'context': ctx, 'flow_contexts': flow}
        findings.append(row)
        if ctx is None or None in flow:
            unlocated.append({'kind': 'finding', 'row_index': len(findings)-1, **common})
    for pointer, before, after in [('/warnings', reference['warnings'], report['warnings']), ('/static_analysis/coverage/unresolved_flows', reference['static_analysis']['coverage']['unresolved_flows'], report['static_analysis']['coverage']['unresolved_flows'])]:
        for direction, index, diagnostic in occurrences(before, after, all_current):
            ctx = diagnostic_context(files, diagnostic)
            diagnostics.append({**common, 'pointer': pointer, 'direction': direction, 'index': index, 'diagnostic': diagnostic, 'context': ctx})
            if ctx is None:
                unlocated.append({'kind': 'diagnostic', 'row_index': len(diagnostics)-1, **common})
    for direction, index, surface in occurrences(reference['static_analysis']['coverage']['surfaces'], report['static_analysis']['coverage']['surfaces'], all_current):
        loc = surface['location']
        ctx = context(files, loc['path'], loc['range']['start_line'])
        surfaces.append({**common, 'direction': direction, 'index': index, 'surface': surface, 'context': ctx})
        if ctx is None:
            unlocated.append({'kind': 'surface', 'row_index': len(surfaces)-1, **common})
    for delta in attempt['reference_deltas']:
        other.append({**common, **delta})
    rows.append({**common, 'label': item['input']['label'], 'entire_reference_equal': attempt['entire_reference_equal'], 'all_current_occurrences_indexed': all_current, 'findings': len(report['findings']), 'warnings': len(report['warnings']), 'unresolved_flows': len(report['static_analysis']['coverage']['unresolved_flows']), 'surfaces': len(report['static_analysis']['coverage']['surfaces']), 'source_assessment_complete': False})
for name, value in [('inventory.json', {'rows': rows, 'qualification': 'Inventory only. Every current four-source occurrence and each changed earlier occurrence requires source assessment. Array deltas retain original ordering; unchanged references still require explicit prior-assessment bindings.'}), ('source-contexts.json', contexts), ('finding-inventory.json', findings), ('diagnostic-inventory.json', diagnostics), ('surface-inventory.json', surfaces), ('report-deltas.json', other), ('unlocated-inventory.json', unlocated)]:
    with (OUT/name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
print('Indexed', len(rows), 'reports,', len(contexts), 'source contexts;', len(unlocated), 'unlocated items remain for review. No new scans.')
