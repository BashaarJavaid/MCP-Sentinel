# Selected 1.4.0 candidate: local preparation and delivery review

The maintainer selected **1.4.0**. The [receipt](version-receipt.json) binds the
previously prepared ten-file version patch. Package metadata, CLI/report version
checks, Action installation and current installation examples now use 1.4.0.
The dated [changelog](../../../CHANGELOG.md) contains all accepted changes since
1.3.0. Its preparation date is not evidence of publication.

## Complete contents and compatibility

The [complete release inventory](../release-review-v1/README.md#complete-release-contents)
includes accepted Phase 19 report coverage and review activity, Phase 20 execution
corrections, Phase 22 source analysis and SENT-012–016, and Phase 23 detector,
regression and maintenance changes. Native reports use **1.7.0**, with baseline
migration from 1.3–1.7. SARIF remains 2.1.0. Canonical Finding, rule meanings,
baseline matching, suppression, model contracts and CLI exit semantics remain.
Consumers requiring an exact native schema must support 1.7.0. New default rules
can produce additional findings. No dependency pin changes beyond the project's
own version, and no additional service or framework.

The accepted advisory gate and actual deliberate-regression rejection remain
source-bound. The 56 unrelated advisory finding occurrences stay `needs_review`.
All 106 non-FAF historical reports / 53 pairs remain verified. The current FAF
1,800.011759-second timeout remains failed, with no report and five unstarted
observations closed; current detection/support/repeat compatibility is
unestablished. Proxmox remains unsupported. Phase 22's accepted limitations and
all original failures remain. Recovery, optimization, pilots and paid benchmarks
remain deferred; Phase 21 and Phase 24/15 are unchanged.

## Local distributions

The [package verification](package-verification.json) checks all 134 scanner
files and 20 bundled resources. Only the scanner's package fallback version
differs from the accepted hosted candidate. The source distribution contains the
exact selected source, metadata, README, license and finalized changelog.

```text
fc9c0155b08687e2a50e327cca4ebc8b7be759539eaef3e4aa4e08801d23f1af  portunusmcp_sentinel-1.4.0-py3-none-any.whl
3f61b8a914f6fe4fe3a8d10521c031dfa00a1e80132291b35d719640f371d4c6  portunusmcp_sentinel-1.4.0.tar.gz
```

These are locally prepared artifacts. Hosted canonical distributions must match
the reviewed source and these hashes before publication approval. The offline
editable environment refresh initially lacked the cached `editables` build
helper; normal frozen sync resolved that prerequisite without changing lock pins.
See [the retained prerequisite record](environment-prerequisite.json).

The first full local run retained eight test failures (2,758 passed / 36 skipped):
mocked current reports still carried the historical 1.3.0 version. The production
comparator correctly expected installed 1.4.0. The [test-only correction](version-test-correction.json)
sets the current version in memory at all three test callers and first proves
that each unchanged report passes before injecting deliberate drift. All 52
focused checks pass. Frozen reports, references and production code are unchanged;
the original failed run remains preserved.

## Final local checks

The corrected full `make check` **passed: 2,766 tests / 36 skips**, in
1,376.17 seconds for pytest, with 90.52% combined coverage. Lint, formatting,
typing, schema, dependency audit, notices and strict documentation checks pass.
The [local verification record](local-checks.json) binds exact identities and
logs, including the original eight failures and 52 passing focused checks.
Hosted verification of this selected 1.4.0 candidate remains pending.

## Next delivery checkpoint

The pending delivery proposal binds the exact local candidate commit and tree,
changed blobs, local checks and [PR description](pr-body.md). It requests one
update to the existing **draft PR40**, followed by its normal hosted CI and docs.
That CI includes seven advisory observations once, with network isolation after
dependency installation and the existing 1,800-second input, 10-second Semgrep,
15-second cleanup and four-worker limits. The helper has a 220-minute outer cap;
the hosted job retains its existing 230-minute setup/evidence allowance.
Full platform, packaging, replay, isolation, documentation and dependency gates
remain. No historical corpus retry or paid call is included.

Expected remote main is `dd9101ddfead19d65b7a84b374e4cf7e85462ff7` and expected
PR40 head is `4bc28d050bdbfcbf675bb0cf0c77c82f855acd7f`. Stop on drift or failed
checks. No automatic retry, reference promotion or timeout extension.

## Remaining publication checkpoint

After hosted verification, bind the canonical package hashes and provenance,
reviewed main revision and immutable Action commit in the final publication
proposal. The exact package pin is `portunusmcp-sentinel==1.4.0`.

Publication approval must cover ready/merge actions, an explicitly SSH-signed
annotated `v1.4.0` tag on reviewed main HEAD with message `Release 1.4.0`, and the
existing complete release workflow: full CI, TestPyPI verification, PyPI
publication/provenance and all supported-platform public installation checks.
GitHub release assets, the exact Action pin and compatible signed `v1` alias are
separate actions to include explicitly; the package workflow does not do them.
Preserve all immutable historical version tags and artifacts.

The final packet must also bind seven released-wheel regression observations
using the reviewed helper comparisons and normal limits. Ordinary CI's source
checkout identity guard stays intact; the installed wheel must receive explicit
file/hash verification. This check is not authorized or executed here.
Retain actual publication and verification milestones, then request explicit
final acceptance. Phase 23 remains incomplete until that verified release loop.

## Rollback

Pin `portunusmcp-sentinel==1.3.0` and Action commit
`c45e10cf878cfa0f926687f88a5679729ce9a19f`, accepting loss of newer fixes and
coverage. Preserve immutable tags and artifacts. Moving mutable `v1` back needs
explicit approval. Nothing in the version selection authorizes publication.
