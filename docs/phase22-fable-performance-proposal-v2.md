# Phase 22 performance: final revised proposal (v2, review and design only)

Prepared 2026-09-10 in `/private/tmp/mcp-phase22-options`, branch `phase22/integration`, HEAD `c07ffeb8a621d00a0ebbe762eda9444ff1f76c40`. This document supersedes `docs/phase22-fable-performance-proposal.md` (v1), which is preserved unchanged. Nothing was implemented, executed, dispatched, installed or paid for. Neither Stage 0 nor Stage 1 is approved by this document; it requests two separate decisions in section 10.

Identities, verified by reading the checkout: scanner source SHA-256 `9639435c0657e28f7c9a16ff25b05b4101910241dc35413f5c26392f9fc36647`; `path_flow.py` SHA-256 `322aa43e4af1fbdc3ab30e2c1ff81037e146f0347c87f522e855153755a2524c`; harness `9bfc9229…`; `uv.lock` `c34da413…`. Line numbers refer to the current files.

What changed from v1, in one place:

1. Stage 0 now measures completed work per second with a deterministic checksummed workload, not CPU occupancy.
2. The v1 estimate of a 10 to 15 percent "real and portable" gain is withdrawn. Observed profile costs and realistically removable costs are now listed separately, without summing overlapping shares. The candidate now expected effect is 3 to 5 percent, which is below the demonstrated run-to-run variability.
3. M1 (hash cache) is fully resolved for serialization and then excluded from the candidate, because it also changes TypeScript record-key derivation and its net effect may be negative. M3 and M4 are excluded on measured cost. The candidate is M2 plus M5.
4. Stage 1 keeps every bound from v1, keeps the conservative per-observation rule with its false-rejection cost stated, and defines every failure case you listed.
5. The partitioning skeleton now records a slot for every tool in every partition, including empty unowned slots, and warnings are reconstructed from attempt events, not from slices.
6. Recommendation: approve Stage 0; do not approve Stage 1 on its own.

## 1. Stage 0 corrected: throughput probe, not CPU occupancy

Why v1 was wrong: two SMT threads on one core each accumulate CPU time at full rate while each completes fewer operations. Aggregate CPU divided by wall therefore approaches the vCPU count regardless of real throughput. The retained Linux data (2.66 to 3.02 child CPU-seconds per wall-second across the six timeouts) has exactly this limitation.

Workload, fixed and deterministic per process:

```python
# probe.py: standard library only, no scanner import, no target input, no network
import json, os, sys, time

KEYS = ["k%03d" % i for i in range(512)]
MASK = 0xFFFFFFFF

def helper(a: int, b: int) -> int:
    return (a * 31 + b) & 0xFFFF

def unit(acc: int) -> int:
    env: dict[str, tuple[int, int]] = {}
    for i in range(100_000):
        key = KEYS[i & 511]
        prev = env.get(key)
        acc = (acc * 1103515245 + 12345 + (prev[0] if prev is not None else 0)) & MASK
        env[key] = (acc, i)
        parts = frozenset((acc & 15, i & 15, 3))
        acc ^= len(parts) + helper(acc, i)
    return acc

def child(units: int, start_at: float, seed: int) -> None:
    while time.time() < start_at:
        time.sleep(0.001)
    wall0, cpu0 = time.monotonic(), time.process_time()
    acc = seed
    for _ in range(units):
        acc = unit(acc)
    print(json.dumps({"checksum": acc, "units": units, "pid": os.getpid(),
                      "wall": time.monotonic() - wall0, "cpu": time.process_time() - cpu0,
                      "ended_at": time.time()}))
```

1. The loop is bytecode-bound and uses dictionaries, tuples, frozensets and Python function calls, the same kinds of operations the scanner's interpreter performs. It never iterates a set or hashes a string into the checksum, so the checksum is independent of hash randomization, which is on because children run with `-I`.
2. Work unit: 100,000 iterations. Units per process: 40, chosen so one process takes about 10 to 15 seconds on the runner. The parent runs one unit in-process before the observations to record calibration; if a unit takes more than 1.0 second the parent halves `units` once and records that.
3. Checksum validation: the parent computes the expected checksum for `units` and seed in-process before any observation. Every child's checksum must equal it, and every process in every observation uses the same seed, so all checksums must be identical. Any mismatch stops the probe and the result is reported as invalid.

Interpreter and runner identity, recorded in the probe's JSON:

1. `ubuntu-latest` standard runner, Python 3.12 from `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065`, the same action pinned in `ci.yml`; no `uv sync`, no dependencies.
2. `sys.version`, `platform.platform()`, `os.cpu_count()`, `os.getloadavg()`, and the outputs of `nproc`, `lscpu`, `/proc/cpuinfo` (model name, physical id, core id, siblings), `/proc/meminfo`.
3. `ImageOS`, `ImageVersion`, `RUNNER_NAME`, `GITHUB_RUN_ID`.

Launch synchronization and timing boundaries:

1. For each observation with N processes, the parent sets `start_at = time.time() + 1.0`, spawns N children with `sys.executable -I probe.py child <units> <start_at> <seed>`, and each child busy-waits on the shared wall clock until `start_at`.
2. The observation wall time is `max(child ended_at) - start_at`, so it includes all N processes from the common start to the last finish. Per-child wall and CPU are recorded for context.
3. Completed work for the observation is `N * units`. Aggregate throughput is `N * units / wall`.

Observation counts, order, deadline and stopping:

1. Configurations: N = 1 (baseline), 3, 4, 6.
2. Three repetitions, interleaved: 1, 3, 4, 6, 1, 3, 4, 6, 1, 3, 4, 6. Twelve observations.
3. Per-observation timeout 180 seconds; job timeout 15 minutes; expected total under 5 minutes.
4. Stop on the first checksum mismatch, child failure or timeout; report whatever completed as invalid for the decision rule.

Decision rule, based on completed work only:

1. `T_N` is the median aggregate throughput over the three repetitions; `E_N = T_N / T_1`.
2. `E_3` at or above 2.7 confirms that three workers today get near-full throughput. If `E_3` is below 2.7, today's wall is already contention-limited and the partitioning model in v1 section 5 does not apply; report and stop.
3. Partitioning is justified as a Stage 2 candidate only if `E_4` is at least 3.4 and `E_6` is at least `0.95 * E_4`.
4. Partitioning is closed if `E_4` is below 3.2.
5. `E_4` between 3.2 and 3.4 is reported as inconclusive; nothing is built.

What the probe can and cannot predict:

1. It predicts how much extra bytecode-bound throughput a fourth and a sixth simultaneously busy Python process obtain on this runner, which is the premise partitioning depends on.
2. It does not predict the scanner's memory behaviour (270 to 345 MB working set per worker on Linux), garbage collection, process start and unpickling cost, duplicated preparation, or partition balance across tools. A favourable probe makes partitioning worth designing and measuring; it does not establish a scanner gain. An unfavourable probe is sufficient to close partitioning.
3. CPU topology from `lscpu` is context, not proof either way.

Cost that must be stated: dispatching the probe requires a workflow change on `phase22/integration` (a new gated job or a new approval directory for the existing gated job pattern, see `artifacts/phase22/integration/v9-linux-diagnostic-proposal-v1/`). That commit changes a workflow input, so the statement that code, test, workflow and package inputs equal `592a9cd` no longer holds for later commits; the normal CI run on that commit and the documentation bindings would need to record it. The probe itself never imports the scanner or touches an input.

## 2. Performance claims corrected

Observed costs, from the retained partial Linux cProfile of SENT-015 on `meta-image-ssrf-vulnerable` at `7555a9d` (94.17 profiled seconds, `v10-hosted-05309f9/.../SENT-015.prof`), each stated alone and not summed:

1. `Value.__hash__`: 1,424,847 calls, 0.93 s self, 1.53 s cumulative (1.6 percent). v17 macOS sampled leaf share 2.9 to 3.0 percent.
2. `_combine`: 4.13 s self; generic-branch generator expressions (lines 134 to 156) about 0.95 s; the identical-value check at line 62 is another 0.57 s and is not touched. v16 instrumented the generic body at 5.39 s of 54.9 worker CPU-seconds (SENT-012) and 4.21 of 64.9 (SENT-015), timer overhead included; 343,062 generic calls with 1.84 M operands, about 5.4 operands per call.
3. `merge`: 5.18 s self; the multi-branch generator at line 1287 is 877,996 calls and 0.81 s cumulative (0.9 percent).
4. `ast.literal_eval`: 142,251 calls, 2.19 s cumulative, of which `member_label` accounts for 71,304 calls and 1.57 s cumulative (1.7 percent); the rest is SENT-015's own prefix and literal handling.
5. `fixed_destination`: 483,793 calls, 0.49 s cumulative (0.5 percent) on Linux. The v17 macOS sample attributes 4.6 percent inclusive to it in SENT-015; the sampler attributes signals at bytecode resume points, so that share is not reliable.
6. `dataclasses.replace`: 430,980 calls, 4.37 s self, 9.37 s cumulative, of which 6.26 M `getattr` calls are 1.42 s. Not part of any correction below.

Realistically removable costs, all hypotheses until measured:

1. M2, single-pass generic `_combine`: the generic branch currently makes about 17 passes over 5.4 operands through generator frames; one pass with constant per-operand work plausibly halves the generic body. Expected 2 to 4 percent of a worker. Lost short-circuiting is real but small: `all` and `any` stop early only when a field is already decided, and the single pass still does bounded work per operand. The explicit loop is Python bytecode either way; the gain is from removing 17 generator frames and 17 traversals per call, not from any C-level acceleration.
2. M5, empty-prefix guard: 0.5 to 1 percent on Linux, possibly more on macOS if the sampled share is real.
3. M1, hash cache: at most the 1.6 percent observed, minus added costs. Every `Value` gains one slot (8 bytes) and a first-hash cost. With an unset slot and `try/except AttributeError`, the first hash of each `Value` pays an exception, about 1 microsecond; with `__post_init__` every construction pays an extra Python call. Repeated hashes per `Value` are not measured. The net effect could be negative. This, with the serialization and TypeScript issues in section 4, is why M1 is excluded.
4. M3, explicit merge loop: bounded by the 0.9 percent of the line 1287 generator; the 5.18 s of `merge` self time is the per-key loop itself and stays. Excluded.
5. M4, `member_label` memo or prefilter: bounded by 1.7 percent, and only the unknown fraction of calls whose key is a digest is removable; a cache of unique digests adds misses. Excluded.

Candidate expectation: M2 plus M5, 3 to 5 percent of the slowest worker's CPU, as a hypothesis. That is below the 10 to 23 percent spread observed between two baseline runs of the same input (v13, v14) and far below the 13 to 40 percent range derived in v1 section 7 for the Linux gate.

What the single Stage 1 candidate experiment must demonstrate, and only this:

1. Whole ordered report equality on all nine candidate observations across three real inputs, which is the correctness evidence unit tests cannot give.
2. A median child-CPU reduction on both Meta inputs that clears the prospective retention rule in section 3 under the conservative guard, with the range of all six values per input reported.
3. No regression on `atlassian-upload-fixed`.

It cannot and does not promise a Linux pass. The later Linux scanner diagnostic remains a separate approval.

## 3. Stage 1 measurement and stopping rules, finalized

Bounds retained from v1, unchanged, with no change proposed: one candidate attempt; 18 alternating native observations (3 baseline, 3 candidate, per input, per pair B then C); at most one profile; 30 conditional exposed SSRF observations; unchanged 120-second native and end-to-end caps; complete ordered-report equivalence with only the eleven recorded volatile fields excluded; no automatic retries.

Retention rule, prospective:

1. Materiality: candidate median child CPU at most 0.92 of the baseline median on both Meta inputs; candidate median wall at most 0.95 of the baseline median wall on both Meta inputs.
2. No regression: candidate medians not above baseline medians on any input, including `atlassian-upload-fixed`.
3. Conservative guard, retained: no candidate observation exceeds the three-sample baseline maximum on either metric for its input.
4. Acknowledged consequence: with a true 3 to 5 percent gain and the observed variability, rule 1 will probably fail and rule 3 may fail even when the change is beneficial. That false rejection is accepted rather than replaced with a rule that three observations cannot support. A gain too small to clear these rules is also too small to affect the Linux gate, so a false rejection costs nothing that matters to Phase 22.
5. Variability reporting: all three values per cell, the median and the range; no pooling across inputs or with historical observations; no confidence statement.

Failure classifications and consequences:

1. Baseline timeout or failure: classified as incomplete execution, cause unestablished. The experiment stops; retention is not established; the observation is retained and counted. It is labelled an environment failure only if independent recorded evidence identifies one (for example the recorded load or a concurrently running owned process), and even then it stays an incomplete observation, not a discarded one.
2. Candidate timeout, failure or interruption: retained and counted; the experiment stops; retention not established; the candidate is reverted.
3. Load precondition (1-minute load average below 2.0 before every observation; up to three rechecks 60 seconds apart) failing after some observations have completed: the sequence is suspended, not abandoned. Completed observations are retained and counted in their positions. Resumption is permitted only within 24 hours of the first observation, on identical scanner bytes, continuing the pre-planned order from the next unstarted observation. No completed observation is repeated or discarded. If the sequence cannot resume within 24 hours, the experiment ends incomplete and retention is not established.
4. Attribution profile: it is not a retention condition. It runs only after all 18 native observations. If it completes, its ordered report must equal the baseline report; a mismatch blocks retention because it indicates nondeterminism. If it times out or fails, that is recorded and retention is unaffected, since the sampler adds overhead and its report is not a timing observation.
5. M4 is excluded before the candidate is frozen (section 2). The frozen candidate is M2 plus M5 and their tests, nothing else.
6. Stopping language, reconciled: the experiment ends after the 18 native observations and the profile if retention fails. If retention holds, the 30 conditional exposed SSRF observations (three families, five inputs, twice) are the final part of the same approval and the experiment ends after them. Any failure among the 30 reverts the candidate and retains all evidence. Unused observations at any stop are closed.

## 4. M1 hash-cache serialization, resolved

Facts from the interpreter and the source:

1. `dataclasses.py` in the locked interpreter adds `__getstate__` and `__setstate__` to frozen slotted dataclasses unless the class defines them (`_add_slots`, lines 1239 to 1242). `_dataclass_getstate` returns `getattr` of every field, and `_dataclass_setstate` restores every field with `object.__setattr__`. `__post_init__` does not run during unpickling.
2. A field declared `init=False` with a plain default gets no `__init__` code (`_field_init` returns `None`), and `_add_slots` removes the class-level default, so the slot is unset until something sets it.
3. Serialization paths in the scanner: `workers.py:57` to `:60` pickles `(configuration, files, deadline, trees)` into a worker; `workers.py:136` pickles a `RuleRunState` or `SentinelError` back. `RuleRunState` holds `StaticMatch` (strings and a `SourceRange`), `ReportWarning`, visits and counts (`model.py:42` to `:90`). No `Value` crosses the worker boundary today. `copy.copy` is applied only to AST nodes (`path_flow.py:488`, `:667`, `:1177`; `sent015.py:259`). `deepcopy` returns `self`.
4. `typescript_path_flow.py:643` (`record_state`) iterates `dataclass_fields(Value)` and reads every field with `getattr` into a `json.dumps` that becomes a record key. A new `_hash` field would either raise `AttributeError` when unset or inject a process-specific integer into TypeScript record keys.

Design that would make M1 correct, described for the record:

```python
@dataclass(frozen=True, slots=True)
class Value:
    ...                                   # 17 fields unchanged, same order
    _hash: int = field(init=False, compare=False, repr=False)   # no default

    def __hash__(self) -> int:
        try:
            return self._hash
        except AttributeError:
            value = hash((self.sources, self.key, self.resolved, self.contained,
                          self.locations, self.path_object, self.repository_object,
                          self.instance, self.option_safe, self.url_checks,
                          self.operator_credential, self.credential_fallback,
                          self.credential_present, self.maybe_missing, self.maybe_none,
                          self.operator_opt_in, self.checked_path_parent))
            object.__setattr__(self, "_hash", value)
            return value

    def __getstate__(self) -> tuple:      # discard the cache on every serialization
        return tuple(getattr(self, f.name) for f in fields(self) if f.init)

    def __setstate__(self, state: tuple) -> None:
        for f, item in zip((f for f in fields(self) if f.init), state):
            object.__setattr__(self, f.name, item)
```

1. Equality is unchanged (`compare=False`). `dataclasses.replace` skips non-init fields and produces a fresh object with an unset cache. `deepcopy` returns `self`. The hash value equals the generated field-tuple hash, so in-process behaviour is unchanged.
2. Every serialization path (`pickle`, `copy.copy`, any future worker transfer) drops the cache, so a `Value` loaded under another hash seed recomputes with the loading process's seed and stays consistent with an equal newly constructed `Value`.
3. `record_state` at `typescript_path_flow.py:643` must filter `if attribute.init` (or `attribute.compare`) so the TypeScript record key derivation is byte-identical.
4. Tests, described only: (a) same-process: `hash(v) == hash(field tuple)`, repeat stability, `replace` produces an unset cache, `v == replace(v)` independent of caching, `copy.copy(v) == v` with a recomputed hash, `set` and `dict` membership; (b) cross-seed: a subprocess with `PYTHONHASHSEED=1` hashes a `Value` then pickles it; a second subprocess with `PYTHONHASHSEED=2` unpickles it, constructs an equal fresh `Value`, and asserts equal hashes and that a set containing the loaded object finds the fresh one; repeated with the seeds swapped; (c) TypeScript record keys for a fixture equal the pre-change keys; (d) `dataclass_fields(Value)` consumers are enumerated by grep (one site) and the test fails if a new consumer reads a non-init field.

Decision: M1 is excluded from the Stage 1 candidate. The v1 claim that M1 is a one-file, output-identical change is withdrawn: it needs the TypeScript filter, explicit serialization methods, and a first-hash cost that may exceed its saving. It may be reconsidered as part of a later candidate that has a larger expected effect, with the design and tests above.

## 5. Partitioning skeleton with empty slots (design for a possible Stage 2 only)

Every partition records the same ordered logical slots. Unowned forks are recorded as empty slots without executing the fork or building its memo copy.

```python
# path_flow.entry_group, replacing lines 323 to 328; everything before is unchanged,
# including entries[0], for_tool, launch_variants, prepare_launch and the memo.
for tool_index, (current, parameters) in enumerate(entries):
    key = (group_index, launch_index, variant_index, kind, state_index, tool_index)
    owned = self.partition is None or tool_index % self.partition.count == self.partition.index
    opened = self._open_segment("fork", key, owned)
    if owned:
        check_deadline(self.deadline)
        fork = copy.deepcopy(self, memo.copy())
        fork.entry_handler(current, {**parameters, **local})
    self._close_segment(opened)      # unowned slots close with empty ranges
```

1. The skeleton is the ordered list of `(kind, key)` for every segment. It is identical in every partition by construction, because the loops over groups, launches, variants, states and tools are executed identically and only the fork body is conditional.
2. Ownership is a per-partition flag; the parent asserts that each fork key is owned by exactly one partition and that every partition's skeleton equals partition 0's. Mismatch raises `InfrastructureError` before any merge.
3. Preparation context is unchanged: `entries[0]` still selects launches and variants; `local` and `memo` are built as today; `state.visit` in `analyze()` still runs for all tools in every partition.
4. Finding slices are materialized only after `analyze()` returns, that is after every `launch_evidence` (lines 329 to 331 and 348 to 350) and after TypeScript analysis, by cutting `self.state.matches[m0:m1]` for each owned segment. `launch_evidence` rewrites entries in place by index and never inserts, deletes or reorders, so recorded ranges address the final annotated findings with every capture.
5. Preparation findings and warnings fall in the shared segment before `start` (line 296); the parent keeps them from partition 0 only.
6. Skipping `check_deadline` for unowned slots changes only when a deadline error can be raised, not any output.

## 6. Shared-warning reconstruction by attempt events

The v1 assumption of equal shared warning-slice lengths is wrong, as your example shows:

1. Partition 0 owns tool 0 in variant A. Tool 0's fork calls `unresolved(auth.py, 137, R)` and emits warning W with identity I. `reported_warnings` in partition 0 now contains I.
2. Later, preparation of launch 2 (a shared segment) calls `unresolved(auth.py, 137, R)` again. Partition 0 suppresses it. Partition 1 never ran tool 0's fork, so it emits W in that shared segment.
3. The two partitions' shared slices differ in length and content, and sequential execution emitted W once, at tool 0's position.

The reverse also happens: a fork owned by partition 1 emits a warning that, in sequential order, suppresses a later preparation warning; partition 0 did not run that fork and emits the preparation warning in its shared slice.

Design: record every `unresolved` attempt as an event, before the suppression check, and replay suppression in the parent in sequential order with a fresh set.

```python
def unresolved(self, symbol, node, reason):
    identity = (symbol.file.relative_path, getattr(node, "lineno", 1), reason)
    warning = ReportWarning(code="static_flow_unresolved", message=...)   # unchanged text
    if self.partition is not None:
        self.events.append(("python", identity, warning))   # every attempt, suppressed or not
    if identity in self.reported_warnings:
        return
    self.reported_warnings.add(identity)
    self.state.warnings.append(warning)                      # unchanged sequential behaviour
```

1. Each segment records the index range of `self.events` it produced, exactly as it records match ranges. Warnings in `state.warnings` are ignored for reconstruction in partition mode.
2. TypeScript's emitter at `typescript_path_flow.py:244` to `:253` suppresses by equality against the whole `state.warnings` list, which in sequential mode includes Python warnings. It records `("typescript", None, warning)` attempts the same way, before its membership check.
3. The final `state.warnings.extend(program.warnings)` in `analyze()` records `("program", None, warning)` events; `for_tool` already deduplicates these by equality per process.
4. Parent replay: walk partition 0's skeleton; for each segment take the owner's event range (partition 0 for shared segments). Maintain `seen_identities` (a set) and the reconstructed warning list. For a `python` event, append if its identity is not in `seen_identities`, then add it. For a `typescript` event, append if an equal warning is not already in the reconstructed list. For a `program` event, append unconditionally. This reproduces sequential first-occurrence suppression for both mechanisms, in order, because sequential execution is exactly this replay with the same events.
5. Worked example: slots in order are [preparation A, fork tool 0 (owner 0), fork tool 1 (owner 1), preparation B, ...]. Partition 0's preparation B events contain an attempt with identity I (suppressed locally); partition 1's contain the same attempt (emitted locally). Replay: fork tool 0's event emits W and marks I; preparation B's attempt from partition 0 is skipped because I is seen. Result: W once, at tool 0's position, as in sequential execution. In the reverse case, fork tool 1's event (owner 1) marks I first, and partition 0's later preparation attempt is skipped although partition 0 had emitted it locally.
6. Consistency check, replacing the slice-length assumption: the attempt sequences of every shared segment must be identical across partitions, because attempts depend only on the analysis path, which is replayed identically, and not on `reported_warnings`. The parent asserts this and fails closed on mismatch. It also asserts equal `exemptions` and `skip_reason`.

Additional shared-state assumptions this introduces, audited:

1. `unresolved` at `path_flow.py:624` is the only Python-flow site that appends to `state.warnings` (grep: `path_flow.py:629`; `launches.py:141` appends to `program.warnings`). `http_context.py` calls `flow.unresolved`, so it is covered.
2. TypeScript appends only at `typescript_path_flow.py:253`.
3. No site reads `state.warnings` during flow analysis except the TypeScript membership check, which is replayed. `typescript.py:847` and `coverage.py:584` read warnings outside the workers.
4. Findings are never suppressed at append time, so per-segment match ranges remain exact; `engine._deduplicate` runs on the reconstructed sequential order.
5. Replay does not depend on message text or slice lengths. It depends on identity tuples for Python and on `ReportWarning` equality for TypeScript, which are the two mechanisms the sequential code uses.

These corrections are design for a possible Stage 2. They do not authorize building or measuring partitioning.

## 7. Exact revised Stage 0 proposal

1. Purpose: measure the runner's effective throughput scaling for 3, 4 and 6 concurrent bytecode-bound Python processes against a 1-process baseline, to decide whether partitioning has a premise.
2. Mechanism: one `workflow_dispatch` on `phase22/integration`, standard `ubuntu-latest`, Python 3.12 from the pinned `setup-python` action, standard library only, `probe.py` stored under a new approval directory `artifacts/phase22/integration/v18-linux-scaling-probe-v1/` with a packet recording its SHA-256; the job copies it, runs it, and uploads the JSON output as an artifact, with `if: always()`.
3. Workload, validation, identity, synchronization, counts, order, deadlines, stopping and decision rule exactly as in section 1.
4. Bounds: 12 observations; N in 1, 3, 4, 6; 40 units of 100,000 iterations per process (one halving allowed by calibration, recorded); 180 seconds per observation; 15-minute job; one dispatch.
5. Exclusions: no scanner import, no corpus input, no dependency installation beyond the interpreter, no model call, no target execution, no runner change.
6. Approval boundary: the workflow change commit and one dispatch. It authorizes nothing about the scanner.
7. Output: a versioned assessment recording `E_3`, `E_4`, `E_6`, the topology context, and the decision under the rule in section 1.

## 8. Exact revised Stage 1 proposal

1. Candidate: M2 (single-pass generic `_combine`, v1 section 6 pseudocode) and M5 (`if prefix and fixed_destination(prefix)` at `sent015.py:390`), each as its own commit with its property test, frozen as one commit whose scanner source SHA-256 and the hashes of `path_flow.py` and `sent015.py` are recorded in a versioned receipt before any observation. Ruff, format, strict mypy, schema drift and the full suite must pass at that commit. No other product change; any further edit voids the observations.
2. Baseline: current HEAD bytes, scanner source SHA-256 `9639435c…`, `path_flow.py` `322aa43e…`, harness `9bfc9229…`, lock `c34da413…`.
3. Inputs and configuration: `meta-image-ssrf-vulnerable` and `meta-operator-fallback-fixed-mutation` (manifest `a5ea6930…`), `atlassian-upload-fixed` (manifest `f69d043c…`), configuration `f996757169…`, rules-only, through `scripts.phase20_measurements.measure` with the frozen manifest subset as in `/private/tmp/phase22-v17-run.py`, model transport disabled, zero model calls asserted.
4. Counts: 1 candidate attempt; 18 native observations, order per input B, C, B, C, B, C; at most 1 non-modifying sampled profile of the candidate on `meta-operator-fallback-fixed-mutation` after the 18; 30 conditional exposed SSRF observations only if retained.
5. Caps: 120 seconds native and 120 seconds end-to-end per input, unchanged, for every observation including the profile and the 30 regressions.
6. Load and environment: existing locked macOS venv; 1-minute load below 2.0 before every observation with the recheck and suspension rules of section 3; no overlapping owned work; every observation records scanner identity before and after, git diff emptiness, wall, native duration, `getrusage` for parent and children, load before and after, report and stable hashes, full report and SARIF; unique labels.
7. Equivalence: every candidate report equals its baseline report as an entire ordered document, warnings order and coverage included, excluding only `applied_at`, `completed_at`, `duration_ms`, `execution_latency_ms`, `finding_id`, `latency_ms`, `origin_latency_ms`, `reviewed_at`, `scan_id`, `started_at`, `timestamp`; JSON and SARIF valid.
8. Retention, variability and failure handling exactly as in section 3.
9. Conditional regressions: if retained, the three exposed families, five inputs, twice, with their unchanged condition, ordering, validity and provenance gates; any failure reverts.
10. Stop and revert: as in section 3, item 6. On any stop without retention, revert product code, keep tests and evidence, close the budget, propose no further micro-optimization experiment.
11. Nominal maximum: 49 executions at 120 seconds, 98 minutes.

## 9. Remaining uncertainties

1. The Linux requirement is a range, 13 to 40 percent, whose upper part rests on applying two completed-input ratios to censored inputs. Nothing in this proposal measures it.
2. The Stage 1 expected effect of 3 to 5 percent is a hypothesis from a partial Linux profile and an instrumented macOS run on different inputs; the macOS-versus-Linux discrepancy on `fixed_destination` shows that attribution is uncertain.
3. The number of repeated hashes per `Value`, the fraction of digest keys reaching `member_label`, and the distribution of merge branch widths were never measured; they decide whether M1, M4 and M3 could ever matter.
4. Partition balance across tools and the scanner's memory-bound behaviour under six processes are unmeasured; Stage 0 cannot resolve them.
5. Whether cross-tool helper contexts repeat remains unknown; a reduced-signature count would only find candidates and would not establish safe reuse, so no reuse work is proposed.

## 10. Recommendation and gating

1. Stage 0: worth approving. It is cheap, it cannot affect any scanner evidence, and its result either closes partitioning or justifies designing it. Its one real cost is the workflow commit and the re-binding it forces.
2. Stage 1: not worth approving on its own. The candidate is exact and reviewable, but its expected effect is below what the retained variability lets three observations detect, below the conservative guard's false-rejection band, and immaterial to the Linux gate. Its best use is inside a later candidate with a larger expected effect, if Stage 0 justifies one. If you approve it anyway, section 8 is the complete bound.
3. If Stage 0 closes partitioning, the remaining routes are a dependency-aware reuse redesign, which needs its own correctness design before any measurement, or a timing-scope decision that keeps the 15 of 25 Linux result and the ten Meta timeouts visible. Neither is proposed here.
4. Separately gated and not requested by this document: Stage 2 (partitioning), the later Linux scanner diagnostic (four native runs on the two Meta inputs at unchanged caps), the full 25 + 45 + 45 Linux sequence with its unchanged gates, the fresh post-stabilization freeze and evaluation, and final Phase 22 acceptance.

Decision requested: approve or decline Stage 0 (section 7). Stage 1 (section 8) is documented as ready but recommended against as a standalone experiment.
