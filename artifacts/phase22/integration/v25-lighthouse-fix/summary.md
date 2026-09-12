# Phase 22 corrected Lighthouse checkpoint

The requested Lighthouse source correction is implemented at **`6db3858`**.
It follows actual module class construction and saved SDK setter forwarding,
recognizes Lighthouse URL sinks, and retains narrow initial link-local IPv4
rejection evidence. Replaced/escaped methods, wrong receivers, callback changes,
unknown array aliases and ineffective guards remain conservative. A qualified
finding still leaves other destinations, DNS, redirects and IPv6 unresolved.

The initial `b830027` candidate passed 2,229 tests locally and in all 12 suites,
but a later synthetic import-alias counterexample found another binding gap.
Canonical SDK identity invalidation corrects it at `6db3858`. That counterexample,
the original successful engineering results and both unexecuted proposals are
preserved; no corpus observation was consumed during this correction.

Verification passes **2,230 tests / 36 skips** locally and in all 12 hosted
Linux/macOS/Windows × Python 3.10–3.13 suites. Local branch coverage is **89.76%**;
hosted coverage is **89.75–89.78%**. All **29 normal CI jobs**
and documentation pass at workflow **`51fd2cb`**
([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34615835606),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34615835565)).
Wheel/sdist sources are byte-verified. Six actual production requests regenerate
and checked-replay with unchanged fingerprints/request hashes and **zero paid
calls**. The owned Docker demo completes 20/20 attempts with 14 findings and
cleanup; the unchanged approved Git runtime retains 13 incomplete campaigns,
312/1,040 attempts. This demo is separate from corpus evaluation.

The exact **unapproved** proposal is
`artifacts/phase22/integration/v25-lighthouse-fix/evaluation-proposal-final.json`
(SHA-256 `26ac27d01740faa0ac664a13963ef7a4d91f199818bba29d9a257d98f1f4206a`). It requests the same five exposed Lighthouse inputs twice:
**ten native observations**, one standard Linux job capped at **60 minutes**,
120-second target / 300-second whole-input maximum, 15-second cleanup cap,
**zero retries, profiles, comparator runs, target execution or paid calls**.
Stop at the first execution, named-condition or ordered-repeat failure and close
all unstarted observations. All four optional corpus jobs are disabled in normal
CI. No corrected-source corpus observation has occurred.

The first fresh result stays **0/2 vulnerable hits** per native batch and in
Semgrep at frozen **`1f3f72f`**: all 15 observations completed, all five ordered
native repeats equal, zero findings, unknown tool coverage and 232 source-assessed
diagnostics. Its budget is closed. The user chose correction rather than accepting
the limitation-only proposal. Any corrected Lighthouse result is an exposed
regression, not fresh generalization or independent human review.

The **89-row audit is 82 passed, two user-deferred and five unresolved**;
66 added rows are 61 passed and five unresolved, including three closed historical
failures. Current-source compatibility of the three earlier exposed SSRF families
and whole timing/condition gates remains to be established after the TypeScript
changes. Their passes retain measured `2ac39aa` / `1f3f72f`; no pooled or new
whole-batch claim, silent waiver or reopened budget. R66/R88 and explicit final
human technical acceptance remain open. **Phase 22 is incomplete.** Paid benchmark
and pilots remain deferred, Phase 21 incomplete, Phase 24/15 unchanged. No merge,
release, ready-state, outreach or Phase 23 work. “v25” names evidence only.

The user’s correction receipt, synthetic failure history, source snapshot binding,
current local checks, runtime/replay compatibility and source-only prior-gate scope
review are retained in this directory. The complete hosted artifacts/logs and
package source audit are in `../v25-final-quality/` and `../v25-final-quality-audit/`.
All earlier evidence seals remain unchanged; the new seal includes the correction
and its verification. Final documentation/delivery bindings are supplemental.

The next decision approves only the exact ten-observation exposed regression.
It does not approve additional historical/fresh experiments or final technical
acceptance. Further current-source gates and the first fresh miss must receive
an explicit disposition before Phase 22 acceptance is requested.
