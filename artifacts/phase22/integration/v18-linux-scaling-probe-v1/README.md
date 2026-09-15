# Approved Stage 0 CPU throughput probe

The user approved Stage 0 only with “go ahead then”, following the bounded Fable
v2 proposal and the assistant's monotonic/readiness/cleanup safeguards.
`proposal.md` preserves that review; `authorization.json` and `packet.json` bind
the approval and exact implementation. Stage 1 and partitioning remain unapproved.

One standard Linux dispatch runs 12 observations: process counts 1, 3, 4 and 6,
three repetitions, 40 fixed work units per process (one recorded calibration
halving allowed). Every result is checksummed. The cap is 180 seconds per
observation and 15 minutes for the job, with an internal cleanup/upload reserve.
There are no scanner imports, corpus inputs, model calls or target executions.

The existing gated CI job is reused; `phase22_historical=true` selects this probe
at this source, not the spent historical scanner diagnostic. All normal jobs
remain structurally unchanged. The workflow change needs fresh normal CI;
the scanner/test/package inputs still match their actual prior verification.

`probe.py selfcheck` runs tiny implementation controls only. The real `run` mode
requires the approved script hash, integration branch, Linux and run attempt 1.
The dispatcher records one consumed dispatch before invoking GitHub; no retry.

Results assess this synthetic workload on one runner. A favorable result only
supports preparing a separately approved scanner partitioning experiment.
Unfavorable or inconclusive evidence does not prove all parallelism ineffective.
Timing, fresh evaluation and final human Phase 22 acceptance remain unmet.
