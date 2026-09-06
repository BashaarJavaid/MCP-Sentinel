# Phase 19 verification

Status: **implementation under verification; final acceptance pending**.
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

Local and hosted results, source commit identifiers, representative reports,
and distribution checks are retained in `artifacts/phase19/`. Final results are
recorded after the gates finish. An initial sandboxed test run passed 567 tests;
four loopback HTTP emulator tests required execution outside the filesystem
sandbox and then passed. Docker startup diagnostics are retained separately from
the final regression gate; unsuccessful attempts are not counted as passed.

Required acceptance checks remain: `make check`, generated schemas, historical
artifacts, real Docker controls, wheel/sdist installation, installed-wheel
replay/report validation, hosted Linux/macOS/Windows Python 3.10–3.13 quality and
distribution, Docker replay, rules-only isolation, and documentation.

These are implementation checks, not evidence of broad detection accuracy or
maintainer value. Phase 20 benchmarking, package-version changes, merging,
release, publication, and expanded detector/probe campaigns remain outside this
delivery. The draft PR awaits one final user acceptance after verification.
