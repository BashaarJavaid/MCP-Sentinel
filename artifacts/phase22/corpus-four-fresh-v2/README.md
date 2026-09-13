# Four-repository corpus v2

## Current v48 allocation candidate: regression approval pending

The approved single source-only merge optimization is engineering-verified at
**`6e4fd67`**. It avoids constructing unused record fallbacks; **10,944 synthetic
comparisons** preserve environment, complete flow state and inputs. Allocation
checks preserve needed fallbacks. Full local and all 12 hosted suites pass
**2,384 tests / 36 skips**; local combined statement/branch coverage is
**89.98%**, branch-only **85.85%**. All **29 normal CI jobs** and docs
pass in **34743452798 / 34743452818**, with exact candidate checkout/package
bindings. Six production requests checked-replay unchanged with zero model calls;
Git runtime/image remains compatible. No new corpus observation or profile ran.

The new **205-observation exposed regression** is prepared, **unapproved and
unexecuted**: 24 four-repository, 94 TypeScript and 87 Python, on 110 inputs and
95 ordered repeat pairs. Bounds are 120-second target, 300-second native/whole
maximum, 15-second cleanup and one 1,150-minute serial local sequence; no retry,
profile, comparator, new repository, target execution or paid call. Exact scope
is in `v48-merge-allocation/evaluation-proposal.json` and `launcher-binding.json`.
The earlier shared source recovery still lacks completed corpus validation, so
both prior-language schedules remain necessary. Synthetic allocation reduction
establishes no native speedup or 300-second completion. The old native timeout
and 204 unstarted closed, sampled timeout and all original fresh failures remain
unchanged. No closed budget is reused and no failed gate is waived.

The audit retains **all 247 requirements**, including 89 original and 158 added
rows. Corrected corpus gates, six historical closure decisions and explicit human
technical acceptance remain unresolved. **Phase 22 remains incomplete.** Git
campaigns stay 312/1,040 incomplete with 728 deferred; paid benchmark/pilots stay
deferred, Phase 21 incomplete and Phase 24/15 unchanged. No merge, ready-state
change, release, outreach or Phase 23 is authorized.

## Historical v47 sampled timeout: source-only proposal pending

The separately approved single FAF worker profile at frozen `17b4784` timed out
at 300 seconds with verified cleanup: **one incomplete sampled input, four partial
snapshots / 86,659 samples, no report, zero budget remaining**. The [review packet](../integration/v47-faf-sampling/summary.md)
attributes 58.36–59.06% of worker samples inclusively to TypeScript branch merging
and 25.78–26.41% as leaves in its fallback Value constructor. These overlapping
sample shares are not promised savings; unused allocations remain uncounted.
One narrow **source-only fallback-allocation optimization** is proposed, unapproved
and unstarted, with zero new corpus/profile/paid budget. The prior regression's
one incomplete attempt and 204 closed unstarted observations remain unchanged.
Corrected detection/compatibility gates remain unresolved. Engineering retains
tested `17b4784`: 2,380 tests / 36 skips locally and in all 12 hosted suites,
29 normal CI jobs and docs passed; combined coverage 89.98%, branch-only 85.85%.
All 239 audit rows and original fresh failures remain. **Phase 22 is incomplete**;
no limitation or human technical acceptance is inferred. Git remains 312/1,040
incomplete, paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15
unchanged. No optimization, retry, paid call, target execution, merge, ready-state,
release, outreach or Phase 23 occurred or is newly authorized.


## Historical v46 regression timeout: budget closed

The approved 205-observation sequence at frozen `17b4784` stopped on its first
FAF vulnerable input at the 300-second whole-input maximum: **one incomplete,
zero completed reports, 204 unstarted closed, zero remaining**. Cleanup passed.
No finding, guard, negative-path or ordered-repeat result is available; corrected
four-repository and prior-language compatibility gates remain unestablished.
The [review packet](../integration/v46-four-source-regression/summary.md) retains the failure and an **unapproved single
300-second CPU-sampling diagnostic** on the same FAF input. No retry, profile,
target execution or paid call has occurred. All original fresh failures and
historical source-bound passes remain unchanged. Engineering retains `17b4784`:
2,380 tests / 36 skips locally and in all 12 hosted suites, 29 normal CI jobs and
docs passed; combined coverage 89.98%, branch-only 85.85%. The audit retains all
233 requirements. **Phase 22 remains incomplete**; no failure/limitation or human
technical acceptance is inferred. Git stays 312/1,040 incomplete; paid benchmark
and pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged. No merge,
ready-state change, release, outreach or Phase 23.


Current source-only packet: exact24-observation evaluation proposal is unapproved; zero observations.

See the [preparation summary](../integration/v43-four-fresh-preparation/summary.md), complete per-repository manifests, source reviews and checkpoint. All original source archives and historical manifests are preserved.
