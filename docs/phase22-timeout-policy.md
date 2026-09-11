# Phase 22 static timing policy

The user approved this policy with “okay go ahead with this.” on 2026-09-10.
It replaces the 120-second hard timing requirement prospectively. It does not
change the outcome of any earlier measurement or establish a speed improvement.

## Target and maximum

Deterministic static analysis has a **120-second normal performance target** and
a **300-second shared deadline**. The same policy applies to every input, on
every supported platform. A fast scan returns as soon as it finishes. A slow
scan continues in the same execution after 120 seconds; it is not killed and
restarted. The caller may supply an earlier deadline but cannot extend the
engine beyond 300 seconds.

The engine, source-flow workers, Semgrep batches and TypeScript parser use the
remaining shared deadline. Coverage/report assembly must also finish before
the deadline. Expiry is an infrastructure failure, never a completed clean scan;
worker failure and interruption retain termination and reaping of all children.
Checks inside Python analysis are cooperative. The proposed Linux measurement
supervisor additionally enforces the whole-input wall-clock limit and reaps the
process group; cleanup and evidence upload have a separate job reserve.

This is the deterministic static budget. It is not a five-minute cap on a full
static + model review + dynamic invocation. Model review, dynamic campaign and
Semgrep's existing per-rule/per-file safety limits keep their own budgets.
The native Finding/report schema and detector semantics are unchanged.

## Measurement and reporting

New timing assessments retain both native scan duration and whole-input elapsed
time, alongside completion, findings, coverage, warnings and source identities.
Whole-input time includes source materialization, configuration, scan, report
validation and writing. The supervisor has a 300-second limit from the start
of that input; it does not grant a fresh 300 seconds after setup.

| Classification | Requirement |
| --- | --- |
| `completed_within_target` | Complete analysis and both native and whole-input times at most 120 seconds |
| `completed_using_extended_time` | Complete analysis and both times at most 300 seconds, with at least one above 120 seconds |
| `incomplete` | Deadline expiry, interruption, invalid report or another incomplete execution |

Retain the underlying incomplete reason; do not describe every failure as a
timeout. A complete report written after the whole-input cap is retained as raw
evidence but does not pass the timing gate. No rounding tolerance silently turns
an over-limit duration into a pass. Classification is assessment metadata;
the existing static `duration_ms` and raw reports remain available without
adding timing-dependent findings or changing warning order.

## What remains unverified

The original standard-Linux run at `7555a9d` completed 15 of 25 development
inputs under 120 seconds; all ten Meta inputs timed out and both historical
batches were skipped. Those results remain unchanged. The successful Stage 0
probe at `0b71a29` failed its prospective throughput premise; no partitioning
or micro-optimization is included in this policy change.

The first proposed diagnostic is the two named slow Meta inputs, each twice:
`meta-image-ssrf-vulnerable` and `meta-operator-fallback-fixed-mutation`.
It would allow four native observations at 300 seconds each in one standard
Linux job, with zero paid calls, profiles, target execution or retries. Its
exact source-bound proposal is prepared separately before requesting approval.
No new corpus measurement is authorized merely by this document.

If the diagnostic passes, the entire 25 + 45 + 45 sequence remains a separately
approved gate, with its original detection conditions and repeat equivalence.
Its revised timing requirement is completion within 300 seconds per input,
with the count meeting the 120-second target reported separately. The former
240-minute total job budget cannot simply be reused for the larger input cap;
the next proposal must bound each sequential job and the total run budget.

Fresh evaluation after stabilization, final human acceptance, and complete
evidence/draft delivery remain required. Phase 22 is not complete. The policy
approval does not authorize new paid calls, a runner upgrade, merge or release.
