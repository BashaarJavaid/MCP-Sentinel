# Phase 22 — Filesystem containment conditions

Source `276722a` follows enforced TypeScript collection checks and new-file parent
checks. The parent is the shared-containment draft (#34). Native reports remain
1.6.0; this increment does not complete Phase 22.

## Behavior and verification

- Canonical path identity survives supported native normalization, helper returns,
  arrays and `Promise.all`. Caller paths require real-path protection; lexical
  normalization alone does not establish symlink containment.
- A successful `some` predicate can establish a related boundary. `every` on an
  empty collection and the truthiness of `map`, `filter` or `find` cannot substitute
  for that check. Root-directory special cases require the matching allowed root.
- New-file handling requires both the original lexical boundary and the resolved
  parent boundary against the same root. Unrelated parents, discarded checks,
  changed values and replaced closure variables retain findings.
- Unavailable inherited compiler settings are explicitly reported as not applied.
  Available local mappings and declared external imports remain usable. No parent
  configuration outside the included source is read. Cycles and ambiguous local
  bindings remain unresolved. Resolution does not claim unavailable settings were
  applied; their possible effect remains a reported limitation.

The focused discovery/containment suite passes **102 tests**. The full suite
passes **798 tests**, with **36 opt-in Docker skips** and **86.88% branch
coverage**. Ruff, formatting, mypy, schemas and notices checks pass. Hosted checks
are recorded separately.

## Exposed filesystem measurement

The existing Phase 20 runner measured the four approved `filesystem-prefix`
inputs with the unchanged 120-second deadline and no model calls. Source,
configuration and manifest identities are retained under
`artifacts/phase22/containment-conditions/`.

Both vulnerable inputs produce 12 SENT-012 candidates. Source adjudication matches
them to caller paths passing the bare-prefix guard. Both fixed inputs produce
four other candidates and no alerts matching the frozen sibling-input condition.
This is **2/2 vulnerable conditions detected and 0/2 fixed condition alerts** for
this subset; it is not a 45-input measurement or independent held-out accuracy.

The eight other fixed-input candidates were reviewed separately. Four concern
possible sibling temporary writes/cleanup after a validated root path reaches the
exclusive-create fallback. Four in the edit helper have platform-dependent
reachability because file reading precedes temporary-name construction. These
remain source candidates or abstentions, with no runtime proof. Node documents
platform-dependent directory reads and exclusive-create behavior in its
[file-system reference](https://nodejs.org/api/fs.html). The original condition
scorer keeps unmatched keys separate; `filesystem-adjudications.json` records
this additional review explicitly. Unchanged historical findings remain
unadjudicated.

Initial exploratory scans with missing discovery and intermediate false alarms
are not accepted measurements. The retained four-input run uses the committed
source. Full integrated repetitions, all other containment families, remaining
detectors, compatibility, review/campaign/schema work, paid evaluation and
external acceptance remain pending.
