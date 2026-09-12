# Replacement-v6: DDG shared-space URL condition

## Current v34 fixed-request correction checkpoint

The user approved correcting the DDG fixed-path coverage gap before acceptance.
Corrected scanner candidate **`2624578`** follows source-established HTTPX
`build_request` → `send` and retains a narrow initial `100.64.0.0/10` rejection
qualification. Synthetic controls cover guard removal/bypass, URL replacement,
client rebinding and unknown mutation. The old six negative IP flags alone no
longer imply shared-space rejection. Broader destinations, DNS, redirects and
subsequent URL transformations remain unestablished.

The initial `5b5016e` full suite retained one failure, 2,269 passes and 36 skips.
The correction preserves known IP type inspection while treating unknown/replaced
classes conservatively, including direct module-level imported-attribute writes.
All **37 focused controls pass**; the initial failure and correction checks are retained.
Full current-source engineering verification is in progress. Earlier `439c3fe`
quality results describe earlier bytes. No new corpus observation is authorized
or executed: an exact exposed DDG and affected Python compatibility proposal is
being prepared in `artifacts/phase22/integration/v34-fixed-coverage-final/`.
The original `f85a90f` fresh result and its fixed-coverage limitation remain
immutable; the later correction is exposed engineering, not a new fresh result.

**Phase 22 remains incomplete.** The v33 acceptance-ready proposal is superseded
by the requested correction, its verification and separate regression checkpoint.
Git runtime stays **312/1,040 incomplete** under the user's instruction. Paid
benchmark/pilots remain deferred; zero additional paid calls. Final human
technical acceptance and verified closeout remain separate decisions. No merge,
release, ready-state, outreach or Phase 23 is authorized.


Approved first-frozen evaluation completed: 10 native + 5 Semgrep, zero paid calls or target execution. Native2/2 hits per batch and0/3matching negative alerts;5ordered repeats. Fixed HTTP send remains unresolved, so no recognized-fix claim. See `../integration/v33-fresh-v6/assessment.json` and `summary.md` for complete source assessments and the proposed limitation.

The complete upstream AGPL v3 source archives are retained verbatim with their
licenses and notices. The two mutation overlays rename one local helper and its
two calls; each changed file carries a dated modification/license notice. These
are evaluation source assets, not code incorporated into the Sentinel package.

Upstream repository: https://github.com/isyuricunha/mcp-ddg-research
Direct vulnerable parent: `97d3c6c511946be4dee99de0bfce82dbf3eb8687`.
Fixed child: `cf0a415758ce156f42db1dd48ec09663d0a21fd2`.
Both package versions say 0.5.1; labels bind exact source, not a patched release.

See `review/condition-review.json` for the complete flow, dependency prerequisites,
literal-address checks and unrelated upstream changes. See `provenance/novelty.json`
for the seven-manifest/96-tree exclusion check, `checkpoint-f85a90f.json` for the
source freeze, and `../integration/v32-fresh-v6/evaluation-proposal.json` for the
exact separately approvable scope and prospective scoring rubric.

One repository and one narrow vulnerability, with correlated variants. No target
imports, tests, builds, dependency installation, DNS or HTTP requests occurred.
Current-source first-frozen candidate detection is demonstrated for this narrow condition. Earlier misses and exposed regressions
are preserved; a fix after observing this source cannot count as fresh success.
