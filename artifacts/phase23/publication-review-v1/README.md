# Publication review: PortunusMCP Sentinel 1.4.0

**Prepared for review; publication is not yet authorized.** Version 1.4.0 was
selected explicitly. Technical acceptance, source labels, CI references and the
current FAF limitation are already accepted. The exact candidate is
`d5365dce6184707248dab17a921b3257cc508069`, tree
`a736214212f90dbfec34f4b6362b4e3c741a3922`.

## Contents, identities and compatibility

The [complete release notes](release-notes.md) cover all accepted changes since
1.3.0: Phase 19 review/coverage reporting, Phase 20 execution corrections,
Phase 22 source analysis and SENT-012–016, and Phase 23 TypeScript export,
promisify, callback and composed Zod corrections with maintained feedback and
seven-input offline regression CI. Native reports use schema **1.7.0**, with
baseline migration from 1.3–1.7; SARIF remains 2.1.0. Canonical Finding, existing
rule meanings, suppressions, baseline matching, model and exit-code contracts
remain. New default rules can produce new findings. No dependency is added.

The exact package pin is `portunusmcp-sentinel==1.4.0`. The immutable Action pin is
`BashaarJavaid/MCP-Sentinel@d5365dce6184707248dab17a921b3257cc508069`.
The proposed signed version tag is `v1.4.0`; the compatible moving alias is `v1`.

Reviewed local and hosted distribution SHA-256 hashes agree:

```text
fc9c0155b08687e2a50e327cca4ebc8b7be759539eaef3e4aa4e08801d23f1af  portunusmcp_sentinel-1.4.0-py3-none-any.whl
3f61b8a914f6fe4fe3a8d10521c031dfa00a1e80132291b35d719640f371d4c6  portunusmcp_sentinel-1.4.0.tar.gz
```

The reviewed corpus manifest is
`8a489a5593bf9397382519beccb1e01b6e5add3a7dfd1fba9b1cf070e5011d5c`.
The candidate scanner source digest is
`0d1abf75a0fe2a5203e834da096c63ad5857c5b738657ac000a12a4645ee6b28`;
the only scanner difference from the technically accepted candidate is its
fallback version string. Rule and schema identities are retained in the local
and hosted execution records. The regression helper is unchanged at
`f19741a308201668d0bab06e8c1cb86b67633c73f2b91ccb493998bf17862cb7`.
The [rule/corpus identity record](rule-corpus-identities.json) retains the complete
16-rule catalog, 12 static rules and four dynamic probes, and all static/dynamic
source hashes. The five new IDs since 1.3.0 are SENT-012–016.

The selected version's first local suite exposed eight synthetic report-version
failures. A five-line test-only correction now supplies the installed version
and verifies unchanged controls before deliberate drift. The corrected full
`make check` passed **2,766 tests / 36 skips**; all 52 focused checks pass. The
original failed run remains retained. The [hosted summary](../release-hosted-v1/summary.json) verifies all **30 CI jobs,
documentation and 12 platform suites**: Linux/macOS 2,766 / 36; Windows 2,744 / 58.
Seven current-candidate reports match reviewed references: three vulnerable
detections, four supported negatives, 31 findings and 4,377 warnings retained,
135.11053036 input-seconds, all cleanup verified. The test-merge tree equals the
reviewed candidate exactly; the PR remains draft and main unchanged.

## Limits retained in this release

The advisory result is one correlated case, not seven independent vulnerabilities.
All 56 unrelated finding occurrences from the accepted two-pass advisory run stay
`needs_review`. All 106 non-FAF historical reports / 53 pairs remain verified.
The current FAF timeout stays failed: 1,800.011759 seconds, no report, five
unstarted observations closed. Current FAF detection/support/repeat compatibility
is unestablished. Proxmox remains unsupported. Phase 22's accepted closeout,
493-row audit and limitations remain. Recovery, optimization, pilots and paid
benchmarks remain deferred; Phase 21 and Phase 24/15 gates are unchanged.

## Exact proposed publication sequence

1. Recheck PR40 is still draft/open at the exact candidate above, main is still
   `dd9101ddfead19d65b7a84b374e4cf7e85462ff7`, and all approved hosted gates passed.
   Mark PR40 ready and merge with the explicit merge strategy, matching its head.
   Use [the prepared merge message](merge-message.md). Do not use admin bypass,
   delete branches or introduce another commit.
2. Record the actual merge commit **M**. Its tree must equal the reviewed tree,
   its parents must be the approved main and candidate, and remote main must equal
   M. M is a runtime result of the approved merge, not a new content choice.
   Stop if any identity differs. Wait for all ordinary main CI and documentation
   deployment checks. Their seven-input regression runs once.
3. Create and locally verify an SSH-signed annotated `v1.4.0` tag at M, with exact
   message `Release 1.4.0`, then push that new tag. It must not already exist.
   The existing release workflow checks GitHub's verified signature and main HEAD,
   runs full CI (seven advisory inputs once), publishes to TestPyPI, verifies
   its distributions/provenance/install/replay controls, publishes PyPI, then
   verifies public provenance/hashes and the full supported installation matrix.
4. Download the published files, require both reviewed hashes and release-revision
   provenance, and run the seven released-wheel observations described below.
   Stop on any mismatch, failed/incomplete result or changed support judgment.
5. Create the GitHub release for the existing verified tag, using the exact
   [release notes](release-notes.md), and attach the same verified wheel and sdist.
6. Push only the prepared external proof commit to its new branch, then dispatch
   the exact-pin proof once. After success, create and verify a signed `v1` alias
   at M and update it with the exact prior-tag lease. Dispatch the alias proof
   once. Verify both reports and SARIF assets, including installed 1.4.0, complete
   zero-finding clean results, null model review and rules-only skipped stages.
7. Record actual publication/verification times and evidence. Prepare final
   acceptance for the maintainer; Phase 23 stays open until that explicit decision.

The proposal contains exact commands and preconditions. Any failed/incomplete
stage stops later actions; no automatic retry, timeout extension, hidden reference
promotion or paid call is included. Existing required gates remain intact.

## Released-wheel verification without changing the regression helper

The isolated review checkout is `/private/tmp/phase23-released-wheel-review`, at
the approved candidate commit. Only helper/evidence/schema files are checked out.
The wheel is installed with `--no-deps --target .../src`; an isolated virtualenv
loads that directory through a one-line `.pth` file. Its interpreter also loads
the installed package under `-I`, which is what the helper uses for scanner
children. No editable scanner is installed, and the production identity guard
is unchanged.

[The preflight](verify_installed_wheel.py.txt) verifies the wheel hash, installed
package bytes and closed file inventory, version, isolated parent/child imports,
helper digest, reviewed corpus/references and normal limits. Its positive result
is [wheel-identity.json](wheel-identity.json). Wrong wheel, wrong interpreter and
altered installed schema all reject before scanning; see
[the controls](wheel-identity-controls.json). The altered schema was restored.
The installed scanner digest is
`f04f31639477256c24c3307b52b3d7b2ec8299792e664bc3bed8b12a989d92b3`.
It includes bundled schema/fixture resources physically installed under the
package directory, so it is distinct from the 134-file source checkout digest.
All 158 non-RECORD archive files are byte-verified; RECORD is regenerated on installation;
the unmodified helper records the actual installed tree and dependency identities.

Preparation used the canonical hosted candidate wheel, whose bytes equal the
reviewed local wheel. **It is not a published-wheel result.** After publication,
download and verify the public wheel, reinstall those bytes into this same
isolated environment, repeat the identity preflight, then invoke the existing
`scripts.phase23_regression ci` command once. This produces seven observations in
the approved order, using the eight reviewed volatile exclusions and installed
1.4.0 as the expected version. Preserve complete ordered reports, timings,
diagnostics, cleanup, findings and support judgments. No new scanner implementation
or comparison contract is introduced.

Bounds remain 1,800 seconds per input, 10 seconds per Semgrep operation, 15 seconds
cleanup, four workers, and a 220-minute helper outer cap. The local proof uses
rules-only with the helper's credential-free environment. The ordinary Linux CI
network namespace and installed-wheel isolation gate remain separate verified
evidence; this local macOS run is not claimed to create a Linux network namespace.

Proposed new advisory observations after this approval: **21 total**—seven in
main CI, seven in release CI, and seven on the downloaded released wheel. The
two external Action invocations use the existing clean demonstration fixture,
not the advisory corpus. Ordinary unit/package/replay/isolation gates remain.

## External Action proof: exact branch and no paid workflow trigger

Repository: `BashaarJavaid/mcp-sentinel-action-demo`. The local prepared commit is
`26615d0da25c8af1b9944010397b79765cc365d5`, parent
`d15df2851771f331849d1f0e1c4531090de7bd3e`, on proposed new branch
`phase23-1.4.0-release-proof`. The [two-file patch](action-proof.patch) updates the
existing manual release-proof workflow and its version assertion. Both jobs use
explicit empty credentials and `rules-only: "true"`; the exact job pins the
reviewed Action commit and the alias job uses `v1`.

Do not push external main or open a PR: those events trigger another existing
workflow with model credentials. A new non-main branch push triggers neither;
dispatch only `phase15.yml` with `release=exact`, then `release=alias` after the
alias update. This reuses a historical filename; it does not change Phase 15 or
Phase 24 adoption/launch acceptance. No outreach or adoption claim is proposed.

## Rollback and historical preservation

Return to package `portunusmcp-sentinel==1.3.0` and exact Action commit
`c45e10cf878cfa0f926687f88a5679729ce9a19f`, accepting loss of newer coverage/fixes.
Current `v1` tag object is `089adf0891465ddcb78100e06ecf2a2228566c51`; the proposed
update must use that exact lease. A later rollback of mutable `v1` requires
explicit approval. Preserve immutable version tags and published artifacts.
Do not erase earlier failures, accepted limitations or publication timestamps.

Advisory publication, Phase 23 intake, triage, reproduction, fix verification,
human review and release publication remain distinct lifecycle milestones.
Unknown message times and waiting durations stay null. Actual publication is
still unknown; preparation and prior technical acceptance are not publication.
