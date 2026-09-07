# Phase 22 — Shared containment follow-up

This is a bounded follow-up to the workspace increment. It does not complete
shared discovery or the Phase 22 technical gate. Production source is commit
`cee0283`; native reports remain 1.6.0 and the schema 1.7.0 draft stays separate.

## Implemented behavior

- Python containment identifies imported SDK `Context` annotations separately
  from caller parameters, including `Annotated` wrappers. Similarly named or
  rebound annotations remain caller-controlled. TypeScript registrations treat
  the first handler argument as caller input and the second as injected context.
- Python containment follows a simple factory returning a statically constructed
  local instance into its method. Return annotations alone do not establish the
  implementation. Replaced instance methods remain unresolved.
- Discovery follows a single recoverable implementation in local base classes.
  Conflicting base implementations and replaced inherited members are unresolved.
- `pathlib` division retains the path type through an anchored join. Canonical
  resolution and an enforced related boundary check remain required.
- TypeScript helpers retain path identity through native normalization of an
  already canonical path. An enforced component-safe prefix or equality against
  a canonical operator root can establish containment. Bare prefixes, unrelated
  inputs and arbitrary suffixes cannot.

The regression tests first reproduced the misses and false alarms. They retain
source/sink locations and paired safe/unsafe controls. The focused containment
and discovery suite passes 71 tests. The full suite passes **776 tests**, with **36 opt-in Docker skips** and
**86.86% branch coverage**. Ruff, formatting, strict mypy, native schema checks
and the strict documentation build pass. Exposed-input measurements
are retained separately under `artifacts/phase22/shared-containment/`; only
completed records establish their respective checks.

## Limits and remaining work

These changes do not establish the complete Atlassian service-factory/upload
flow or Mastra's security-failure return/fallback behavior. Filesystem collection
guards, non-existent-path/symlink branches and all approved independent
vulnerable/fixed conditions still need condition-level adjudication. Arbitrary
factory results, reflection, custom construction and dynamic instance state are
not validated by the simple-factory regressions.

The new source support currently feeds SENT-012. Recognition does not prove
that the other detectors follow the same flows. SENT-013 through SENT-016,
Kubernetes SENT-002, complete compatibility coverage, candidate-bound review,
runtime campaigns and coordinated schema migration remain pending. The
[technical contract](phase22-technical.md) remains authoritative. No paid model
calls, holdout-driven tuning, merge, publication or pilot acceptance occurred.
