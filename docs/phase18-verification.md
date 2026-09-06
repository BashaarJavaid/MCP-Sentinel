# Phase 18 verification

Status: implementation and verification in progress. Final acceptance is pending.
Prepared version: **1.3.0** (Phases 16–18). Public release availability is separate:
no merge, release tag, PyPI/Marketplace publication, or announcement is authorized.

The branch is `phase18-rules-only`; hosted gates will run through a draft PR.
No paid model calls are part of this gate. Historical evaluation captures remain
recorded replay, not new accuracy measurements.

## Required evidence

- Configuration precedence, inactive LLM validation, and explicit negative override.
- Absent/dummy credentials, reviewer/client/cache/network/Docker spies, unchanged
  existing cache, supported Python/TypeScript clean and vulnerable controls.
- Null reviews, stages, offline JSON/SARIF validation, thresholds, baseline,
  inline suppression, exit codes, default init, upgrade preservation, and rollback.
- Keyless ordinary/fork Action paths, inherited/explicit inputs, unchanged
  credential and upload policies, and actual pre-commit execution.
- `make check`, historical artifacts, distribution builds/smokes, Docker replay,
  and Linux/macOS/Windows Python 3.10–3.13 hosted gates.
- Installed-wheel scans in a Linux network namespace after dependencies install;
  namespace setup failure fails the gate. Spies and Semgrep adapter assertions
  separately establish avoidance of prohibited paths.

## Compatibility

Native schema stays 1.5.0 as agreed. Its canonical finding review field now admits
null for rules-only results; object review records remain valid. Older validators
requiring an object must update. Baseline-v2 is retained; rules-only and reviewed
static reports share static-mode compatibility. Historical evidence is preserved.

These checks establish offline completion and implementation compatibility. They
do not measure broad detection accuracy, security assurance, or maintainer value.
