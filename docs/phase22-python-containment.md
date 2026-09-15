# Phase 22 — Python containment increment

This draft implements the Python portion of SENT-012 and extends local source
discovery. Phase 22 technical acceptance remains pending. TypeScript containment,
the remaining compatibility forms and detector families, review-context expansion,
campaign scheduling and schema 1.7.0 still require implementation and verification.
The external pilot gate remains pending independently.

## Implemented behavior

SENT-012 follows caller values into supported filesystem APIs, Git staging and
repository selection. It resolves included Python imports, re-exports, aliases,
explicitly bound methods and helper chains without importing or executing target
code. Discovery includes nested literal and enum-backed dispatchers. Reports
preserve original sink locations, canonical Finding identities, rule selection,
severity calculation, suppression and baseline behavior. Imported registrations
report their registration and handler locations separately.

Containment requires canonical path resolution and an enforced component check
against an operator boundary. Tests cover traversal, absolute paths, colliding
prefixes, lexical checks without symlink resolution, unrelated or discarded
validation, swallowed failures, replaced values, imported guards, bound methods,
collections, conditional uses and finally blocks. The standard library's
permissive `walk_up` mode cannot establish containment. Validation of a transformed
path does not validate its original value.

Python SENT-012 is selected by default. TypeScript currently emits an explicit
skipped outcome. Recursive/deeper-than-64 helper or binding chains and unsupported
calls remain unresolved. Traced evidence outside the current GPT blocks produces
`static_review_context_incomplete`; expanded review context is still pending.
No model-retention or race-free filesystem guarantee is claimed.

## Verification

Final source commit `32e80f0` has production source SHA-256
`cdcfaccbca1c1cb29dd29446939857dbf54ce8608ca3d8da9dbcef82b49f354f`.
The final measurements began before that commit was created, so their recorded
Git revision is its parent; their recorded production-source digest matches the
committed implementation. The verification packet checks both identities.

- **718 tests pass**, with 36 opt-in Docker tests skipped; branch coverage is
  **86.84%**, above the established 80% floor.
- Ruff, formatting, strict mypy, native schema checks, dependency/notices checks
  and the strict documentation build pass.
- Both final-source rules-only runs complete **45/45 exposed Phase 20 inputs**
  at the unchanged 120-second deadline. Stable findings, coverage and warnings
  match across all 45 inputs. JSON and SARIF validate through the existing harness.
- The condition scorer matches SENT-012 to **4/4 vulnerable Git staging and
  repository-selection inputs**, including their mutations. Their **four fixed
  partners have no condition-matched alerts**. A staging warning in a repository
  selection case is a separate condition. Other findings remain unadjudicated.
- No fresh holdout evaluation or live model calls occurred. These results do not
  establish overall benchmark recall or reviewed-tier retention.

Final summed input wall times are 1,340.769 and 1,339.115 seconds. Measurements
overlapped the full test suite and another benchmark run; they are completion and
repeatability evidence, not isolated throughput measurements. The earlier
prototype and its repeat are retained separately, as are the failing guard
counterexamples and corrected checks. The final guard corrections leave the
45-input stable reports unchanged from that prototype.

The first full suite found two assertions hard-coding the old seven-rule catalog;
the report tests passed after using the canonical catalog. Three additional
failing-before guard counterexamples were corrected before the final full run.
The initial cache-permission failures and authorized passing documentation and
dependency checks are retained. Execution PR #22's 30 successful hosted checks
are evidence for that earlier increment, not this new implementation.

## Evidence and remaining gates

`artifacts/phase22/containment-python/verification.json` records source identities,
timings, engineering gates and scope. Its sibling directories retain all four
measurements, native/SARIF reports, condition adjudications, coverage and JUnit
diagnostics. Reproduce the final comparison with the existing harness and fresh
output directories:

```sh
python -m scripts.run_phase20_benchmark rules --output /tmp/phase22-containment
python -m scripts.run_phase20_benchmark rules --output /tmp/phase22-containment-repeat --compare-to /tmp/phase22-containment
```

The [corpus proposal](phase22-corpus-review.md) and tested Git environment were
authorized by the user's subsequent “continue” instruction; the separate record
`artifacts/phase22/authorization.json` binds their exact packet digests. The
immutable proposal does not approve itself. Fresh held-out source remains outside
detector tuning. The Mastra development source has been inspected for the next
TypeScript increment; it has not been counted as a successful detector evaluation.

The [full technical contract](phase22-technical.md) remains the intended scope.
Paid evaluation still requires its concrete requests and bounded budget packet.
Merging, publication and external pilot acceptance have not been authorized or
completed by this increment.
