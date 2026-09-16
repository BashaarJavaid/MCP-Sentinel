# Release contents inventory — preparation only

Version selection, technical acceptance and all merge/tag/publication actions
remain pending. This inventory does not authorize them. It compares released
`v1.3.0` (`c45e10cf878cfa0f926687f88a5679729ce9a19f`) with accepted main
`dd9101ddfead19d65b7a84b374e4cf7e85462ff7` and the Phase 23 candidate.
The reviewed candidate source SHA-256 remains
`2fa09818900817337863f90c41b71ab6d9e27458f11b8b1d80e1b882682c051d`.

## Contents requiring release review

- **Accepted Phase 19:** native schema 1.6.0, actual static/rule/runtime coverage,
  explicit unknown/skipped activity, actionable console/SARIF evidence, and
  in-memory native 1.3–1.6 baseline migration. Canonical Finding, matching,
  suppression, model and exit-code contracts remain stable. Acceptance is recorded
  in `docs/phase19-verification.md`; the stale pending sentence in Unreleased
  notes is corrected during this preparation.
- **Accepted Phase 20 and execution corrections:** retained benchmark evidence,
  Git in pinned Python runtime images, base-image digest cache identity, nullable
  and union probe validation. Historical failed measurements remain separate.
- **Accepted Phase 22 under revised scope:** SENT-012 path containment,
  SENT-013 tool-description poisoning, SENT-014 command option injection,
  SENT-015 SSRF and SENT-016 operator-credential fallback; shared Python and
  TypeScript source-flow support, imported/registered handlers and workspace
  recovery; bounded guard/receiver/dispatch corrections; explicit unsupported
  paths; static 1,800-second deadline and accepted private performance contracts.
  Existing rule IDs retain their meanings. These five additions were missing
  from Unreleased notes and are now named explicitly.
- **Phase 23, technical acceptance pending:** unique local TypeScript star exports,
  proved promisify(exec/execFile) identities, handler invocation-stack separation,
  bounded Zod metadata composition, the seven-input current-candidate offline CI
  regression, deliberate regression rejection, reviewed feedback intake and
  maintenance/release guidance. No new dependency or service.
- **Engineering/documentation:** preserve the full OS/Python matrix, packaging,
  replay, isolation, docs and dependency gates. Linux CI isolates the advisory
  regression after dependency installation. Windows POSIX guards and frozen
  source byte handling preserve platform support.

`accepted-main-source-changes.txt` lists every changed scanner file from the last
release to accepted main. `candidate-source-changes.txt` lists the exact Phase 23
scanner diff from accepted main to hosted draft `4bc28d0`. The Unreleased changelog
is the user-facing release-note basis. Evidence-only continuation files will also
need delivery verification before a publication revision is approved.

## Compatibility and limitations

The meaningful coverage expansion includes five new static rule IDs and schema
1.6.0, even though Phase 23 itself keeps public Finding/report interfaces stable.
Consumers that enforce exact report schema versions must account for the accepted
schema expansion. Default rules can report additional findings, including
unrelated findings needing review; zero findings do not establish safety.

Phase 22's 493-row accepted closeout and all 30 accepted limitations remain.
Proxmox is unsupported, ordinary FAF completion within 1,800 seconds remains
unestablished, Git is 312/1,040 incomplete with 728 deferred, and paid benchmark/
pilots are deferred. Phase 21 is incomplete; Phase 24/15 gates do not change.
The Phase 23 historical run is still active when this inventory is prepared.
No final result, broad accuracy, speedup or release readiness is inferred.

## Existing publication path to bind after version selection

1. Review the complete contents and choose the release version; bind the final
   revision, distribution hashes, rules/corpus identities and exact actions.
2. Deliver the accepted changes and run the required main/release checks under
   separately approved merge/push actions. Preserve the existing full gates.
3. Create a verified SSH-signed annotated version tag on the reviewed main HEAD,
   with the exact `Release VERSION` message required by `release.yml`.
4. The existing release workflow builds canonical artifacts, publishes and checks
   TestPyPI, then publishes PyPI and verifies hashes, provenance and platform
   installs. Its current last job is public-install verification.
5. Separately perform the approved GitHub release/assets action and verify hashes;
   verify the exact Action commit and compatible signed `v1` alias through the
   established external Action proof. These are not implicitly performed by the
   package release workflow.
6. Reproduce the accepted seven-input gate with the downloaded released detector,
   retain actual UTC publication/verification events, then obtain final acceptance.

Exact commands, package/Action pins and hashes cannot be final until version and
publication revision are chosen. No placeholder here is a publication approval.
The existing tested development packages still identify version 1.3.0 and must
not be uploaded as a replacement for immutable public 1.3.0.

## Rollback basis

The prior verified package pin is `portunusmcp-sentinel==1.3.0`; the matching exact
Action commit is `c45e10cf878cfa0f926687f88a5679729ce9a19f`. Its retained public hashes
are wheel `e5c529967c58735303b3ab5d6a836607d85f5f078949587a1335c5d6544d6cbf`
and sdist `859022c18bfd62f19983f98a40ad7ddb6ee14b655462f7217d6defd4acfd9523`.
Selecting that prior version loses the newer detection and coverage improvements.
Do not replace immutable tags/artifacts; moving `v1` back is a separately reviewed
action. Recheck these public bindings during the actual release review.
