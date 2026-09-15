# First-advisory compatibility — execution review

Prepared, not approved or executed: the original GHSA-5w57-2ccq-8w95 corpus,
**seven frozen inputs twice = 14 observations / seven ordered pairs**. The original
baseline already passed; this is a compatibility check of the current corrected
scanner, not a new independent advisory or a manufactured detector correction.

[proposal.json](proposal.json) binds exact source, scanner/helper/dependencies,
configurations, commands, order, eight existing volatile exclusions and limits.
The final checkpoint index binds its hash after local engineering completes.

```bash
.venv/bin/python -m scripts.phase23_regression run \
  --proposal artifacts/phase23/compatibility-advisory-review-v1/proposal.json \
  --approval artifacts/phase23/compatibility-advisory-authorization-v1.json \
  --output artifacts/phase23/compatibility-advisory-v1
```

Order: full vulnerable/fixed, minimized vulnerable/fixed, safe literal, renamed
vulnerable/fixed, then repeat. Limits: 1,800 seconds per input, 10 seconds Semgrep,
15 seconds cleanup, maximum four workers and a 440-minute outer cap plus active
cleanup. No retry or timeout extension. Failures close unstarted slots.

Retain complete reports, native/offline SARIF validation, diagnostics, support
judgments, timings and all changes from the original baseline. Full source remains
separate from derived cases. No paid calls or advisory-target execution. The prior
accepted source freeze and baseline evidence remain immutable.
