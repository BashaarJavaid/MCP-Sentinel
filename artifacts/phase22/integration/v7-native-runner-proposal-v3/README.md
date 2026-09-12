# Revised bounded Linux execution proposal

Explicit user decision pending; no workflow change or dispatch has occurred.
This revision supersedes the unapproved v2 proposal after original development
finished24/25 with a new120.063s Meta fixed-mutation timeout. The approved Meta
label erratum does not make that missing execution a pass.

The exact patch runs one original25-input development batch, then (only after its
gate passes) the required historical45-input pair, with the second historical
batch requiring the first to pass. Every native and end-to-end input limit stays
120 seconds. Development requires10 vulnerable hits, only the two approved raw
Meta fixed alerts, and zero alerts on13 valid negatives. Historical requires20
vulnerable hits and zero fixed/control alerts in each complete batch.

At most115 native input runs,230 minutes nominal input budget and a240-minute job
ceiling. No retries, pooled successes, fresh-v2 evaluation, target execution or
paid model calls. The immutable detector remains62987a6; normal CI jobs retain
their behavior for ordinary runs. Any result must still be assessed and retained;
the execution decision does not waive a gate or approve final technical acceptance.
