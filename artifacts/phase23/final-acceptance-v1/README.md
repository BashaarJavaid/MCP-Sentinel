# Phase 23 final acceptance: verified 1.4.0 release

**All implementation and release verification is delivered. Final human acceptance
is the only open Phase23 gate.** This request does not treat publication approval
as technical closeout or change any retained limitation.

## Released result

- [GitHub release1.4.0](https://github.com/BashaarJavaid/MCP-Sentinel/releases/tag/v1.4.0)
  and [PyPI1.4.0](https://pypi.org/project/portunusmcp-sentinel/1.4.0/).
- Release revision: `fd10cba1297a32ec35ec647e17f3491dbb3b0979`;
  reviewed tree: `a736214212f90dbfec34f4b6362b4e3c741a3922`.
- Package pin: `portunusmcp-sentinel==1.4.0`.
- Exact Action pin: `BashaarJavaid/MCP-Sentinel@d5365dce6184707248dab17a921b3257cc508069`.
  That candidate and the merge have the same reviewed tree. Signed `v1` resolves
  to the release merge. Immutable `v1.4.0` and old version tags remain.
- The release includes the applicable accepted main changes, five added rules
  SENT012–016 and report schema additions, plus the maintained advisory corrections.
  It retains16 rule IDs (12 static/four dynamic); Phase23 expands no canonical
  Finding/report contract. [Reviewed contents and identities](../publication-review-v1/README.md).

## Verification

| Gate | Result and retained evidence |
| --- | --- |
| Local engineering | Corrected `make check`:2,766 passed/36 skips;90.52% combined/86.58% branch coverage. Earlier eight-test failure remains. [Evidence](../release-review-v2/local-checks.json) |
| Main gates | All30 CI jobs, deployed docs and12 platform suites passed. [Evidence](../publication-main-v1/summary.json) |
| Release workflow | All47 jobs passed, including TestPyPI verification, PyPI provenance and12 public installs. [Evidence](../publication-release-v1/summary.json) |
| Public packages | Both indexes have exact reviewed wheel/sdist hashes and signed provenance at the release merge. [Evidence](../publication-v1/public-artifact-verification.json) |
| GitHub assets | Downloaded public assets and notes match the approved release. [Evidence](../publication-completion-v1/github-assets-verification.json) |
| Released detector | Seven downloaded-wheel inputs complete and equal reviewed entire reports:3 vulnerable detections/4 supported negatives;31 findings/4,377 warnings retained;97.037248625 seconds. [Evidence](../publication-v1/regression-assessment.json) |
| Durable CI | Main CI7 +release CI7 +released wheel7 =21 approved observations, all complete, no retries. These are repeated correlated inputs for one advisory, not independent vulnerabilities. |
| Regression rejection | One deliberately reversed approved fix is rejected by the actual CI assertion; report, patch and failed assertion retained. [Evidence](../regression-rejection-v1/verification.json) |
| Exact Action | Complete clean result,1.4.0,0 findings, valid uploaded SARIF, correct immutable reference and rules-only stages. [Evidence](../publication-completion-v1/exact/verification.json) |
| Compatible alias | Same complete clean checks; GitHub verifies signed `v1` at the release merge. [Evidence](../publication-completion-v1/alias/verification.json) |
| Guidance | Live maintenance/contribution pages and shipped forms match the reviewed revision. [Evidence](../publication-completion-v1/guidance-delivery-verification.json) |

All12 platform suites at each hosted code stage retain2,766/36 on Linux/macOS and
2,744/58 on Windows. Zero paid/model calls or advisory-target execution. The two
external Action observations use the existing clean fixture with explicit empty
credentials; they do not add advisory observations or establish Phase24 adoption.

## Scope and limits remain unchanged

The original GHSA-5w57-2ccq-8w95 baseline already passed; it remains a compatibility
control. The approved replacement GHSA-3q26-f695-pp76 (`git_init.initialBranch`)
completed the reviewed reproduction/correction/regression/release loop. Its
seven full/minimized/mutated/control inputs remain correlated examples of one
advisory. Full-source results remain distinct from reduced examples.

The56 unrelated finding occurrences remain `needs_review`; their exploitability
is unestablished. Historical compatibility retains106 non-FAF reports/53 equal
pairs and14 first-advisory reports/seven pairs. Current FAF timed out after
1,800.011759 seconds with no report; five slots are closed unstarted. That failure
remains failed and current FAF compatibility unestablished. Proxmox remains
unsupported. Recovery/FAF optimization, paid benchmarks and pilots remain deferred.
Phase22v93 acceptance and its493-row audit/30 accepted limitations are preserved;
Phase21 remains incomplete and Phase24/15 unchanged.

All prior failed local/hosted/advisory attempts, incomplete observations and
qualifications are retained. Three earlier automatic-review denials did not run
their commands. PyPI's protected environment was separately approved by the owner
through GitHub. The subsequent explicit continuation approval authorized the
completed GitHub release and Action steps. Git reported existing owner rule
exceptions for authorized tag writes; repository protection settings were unchanged.

## Maintenance, timing and rollback

BashaarJavaid owns labels, corrections, publication and final acceptance. Weekly
SDK/advisory review is Monday09:00 America/Los_Angeles; the next record is
[2026-09-21](../weekly/2026-09-21.json), scheduled and not claimed complete.
Source checks, decisions and missed reviews are recorded manually, without an SLA.
Optional reuse permission, sanitization, private Sentinel reporting and upstream
third-party disclosure routing are delivered in the existing forms/guidance.

[Lifecycle](../lifecycle/ghsa-3q26-v21-release-verified.json) separates advisory
publication, intake, human review, package publication, GitHub publication and
verification. Unknown message/intake times remain null; no unsupported turnaround
or active-engineering-time claim is made.

Rollback pins: `portunusmcp-sentinel==1.3.0` and
`BashaarJavaid/MCP-Sentinel@c45e10cf878cfa0f926687f88a5679729ce9a19f`.
Rollback loses newer fixes/features. Moving `v1` back requires separate approval;
immutable versions and artifacts remain preserved.

## Final decision

Accept Phase23 completion with this delivered release, actual regression-rejection
proof, maintenance/contribution guidance and all unchanged limitations above.
[Requirement map](requirements.json) keeps this final acceptance pending.
Approval authorizes recording acceptance and verifying its local closeout delivery;
it adds no scan, retry, paid call, publication, main commit, branch cleanup,
recovery work, pilot, adoption or launch acceptance. Post-release evidence/status
records remain local, as specified in the approved publication sequence.
