# Replacement-v6: DDG shared-space URL condition

## Current v37 diagnostic and caller-route correction checkpoint

The approved **single DDG diagnostic passes** at frozen **`a50e9b7`**:
**3.967 seconds native / 8.369 seconds whole input**, identical entire ordered
report after the established 11 volatile exclusions, valid JSON/SARIF, complete
trace and verified cleanup. All **1,066 events** were retained, with no dropped
events and all hooks restored. Its **one-observation budget is closed**.

The trace establishes that the direct `web_fetch` caller reaches the actual send
with its initial CGNAT guard recognized. A separate search-derived caller reaches
the same send without that qualification. Whole-location deduplication drops the
recognized direct-route qualification. The broader search-derived uncertainty
remains visible; the trace does not establish complete SSRF protection.

The approved source correction is frozen at **`8c62567`**. It preserves narrow
guard qualifications by analyzed caller route within **one canonical finding per
sink**. Conflicting guarded/unguarded visits to the same route cancel that route's
qualification. Other caller routes, later transformations, DNS, redirects and
broader destination protection remain unresolved. Python scheme plus six-flag
address guards now retain the existing narrow private-literal qualification;
they do not become CGNAT guards or universal SSRF suppression.

Both new reproductions failed before correction. The affected suite passes
**436 tests**. Full local and all **12 hosted quality suites pass 2,283 tests /
36 skips**; local branch coverage is **89.91%**. All **29 normal CI jobs**
and docs pass at actual `8c62567`; package members match Git blobs and all actual
CI checkout trees equal that source. Six exact production requests regenerate and
replay with **zero paid calls**. The abbreviated-revision replay check failure
and corrected runtime receipt are preserved. Existing Git runtime components and
image are unchanged; its **312/1,040 attempts remain incomplete**, as requested.

**No corrected-scanner corpus observation has occurred.** The next exact
**unapproved** proposal is
`artifacts/phase22/integration/v37-ddg-trace/evaluation-proposal.json`:
**87 native observations** at `8c62567` (five DDG inputs twice, 15 Python development
inputs once, 31 Python historical inputs twice), one local serial sequence,
120-second target, **300-second native/whole-input maximum**, 15-second cleanup,
**480-minute sequence maximum**, zero retries, profiles, comparators, target
execution or paid calls. The original rubric, inputs, conditions and **36 entire
ordered repeats** remain mandatory; qualification must cover the exact initial
caller route, never an uncertain sibling. Execution/identity/time/schema/cleanup/
repeat failure closes all unstarted observations. Detection changes require
individual source assessment after collection and confer no repair/retry authority.

The previous **v35 87-observation regression still fails** DDG guard coverage and
Meta compatibility at `a50e9b7`; its 79 target / eight extended completions,
241.846285-second maximum, 36 ordered repeats and every source assessment remain.
Original first-frozen DDG detection at `f85a90f` remains two vulnerable hits per
batch and zero matching negative alerts, with its original fixed-path limitation.
All original misses and exposed corrections remain distinct. TypeScript's prior
54-observation compatibility and ten Lighthouse observations retain compatible
source bindings; whole Linux timing remains at `1f3f72f`. No partial batches are
pooled and no new fresh-source, speedup or runtime protection claim is made.

The audit retains **89 original rows: 84 passed, two user-deferred and three
unresolved (R33, R65, R84)**, plus **106 added rows: 98 passed, five historical
proposed limitations and three unresolved**. Corrected DDG/Meta regression and
explicit human technical acceptance remain. **Phase 22 remains incomplete**;
paid benchmark/pilots stay deferred, Phase 21 incomplete and Phase 24/15 unchanged.
No merge, ready-state, release, outreach or Phase 23 is authorized.


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
