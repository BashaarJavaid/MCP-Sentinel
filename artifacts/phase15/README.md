# Phase 15 — 1.2.1 launch evidence and approval packet

Prepared 2026-09-04. **Release candidate; publication is not approved. Phase 15
remains incomplete and Phase 14 remains deferred.** No paid GPT calls were made.
The branch is `release/1.2.1-launch`, based on
`4e38916` (the existing cold Semgrep startup fix).

## Prepared changes

Package metadata, fallback version, Action pin, wheel smoke expectations, tests,
and current install/pre-commit examples agree on 1.2.1. The existing Unreleased
changes moved into the dated changelog entry. Public walkthrough/navigation and
live documentation smoke cover the new page. SECURITY.md explains private reports
and coordinated disclosure without promising deadlines. Historical records,
scanner capabilities, dependencies, rule IDs, JSON 1.4.0, SARIF 2.1.0, and Action
interfaces are preserved.

Review [release notes](release-notes.md), [launch drafts](launch-drafts.md), and
the [walkthrough source](../../docs/walkthrough.md). The owner revises and
publishes list submissions and announcements.

## Rehearsal evidence

- `pytest.txt`: 229 tests passed, 83.32% branch-enabled coverage on macOS Python
  3.12.13. An initial sandboxed run failed four loopback-server tests because
  binding was prohibited; the complete rerun with loopback access passed.
- Ruff lint/format, strict mypy, schema drift, historical artifact checks, and
  generated notices passed. `dependency-audit.txt`: no known vulnerabilities.
- `maintenance-check.txt`: focused maintenance checks pass after allowing only
  the exact required historical video label in the branding guard. The first
  hosted run caught this documentation-only conflict; no scanner change was needed.
- `docs-build.txt`: strict MkDocs build passed. The new page is 600–900 words;
  navigation and the existing deployed-site smoke include `/walkthrough/`.
- `package-smoke.txt`: isolated pip, pipx, uv, and sdist verification log.
- `replay/report.json`, `replay/report.sarif`, `replay-console.txt`: installed
  candidate-wheel Docker replay, all 11 rule IDs; ten confirmed, one needs review.
  Fresh Docker probes executed. Cache was disabled for retained GPT cassette
  replay; current model cost and tokens are zero. Origin cost is historical.
- `walkthrough.json`, `walkthrough.sarif`, exit files and `walkthrough-log.txt`:
  two successful static scans, five files, zero findings, no model batches.
  All seven static rules selected; SENT-001 skipped for absent permissions;
  SENT-002–007 evaluated; dynamic stages intentionally skipped. No target code
  or target dependency installation was executed.
- `walkthrough-config.json`: effective native-JSON scanner configuration;
  SARIF changes only the output format. `--static-only` and `--allow-degraded`
  are explicit CLI switches. `walkthrough-log.txt` records the entire scan
  environment: PATH and shell PWD only, with no GPT/Sentinel overrides.
- `linux-installed.txt`, `linux-image.txt`, `linux-build.txt`: Linux arm64,
  Python 3.12.14, pipx 1.16.0, Git 2.47.3, installed dependency versions and
  verification-image identity. Semgrep is pinned to 1.176.0.
- `SHA256SUMS`: retained evidence and candidate distribution hashes.
  `target-SHA256SUMS` hashes every tracked file under the pinned `src/git`.
- `links.json`: existing launch links resolve. The 1.2.1 PyPI endpoint and new
  walkthrough return the expected pre-publication 404; verify both after release.
- `private-reporting.json`: enabled. The public repository Security page exposes
  `/BashaarJavaid/MCP-Sentinel/security/advisories/new` as “Report a vulnerability”.
  Filing requires GitHub login. No test advisory was submitted.
- `video-metadata.json` and `video-review.md`: supplied public video is 165 seconds
  by Bashaar Javaid. Visual review supports reuse with the adjacent v0.1.0 label.

`verify-reports.py` independently validates both formats, coverage, zero current
model spend, installed branding, and the replay rule/stage outcomes:

```sh
/tmp/sentinel-phase15-wheel-env/bin/python artifacts/phase15/verify-reports.py
```

The pipx rehearsal installed a **local candidate wheel**, because 1.2.1 is not
published yet. It does not establish that `pipx install
portunusmcp-sentinel==1.2.1` works from PyPI. Public-index installation and
provenance are post-approval gates. Candidate artifacts are under
`/tmp/sentinel-phase15-dist`; the release workflow builds its canonical artifacts.
Compare source/content and use the workflow's canonical hashes for publication,
not these rehearsal archive hashes.

## Exact rehearsal commands

```sh
.venv/bin/uv sync --locked --extra dev --extra docs
.venv/bin/python -m build --outdir /tmp/sentinel-phase15-dist
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/python -m sentinel.schema check
.venv/bin/python -m scripts.generate_phase5_artifacts --check
.venv/bin/python scripts/generate_third_party_notices.py --check
env -u OPENAI_API_KEY .venv/bin/pytest
.venv/bin/uv export --locked --no-dev --no-editable --no-emit-project \
  --format requirements-txt --output-file /tmp/sentinel-phase15-runtime.txt
.venv/bin/pip-audit --no-deps --disable-pip -r /tmp/sentinel-phase15-runtime.txt
.venv/bin/mkdocs build --strict
.venv/bin/python scripts/smoke_wheel.py artifacts /tmp/sentinel-phase15-dist --install-sdist
.venv/bin/uv venv /tmp/sentinel-phase15-wheel-env
.venv/bin/uv pip install --python /tmp/sentinel-phase15-wheel-env/bin/python \
  /tmp/sentinel-phase15-dist/portunusmcp_sentinel-1.2.1-py3-none-any.whl
env -i PATH="$PATH" SENTINEL_LLM_CACHE_ENABLED=false \
  /tmp/sentinel-phase15-wheel-env/bin/sentinel demo --replay-review \
  --output-dir artifacts/phase15/replay
```

The walkthrough target clone and explicit checkout were:

```sh
git clone https://github.com/modelcontextprotocol/servers.git /tmp/sentinel-phase15-servers
git -C /tmp/sentinel-phase15-servers checkout d73f99efbfd40c3aa1b61e88728b3d49fb52608f
```

`walkthrough-scan.sh` contains the exact scan/validation commands. The target was
mounted read-only, reports outside it, runtime network disabled, and an empty
environment passed to the shell. The entire checkout was clean before and after.
The container recipe is retained as `walkthrough.Dockerfile` (build with the
candidate wheel in its context). No new recurring CI workflow was introduced.

```sh
docker build -t sentinel-phase15-walkthrough /tmp/sentinel-phase15-dist
docker run --rm --network none \
  --mount type=bind,src=/tmp/sentinel-phase15-servers,dst=/work/servers,readonly \
  --mount type=bind,src="$PWD/artifacts/phase15",dst=/evidence \
  sentinel-phase15-walkthrough env -i \
  PATH=/root/.local/bin:/usr/local/bin:/usr/bin:/bin sh /evidence/walkthrough-scan.sh
```

## Publication procedure — requires owner approval

1. Review the PR, final commit, changelog, notes and all hosted checks. Obtain
   explicit approval before merging/publishing and before updating signed `v1`.
2. Merge the approved PR; verify the resulting main HEAD and green CI/docs checks.
   Update the dated entry if readiness moves to another date. Use the configured
   SSH signing identity to create annotated tag `v1.2.1`, message `Release 1.2.1`.
   Verify the tag locally, push only that tag, and verify GitHub reports its
   signature as valid. It must peel to main HEAD.
3. Let `.github/workflows/release.yml` enforce all 12 OS/Python quality and
   distribution jobs, installed-wheel Docker replay, canonical artifact build,
   attested TestPyPI upload, matching hashes/provenance, TestPyPI pip/pipx/uv
   installation and fixture scans. Do not supply GPT credentials.
4. After TestPyPI verification passes, approve the protected `pypi` environment.
   Verify canonical wheel/sdist hashes, both PyPI attestations, and all 12 public
   installation matrix jobs. Retain run URLs and provenance under this directory.
5. Perform the one-time walkthrough using the published exact pipx package in
   clean Linux Python 3.12; retain reports/checksums and compare coverage/findings.
6. In the existing public proof repo, use `action-proof.yml` as a dispatch-only
   clean-fixture workflow, with no GPT key. Do not dispatch the old vulnerable or
   adoption workflows: they can require paid review. A workflow-only commit can
   use `[skip ci]` to avoid triggering the legacy push workflow. Dispatch `exact`;
   verify 1.2.1 installed, no findings, complete validated SARIF and upload success.
7. Publish the GitHub Release/Marketplace update with the verified notes and
   evidence. Preserve the existing Marketplace identity/slug. Once exact-tag
   proof passes and alias approval is recorded, update `v1` with an SSH-signed
   annotated tag pointing to the release commit. Push only `refs/tags/v1` using
   an explicit force-with-lease against the recorded old tag object; verify
   GitHub's signature and peeled commit. Dispatch `alias` and retain clean proof.
8. Verify live docs, walkthrough anchor, all launch URLs, video label, security
   destination, and public installation command. Record links in `publication.json`.
9. The owner personally revises and publishes both selected list submissions and
   all three announcements, confirms a permitted Glama-linked showcase channel,
   then supplies URLs. Verify access and both list merges; rejected submissions
   or scope changes return to the owner without selecting replacements.
10. Only after every gate passes, update ROADMAP.md and AGENTS.md to mark Phase 15
    complete. Until then leave both phase-completion markers unchanged.

## Pending gates

Hosted PR checks and exact tested commit are recorded with the PR. Product
publication, canonical TestPyPI/PyPI provenance, public installs, clean exact/alias
Action runs, published walkthrough smoke, two merged list submissions, and three
accessible announcements remain required. Local evidence never substitutes for
these external gates. `publication.json` starts with null URLs deliberately.

Historical positive code-scanning upload proof remains
[v0.1.0 on 2026-07-21](../phase4-action-evidence.md). A new clean workflow run is
integration proof only and must not be described as fresh positive-alert proof.
