"""Reconcile final owning docs only after completed engineering evidence."""
import json
from pathlib import Path
ROOT=Path.cwd();BASE=ROOT/'artifacts/phase22/integration';OUT=BASE/'v29-loopback-fix'
quality=json.loads((BASE/'v29-quality-audit/packet.json').read_text())
assert len(quality['quality'])==12 and all(q['passed']==2242 and q['skipped']==36 for q in quality['quality'])
assert json.loads((BASE/'v29-full-suite.json').read_text())['exit_code']==0
coverage=json.loads((BASE/'v29-full-suite-coverage.json').read_text())['totals']['percent_covered']
hosted=[q['branch_coverage_percent'] for q in quality['quality']]
common=(OUT/'preparation-summary.md').read_text().split('\n\n',1)[1]
common=common.replace('All **518 affected tests pass**. Full engineering verification is in progress.',f'''All **518 affected tests pass**. Full local and all 12 hosted suites pass
**2,242 tests / 36 skips**, with **{coverage:.2f}%** local branch coverage and
**{min(hosted):.2f}–{max(hosted):.2f}%** hosted coverage. All **29 normal jobs** and documentation
pass at workflow **`439c3fe`**
([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34642059839),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34642059977)).
Wheel/sdist source members match actual Git blobs. Ruff/format/strict mypy,
lock/schema/notices/offline artifact checks pass. Six production requests regenerate
and checked-replay with unchanged fingerprints/request hashes and zero paid calls.
The owned Docker demo completes 20/20 attempts with 14 findings and cleanup.
Git runtime/image bindings remain unchanged; its campaigns remain incomplete.''')
common=common.replace('**Phase 22 remains incomplete**', '''The **89 original rows remain 82 passed, two user-deferred and five unresolved**.
The **78 added rows are 71 passed and seven unresolved**, including five closed
historical failed gates. No stopped budget is reopened. The original held-out result
remains 10 completed, 10 unsupported and five incomplete, with zero hits among
four completed vulnerable inputs out of ten vulnerable inputs total.

**Phase 22 remains incomplete**''')
names=['AGENTS.md','ROADMAP.md','docs/phase22-technical.md','docs/phase22-implementation-status.md','docs/phase22-ssrf-follow-up.md','docs/phase22-timeout-policy.md','docs/phase22-corpus-review.md','artifacts/phase22/integration/README.md','artifacts/phase22/integration/requirements.md','artifacts/phase22/integration/progress.md']
for name in names:
 p=ROOT/name;s=p.read_text();level='###' if name=='ROADMAP.md' else '##'
 start=s.index(level+' Current loopback qualification correction under verification\n');end=s.index(level+' Historical v27 constructor-scope checkpoint\n',start)
 s=s[:start]+level+' Current loopback qualification correction and regression checkpoint\n\n'+common+'\n'+s[end:]
 if name=='artifacts/phase22/integration/README.md':
  s=s.replace('batches 1–55','batches 1–56',1)
  marker=level+' Current loopback qualification correction and regression checkpoint\n\n'
  s=s.replace(marker,marker+'Review the [current summary](v29-loopback-fix/summary.md), [89 + 78 row audit](v29-loopback-fix/audit.json), [stopped regression](v28-lighthouse-regression/assessment.json) and [exact unapproved proposal](v29-loopback-fix/evaluation-proposal.json). Restore seal 56 after seals 1–55 using the existing numeric-order procedure and verify every archive/member hash.\n\n',1)
 p.write_text(s)
p=ROOT/'ARCHITECTURE.md';s=p.read_text().replace('Full engineering verification is in progress;\nanother corpus evaluation is unapproved.', 'Engineering verification passes at `439c3fe`;\nanother corpus evaluation is unapproved.');p.write_text(s)
(OUT/'summary.md').write_text('# Phase 22 loopback qualification correction checkpoint\n\n'+common+'\nAll stopped observations, findings/diagnostics and source deltas, source corrections and verification are retained in seals1–56. Final documentation/delivery bindings are supplemental.\n')
(OUT/'pr-body.md').write_text('Phase 22 integrates bounded security source analysis and ordered runtime campaigns. Technical acceptance remains open.\n\n'+common+'\nReview `artifacts/phase22/integration/v29-loopback-fix/summary.md`, its complete audit and exact unapproved proposal. Evidence seals1–56 preserve all earlier failures and closed budgets at actual measured sources.\n')
print('Final documentation and draft description prepared from completed evidence.')
