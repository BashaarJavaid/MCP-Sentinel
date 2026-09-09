# Approved replacement SSRF holdout

The user approved the recommended freeze. The additive `authorization.json`
binds this exact manifest, five input IDs and only `rules`/`semgrep` treatments.
The original preparation packet remains unchanged as a historical proposal.
Evaluation is complete and recorded in `results-summary.json`; no additional
paid calls are approved. The detector implementation remains frozen at the revision below.

This proposal replaces the five exposed auth-fetch inputs in a separately
versioned 50-input manifest. The other 45 input records are exactly
unchanged as JSON values. The original approved manifest, labels, sources,
measurements and exposure record remain unchanged. This does not create a new
fresh 25-input holdout: only these five replacement inputs would be newly evaluated.

- Manifest: `manifest.json`
- Manifest SHA-256: `159278d40a7d6fe2faa1c240a26f51009b37cdca30c862d5e9df1d66a6fed0da`
- Review and identities: `packet.json`, `review/condition-review.json`
- Repository: `Aas-ee/open-webSearch`
- Vulnerable: 2.1.6, `e29b2357a11d25c9288e1bb006728ddde4d4b6b1`
- Fixed: 2.1.7, `739aef2bf7f2c822236bcce0f404c43b57f42503`

The named condition is rejection of a caller-supplied IPv4-mapped IPv6 loopback
URL before the initial `fetchWebContent` HTTP request. The ordinary no-argument
server launch selects the full in-process runtime; injected service replacements
and operator proxies are excluded prerequisites. DNS, redirects, browser/cookie
fallback and successful response retrieval are outside this condition. The safe
control checks classification of an ordinary public IPv4 literal; no public
service is contacted. The upstream fixed source includes broader defenses,
which are retained without claiming they have all been independently validated.

Both complete upstream archives and Apache-2.0 licenses are retained, with no
projection or omitted source files. Each paired mutation renames the actual
hostname predicate and every local TypeScript reference; reversing that rename
restores the exact original bytes. Existing corpus validation passes for hashes,
source/evidence ranges, mutation lineage, population and repository split.

The implementation agent curated the source after scanner implementation was
fixed at `6e6833198989e06bd8c369abab0ee1a9d3db1ef8`. Advisory excerpts and repository
source were read; this is explicitly not an unseen-source claim. No detector
change followed that exposure, and no scanner, comparator, model or target
evaluation has run against these inputs. Upstream tests were read as corroborating
source expectations and were not executed. Independent human acceptance remains
separate. An independent agent review can be added if authorized.

Explicit approval of this exact manifest was recorded before evaluation, under
the handoff's replacement-holdout freeze process and the project's corpus-freeze
checkpoint. Approval permits source-only deterministic and pinned comparator
evaluation of the five replacements. It does not approve paid calls, target
execution, label changes, new detector tuning or a claim that Phase 22 is complete.

Reproduce validation from the integration checkout without executing target code:

```sh
PYTHONPATH=src:. /Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python -c "from pathlib import Path; from scripts.phase22_corpus import validate; m = validate(Path('artifacts/phase22/corpus-replacement-v1/manifest.json')); print(len(m.inputs))"
```

The 28 expanded inspection copies under `review-source/` remain local.
`review-source-inventory.json` verifies each against the corresponding complete
upstream archive, which is the canonical reproducible source.

## Measured results

At committed runner revision `052379c`, using detector code unchanged from
`6e68331`, both Sentinel and pinned Semgrep 1.176.0 complete all five inputs.
**Both miss the named vulnerability in both vulnerable variants (0/2 detected).**
Neither reports the named condition on the two fixed variants or safe control.
Sentinel's repeat completes all five with identical stable reports and outcomes.

Sentinel retains 70 authentication warnings outside the named SSRF condition;
Semgrep retains 33 unrelated logging/TLS warnings. Every instance has a source hash,
location, excerpt and separate scope assessment. Their separate risk is unvalidated;
they are not automatically false positives. Each native scan reports 13 recognized
HTTP surfaces and seven unresolved surfaces, including six computed MCP tool names.
Completion therefore does not establish full MCP handler coverage or a defense.

These five correlated replacement cases are reported separately. The original
manifest, 45 unchanged records and original held-out results remain unchanged.
No detector tuning followed curation or this evaluation. No target code or live
model ran. Full reports, raw comparator output, commands, identities, assessments
and repeat evidence are retained in integration batch 30; verify its manifest on
extraction. These measurements do not establish overall precision, competitor
superiority, independent human acceptance or Phase 22 completion.
