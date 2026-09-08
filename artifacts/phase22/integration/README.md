# Integration evidence, batches 1–6

This packet preserves intermediate implementation, failures and measurements
through source commit `536bb69`. **It is not final technical acceptance.**
[requirements.md](requirements.md) lists the complete outstanding contract;
[progress.md](progress.md) explains source-specific results and limitations.

The first batch covers `536bb69`; subsequent numbered batches extend it.
Batch 6 (`evidence-v6.tar.gz`, `evidence-v6.json`) adds 251 files through
`5065f16`, including the exact `f12e891` full-suite milestone, its coverage
database, the 18-input incomplete development run, TypeScript HTTP regressions,
and the five-input Kubernetes measurement/adjudication. Extract batches in
numeric order into the same evidence directory. Verify each batch immediately
after extraction using its own manifest before applying the next batch; later
versions may retain newer bytes at a shared diagnostic path. Sealed archives
are unchanged. Source-specific limits and failed attempts are in `progress.md`.

`evidence-v1.tar.gz` is lossless. `evidence-v1.json` records its SHA-256 and the
size and SHA-256 of every member. Every archived member was read back and checked
against its original bytes. Expanded files remain locally available but are
ignored by Git; fresh checkouts recover them from the archive.

```sh
mkdir -p /tmp/phase22-evidence
tar -xzf artifacts/phase22/integration/evidence-v1.tar.gz -C /tmp/phase22-evidence
```

Verify extracted files with the standard library:

```python
import hashlib
import json
from pathlib import Path

packet = Path("artifacts/phase22/integration")
manifest = json.loads((packet / "evidence-v1.json").read_text())
assert hashlib.sha256((packet / manifest["archive"]).read_bytes()).hexdigest() == manifest["sha256"]
for item in manifest["files"]:
    data = (Path("/tmp/phase22-evidence") / item["path"]).read_bytes()
    assert len(data) == item["bytes"]
    assert hashlib.sha256(data).hexdigest() == item["sha256"]
```

Each command record includes its arguments, working directory, environment
overrides, source commit, tracked-diff hash, exit code and raw log. Later records
also retain the tracked patch. The earliest records did not preserve untracked
source bytes; their final implementation commits and failure logs are retained,
but they are not exact intermediate-source reconstruction packets. The updated
runner additionally archives untracked source/tests before future commands.
`diagnostic-sources.tar.gz` and `diagnostics-current.tar.gz` preserve diagnostic
scripts; their adjacent JSON files give per-file hashes. Diagnostics were never
used as substitutes for production measurements.

Measurements use the existing locked root environment and the active worktree's
`PYTHONPATH=src`. Restore the recorded source commit in a separate worktree and
run the command in its JSON record with that environment. The Phase 22 records
bind the unchanged frozen manifest, scanner source, harness, configuration and
report hashes. Reproduction requires the original corpus archives already
referenced by that manifest. The per-input static deadline remains 120 seconds.

The two final development commands in this batch select only
`dbt-option-selection` and `meta-image-ssrf`, using the existing
`scripts.phase20_measurements.measure` runner and authorized
`scripts.phase22_corpus.frozen()` validation. They make no model calls and do not
execute target code. Their source revision is `536bb69`; their results are scored
separately in [development-conditions.json](development-conditions.json).
The earlier dbt source review is retained in
[dbt-adjudication.json](dbt-adjudication.json). Historical Phase 20 source,
results, captures, costs and the unadjudicated 70-warning backlog are unchanged.

The milestone full suite belongs to `192296d`, not the later candidate.
Focused checks after later changes do not replace the final full quality gate,
45-input deterministic repeats, frozen holdout, competitor run, Docker campaigns,
installed-wheel/Action/isolation/hosted OS matrix or reviewed-tier evaluation.
Concurrent timings are verification latency, not isolated throughput.

No paid approval packet or consolidated final PR is ready. Paid calls, merge,
publication, human acceptance and external pilot evidence remain separate
checkpoints; substantial authorized implementation also remains.


The second packet, `evidence-v2.tar.gz`, adds source-flow regressions through
`d259126`, including recorded failures and corrections, command/source patches,
untracked regression-source snapshots, and the exposed Atlassian profiling run.
Its 237 files were read back and checked against `evidence-v2.json`. Extract it
after version 1 into the same directory. It excludes the still-running second
full-milestone records; those remain expanded until their result is available.

```sh
tar -xzf artifacts/phase22/integration/evidence-v2.tar.gz \
  -C /tmp/phase22-evidence
```

The Atlassian profile completed its harness command but the selected input was
**incomplete**: the 120-second static deadline expired. Profiling and concurrent
verification add overhead; this is not an isolated-throughput result. The raw
profile identifies repeated HTTP-scope and tool-discovery traversals for correction.


`evidence-v3.tar.gz` adds 111 files through `de1af5a`, including the completed
second milestone, its original mypy/cache failures, the subsequent corrections,
SDK HTTP caller/CLI regressions, and the repeated exposed Atlassian profile.
Every member was read back and checked against `evidence-v3.json`.

```sh
tar -xzf artifacts/phase22/integration/evidence-v3.tar.gz -C /tmp/phase22-evidence
```

The second full milestone passed 1010 tests, 36 skipped, with 87.38% branch
coverage at `d259126`. At `aaa759a`, the repeated instrumented Atlassian run
completed (84.2 seconds in static analysis, 93.2 seconds including reporting).
It reported 90 SENT-003 candidates and one SENT-012 candidate, and **no SENT-016
condition hit**. Completion does not establish detection of the labeled fallback.
The subsequent SDK HTTP source changes pass 201 affected regressions but have
not been measured against that condition yet. No final repeated benchmark,
fresh holdout, runtime campaign, paid review or acceptance gate is implied.

Batch 4 adds `evidence-v4.tar.gz` / `evidence-v4.json`: 437 files through
`9d396a4`, covering the preserved constructor work, campaign migration, Docker
failures/recovery, failed full milestone, corrections and bounded lifespan flow.
Every member was read back against its hash. Extract after batches 1–3 and run
the same verification snippet with `evidence-v4.json`:

```sh
tar -xzf artifacts/phase22/integration/evidence-v4.tar.gz -C /tmp/phase22-evidence
```

The full milestone failed and overlapped subsequent edits; its coverage output
is not evidence for a fixed source revision. The exposed Atlassian condition
still misses. See the batch-4 section in `progress.md` for exact limits, retained
failed attempts and diagnostic-source reconstruction limitations.


Batch 5 adds `evidence-v5.tar.gz` / `evidence-v5.json`: 439 files through
`4d88844`, including source-established service construction, client credential
sinks, interpretation profiles, incomplete Atlassian runs, regressions and their
failed/corrected checks. Each archived member was read back against its SHA-256.
Extract after batches 1–4 and use the existing verification snippet with
`evidence-v5.json`:

```sh
tar -xzf artifacts/phase22/integration/evidence-v5.tar.gz -C /tmp/phase22-evidence
```

The packaging command was the locked environment's Python running
`/private/tmp/phase22-package-evidence-v5.py` (exit 0). The script is retained in
`diagnostics-v5.tar.gz` inside the packet; it refuses to overwrite the sealed
version-5 archive/index. The archive holds 2,892,761 raw bytes in 589,041 compressed
bytes. Per-command JSON records link exact commands, source patches, diagnostic
snapshots and exit codes. Later documentation bookkeeping is recorded in Git.
The input deadline and the frozen credential-fallback condition remain unmet;
four incidental single-tool client candidates are not condition hits.

Batches 6 and 7 extend that history without replacing the earlier seals. Batch 6
contains 251 files through `5065f16`, including the fixed `f12e891` full-suite
milestone, eighteen exposed gap measurements and Kubernetes development scoring.
Batch 7 contains 531 added/changed files through `2a332f2`, including the original
dirty September 8 handoff/recovery archive, corrected registration and containment
flows, the fixed `4dfd24c` full suite and coverage, Excel/mobile/Meta/Mastra
measurements, revised unrelated-finding adjudication and all failed regressions.
Every member was read back against its per-file SHA-256. Batch 7 is 121,265,808 raw
bytes in 3,563,339 compressed bytes; archive SHA-256:
`68cdc015de92912b4dd746000f28ca6a5b1521ab9bc4f74d6e78a7ec434837f6`.

Extract in order, verifying each batch against its own manifest before extracting
the next batch, because later batches can retain newer diagnostic files at the
same relative path:

```sh
tar -xzf artifacts/phase22/integration/evidence-v6.tar.gz -C /tmp/phase22-evidence
# Run the verification snippet above with evidence-v6.json before continuing.
tar -xzf artifacts/phase22/integration/evidence-v7.tar.gz -C /tmp/phase22-evidence
# Run the verification snippet above with evidence-v7.json.
```

The batch-7 packaging command and script are recorded in `evidence-v7.json` and
its nested `diagnostics-v7.tar.gz`. The command refuses existing output seals.
`continuation-4dfd24c-full-suite` passed 1,215 tests, 36 skipped, at 88.27% branch
coverage; the original combined database was copied, and the older detached
checkout/database remain untouched. Later commits have separate focused evidence.
These packets do not establish the final Phase 22 benchmark, reviewed, runtime,
hosted or delivery gates; see the full requirement map and progress history.
