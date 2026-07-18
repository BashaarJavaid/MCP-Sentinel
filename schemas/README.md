# Vendored and generated schemas

`finding.schema.json`, `report.schema.json`, and `gpt-review.schema.json` are
generated from Sentinel's Pydantic models with
`python -m sentinel.schema generate`. The native report contract is version
`1.2.0`; `gpt_review` is nullable for pre-Phase-2 or stage-skipped reports.

`sarif-2.1.0.schema.json` is the OASIS SARIF 2.1.0 JSON Schema with Errata 01:

- Source: https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json
- Retrieved: 2026-07-17
- SHA-256: `c3b4bb2d6093897483348925aaa73af03b3e3f4bd4ca38cef26dcb4212a2682e`
- Publisher: OASIS Open

The vendored file is retained unmodified and used for fully offline validation.
See the OASIS document notices and intellectual-property policy for its terms.
