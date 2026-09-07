# Nullable probe-field validation correction

The user authorized this correction after the Phase 20 benchmark exposed repeated
`injection probe requires a string field` failures. It is a separate correction
on `fix-nullable-probe-validation`, based on frozen benchmark branch commit
`daeefe7`. It is not a tuning change applied to the retained baseline.

Excel's `create_table.table_name` is declared as `anyOf: [string, null]`. The old
review validator checked only a top-level `type: string`, rejecting this field
even though it accepts a string. The same check also affected oversized-probe
bindings and whether a tool with only nullable string fields was eligible for a
probe plan. Malformed type arrays could additionally raise an unhashable-type
error. Retained errors and request schemas identify this mismatch; discarded
failed responses are not recoverable and have not been reconstructed as captures.

One shared helper now classifies declared primitive types, `type` arrays, and
nested `anyOf` branches for all three checks. Numeric-only, unknown, and malformed
untyped fields remain ineligible. This is type classification for existing inert
probe templates, not a full schema satisfiability check or expanded Docker schema
support. Runtime schema validation, baseline prerequisites, probe payloads,
prompts, finding identities, and JSON/SARIF schemas are unchanged.

Regression tests failed before the fix (six failures, four passing controls) and
pass after it (all ten cases). They cover nullable strings, type-array syntax,
nested unions, nullable containers, numeric-only unions, and malformed/untyped
fields. Both binding validation and eligibility use the same cases. Reproduce:

```sh
python -m pytest tests/test_gpt_review.py -k probe_plan_union_field_types --no-cov -q
python -m pytest tests/test_gpt_review.py tests/test_phase20_measurements.py --no-cov -q
make check
```

Evidence is retained under `artifacts/corrections/nullable-probe-validation`.
All 17 previously accepted captures still validate through the corrected native
reviewer in offline replay (`accepted-capture-check.json`). This is compatibility
verification, not a new detection measurement or recovery of rejected responses.
The historical baseline in `docs/phase20-verification.md`, the corpus, approved
request packet, capture ledger, all successful captures, and failed-attempt
accounting remain unchanged. The benchmark's paid-capture source-identity guard
rejects the corrected scanner against the original approval; its test explicitly
checks this boundary. Any measurement of the corrected scanner needs separately
identified preparation and the selected budget approval before new paid calls.
No paid call is part of this correction's verification. The subsequently approved
[completion measurement](phase20-completion-v2.md) captured the remaining requests;
Phase 20 is now [accepted](phase20-acceptance.md).
