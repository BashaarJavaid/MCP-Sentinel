# Phase 22 performance: refined review and bounded proposal (review and design only)

Prepared 2026-09-10 in `/private/tmp/mcp-phase22-options` on `phase22/integration`, HEAD `c07ffeb8a621d00a0ebbe762eda9444ff1f76c40`. Nothing was executed, modified, dispatched or paid for while preparing this document. It is an untracked review file, like the user prompt files beside it. Nothing in it is approved; it requests approval for the items in section 9 only.

Identities verified by reading the checkout:

1. Scanner source SHA-256 `9639435c0657e28f7c9a16ff25b05b4101910241dc35413f5c26392f9fc36647` (recorded in `v17-timing-disposition.json`; code inputs unchanged since `592a9cd`).
2. `src/sentinel/static/path_flow.py` SHA-256 `322aa43e4af1fbdc3ab30e2c1ff81037e146f0347c87f522e855153755a2524c`, unchanged since `7555a9d`.
3. Measurement harness SHA-256 `9bfc9229b7ec7d23580c44f2306edb9274bc1d2a3c2261d01db0445b8b480add`; `uv.lock` SHA-256 `c34da413d4761ca42f243bc41a10afd8961a98daa1f3a236d37fe03720743b2b`.
4. Line numbers below refer to the current `path_flow.py`, `http_context.py`, `rules/sent012.py`, `rules/sent015.py`, `rules/sent016.py`, `workers.py`, `engine.py` and `model.py` at this HEAD.

Summary of the revision: the partitioning idea survives review as a design, but its Linux benefit depends on an unmeasured property of the runner (whether the fourth vCPU adds throughput). I therefore no longer recommend bundling partitioning with the micro-corrections. The proposal to approve now is the exact micro-correction bundle with one bounded native experiment, plus a tiny Linux scaling probe that decides whether partitioning is worth building at all. Section 10 states this plainly, including that the micro-corrections alone are unlikely to clear the Linux gate.

## 1. Finalized finding slices and `launch_evidence`

Facts from `path_flow.py`:

1. In `entry_group`, `start = len(self.state.matches)` is taken at line 296, once per prepared launch variant, before the loop over states and tools.
2. Forks are created and run at lines 323 to 328. Each fork appends matches and warnings to the shared `self.state` (shared through the memo at lines 297 to 309).
3. `launch_evidence(start, ...)` at line 329 runs after all states and all tools of that variant. At lines 359 to 393 it rewrites `self.state.matches[index]` in place for every index in `range(start, len(...))`. It only reads that match's own captures plus `self.http_context.decisions` and `decision_sources`, which are variant-level and identical in every partition because preparation is replayed identically (section 3). It never inserts, deletes or reorders.
4. The fallback launch-state path at lines 344 to 350 also calls `launch_evidence` per launch state. That path is not partitioned (section 3).

Design: partitions never capture match objects at fork time. They record index ranges and materialize slices only at the end of `analyze()`.

```python
# path_flow.PathFlow (partition mode only; sequential mode records nothing)
self.segments: list[tuple[str, tuple, int, int, int, int]] = []
#            kind      key    match_start, match_end, warning_start, warning_end

def _open_segment(self, kind, key):
    return (kind, key, len(self.state.matches), len(self.state.warnings))

def _close_segment(self, opened):
    kind, key, m0, w0 = opened
    self.segments.append((kind, key, m0, len(self.state.matches), w0, len(self.state.warnings)))
```

1. Everything that is not a fork is recorded as a `shared` segment (preparation inside `launch_variants`, the fallback path, HTTP-only groups, TypeScript, the final `state.warnings.extend(program.warnings)`).
2. Each fork is recorded as a `fork` segment with key `(group_index, launch_index, variant_index, kind, state_index, tool_index)` where `kind` is 0 for `prepared` states and 1 for `initialization_states`.
3. Because `launch_evidence` rewrites in place, a range recorded at fork time still addresses exactly that fork's matches after the rewrite. Slices are cut from `self.state.matches` only after `analyze()` returns, so they contain the final annotated findings with every capture.
4. Preparation findings and warnings (produced by `flow.function(context, env)` inside `prepare_launch`, `http_context.py:741`) fall in a `shared` segment before `start`. `launch_evidence` never touches them, which matches sequential behaviour. Every partition produces them; the parent keeps them from partition 0 only (section 4).

The partition skeleton (the ordered list of segment kinds and keys, without ranges) must be identical across partitions. The parent verifies this and fails closed with `InfrastructureError` if it is not.

## 2. Original preparation context

`entry_group` at lines 274 to 354 uses `entries[0]` at line 279 to select launches through `for_tool`, and `launch_variants(tool, launch)` at line 292 uses that same first tool to prepare startup variants. Filtering `entries` before `entry_group` would change the representative tool and the preparation context. It would also change `state.visit` order in `analyze()` at `sent012.py:27` to `:30`.

Selection therefore happens only inside the fork loop:

```python
# path_flow.py, replacing lines 323 to 328
for tool_index, (current, parameters) in enumerate(entries):
    if self.partition is not None and tool_index % self.partition.count != self.partition.index:
        continue
    check_deadline(self.deadline)
    opened = self._open_segment("fork", (group, launch_index, variant_index, kind, state_index, tool_index))
    fork = copy.deepcopy(self, memo.copy())
    fork.entry_handler(current, {**parameters, **local})
    self._close_segment(opened)
```

1. `analyze()` in `sent012.py` is unchanged in grouping, ordering and `state.visit` calls. Every partition visits every tool, so coverage is identical; the parent keeps partition 0's visits.
2. `entries`, `entries[0]`, `for_tool`, `launch_variants`, `prepare_launch`, `initialization_states`, the memo and `local` are unchanged.
3. `self.partition` is `None` in sequential mode. The code path for a single partition is byte-for-byte the current behaviour apart from the segment bookkeeping.

## 3. Exact partition boundary

Paths that are demonstrably isolated:

1. The deep-copied fork path at lines 323 to 328. Isolation is established by the existing design: `copy.deepcopy(self, memo.copy())` copies all mutable flow state, and the memo shares only `program`, `state`, `reported_warnings`, `registrations.calls`, AST nodes and files (audited in section 4). The retained Linux profile for `meta-image-ssrf-vulnerable` shows 112 top-level `deepcopy` calls and 112 `entry_handler` calls, so every tool analysis on that input ran through this path. The v11 counters show 351 `meta_api_tool.wrapper` interpretations for 43 tools, about 8 per tool, all through forks.
2. The TypeScript fork site at `typescript_path_flow.py:1992` is structurally similar but is out of scope for this proposal. It stays sequential.

Paths that are not isolated, because they mutate the shared flow instance whose state later groups depend on:

1. The no-launch path, `entry_group` lines 281 to 284: `entry_handler` on `self`.
2. The fallback launch-state path, lines 334 to 350: `self.function(launch.function, {})` and `entry_handler` on `self`.
3. HTTP-only groups, `sent012.py:80` to `:82`: `flow.function(tool.handler, bindings)` on `self`. SENT-016 passes `context.python_http_handlers` as entries (`sent016.py:657`), so such groups exist for some inputs.
4. TypeScript analysis after the Python pass (`sent012.py:78`, `sent016.py:660`).
5. Preparation itself: `launch_variants`, `prepare_launch`, `middleware_states`, `http_context.prepare`.

Why these cannot simply run in one partition: they leave state in `self` that later forks deep-copy. Concrete first-touch dependencies include `member_defaults.setdefault` at line 1091 (the first fallback computed for a member key becomes the merge default at line 1271 for the rest of the run), `members`, `callables`, `record_keys`, `mapping_keys`, `globals` outside `entry_group`, `program.parents` updates at `http_context.py:408` and `:711`, and `program.warnings` appended by `for_tool` at `launches.py:141`.

Rule: every partition executes every non-fork path, in the original order, so that its base state before each fork equals the sequential base state. Only partition 0's outputs from those paths are kept. This is exactly-once output, not exactly-once execution. The duplicated cost is the preparation and the non-fork analyses; for the Meta inputs that is preparation only (Linux profile: `prepare_launch` 2 calls, 4.2 profiled seconds; discovery walks about 9 profiled seconds, already duplicated per rule worker today). For an input whose tools all take the fallback path, partitioning yields no gain and doubles that work; that is a cost to accept, not a correctness issue.

Ordering: the parent walks partition 0's skeleton in order. For a `shared` segment it copies partition 0's slice. For a `fork` segment it copies the slice from the partition that owns `tool_index % count`. All other partitions' `shared` slices are discarded after being checked for equal length and equal skeleton position.

## 4. Shared state audit and deterministic reconstruction

Objects shared through the memo at lines 297 to 309, with what I found in the code:

1. `self.program` (`PythonProgram`, `discovery.py:60` onward). Mutable attributes: `warnings` (appended only by `for_tool` at `launches.py:141`, guarded by `if warning not in program.warnings`, always before forks); `parents` (updated at `http_context.py:408` and `:711` during preparation and middleware layering, before forks, deterministic); lazy caches `_resolved`, `_resolved_in`, `local_bindings`, `scope_variables`, `_method_orders`, `_instance_methods`, `_plain_instances`, `_tools`, and the `cached_property` values `launches` and `server_parents`. Every cache is a function of the AST plus a deterministic query, so recomputation in another process yields equal values. No fork-time write to `program` was found other than cache fills.
2. `self.state` (`RuleRunState`, `model.py:79` to `:90`): `matches`, `warnings`, `visits` are append-only lists. `exemptions` is never written by the flow rules (no `.exempt(` call in `path_flow.py`, `http_context.py`, `sent012/015/016.py`). `skip_reason` is never written by the flow rules. `visits` is written only in `analyze()` for all tools and by TypeScript.
3. `self.reported_warnings`: a set used only for first-occurrence suppression in `unresolved` at line 624. Not an output. Its effect must be replayed.
4. `self.registrations.calls` (`registration_flow.py:22` to `:36`): a lazily built map from function node to caller symbols, computed from the AST via `resolve_in`. Pure.
5. AST nodes and `program.files`: read-only after preparation; `ast.copy_location` on synthesized nodes happens inside preparation.

Not shared, deep-copied per fork: `http_context` (including `prepared_states`, `decisions`, `sdk_class_intact`, `launch_paths`), `lifespan_states`, `members`, `member_defaults`, `callables`, `closures`, `globals`, `global_members`, all other flow dictionaries.

Warning identity: `unresolved` suppresses on `(file, lineno, reason)` and emits a message built from `rule_id`, file, line and reason. Message equality is not provably equivalent to identity equality (a relative path could contain the pattern `:<n>: `), so the design records identities explicitly in partition mode:

```python
def unresolved(self, symbol, node, reason):
    identity = (symbol.file.relative_path, getattr(node, "lineno", 1), reason)
    if identity in self.reported_warnings:
        return
    self.reported_warnings.add(identity)
    self.state.warnings.append(ReportWarning(...))          # unchanged
    if self.partition is not None:
        self.warning_identities.append(identity)           # parallel to state.warnings
```

The only other warnings appended to `state.warnings` are the `program.warnings` extension at the end of `analyze()` (identity `None`, part of the final `shared` segment) and TypeScript warnings (shared segment).

Reconstruction in the parent, per rule:

1. Load every partition's `RuleRunState`, `segments`, and `warning_identities`.
2. Assert equal skeletons (kinds and keys, in order) and equal `shared` slice lengths across partitions; otherwise raise `InfrastructureError`.
3. Walk partition 0's skeleton. For each segment select the owning partition (0 for `shared`, `tool_index % count` for `fork`).
4. Append the owner's match slice unchanged. This preserves final captures, because slices were cut after `launch_evidence`, and preserves original order, because the skeleton is the sequential order.
5. For warnings, keep a `seen` set of identities. For each warning in the owner's slice, skip it if its identity is in `seen`, otherwise append it and add its identity. Warnings with identity `None` are appended unconditionally. This reproduces the sequential first-occurrence suppression exactly, including suppression across preparation, states, variants and groups.
6. `visits` are taken from partition 0. `exemptions` and `skip_reason` are taken from partition 0 and asserted equal across partitions.
7. Return the reconstructed `RuleRunState`. `engine._deduplicate` at `engine.py:277` then runs unchanged on the sequential order, so earlier-capture precedence (`{**match.captures, **existing.captures}`) is identical.

Failures, deadlines and cleanup: partitions are additional entries in the existing `processes` dictionary in `run_flow_rules` (`workers.py:53` to `:107`). Any nonzero exit, invalid state, or `TimeoutExpired` already raises `InfrastructureError` and the `finally` block kills and reaps every started process. No partial reconstruction is ever attempted. The absolute deadline is passed unchanged in the input pickle.

Example that breaks naive approaches. Two tools, two partitions, round robin (tool 0 and 2 in partition 0, tools 1 and 3 in partition 1), one prepared state:

1. Tool 1 and tool 2 both reach helper `auth.py:137` through a recursion limit, so both would call `unresolved(auth.py, 137, "recursive, deeper than 64 calls, or unsupported helper")`.
2. Tool 1 and tool 2 both reach a sink at `api.py:200` with different `flow_locations`.
3. Preparation produced one SENT-016 finding in `server.py:main`.

Sequential output: preparation finding; tool 0 findings; tool 1 findings including `api.py:200` with tool 1's captures, then the warning; tool 2 findings including `api.py:200` with tool 2's captures, no warning. After `_deduplicate`, the `api.py:200` finding keeps tool 1's captures.

Naive concatenation of partition 0 then partition 1 gives: preparation finding, tool 0, tool 2 with its `api.py:200` and its warning, preparation finding again, tool 1 with its `api.py:200` and its warning. Deduplication would keep tool 2's captures, the preparation finding appears twice, and the warning appears twice at the wrong position. Sorting matches by location would not restore tool order, and deduplicating warnings by text would keep the wrong occurrence. The skeleton replay produces the sequential list exactly: preparation from partition 0 once; slot 0; slot 1 from partition 1 with its warning appended and its identity marked seen; slot 2 from partition 0 with the warning skipped.

## 5. Concurrency and resource limits

Measured facts:

1. Current maximum simultaneous processes: one per selected flow rule, at most 4 (`workers.py:18`, `:53`), only when at least 2 rules are selected, `os.cpu_count()` is at least 2, and source exceeds 128 KiB.
2. Per-worker CPU seconds on the operator input, v17: SENT-012 48.4, SENT-015 59.6, SENT-016 57.7, SENT-014 1.7, parent 6.6.
3. Linux runner: `cpu_count` 4, `MemTotal` 16,373,452 kB, kernel `Linux-6.17.0-1022-azure-x86_64`, load before runs 0.80 (`v10-hosted-05309f9/.../environment.json`). Child maximum RSS per run 270,816 to 345,024 kB. macOS worker maximum RSS 167 MB.
4. During the six Linux timeouts, child CPU was 319 to 362 seconds per 120-second wall, that is 2.66 to 3.02 CPU-seconds per wall-second.

Assumptions, stated as such:

1. The standard GitHub Linux runner's 4 vCPUs are two physical cores with SMT. I could not find CPU topology (`lscpu`, threads per core) in any retained artifact; only `cpu_count` was recorded.
2. Native duplicated setup per extra process on Linux is 3 to 5 seconds (discovery about 9 profiled seconds, preparation 4.2 profiled seconds; cProfile inflates call-heavy code by roughly 2x).

Proposed limits:

1. Partition count 2 for SENT-012, SENT-015 and SENT-016 only when `os.cpu_count() >= 4`. Below 4 CPUs, behaviour is unchanged (1 partition). No configuration knob.
2. SENT-014 stays a single process (1.7 CPU seconds).
3. Maximum simultaneous processes: 7 (3 rules x 2 partitions + SENT-014), plus the parent.
4. Memory: 7 x 345 MB is about 2.4 GB against 16 GB on the runner and against the local machine. Each partition holds a full parsed program and its own flow state.
5. Load balancing: round robin by tool index. This is deterministic and needs no cost estimate. Tool costs are not measured; if one tool dominates, the gain shrinks toward the single-tool time. A later refinement could interleave by handler size, but not in this proposal.
6. Duplicated preparation: each extra process repeats interpreter start, unpickle, discovery and preparation. Total CPU rises by roughly 3 x 3 to 5 seconds.

Why it may or may not help the runner. Let `T` be total heavy CPU (about 167 seconds local-equivalent), `W` the slowest worker (about 60), and `E` the effective parallelism the runner delivers for 4 busy Python processes:

1. Today the wall is bounded by `W` because 3 busy processes fit in 4 vCPUs. The measured 2.66 to 3.02 CPU-seconds per second is consistent with 3 saturated processes; it cannot tell whether the fourth vCPU would add real throughput, because CPU time is charged at whatever per-thread speed the core delivers.
2. With 6 balanced partitions, wall is about `max(T / E, largest partition) + duplicated setup`.
3. If `E` is 3 (the fourth vCPU adds nothing), wall goes from 60 to about 56 plus setup, roughly 0 to 5 percent. Partitioning would not be worth its complexity.
4. If `E` is 3.5, wall is about 48, roughly 20 percent. If `E` is 4, about 42, roughly 30 percent.
5. Therefore partitioning should not be built before `E` is measured. Section 9 proposes a two-minute Linux probe that measures it without the scanner or any input.

## 6. Micro-corrections, separately reviewable

All five are intended to be output-identical by construction. Each would be one commit with its own property test, reviewable and revertible on its own. Their performance would be measured once, as a bundle, because the expected individual gains (1 to 5 percent each) are below the demonstrated run-to-run variability, and a per-item native experiment would be the open-ended loop this project must avoid. Attribution without more native runs: one non-modifying sampled profile of the candidate (the v17 sampler, `v17-sampled-profile/worker-profile.py`, which replaces no scanner method) compared function-by-function with the retained v17 baseline profile at `127763c`. If the bundle regresses, the bundle is reverted as a whole; no per-item bisection is proposed.

Why not bundle with partitioning: partitioning changes process count, memory and a documented resource contract, and its benefit depends on section 5's unmeasured `E`. Mixing it with exact CPU reductions would make a wall-time result uninterpretable and could hide a CPU regression behind a scheduling gain. The micro-corrections reduce CPU in every environment, including the historical batches and any 2-CPU host; partitioning does not.

### M1. Cache the `Value` hash

Function: `Value` at `path_flow.py:26` to `:48`. Evidence: Linux profile `<string>:2(__hash__)` 1,424,847 calls, 0.93 s self, 1.53 s cumulative, plus 1.45 M `builtins.hash`; v17 leaf share 2.9 to 3.0 percent per worker. Every `combine` call hashes a tuple of `Value`s for the `_combine` LRU key; the same immutable `Value` objects are hashed repeatedly across merges.

```python
@dataclass(frozen=True, slots=True)
class Value:
    ...  # the 17 existing fields, unchanged, in the same order
    _hash: int | None = field(default=None, init=False, compare=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_hash", None)   # slot exists before first hash

    def __hash__(self) -> int:
        cached = self._hash
        if cached is None:
            cached = hash((self.sources, self.key, self.resolved, self.contained,
                           self.locations, self.path_object, self.repository_object,
                           self.instance, self.option_safe, self.url_checks,
                           self.operator_credential, self.credential_fallback,
                           self.credential_present, self.maybe_missing, self.maybe_none,
                           self.operator_opt_in, self.checked_path_parent))
            object.__setattr__(self, "_hash", cached)
        return cached
```

Correctness notes and risks:

1. The tuple is the same tuple the generated `__hash__` uses (all compare fields in definition order), so hash values are unchanged, not merely consistent.
2. `compare=False` keeps `__eq__` unchanged. `init=False` keeps `dataclasses.replace` working; it skips non-init fields and the new object recomputes lazily. `__deepcopy__` already returns `self`.
3. With `eq=True, frozen=True` and an explicit `__hash__`, `dataclass` leaves the explicit method in place.
4. `Value` objects are not pickled across the worker boundary (`RuleRunState` carries strings and ranges), but `__post_init__` guarantees the slot is always set, so pickling would still work.
5. Risk: a test that constructs `Value` positionally with 18 arguments would break; none exists.

### M2. Single-pass generic branch of `_combine`

Function: `_combine` at `path_flow.py:58`, generic branch lines 130 to 157. Evidence: v16 measured the generic body at 7.81, 5.34 and 6.81 percent of worker CPU with 343 K, 322 K and similar generic calls; Linux profile `_combine` 4.13 s self plus about 1.5 s in its per-field generator expressions (lines 62, 134 to 156). The current branch iterates the operand list about 17 times, once per field, each through a generator frame.

```python
    # generic branch, after identical-value, None/#missing and two-value handling
    sources: set[str] = set(); locations: set[tuple[str, int]] = set(); keys: set[str] = set()
    resolved = path_object = repository_object = credential_present = True
    contained = option_safe = checked_path_parent = True
    tainted_seen = operators_seen = False
    url_checks: frozenset[str] | None = None
    opt_in: frozenset[str] | None = None
    operator_credential = credential_fallback = maybe_missing = maybe_none = False
    instance = values[0].instance if values else None
    same_instance = True
    for v in values:
        sources |= v.sources; locations |= v.locations; keys.add(v.key)
        resolved &= v.resolved; path_object &= v.path_object
        repository_object &= v.repository_object; credential_present &= v.credential_present
        credential_fallback |= v.credential_fallback
        maybe_missing |= v.maybe_missing; maybe_none |= v.maybe_none
        if v.instance != instance: same_instance = False
        if v.sources:
            tainted_seen = True
            contained &= v.contained; option_safe &= v.option_safe
            checked_path_parent &= v.checked_path_parent
            url_checks = v.url_checks if url_checks is None else url_checks & v.url_checks
        if v.operator_credential:
            operators_seen = True
            opt_in = v.operator_opt_in if opt_in is None else opt_in & v.operator_opt_in
    ordered = sorted(keys)
    return Value(
        frozenset(sources),
        key or (ordered[0] if len(ordered) == 1 else _key("merge", *ordered)),
        bool(values) and resolved, tainted_seen and contained, frozenset(locations),
        bool(values) and path_object, bool(values) and repository_object,
        instance if (values and same_instance) else None,
        tainted_seen and option_safe, url_checks if tainted_seen else frozenset(),
        operators_seen, credential_fallback, bool(values) and credential_present,
        maybe_missing, maybe_none, opt_in if operators_seen else frozenset(),
        tainted_seen and checked_path_parent,
    )
```

Correctness notes and risks:

1. Every reduction mirrors an existing expression: `union`, `all`, `any`, `frozenset.intersection` over tainted or operator subsets, `sorted` unique keys, and the `instance` equality test against `values[0]`.
2. The empty-operand case must match: today it yields `_key("merge")`, all-`and` fields false, `instance` `None`. The pseudocode preserves that.
3. This branch is reached only after the identical-value branch (lines 61 to 77) and the None/`#missing` branch (lines 78 to 84); those stay untouched, as does the two-value branch.
4. Risk is purely a transcription error, which the property test in section 8 targets with random operands over every field.

### M3. Explicit loop in the multi-branch `merge`

Function: `merge` at `path_flow.py:1243`, per-key reuse test at lines 1284 to 1291. Evidence: v15 counted 6.08 M multi-branch key visits with 5.15 M direct reuse; Linux profile `merge` 5.18 s self and `path_flow.py:1287(<genexpr>)` 877,996 calls; v17 shows merge inclusive minus `combine_instances` inclusive of 6.1, 4.0 and 5.8 percent per worker. The `all(...)` generator creates a frame per key for three or more branches.

```python
        for name in set().union(*(b.keys() for b in branches)):
            default = self.member_defaults.get(name, unknown)
            value = first.get(name, default)
            reuse = False
            if not name.startswith("#path:") and (
                value.sources
                or not (value.contained or value.checked_path_parent
                        or value.option_safe or value.url_checks)
            ):
                reuse = True
                for branch in rest:                      # same short-circuit order
                    other = branch.get(name, default)
                    if other is not value and other != value:
                        reuse = False
                        break
            if reuse:
                env[name] = value
                continue
            values = [branch.get(name, default) for branch in branches]
            env[name] = (Value(contained=all(v.contained for v in values))
                         if name.startswith("#path:") else self.combine_instances(values))
```

Correctness notes and risks:

1. The `second` fast path becomes the general loop with one element in `rest`; evaluation order and short-circuiting are identical.
2. The guard-stripping condition, `member_defaults` fallback, `#path:` handling, and `combine_instances` side effects are unchanged.
3. Set-based key iteration order is unchanged (already hash-random per worker process today).

### M4. Memoise the literal parse inside `member_label`

Function: `member_label` at `path_flow.py:168`. Evidence: Linux profile `ast.literal_eval` 142,251 calls, 2.19 s cumulative including `compile` 1.05 s; called from `member_label` (71,304), `sent015.expression_value` (32,104), `sent015.literals` (20,488), `compared_strings` (15,579); v17 inclusive 1.6 to 1.9 percent.

```python
@lru_cache(maxsize=4096)
def _literal_label(key: str) -> object:
    try:
        label = ast.literal_eval(key)
        hash(label)
        return label
    except (ValueError, SyntaxError, TypeError):
        return UNKNOWN_MEMBER

def member_label(value: Value) -> object:
    return UNKNOWN_MEMBER if value.sources else _literal_label(value.key)
```

Correctness notes and risks:

1. `ast.literal_eval` is deterministic for a given string, and only hashable results are cached, so returning a shared object is safe; hashable literals are immutable.
2. The exception set is unchanged. Exceptions not caught today (for example `RecursionError`) remain uncaught.
3. Cache size 4096 matches the existing `_combine` and `_key` caches; it is not a blind increase. Most keys are unique digests that miss, so the gain is bounded by repeated literal keys such as `'True'`, `'None'`, `'0'` and string constants. This is the weakest item; it can be dropped without affecting the others.
4. The `sent015.expression_value` prefix loop at `sent015.py:378` to `:387` could call `_literal_label` too, but that would change its exception set (`TypeError` is not caught there today); it is excluded from this item.

### M5. Skip the empty-prefix destination check

Function: `URLFlow.expression_value` at `sent015.py:390`, calling `fixed_destination` at `:73`. Evidence: Linux profile `fixed_destination` 483,793 calls, one per expression; v17 SENT-015 inclusive 4.6 percent (`urlsplit` on an empty string each time).

```python
        if prefix and fixed_destination(prefix):
```

Correctness notes and risks:

1. `fixed_destination("")` is `False` today: `urlsplit("")` has scheme `""`, which is not in `{"http", "https"}`.
2. No other behaviour depends on the call. The TypeScript call site at `:1055` is left unchanged.

### Items considered and excluded

1. A cheaper `dataclasses.replace` substitute: 430,980 calls, 4.37 s self, 9.37 s cumulative in the Linux profile. A hand-written constructor call would save perhaps 1 to 2 percent; the v13 attempt to skip no-op replacements was measured inconclusively under two-sample noise, not shown harmful. Excluded to keep the bundle small.
2. Reordering `isinstance` dispatch in `expression` at `:1520`: exact but about 1 percent. Excluded.
3. Replacing `json.dumps` inside `_key` at `:160`: changes key digests. Keys are internal, but proving that no key reaches a report or ordering decision is more review than the 1 to 2 percent is worth. Excluded.
4. Fewer `check_deadline` calls: 2.83 M calls, 1.6 s cumulative, and it is the deadline contract. Excluded.

## 7. Evidence and uncertainty

Directly measured:

1. Local batch versus Linux wall at the same scanner (`v7-final-development-rules-first`, `v8-hosted-88a559e` at `62987a6`; `v9-final-development-rules-first`, `v9-hosted-a4766a9` at `7555a9d`): `meta-operator-fallback-vulnerable` 95.0 s local, 115.9 s Linux; its mutation 80.4 s local, 116.5 s Linux; every Meta image input timed out on Linux while taking 88.5 to 105.1 s locally; `meta-operator-fallback-fixed`, `-fixed-mutation` and `-safe` timed out on Linux, and two of them also timed out locally in the v9 batch.
2. Isolated local baselines (v13, v14 at `2ac39aa`-equivalent bytes): operator fixed-mutation 69.9, 79.4, 75.1, 74.2 s; image vulnerable 68.0, 83.6, 74.6, 81.3 s; child CPU 169 to 201 s; load average 4.6 to 6.5 on 8 cores.
3. v17 per-worker CPU and sampled shares; v15 and v16 counters, as cited above.

Derivation of the required improvement, with assumptions:

1. For the two Meta inputs that completed on Linux, Linux wall over local batch wall is 1.22 and 1.45.
2. For the inputs that timed out, Linux wall is censored: it is at least 120 s and otherwise unknown. Local batch wall for the operator fixed inputs is also censored at 120 s in v9 and was 108.6 and 119.5 s in v7.
3. Assumption A: the completed ratios (1.22 to 1.45) also apply to the censored inputs. Then the operator fixed inputs need at least 132 to 173 s on Linux, and reaching 105 s requires a 20 to 40 percent reduction. This is the source of the earlier "25 to 35 percent" figure. It is an extrapolation, not a measurement.
4. Lower bound without assumption A: Linux times are at least 120 s, so at least a 13 percent reduction is needed to reach 105 s. The true requirement lies between this bound and the extrapolation.
5. Local isolated numbers cannot be used directly: the local batch ran 25 to 50 percent slower than isolated runs of the same input, and the isolated runs themselves had load averages above 4.

Derivation of the removable merge share, about 4 to 6 percent:

1. v17 inclusive shares: `merge` 24.8, 19.2, 22.6 percent; `combine_instances` 18.7, 15.2, 16.8 percent (called almost only from `merge`). The difference, 6.1, 4.0 and 5.8 percent, is the per-key scanning, defaults, guard normalization and subclass wrapper work. That is the part a change-tracking design could avoid at most; the combinations themselves remain.
2. v16 measured the generic combine body at 5.3 to 7.8 percent, which is real combination work of different values.
3. These are sampled and instrumented shares with the limitations recorded in `v17-sampling-assessment.json`; they are not exact partitions of CPU.

What the v11 signature does and does not establish:

1. The counter keyed each helper call on the fork object, the full call-site stack and the active set, so cross-tool and cross-state repeats were undetectable by construction. The 108 repeats therefore do not show that helper contexts are unique.
2. A reduced signature (node plus structurally compared bindings, with or without `locations`) would only count candidate repeats. It would not show equal side effects on `members`, `member_defaults`, `record_keys`, `callables`, `closures`, `path_conditions`, `http_context`, `launch_states`, findings, warnings or provenance, and it would not show that a cached result could be replayed safely. Establishing that requires a design for side-effect capture and replay and its own correctness argument. One profile cannot settle safe reuse; it can only say whether the question is worth designing for. That is why no reuse work is proposed here.

## 8. Correctness tests before any measurement

All are ordinary unit tests on small synthetic programs built with `tests.test_python_discovery.program`, plus property tests on `Value`. None runs a corpus input.

Micro-correction tests:

1. `test_value_hash_cache_matches_field_tuple`: for random `Value`s, `hash(v)` equals `hash(tuple of the 17 fields)`, repeated hashing returns the same value, `replace(v, key="x")` has a fresh cache, equality ignores the cache, `copy.deepcopy(v) is v`, and `pickle` round-trips.
2. `test_combine_generic_single_pass_matches_reference`: keep a verbatim copy of the current generic branch in the test; for 2,000 random operand lists (lengths 0 and 3 to 8, all fields randomized, duplicates, `None` and `#missing` keys, explicit and empty `key`), assert equality of every field and the key against the reference. Extend `test_repeated_values_preserve_distinct_branch_guards` with the same operands.
3. `test_merge_multi_branch_loop_matches_reference`: random branch dictionaries with `member_defaults`, `#path:` keys, untainted guarded values, and 2 to 5 branches; compare `env` after the current and new implementations, including `instance_alternatives` side effects.
4. `test_member_label_memo`: literal, non-literal, unhashable and digest keys give the same results as `ast.literal_eval` semantics; tainted values return the sentinel without parsing.
5. `test_fixed_destination_empty_prefix_is_false`: guards `fixed_destination("")` and checks that a non-empty public prefix still sets the three URL checks.
6. Existing guard, alias, mutation, missing/None and provenance tests in `tests/test_python_state_flow.py`, `tests/test_ssrf.py`, `tests/test_credential_fallback.py` and the full suite, unchanged.

Partitioning tests (only if section 5's probe justifies building it; listed now so the design is reviewable):

1. `test_partition_equivalence_multiple_tools_and_variants`: a FastMCP program with four tools, a launch with a `json_response` branch (two variants), a middleware layer with two continuation paths, and a stdio launch; sequential `RuleRunState` equals the reconstruction of partitions 0 and 1 for SENT-012, SENT-015 and SENT-016: matches, every capture, warnings, visits, in order.
2. `test_partition_preparation_findings_once`: a SENT-016 sink inside `main()` appears exactly once at its sequential position.
3. `test_partition_repeated_warning_first_occurrence`: two tools in different partitions hitting the same unresolved helper; one warning, at the earlier tool's position.
4. `test_partition_launch_annotations_final`: `launch_transports`, `launch_branches` and appended `flow_locations` equal sequential values after reconstruction.
5. `test_partition_duplicate_ranges_keep_earlier_captures`: two tools in different partitions reaching the same sink with different `flow_locations`; after `engine._deduplicate`, captures equal the sequential result.
6. `test_partition_fallback_and_http_groups_once`: a program whose launch preparation returns `None` (an `auth=` keyword on `FastMCP`) plus one FastAPI handler; outputs identical to sequential and produced once.
7. `test_partition_typescript_unchanged`: a workspace input with TypeScript files; TypeScript findings and warnings appear once, after the Python findings.
8. `test_partition_skeleton_mismatch_fails_closed`: a forged partition state with a different skeleton raises `InfrastructureError`.
9. `test_partition_failure_kills_all`: one partition exiting nonzero raises `InfrastructureError` and leaves no live processes; deadline expiry in one partition behaves as today.
10. `test_partition_disabled_below_four_cpus`: with `os.cpu_count` patched to 2, exactly one process per rule is started.

## 9. Bounded experiment proposal

### 9.1 Stage 1: micro-correction bundle (requested for approval now)

Baseline and candidate identities:

1. Baseline: scanner bytes at HEAD `c07ffeb8a621d00a0ebbe762eda9444ff1f76c40`, source SHA-256 `9639435c0657e28f7c9a16ff25b05b4101910241dc35413f5c26392f9fc36647`, `path_flow.py` `322aa43e…`, harness `9bfc9229…`, lock `c34da413…`. v13, v14 and v17 observations are historical context only; they are not pooled into this comparison.
2. Candidate: M1 to M5 (M4 optional) committed as one commit per item on `phase22/integration` (or a topic branch), followed by their tests; frozen as the single resulting commit whose scanner source SHA-256, `path_flow.py` and `sent015.py` hashes are recorded in a versioned proposal receipt before any observation. All local checks (Ruff, format, strict mypy, full suite, schema drift) must pass at that commit before observations start.
3. No other product change is allowed in the candidate. Any further edit invalidates the observations and closes the budget.

Inputs and configuration:

1. `meta-image-ssrf-vulnerable` and `meta-operator-fallback-fixed-mutation`, corpus manifest SHA-256 `a5ea6930e9cd5522f9420bef57875fea5d44d1d1c45fb5136a02a7c0292a9c67`.
2. `atlassian-upload-fixed`, manifest SHA-256 `f69d043cab43e5785e7c8a9dae430bcf146c105a0d23d1d77bc4089637377682`.
3. Configuration SHA-256 `f996757169ce1597b3c6b052f77b267098080ea4557d5b956c953a79f9f813dd`, rules-only treatment, through `scripts.phase20_measurements.measure` with the frozen manifest subset, as in `/private/tmp/phase22-v17-run.py`, with `OpenAITransport.create` disabled and zero model calls asserted.

Counts and caps:

1. Maximum candidate attempts: 1.
2. Maximum native observations: 18 (3 baseline + 3 candidate per input).
3. Maximum profiles: 1, a non-modifying sampled profile of the candidate on `meta-operator-fallback-fixed-mutation` using the v17 sampler, taken after the 18 native observations, for attribution only.
4. Per-input cap: unchanged 120 seconds native and 120 seconds end-to-end; the profile has the same caps.
5. Nominal maximum: 19 executions x 120 s = 38 minutes, plus the conditional regressions below.

Run order and load conditions:

1. Per input, alternate baseline and candidate: B, C, B, C, B, C, sequentially, one process tree at a time, no overlapping owned work.
2. Before each observation record the 1-minute load average; if it is 2.0 or higher, wait and retry the check up to three times at 60-second intervals, then defer the whole sequence and record the deferral. This precondition is new; the v13, v14 and v17 observations ran at load 4.6 to 6.5.
3. Record for every observation: scanner identity before and after, git diff emptiness, wall, native duration, parent and child `getrusage`, load before and after, report SHA-256, stable SHA-256, and the full report and SARIF.
4. Unique labels through `/private/tmp/phase22-check.py`; it does not prevent overwriting, so the labels must be new.

Equivalence criteria:

1. Every candidate report must equal the corresponding baseline report as an entire ordered document, including findings, captures, warnings order and coverage, excluding only `applied_at`, `completed_at`, `duration_ms`, `execution_latency_ms`, `finding_id`, `latency_ms`, `origin_latency_ms`, `reviewed_at`, `scan_id`, `started_at`, `timestamp`.
2. Native JSON and SARIF must validate.
3. Any inequality stops the experiment, reverts the candidate product code, and retains the evidence.

Retention criteria (prospective):

1. All 18 native observations complete within both caps.
2. Per Meta input: candidate median child CPU is at most 0.92 times the baseline median, and candidate median wall is at most 0.95 times the baseline median wall.
3. Per input, including Atlassian: candidate median child CPU and wall are not above the baseline medians.
4. No candidate observation exceeds the baseline maximum on either metric for that input (three-sample maximum).
5. Variability is reported as all three values per cell, the median, and the range; no pooling across inputs or with historical observations.

Interruptions, failed runs and unused observations:

1. No retries. An interrupted or failed observation is retained and counted; the experiment stops at that point and retention is reported as not established.
2. Unused observations at any stop are closed, not carried forward.
3. A baseline timeout on this host stops the experiment as an environment failure and is reported as such.

Conditional final regression budget:

1. Only if retention holds: all three exposed SSRF families, five inputs each, twice, on the frozen candidate: 30 native observations at the unchanged caps, with the unchanged condition gates (two vulnerable condition matches per batch, zero matching fixed or control alerts), ordered repeat equivalence and source assessment of any delta.
2. Any failure reverts the candidate and retains the evidence.

Stopping and reversion:

1. Stop after the 18 observations and the one profile, or earlier on any failure.
2. If retention holds and the 30 regressions pass, the candidate is retained on the branch and the Linux diagnostic in 9.3 is requested separately.
3. Otherwise revert product code, keep tests and all evidence, close the budget, and do not propose a second micro-optimization experiment.

### 9.2 Stage 0: Linux scaling probe (separate small approval, no scanner)

Purpose: measure the effective parallelism `E` of the standard runner for 1 to 6 CPU-bound Python processes, to decide whether partitioning is worth building.

1. One `workflow_dispatch` job on `ubuntu-latest`, added to the workflow as a separate gated job like the existing `phase22-historical-final`, runnable only on `phase22/integration`.
2. Steps: record `nproc`, `lscpu`, `/proc/cpuinfo` and `/proc/meminfo`; then for N in 1, 2, 3, 4, 6 run N concurrent copies of a pure-Python busy loop for 20 CPU-seconds each and record wall and per-process CPU; upload the JSON as an artifact.
3. No scanner import, no corpus input, no dependency beyond the interpreter, no paid call. Runner time about 3 minutes; deadline 10 minutes.
4. Decision rule: build partitioning only if `E` at N = 4 is at least 3.5 and at N = 6 is not lower than at N = 4. Otherwise partitioning is closed as not worth its complexity.
5. Approval boundary: one dispatch. It does not authorize any scanner run.

### 9.3 Linux diagnostic after a retained Stage 1 (separate later approval)

1. Inputs: `meta-image-ssrf-vulnerable` twice and `meta-operator-fallback-fixed-mutation` twice: 4 native runs, no profiles.
2. Scanner: the frozen Stage 1 candidate commit, pinned by ref in a new approval directory using the existing optional job pattern; standard `ubuntu-latest` runner; unchanged 120-second native and end-to-end caps; 30-minute job ceiling.
3. Pass criterion to request the full sequence: all four complete with native and end-to-end times at or below 105 seconds, and each report equals the corresponding local candidate report except volatile fields.
4. Any timeout or inequality stops; no retry on that scanner.
5. The full 25 + 45 + 45 sequence retains its own later approval, unchanged bounds and gates. Fresh evaluation and final acceptance remain separate checkpoints.

### 9.4 Stage 2: partitioning (not requested now)

Only if Stage 0 satisfies its decision rule and Stage 1 is retained. It would be its own proposal with the same experiment shape as 9.1, the tests of section 8, a documented change to the worker contract in `ARCHITECTURE.md`, and its own Linux diagnostic.

## 10. Revised recommendation

1. Reject branch-state change tracking, for the reasons in the first review: at most 4 to 6 percent removable, and it must reproduce the untainted guard stripping and member defaults that a delta design naturally skips.
2. Do not bundle partitioning with the micro-corrections. Its benefit on the runner depends on `E`, which no retained artifact measures; under the SMT-pessimistic assumption it is near zero.
3. Approve Stage 1 as written: five reviewable, output-identical corrections, one candidate, 18 native observations, one non-modifying profile, the load precondition, three-sample medians, and a hard stop. Expected effect from the retained profiles is 10 to 15 percent of worker CPU. That is real and portable, but by the derivation in section 7 it is probably not enough on its own to complete all ten Meta inputs on Linux. I am saying that plainly so the approval is not read as a promise.
4. Approve Stage 0 as a separate two-minute probe. If it shows the fourth vCPU adds throughput, partitioning becomes the next bounded step with a plausible combined 25 to 35 percent. If it does not, the remaining paths are a dependency-aware reuse redesign, which needs its own design before any measurement, or a timing-scope decision that keeps the 15 of 25 Linux result and ten Meta timeouts visible.

The decision requested: approve or decline Stage 1 (9.1) and Stage 0 (9.2) as two separate approvals. Nothing else is requested, and nothing has been started.
