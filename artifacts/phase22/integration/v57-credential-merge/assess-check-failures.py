"""Preserve every failed preparation check and its bounded correction."""
import ast
import hashlib
import json
from pathlib import Path

out = Path(__file__).resolve().parent
base = out.parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
failed = {p.stem: read(p) for p in base.glob('v57-*.json') if read(p).get('exit_code', 0) != 0}
expected = {
    'v57-synthetic': ('v57-synthetic-corrected', 'check-bypass-first.py', 'The initial fixture created self-referential record members. The failing case recursed in the preserved correction-only reference before its candidate comparison; earlier comparisons remain retained. Only synthetic leaf-member topology changed. No product correction or new optimization target was introduced.'),
    'v57-lint': ('v57-lint-corrected', None, 'Ruff rejected the 90-character test parameter line. Test-only formatting corrected it before commit; product bytes were unchanged.'),
    'v57-format': ('v57-format-corrected', None, 'Ruff formatting rejected the same test layout. The test-only formatting correction passed.'),
    'v57-synthetic-reports': ('v57-synthetic-reports-corrected', 'check-synthetic-reports-first.py', 'The initial helper lacked the repository import root and stopped with ModuleNotFoundError: tests before source analysis. Adding the existing repository to sys.path corrected only the helper import context.'),
}
assert set(failed) == set(expected), failed.keys()
assert 'RecursionError' in (base/'v57-synthetic.log').read_text()
assert "No module named 'tests'" in (base/'v57-synthetic-reports.log').read_text()
assert 'E501' in (base/'v57-lint.log').read_text()
assert 'Would reformat' in (base/'v57-format.log').read_text()
rows = {}
for name, (corrected, first, assessment) in expected.items():
    assert read(base/(corrected+'.json'))['exit_code'] == 0, corrected
    rows[name] = {'assessment': assessment, 'receipt_sha256': sha(base/(name+'.json')), 'log_sha256': sha(base/(name+'.log')), 'corrected_receipt_sha256': sha(base/(corrected+'.json')), 'corrected_log_sha256': sha(base/(corrected+'.log')), 'original_helper_sha256': sha(out/first) if first else None}
syntax = {}
for path in sorted(out.glob('*.py')):
    ast.parse(path.read_text(), filename=str(path))
    syntax[path.name] = sha(path)
packet = {'failed_checks': rows, 'helper_syntax_validation': syntax, 'editing_tool_note': 'A combined delete/add patch for the unexecuted delivery-binding helper was rejected as duplicate-path syntax before mutation. The helper was then prepared by adapting the existing verified delivery flow; no product or measurement changed.', 'source_only_attempts': 1, 'corpus_observations': 0, 'profiles': 0, 'paid_calls': 0, 'prior_failures': 'All historical singleton equivalence failures, native timeouts, partial profiles and invalid stale-root attempts retain their original source-bound outcomes and closed budgets. This approved prospective contract does not accept them as historical limitations or relabel them as passes.'}
with (out/'check-failure-assessment.json').open('x') as stream:
    json.dump(packet, stream, indent=2)
    stream.write('\n')
print('Retained all four initial preparation failures and their corrected checks.')
