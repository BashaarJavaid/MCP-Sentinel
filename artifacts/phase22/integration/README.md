# Integration evidence, batches 1–3

This packet preserves intermediate implementation, failures and measurements
through source commit `536bb69`. **It is not final technical acceptance.**
[requirements.md](requirements.md) lists the complete outstanding contract;
[progress.md](progress.md) explains source-specific results and limitations.

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
