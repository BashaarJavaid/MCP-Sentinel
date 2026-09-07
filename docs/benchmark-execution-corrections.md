# Benchmark execution corrections

These changes address execution blockers observed during Phase 20. The frozen
corpus, approvals, captures, adjudications, and original measurements under
`artifacts/phase20` are unchanged. Phase 20 remains open; these corrections do
not establish detection effectiveness or authorize paid review.

## Changes

- Devcontainer configuration uses JSON with comments. Validation now accepts
  comments and trailing commas in `devcontainer.json` and `.devcontainer.json`.
  Strings, original source bytes, and finding line numbers remain intact;
  malformed syntax still fails. No target code or devcontainer command runs.
- Official Python bookworm base images include Git. Their multi-platform
  digests are pinned in `src/sentinel/dynamic/sandbox.py`; dependency cache keys
  now include the base digest. Old slim-image caches cannot mask the change.
  Images are larger; the registry proxy, offline installation, read-only source
  mount, and runtime network denial remain unchanged.
- The separately documented [nullable-field correction](nullable-probe-validation.md)
  handles valid nullable GPT probe bindings. Accepted responses may be reused
  only when the exact production request still matches.
- CI and documentation cancel obsolete runs for the same PR. Distribution
  building starts alongside source checks. The full matrix remains required;
  release and main verification are not canceled by PR updates.
  Corpus/metadata validation uses the PR revision; full-corpus reproduction
  checks out the exact scanner and harness for the separately versioned
  [completion measurement](phase20-completion-v2.md). Deterministic and replay
  verification run in parallel. Current-source regression tests remain in the
  platform matrix; original baseline evidence remains unchanged.

The official [Python image source](https://github.com/docker-library/python/blob/f2c5d1b8a6adecb5b00b3c9331d4f863beade6b3/3.12/bookworm/Dockerfile)
uses buildpack-deps. Its [SCM image includes Git](https://github.com/docker-library/buildpack-deps/blob/master/debian/bookworm/scm/Dockerfile).
GitHub documents [workflow concurrency](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#concurrency).

## Verification

Focused regression checks cover malformed devcontainer content, literal comment
markers inside strings, unchanged secret evidence, and cache invalidation when
the base digest changes. Real Docker checks run `git --version` in all three
pinned bases using native sandbox arguments and verify cleanup.

`make check` passed with 673 tests passed and 36 Docker tests skipped, including
lint, formatting, mypy, schema checks, dependency audit, notices, and the strict
documentation build. The final malformed-JSONC guards passed a separate 34-test
focused run plus final lint, formatting, and mypy checks. Docker was selected
separately: all 36 regression controls passed. These passing controls are
distinct from the two failed historical Git diagnostics below.

```sh
pytest tests/test_static_engine.py tests/test_dynamic_sandbox.py --no-cov
SENTINEL_RUN_DOCKER_TESTS=1 pytest tests/test_dynamic_docker.py --no-cov
python -m scripts.run_phase20_benchmark rules --output /tmp/corrected-rules
python -m scripts.run_phase20_benchmark replay --output /tmp/corrected-replay
make check
```

Corrected-scanner observations are retained under
`artifacts/corrections/execution-blockers`. They use the unchanged corpus and
the native finding/report contracts. Missing captures remain incomplete;
newly observable warnings require adjudication and are not assumed to detect
the labeled vulnerabilities. No new model requests are sent.

Both 45-input diagnostic treatments used scanner bytes matching commit
`613169b5344b12556f6e92be48b88226a3f1bd7e`. Their metadata records the parent
revision because measurement began in the working tree before that source
checkpoint was committed; `diagnostic-summary.json` verifies the exact source
hash. Subsequent malformed-JSONC guards have separate focused test evidence.

| Observation | Result |
| --- | --- |
| Deterministic diagnostic | 32 completed, 13 incomplete; 780.759 seconds |
| Checked static replay diagnostic | 22 completed, 23 incomplete; 780.880 seconds |
| Atlassian after JSONC correction | Four inputs hit the native 120-second static timeout; nine fail on Helm template YAML |
| Retained native reports | All 32 per treatment have unchanged stable findings and coverage compared with the original baseline |
| Docker regression suite | 36 passed, including Git availability in all three pinned bases |
| Historical Git startup trials | Both vulnerable/fixed trials fail after Git initialization: MCP SDK 2.1.1 lacks the expected `Server.list_tools` API |

The upstream Git dependency `mcp>=1.0.0` resolves to SDK 2.1.1 in the new image.
Installed versions are retained in `git-installed-packages.json`; the failing
trials are in `git-baselines.log`. The diagnostic test can be reproduced from
commit `613169b` with
`SENTINEL_RUN_DOCKER_TESTS=1 pytest tests/test_dynamic_docker.py -k phase20_git_legitimate_baseline --no-cov`.
It is not a passing regression control and is excluded from the current
regression suite. No legitimate upstream call or runtime exploit was confirmed.
The snapshot's `src/git/uv.lock` records MCP 1.1.0, which is a candidate for a
separately prepared runtime configuration; that configuration has not been
approved or measured. Neither target dependencies nor corpus configuration
were changed to make these trials succeed.

These are compatibility diagnostics, not new accuracy claims. The next blockers
are Helm template handling, the bounded static pass on the larger Atlassian
snapshots, and a reproducible compatible SDK setup for historical Git servers.
New runtime configuration and any subsequent paid review require their own
evidence/approval checkpoints.

To reproduce the original baseline, use the frozen benchmark source at
`daeefe701a6d51120585ee2054128c33c7efafbc` and the
commands in [the original report](phase20-verification.md). Corrected-scanner
results are a separate revision, not replacements for that baseline.
