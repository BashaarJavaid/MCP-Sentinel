# Phase 22 loopback qualification correction checkpoint

The approved Lighthouse regression at scanner **`4a2359d`**, workflow **`b53581d`**,
run **34641101185**, detects both correlated vulnerable variants, then **fails**
the first fixed-input condition: its finding lacks the required initial link-local
rejection qualifier. All **three observations complete within 120 seconds**
(12.500–14.805 seconds whole input), with valid JSON/SARIF and verified cleanup.
**Seven unstarted observations are closed; zero budget remains.** No complete
five-input batch, control or repeat was observed. All three findings, 261 warnings,
164 unresolved-flow occurrences and six unresolved surfaces are source-assessed.

The minimal correction at **`f85a90f`** preserves the narrow IPv4 link-local fact
on a helper's IPv6 loopback equality return. It adds two shared URL-analysis lines;
broader SSRF candidates remain visible. Six synthetic checks cover loopback and
unsafe literal exceptions, compound range iteration, URL parsing and DNS branches.
All **518 affected tests pass**. Full local and all 12 hosted suites pass
**2,242 tests / 36 skips**, with **89.76%** local branch coverage and
**89.75–89.78%** hosted coverage. All **29 normal jobs** and documentation
pass at workflow **`439c3fe`**
([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34642059839),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34642059977)).
Wheel/sdist source members match actual Git blobs. Ruff/format/strict mypy,
lock/schema/notices/offline artifact checks pass. Six production requests regenerate
and checked-replay with unchanged fingerprints/request hashes and zero paid calls.
The owned Docker demo completes 20/20 attempts with 14 findings and cleanup.
Git runtime/image bindings remain unchanged; its campaigns remain incomplete.
No corpus observation has occurred at this corrected scanner.

The next exact proposal is **unapproved**:
`artifacts/phase22/integration/v29-loopback-fix/evaluation-proposal.json`,
SHA-256 `db93996f070f824b72b9bf2383e82efcde5d674c16e37d339ab7d521b7ace016`.
It retains the same five exposed sources twice: **ten native observations**, one
standard Linux job capped at **60 minutes**, 120-second target / 300-second
whole-input maximum and 15-second cleanup cap. Stop on the first execution,
condition or complete ordered-repeat failure and close the remainder. Zero retries,
profiles, comparators, target executions or paid calls. Normal CI skips this job.

The original fresh `1f3f72f` result remains 15 completed with 0/2 vulnerable hits
per native batch and comparator. The stopped `6db3858` result remains one completed
miss and nine unstarted closed. These later exposed corrections cannot establish
fresh generalization or independent human review. Earlier historical timing and
three exposed-family passes retain their actual `1f3f72f` / `2ac39aa` sources;
current-source compatibility and fresh-result disposition remain unresolved.

The **89 original rows remain 82 passed, two user-deferred and five unresolved**.
The **78 added rows are 71 passed and seven unresolved**, including five closed
historical failed gates. No stopped budget is reopened. The original held-out result
remains 10 completed, 10 unsupported and five incomplete, with zero hits among
four completed vulnerable inputs out of ten vulnerable inputs total.

**Phase 22 remains incomplete**, pending the remaining technical gates and explicit
human technical acceptance. Pilots and the full paid benchmark remain user-deferred;
Git campaigns remain incomplete (312/1,040 attempts), Phase 21 incomplete and
Phase 24/15 unchanged. Zero additional paid calls. No merge, ready-state, release,
outreach or Phase 23. The evidence labels v28/v29 do not change phase numbering.

All stopped observations, findings/diagnostics and source deltas, source corrections and verification are retained in seals1–56. Final documentation/delivery bindings are supplemental.
