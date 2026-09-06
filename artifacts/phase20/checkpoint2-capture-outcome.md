# Checkpoint 2 — Approved capture stopped

The user approved 35 static requests and a $3.72 cumulative ceiling on
2026-09-06, replying “continue, api key is set as well.” to that explicit budget
question. `checkpoint2-approval.json` binds the original packet without changing
its bytes. Six serial requests ran with the approved production settings and no
retries. Five were accepted; the sixth failed production response validation.

The failed fingerprint is
`38216d4d980fc9c94938465cf53abb77e7eae56243c1b80a9fe4ed7045fa7306`, shared by
`excel-boundary-fixed` and `excel-child-path-safe`. It reviews the SENT-003
candidate on `create_table` in `src/excel_mcp/server.py`. The native rejection is
`injection probe requires a string field`. The native reviewer discards rejected
responses; no accepted cassette or usage telemetry exists for this request.
This is incomplete review, not a detector miss, model abstention, or suppression.
No prompt, probe, validator, or source configuration was changed to accept it.

Accepted usage cost is **$0.110620**. The failed request retains its full
**$0.101505** reservation because its actual charge is unknown. Cumulative
accounting is therefore **$0.212125**, not a claim of exact billed cost.
`captures/ledger.json` retains each attempt, approval identity, request fingerprint,
state, reservation, accepted cost, and cassette hash. No further live attempt ran.

The five accepted responses concern unrelated candidate conditions:

- Mobile vulnerable mutation: confirms a hardcoded PostHog key; it does not
  identify output-path traversal. Whole-repository correctness stays unadjudicated.
- Excel vulnerable mutation (`create_pivot_table`) and vulnerable original
  (`validate_excel_range`): suppress generic SENT-003 type-validation warnings
  based on supplied schemas, without assessing remote file containment.
- Excel fixed and child-path control (`copy_range`, one shared capture): abstains
  on framework type enforcement. Its reference to path containment does not
  allege that the approved boundary condition fails.
- Excel fixed mutation (`format_range`): suppresses the generic validation
  warning based on supplied schema; it does not assess the boundary condition.

The pre-capture replay and its repeat evidence are retained as
`replay-before-capture/` and `replay-before-capture-reproducibility.json`.
`replay/` records the partial accepted review treatment. Missing captures remain
visible and incomplete. Original live latency is retained separately from replay
duration. Git had no static candidates, so its retained Docker/replay evidence
is unaffected. There is still no new runtime review request for Checkpoint 3.

`checkpoint2-resume-proposal.json` names the 30 remaining exact requests, including
the failed request, and preserves all five accepted captures. Its conservative
cumulative reservation is **$3.412190**. Completing those requests would require
raising the cumulative request ceiling from 35 to **36**, while retaining the
**$3.72** cost ceiling. This is a reviewable proposal, not approval or an automatic
retry. Another failure would stop again and require another user decision.
