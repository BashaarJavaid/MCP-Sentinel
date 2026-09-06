# Phase 19 verification

Status: **all implementation verification gates passed; final acceptance pending**.
Branch: `phase19-coverage-reporting`. Package version remains 1.3.0;
native report schema is 1.6.0. Phase 19 is not marked complete.

The implementation records static registrations and actual detector visits,
per-session runtime discovery and sent-call flags, stage review activity, and
bounded evidence shared by console and SARIF. Recognition gaps do not change
the selected analysis's completion or exit semantics. Canonical Finding,
baseline-v2 matching, suppression, model request/response contracts, runtime
proof conditions, and the four-attempt campaign remain unchanged.

## Verification scope

`tests/test_phase19.py` covers paired Python/TypeScript targets, partial and zero
finding recognition, duplicate registrations, configured exclusions and skips,
ignored/baseline files, runtime nested fields, pagination, differing catalogs,
discovery failure, baseline failure, unsent attacks, deadlines, and unsupported
field space. It also covers each stage activity state, accepted abstentions,
bounded excerpts, helper references, merged proof, and model disagreement.
Existing tests additionally exercise actual synthetic live/cache/replay paths,
empty-static/dynamic-reviewed orchestration, caps, suppressions, historical
1.3–1.6 baselines, stable fingerprints, JSON/SARIF validation, and offline tiers.

The existing Docker suite adds a multi-tool control with unprobed nested fields
and verifies sent-call/discovery records on completed controls. Targets run only
under Sentinel's existing isolation contract. No paid model calls are authorized
or used. Fake transports are synthetic evidence; packaged review captures are
recorded replay, not fresh model measurements.

## Evidence

The final implementation source is
`1fb17bb9d0f5e33d6f6fd7968c1bfd114853febc`. Evidence-only commits following it
do not change scanner behavior. The draft is
[PR #19](https://github.com/BashaarJavaid/MCP-Sentinel/pull/19).
Local and hosted results are retained in `artifacts/phase19/`.

| Check | Result | Retained evidence |
| --- | --- | --- |
| Final source `make check` | 606 passed, 33 Docker skips; 86.65% branch coverage; lint, formatting, types, schemas, audit, notices, strict docs passed | `make-check-final-source.log` |
| Deadline guard and CLI regressions | 65 passed | `final-corrections-tests.log` |
| Generated schemas and historical judge artifacts | Passed, exit 0 | `schema-check.log`, `historical-artifacts-check.log` |
| Real Docker regression controls | 35 passed | `docker-controls-final-source.log` |
| Wheel/sdist builds and pip, pipx, uv installation smokes | Passed, exit 0 | `build-final.log`, `distribution-final-source.log`, `distribution-hashes-final.json` |
| Installed-wheel Docker replay and report validation | Passed: 11 findings, 8 discovery snapshots, 4 sent attacks | `installed-wheel-final/`, `installed-wheel-final.log`, `installed-wheel-validation-final.json` |
| Paired Python/TypeScript and partial recognition reports | Passed, JSON and SARIF valid | `representative-results.json`, `representative-validation.log`, matching `.console.txt`, `.json`, `.sarif` files |
| Hosted quality/distribution, Docker replay, rules-only isolation | All 27 jobs passed | `hosted-source-ci.json`, `hosted-source-ci.log` |
| Hosted documentation | Passed | `hosted-source-docs.json` |

The [final-source CI run](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34048020653)
checks Linux, macOS, and Windows on Python 3.10–3.13, builds canonical
distributions, installs those distributions across the same matrix, and runs
installed-wheel Docker replay and Linux network-isolated rules-only scans.
The [documentation run](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34048020623)
checks the strict documentation build. Branch verification does not deploy the
documentation site.

The hosted checkout was GitHub's PR merge commit
`f3897d4d4662a44014adc19b67ce2359cad3fb17`, combining final source
`1fb17bb9d0f5e33d6f6fd7968c1bfd114853febc` with base
`6178e63a9ce47380ef2cc2052331cbc0f5c475c8`. The retained checkout logs record
those identities. `verification-results.json` identifies the commands and
source for each final local check; `evidence-sha256.json` hashes the retained
evidence files. Subsequent evidence-only updates are outside packaged inputs.

The installed-wheel run reused seven cached static judgments and four recorded
dynamic judgments. Its aggregate mode is correctly `mixed`; neither stage made
a fresh model call. The multi-tool Docker control records two observed tools,
an attack on `process.value`, and the unprobed tool's nested fields. The partial
recognition input is retained as `partial-recognition-input.json` and is never
executed. Its unresolved imported implementation remains visible even with zero
findings. All representative reports validate against native 1.6.0 and SARIF
2.1.0 schemas.

## Earlier verification and resolved failures

`820ddeb5de86826ed614252ef7475a79a84c5e50` passed the first full local gate
(603 tests, 33 Docker skips, 87% displayed coverage) and the complete
[initial hosted CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34046284322).
`1ac8a85b6a7189415801abefc0ea97470b66a0c6` passed the next full local gate
(605 tests, 33 Docker skips, 85.73% coverage), 35 Docker controls, distribution
smokes, and installed-wheel replay. Those logs remain separate from the final
source evidence. The final source additionally guards inventory completion
against an expired static deadline and corrects verbose-help wording.

An initial sandboxed test run passed 567 tests; four loopback HTTP emulator
tests required execution outside the filesystem sandbox and then passed.
Initial Docker runs stalled before target startup because the local Docker
Desktop daemon could not attach to created containers. Restarting the current
Docker Desktop installation restored the control. The next run exposed test
log serialization of typed discovery objects; commit `1ee5e07` fixed only that
test logging. Failed Docker attempts remain in `docker-controls-initial.log`
and `docker-controls-log-serialization.log`; they are not counted as passes.
The first distribution smoke needed the same pinned `pipx==1.16.0` runner tool
used by CI; the completed rerun is retained separately. No scanner dependency
was added.

These are implementation checks, not evidence of broad detection accuracy or
maintainer value. Phase 20 benchmarking, package-version changes, merging,
release, publication, and expanded detector/probe campaigns remain outside this
delivery. The draft PR awaits one final user acceptance after verification.
