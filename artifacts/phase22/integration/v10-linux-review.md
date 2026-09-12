# Approved Linux diagnostic at scanner `7555a9d`

The single approved standard Linux job, [34446017571](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34446017571), executed exactly four native input runs and two profiled runs. All six reached the 120-second deadline. The workflow completed its diagnostic/retention steps successfully; this is **zero completed native observations out of four**, not a timing-gate pass.

| Exposed input | Native wall seconds | Child CPU seconds |
| --- | --- | --- |
| Meta image SSRF vulnerable, first | 120.054 | 339.450 |
| Meta image SSRF vulnerable, repeat | 120.047 | 356.353 |
| Meta operator fallback fixed mutation, first | 120.038 | 318.897 |
| Meta operator fallback fixed mutation, repeat | 120.040 | 327.102 |

Worker profiles show CPU-bound shared expression/call traversal, branch merging and Value allocation in SENT-012, SENT-015 and SENT-016. SENT-014 finishes in about eight seconds; each other worker retains roughly 100 seconds of partial profiled CPU work before timeout. The previous credential guard cache is not the principal remaining cost. Partial profiles preserve function/caller/count records and missing final worker reports. Profiled times include instrumentation and scheduling effects and cannot replace native measurements.

Missing native reports remain missing, so no report-equivalence claim is made for these four timeouts. The whole development and historical gates remain governed by the earlier failed final run: 15/25 development complete, all ten Meta inputs timed out, both historical batches skipped. This diagnostic did not retry those batches, procure a runner, waive deadlines, execute targets or make paid calls.

Exact source, workflow, approval, input, environment and resource bindings are in `v10-linux-diagnostic-assessment/packet.json` and `v10-hosted-05309f9/`. The subsequent bounded local merge experiment is separate evidence in `v10-local-performance-plan.json`; local desktop successes cannot be substituted for Linux or pooled into a whole-batch pass.
