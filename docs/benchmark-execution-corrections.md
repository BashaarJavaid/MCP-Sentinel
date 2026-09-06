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
  Corpus/metadata validation uses the PR revision; historical full-corpus
  reproduction then checks out the exact original scanner and harness.
  Current-source regression tests remain in the platform matrix. Corrected
  full-corpus measurements are explicit, separately retained observations.

The official [Python image source](https://github.com/docker-library/python/blob/f2c5d1b8a6adecb5b00b3c9331d4f863beade6b3/3.12/bookworm/Dockerfile)
uses buildpack-deps. Its [SCM image includes Git](https://github.com/docker-library/buildpack-deps/blob/master/debian/bookworm/scm/Dockerfile).
GitHub documents [workflow concurrency](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#concurrency).

## Verification

Focused regression checks cover malformed devcontainer content, literal comment
markers inside strings, unchanged secret evidence, and cache invalidation when
the base digest changes. Real Docker checks run `git --version` in all three
pinned bases using native sandbox arguments and verify cleanup.

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

To reproduce the original baseline, use the frozen benchmark source at
`daeefe701a6d51120585ee2054128c33c7efafbc` and the
commands in [the original report](phase20-verification.md). Corrected-scanner
results are a separate revision, not replacements for that baseline.
