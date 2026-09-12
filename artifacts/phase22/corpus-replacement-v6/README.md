# Replacement-v6: DDG shared-space URL condition

## Current v41 source correction and pending exposed regression

The approved focused source correction is implemented and engineering-verified at
**`2e0efb2`**, source SHA-256 **`0eac8832012e213744d752c6c33a0ba6a2e378f6230e273030f5043f00cf6ebb`**.
A single assignment to an initially uninitialized TypeScript module variable was
being discarded as rebinding. That lost the canonical filesystem root before the
checked import return reached the read. Synthetic reproductions failed with both
throwing and terminating startup catches; direct-constant and local-root controls
already passed. The shared analysis now reuses existing branch semantics for this
narrow initialization and recognizes stable, unshadowed Node `process.exit` as
terminal. Later writes, caller-controlled roots, ineffective prefixes, replaced
reads, eval, escaping/rebound process and nonterminating branches stay conservative.

The correction adds **34 synthetic security cases**. An existing SSRF regression
now explicitly requires no reachable tool after unconditional startup termination;
its other 11 effect/placement cases retain their checks. The initial affected run
was **1,172 passed / one failed** on that changed expectation. Initial eval/require
AST controls, catch-parameter shadowing, lint/assertion placement and source-binding
helper failures are preserved with corrections. Initial CI **34712538629** was
superseded and cancelled; its completed documentation and retained artifacts are
not represented as a full pass.

Final local and all **12 hosted suites pass 2,317 tests, with 36 skips**; local
branch coverage is **89.92%**. Final CI
**34712751779** passes all **29 normal jobs**, and documentation **34712751789**
passes. The complete hosted merge tree equals tested `2e0efb2`. Ruff, formatting,
strict mypy, lock, schemas, notices, generated artifacts, wheel/source distribution
bindings and ordinary installed-wheel, Docker replay and isolation checks pass.
Six production request replays used **zero model calls** at product-identical
`12fbdf5`; Git runtime components and the approved image remain byte-bound.
**Git campaigns remain incomplete at 312/1,040**, as the user requested.

**No new corpus observation, comparator, profile, repository or paid call occurred.**
The immutable source is `/private/tmp/mcp-phase22-frozen-2e0efb2`. Complete corpus
source archives, configurations and old source-freeze receipts validate without
execution. These receipts establish provenance; they do not reopen old budgets.
All 87 actual `8c62567` Python regression observations remain source-compatible:
the 51 effective input configurations select Python and its analysis bytes did
not change. The five original DDG manifest records incorrectly say TypeScript;
all ten executed DDG observations used the hash-bound Python configuration. That
metadata error and both fields are now explicit; original bytes/results are retained.

The next **unapproved** proposal is
`artifacts/phase22/integration/v41-path-guard-recovery/evaluation-proposal.json`:
**94 native observations**, one serial local sequence, **47 exposed TypeScript
input records each twice**. The three original memory-keeper inputs run first
(six observations), followed by the 44 prior TypeScript records: three SSRF
families, Lighthouse, ten development and 14 historical inputs. Every input keeps
the **120-second target / 300-second native and whole-input maximum**, with at most
15 seconds cleanup; the sequence ceiling is **520 minutes** (470 nominal input
minutes). There are zero comparators, retries, profiles, target executions, paid
calls or new repositories. Stop on an import-condition failure, incomplete/late
result, identity/schema/cleanup failure or ordered-repeat mismatch and close all
unstarted observations. Other changed findings/coverage require source assessment.
All 47 entire ordered repeats and existing condition/qualifier gates are required.
The actual fixed guard and supported read must be assessed; silence alone is not
proof of support. This is exposed regression, not another fresh-source evaluation.

The original memory-keeper first-frozen result at **`8c62567` remains unchanged**:
**six complete observations**, three entire ordered repeats, **one vulnerable hit
and two matching fixed/control false alerts per batch**. The maximum whole input
was **98.448156 seconds**. The fixed read was supported, but its guard and named
MCP dispatch were not established. Broader export and Git-message candidates and
the upstream test-secret false positive remain visible. A synthetic repair is not
a passing re-evaluation. The repository was absent from eight prior manifests and
100 prior effective trees, but was curated and assessed by the same implementation
agent after freeze; no independent human or training-data novelty claim is made.

Original DDG first-frozen detection, later narrow initial-URL qualification, all
Lighthouse/SSRF original misses and exposed passes remain attached to their actual
sources. The original held-out baseline remains 10 completed, 10 unsupported and
five incomplete, with zero hits among four completed vulnerable inputs out of ten
vulnerable inputs total. The historical whole 45+45 Linux timing/condition passes
and explicitly reused whole 25 development batch retain actual `1f3f72f`; partial
language subsets are never pooled into new whole-batch execution. Original timing
failures, errata, failed experiments and closed budgets remain preserved.

The audit accounts for **all 89 original requirements: 77 passed, two user-deferred,
ten unresolved**. R66/R88 retain the fresh discrimination failure and R84 awaits
explicit human acceptance; seven affected TypeScript condition requirements now
explicitly await verification of the changed source. This does not erase their
historical passes. All **115 added rows** are retained: 108 passed, five historical
closure proposals awaiting decision, and two unresolved evaluation criteria.
**Phase 22 remains incomplete; technical acceptance is not requested.** The exact
regression requires separate approval under the continuation prompt. Paid benchmark
and pilots stay deferred, Phase 21 incomplete and Phase 24/15 unchanged. No merge,
ready-state change, release, outreach or Phase 23 is authorized.


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
