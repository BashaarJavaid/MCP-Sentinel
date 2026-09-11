The static scanner now allows a 300-second maximum while retaining 120 seconds as its performance target. Phase 22 remains incomplete.

The approved **120-second performance target / 300-second static maximum** is
implemented and verified at `1f3f72f`. The same deadline applies to every input;
fast scans return immediately. The TypeScript parser and source-flow workers use
the remaining shared budget, shorter caller deadlines are honored, and coverage/
report assembly checks expiry. No detector rules or model/dynamic budgets change.

Local full verification passes **2,194 tests / 36 skipped**, with **89.68%**
branch coverage. Fresh CI **34545976337** passes all **29 normal jobs**; each of
12 suites passes **2,194 / 36**. Docs **34545976336** and the final local docs build
pass. Six production requests regenerate/replay with **zero paid calls**; Git
runtime components/image remain compatible with the retained incomplete campaigns.
Initial failing deadline regressions, lint/type-check corrections and all earlier
failures are preserved. The scanner bytes now differ from `592a9cd` and `2ac39aa`;
prior exposed detections remain source-bound regressions with deadline-only
compatibility explained in `v19-source-verification.json`.

**No new corpus timing run has occurred.** The original Linux result remains
15/25 development complete, ten Meta timeouts at 120 seconds and both historical
batches skipped. The user approved revising the prospective hard timing criterion
to 300 seconds; completion within the original 120-second target must still be
reported separately. This is no speedup or completed timing-gate claim.

`v19-linux-timeout-diagnostic-proposal.json` is prepared and **unapproved**:
two named slow Meta inputs twice each, four native observations, 300 seconds each,
one 30-minute standard Linux job, no profiles/retries/paid calls. Stop at the first
incomplete or mismatching result. Full 25+45+45 verification, fresh evaluation and
human acceptance remain separate checkpoints. **Phase 22 remains incomplete.**
Paid benchmark/pilots remain deferred; Phase 21 incomplete and Phase 24/15 unchanged.

[Policy](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/docs/phase22-timeout-policy.md), [current audit](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v19-closeout-audit/packet.json), [unapproved diagnostic](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v19-linux-timeout-diagnostic-proposal.json), and [evidence batches 1–48](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/README.md).

Final docs/evidence delivery uses authorized CI skip only after proving product/test/workflow/package inputs equal tested `1f3f72f`. This later delivery is not another hosted code pass.
