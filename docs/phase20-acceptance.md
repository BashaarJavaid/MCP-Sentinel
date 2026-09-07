# Phase 20 — Accepted independent benchmark

**Complete and accepted on 2026-09-07 (UTC).** The user authorized merge,
documentation publication, and cleanup of the merged task branches. PRs
[#20](https://github.com/BashaarJavaid/MCP-Sentinel/pull/20) and
[#21](https://github.com/BashaarJavaid/MCP-Sentinel/pull/21) are merged into `main`.
Phase 21, maintainer pilot and problem validation, is next.

Acceptance means the baseline is reproducible and its limits are recorded. It
does not establish useful detection accuracy or whole-repository safety. No
detection-accuracy threshold was added to close this phase.

## Results and limits

The frozen corpus contains 45 inputs across ten vulnerability families and five
repositories, with vulnerable/fixed pairs, structural mutations, safe controls,
and repository-level development/held-out splits.

| Treatment | Completed / total | Labeled vulnerable inputs detected / completed |
| --- | ---: | ---: |
| Deterministic static | 32 / 45 | 0 / 14 |
| GPT-reviewed static | 32 / 45 | 0 / 14 |
| Eligible Docker pipeline | 0 / 13 eligible | Unmeasured: startup failures |
| Pinned Semgrep comparator | 33 / 45 | 0 / 14 |

Four Atlassian inputs hit the static timeout and nine fail on Helm template YAML.
The 13 eligible Docker inputs pass Git initialization but fail at incompatible
MCP SDK startup; no legitimate baseline or attack was attempted. Another 32
inputs are outside the approved runtime scope. Unrelated warnings remain
unadjudicated, not automatically false positives. Public historical cases cannot
establish absence of prior model exposure.

All 35 prepared static requests have accepted captures. The final 18 succeeded
without new failures, reusing the earlier 17 captures. Accepted usage cost was
$0.804567; cumulative accounting including four earlier failed-attempt
reservations was $1.211247, within the approved $3.72 ceiling. Runtime produced
zero review requests, so no further paid checkpoint was needed or authorized.

## Verification and evidence

- [All 29 CI jobs passed](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34067265137)
  for evidence commit `f37402e48eb49a4495facabc7033e97ed66edd1b`; its
  [documentation build passed](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34067265126).
- Both full 45-input static repetitions match stable findings, coverage,
  outcomes, and failure reasons. Native JSON 1.6.0 and SARIF 2.1.0 reports are
  retained and validated. All 48 benchmark harness tests passed.
- The [completion report](phase20-completion-v2.md) includes denominators,
  split/language/repository/mutation breakdowns, coverage, timing, usage, and
  reproducible commands. The [original partial report](phase20-verification.md)
  remains available for historical comparison.
- The [acceptance record](https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/artifacts/phase20/acceptance.json)
  binds the user decision, merge, evidence hashes, and publication changes.

Measurement artifacts, captures, approved labels, and scoring are unchanged.
The report bytes referenced by the original verification hash remain available
at the immutable evidence commit. Publication updates change status text and
replace temporary branch links; the numeric tables are unchanged. The merge
preserves the exact scanner revisions used by offline CI reproduction.

Phase 21 will validate maintainer workflows and rank blockers. Phase 22 owns
bounded detection and compatibility improvements informed by this benchmark and
the pilot. Neither a passing engineering check nor this phase's acceptance is a
claim of product usefulness.
