"""Retain the first completed FAF report difference with only approved exclusions."""
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
DEST = OUT / 'first-faf-assessment'
OLD = OUT.parent / 'v44-four-fresh-evaluation'
PREP = OUT.parent / 'v69-uncapped-four-repository'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('runner', PREP / 'evaluate.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
excluded = set(read(PREP / 'evaluation-proposal.json')['volatile_exclusions'])
assert len(excluded) == 11
old = read(OLD / 'inventory.json')
current = read(DEST / 'inventory-source-corrected.json')
prior = {(r['input_id'], r['batch'].removeprefix('rules-')): r for r in old['rows']}

def changes(a, b, path=()):
    if a == b:
        return []
    if isinstance(a, dict) and isinstance(b, dict) and a.keys() == b.keys():
        return [d for key in a for d in changes(a[key], b[key], path + (key,))]
    return [{'path': list(path), 'before': a, 'after': b}]

counts = Counter()
rows = []
with gzip.open(DEST / 'complete-report-differences.jsonl.gz', 'xt', encoding='utf-8') as out:
    for row in current['rows']:
        previous = prior[row['input_id'], row['batch']]
        old_path, new_path = ROOT / previous['report'], ROOT / row['report']
        assert sha(old_path) == previous['report_sha256'] and sha(new_path) == row['report_sha256']
        a = runner.supervisor.clean(read(old_path), excluded)
        b = runner.supervisor.clean(read(new_path), excluded)
        delta = changes(a, b)
        reconstructed = json.loads(json.dumps(a))
        for d in delta:
            target = reconstructed
            for key in d['path'][:-1]:
                target = target[key]
            assert d['path'] and target[d['path'][-1]] == d['before']
            target[d['path'][-1]] = d['after']
            counts['/'.join(d['path'])] += 1
        assert reconstructed == b
        binding = {'input_id':row['input_id'],'batch':row['batch'],'old_report':previous['report'],'old_report_sha256':previous['report_sha256'],'current_report':row['report'],'current_report_sha256':row['report_sha256'],'replacement_count':len(delta),'old_finding_count':len(previous['findings']),'current_finding_count':len(row['findings']),'old_diagnostic_count':len(previous['diagnostics']),'current_diagnostic_count':len(row['diagnostics']),'old_surface_count':len(previous['surfaces']),'current_surface_count':len(row['surfaces'])}
        out.write(json.dumps({**binding, 'changes':delta}, separators=(',',':'))+'\n')
        rows.append(binding)
result = {'rows':rows,'completed_report_comparisons':1,'volatile_exclusions':list(read(PREP/'evaluation-proposal.json')['volatile_exclusions']),'changed_paths':dict(counts),'complete_ordered_reconstruction_passed':True,'differences_sha256':sha(DEST/'complete-report-differences.jsonl.gz'),'source_assessment_pending':True,'qualification':'All arrays retain original order and complete before/after contents; no sorting or additional exclusions. Original2e0efb2 failure reports remain source-bound. This comparison attributes no change to a single optimization or the uncapped policy.'}
with (DEST/'report-difference-inventory.json').open('x') as f:
    json.dump(result,f,indent=2)
    f.write('\n')
print(json.dumps({'completed':1,'changed_paths':dict(counts)},indent=2))
