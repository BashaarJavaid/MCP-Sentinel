# Phase 22 description poisoning increment

Parent: filesystem condition PR #35. Source commit `fe40322` adds default
SENT-013 for explicit instruction overrides, secret disclosure and unrelated
tool redirection in recoverable Python and TypeScript metadata. This remains a
bounded candidate detector; dynamic descriptions are unresolved, and neither
model compliance nor exfiltration is demonstrated.

The shared source index recovers imported constants, static concatenations,
parameter descriptions and low-level SDK list-tool metadata. Normal task
instructions, negated directives and explicitly quoted attack warnings have
negative regressions. ANSI and invisible Unicode do not hide active directives.
Metadata recovery does not establish that the corresponding runtime handler
was resolved or executed.

## Verification

The full suite passed **823 tests, 36 skips, 86.74% branch coverage**. Ruff,
formatting, strict mypy, generated schemas and notices passed. The evidence
packet at `artifacts/phase22/description-poisoning/` retains commands, exit
codes, source/harness/manifest identities, logs and per-file hashes. Hosted
checks and the final integrated Phase 22 gates remain pending.

| Approved development condition | Completed | Condition findings |
| --- | ---: | ---: |
| Poisoned calculator, original and structural mutation | 2/2 | 2/2 |
| Description-overlay fixed partners | 2/2 | 0/2 |
| Safe calculator arithmetic metadata | 1/1 | 0/1 |

All five inputs used the existing rules-only runner, unchanged 120-second
per-input deadline and zero model calls. The safe input shares the vulnerable
repository snapshot: its separate poisoned calculator remains a valid unrelated
candidate. The 25 synthetic credential candidates and that unrelated poisoning
candidate were source-reviewed in `adjudications.json`. Synthetic credential
validity was not tested. The reused scorer's `unadjudicated_keys` field means
unmatched to the named condition; the separate `reviewed_unrelated` ledger
records these 26 reviews. Historical Phase 20's 70-warning backlog remains
unadjudicated. This is implementation-agent adjudication, pending human review.

## Rule checklist

- Default catalog, explicit selection, inline suppression, baselines and severity
  behavior have regressions. High impact with theoretical likelihood produces
  initial Medium severity under the existing rubric.
- ASI01 identifies metadata instructions attempting to redirect agent behavior.
  Remediation and false-positive boundaries are in the canonical rule catalog
  and [rule reference](rules.md).
- Python/TypeScript positive and negative cases, imported metadata, parameter
  descriptions, paired approved development cases and mutations passed.
- Fresh holdout, reviewed-tier retention, capture compatibility and final
  integrated technical acceptance remain pending.

## Reproduction

Use the locked development environment at the recorded source commit. Extract
retained reports with `tar -xzf artifacts/phase22/description-poisoning/measurements.tar.gz
-C artifacts/phase22/description-poisoning`; `measurement-files.json` binds all
16 native JSON/SARIF/configuration/results files. To make a separate offline run:

```python
from pathlib import Path
from scripts.phase22_corpus import frozen
from scripts.phase20_measurements import measure

manifest = frozen()
inputs = [i for i in manifest.inputs
          if i.family == "integsec-calculator-poisoning"]
assert len(inputs) == 5 and all(i.split == "development" for i in inputs)
measure(manifest.model_copy(update={"inputs": inputs}), "rules",
        Path("/tmp/phase22-description-repeat"))
```

The runner verifies selected records against the authorized manifest before
materialization. It rejects changed records and Phase 22 paid/replay treatments.
No holdout source was used to tune this increment.
