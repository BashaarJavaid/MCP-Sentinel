"""Retain completed checks without converting prior failed measurements to passes."""
import ast
import hashlib
import json
from pathlib import Path
out = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
checks = {p.stem: read(p) for p in out.parent.glob('v59-*.json') if 'exit_code' in read(p)}
failed = {n: r for n, r in checks.items() if r['exit_code'] != 0}
assert not failed, failed
for p in out.glob('*.py'): ast.parse(p.read_text(), filename=str(p))
packet = {'failed_wrapper_checks': failed, 'completed_checks': {n: {'exit_code': r['exit_code'], 'receipt_sha256': sha(out.parent/(n+'.json')), 'log_sha256': sha(out.parent/(n+'.log'))} for n, r in checks.items()}, 'qualification': 'All completed policy/engineering/preparation wrapper checks pass. Synthetic timeout, invalid cleanup and missing-approval controls deliberately reject invalid conditions; they are not target observations. Read-only diff exit 1 denoted expected source changes; an earlier rg exit 2 referenced a nonexistent test filename before correction to the existing tests. No product or measurement failure is omitted.', 'prior_failures': 'Earlier native timeouts, partial/invalid profiles, both singleton failures and original fresh discrimination failures remain source-bound. The longer prospective policy does not accept or relabel them.', 'new_corpus_observations': 0, 'profiles': 0, 'paid_calls': 0}
with (out/'check-failure-assessment.json').open('x') as f: json.dump(packet, f, indent=2); f.write('\n')
print('All completed v59 wrapper checks pass; prior failures remain preserved.')
