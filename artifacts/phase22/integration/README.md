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

Batch 8 retains 235 added/changed files through `ecdf579`: Mastra's actual
fallback-loop measurements, 13 fixed-source Git campaigns, the Git native/SARIF
orchestrator check, exact review-source corrections and retained failures. Every
member was read back against its hash. The archive contains 17,250,782 raw bytes
in 711,609 compressed bytes; SHA-256:
`15e833494a8fb0293e8517fad40645e6bc1b42721c5484905ed046a5ca0c3fd8`.
After verifying batch 7, extract `evidence-v8.tar.gz` into the same directory and
run the verification snippet with `evidence-v8.json`. Its packaging script is
retained in `diagnostics-v8.tar.gz`.

`git-campaigns-80bd278/verification.json` validates every raw result hash and
canonical campaign summary. All 13 analyses are incomplete: 312 total tested
attempts showed no violation and 728 remain untested. `git-native-80bd278/`
preserves native JSON, SARIF, console and their checksums for a production
orchestrator run on the same fixed source. Model calls were disabled. These are
bounded execution/consumer measurements; they do not establish Git defenses or
the final integrated source gate.

Batch 9 retains 485 added/changed files through `e2b6345`: credential branch
corrections, presence/receiver regressions, static profiles, all failed auth
deadlines, and the unfinished TypeScript class tests captured with commands.
Every member was read back against its hash. The archive contains 4,146,993 raw
bytes in 450,155 compressed bytes; SHA-256:
`20a66027e1c736102f8e23149894d8467bcda47b211b923386d32f4c660a378c`.
After verifying batch 8, extract `evidence-v9.tar.gz` into the same directory and
verify it with `evidence-v9.json`. Its exact packaging script is retained in
`diagnostics-v9.tar.gz`. All earlier seals and coverage databases remain unchanged.
The 331-test focused result does not replace final full-suite or benchmark gates;
auth still exceeds the deadline and the TypeScript class implementation is open.

Batch 10 retains 385 added/changed files through `2066ca7`, including Python
branch/field corrections, all intermediate failures, the immutable `34220b7`
four-input authentication measurement and its condition adjudication, TypeScript
class/receiver controls and the actual mobile spawn trace. All four auth inputs
complete, with two vulnerable condition hits and zero fixed-condition alerts;
eight fixed nondefault candidates remain explicitly qualified. This is exposed
source adjudication, not final repeated, held-out, reviewed or runtime evidence.

Every member was read back against its SHA-256. The archive contains 50,599,629
raw bytes in 1,941,930 compressed bytes; SHA-256:
`d5e418d9b4ac1ef0a3a4cf63673481936336794cbe9f8e3b7ef1a83f9dab3997`.
After verifying batch 9, extract `evidence-v10.tar.gz` and verify it against
`evidence-v10.json` before applying any later batch. The exact packaging script
is retained in `diagnostics-v10.tar.gz`. Earlier seals, the original handoff
recovery packet and all detached checkouts/coverage databases remain preserved.
The first 366-test TypeScript run overlapped formatting; the packet verifies
identical before/after ASTs for all changed scanner/test files. Mobile recording
output/command semantics and the rest of the authorized scope remain unfinished.

Batch 11 retains 170 added/changed files through `b51aee1`, including ordered
TypeScript argv, optional output guards, mobile recording source traces, all
regression failures and the five-input native mobile measurement/adjudication.
All five inputs complete with both vulnerable screenshot/recording conditions
recognized and zero fixed/control condition-matched alerts. Each input adds one
recording candidate; existing candidate content is unchanged. Fixed physical-path
uncertainty and unrelated existing candidates remain separate from the named gate.

Every member was read back against its SHA-256. The archive contains 4,282,281 raw
bytes in 378,003 compressed bytes; SHA-256:
`9b20ec89321f4e6e763d30ccea59f6d21b13a6ae10f61cb9b99df07c39dac7dc`.
After verifying batch 10, extract `evidence-v11.tar.gz` and verify against
`evidence-v11.json` before later batches. The packaging script is retained in
`diagnostics-v11.tar.gz`; all earlier seals and coverage remain untouched.
The initial Meta source-identity diagnostic selected zero records from the wrong
manifest and proves no identity; its corrected development-only check is retained
separately after this seal. Fresh holdout source remains outside tuning.

Batch 12 retains 293 added/changed files through `bfc6a7c`: shared Python HTTP
client identity and evaluation order, source-defined tool decorators, request-local
ContextVar/reset state, bounded Atlassian SDK URL requests, corrected source
inventory checks and all intermediate failures. The Atlassian fixed trace still
alerts because middleware state is not attached to the tool request; this packet
does not establish a passing condition or final technical gate.

Every member was read back against its SHA-256. The archive contains 1,245,896 raw
bytes in 129,337 compressed bytes; SHA-256:
`5f48d05b48cf3e33926e83aac6360a0813c3d2cc19e62c414665af38029837db`.
After verifying batch 11, extract `evidence-v12.tar.gz` and verify it against
`evidence-v12.json` before applying later batches. The packaging script is retained
in `diagnostics-v12.tar.gz`. Earlier seals, the original recovery packet and
detached checkouts/coverage databases remain unchanged.
