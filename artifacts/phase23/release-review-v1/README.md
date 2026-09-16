# Release review preparation: proposed 1.4.0

**The technical result is accepted. The release version is awaiting the maintainer's
choice.** The proposed version is **1.4.0**, reflecting the new rules and report
coverage accepted since 1.3.0. Selecting a version does not authorize publication.

The exact [ten-file version patch](version-1.4.0.patch) is prepared in an isolated
copy. It has not been applied to the working checkout, which remains version
1.3.0. No push, merge, tag, package publication or Action alias change occurred.

## Complete release contents

- Accepted Phase 19 coverage/review activity and actionable console/SARIF evidence.
- Accepted Phase 20 benchmark/execution corrections: pinned runtime Git support,
  dependency-image cache identity and nullable/union probe validation. Historical
  failed measurements remain retained.
- Accepted Phase 22 rules: SENT-012 path containment, SENT-013 tool-description
  poisoning, SENT-014 command option injection, SENT-015 SSRF and SENT-016 operator
  credential fallback. Includes bounded Python/TypeScript source flow, imported
  and registered handlers, receiver/guard/module-dispatch support, workspaces,
  the 1,800-second static deadline and accepted private performance contracts.
- **Current native schema 1.7.0**, including ordered runtime attempts and workspace
  coverage; strict baseline migration accepts native 1.3–1.7. The earlier release
  inventory correctly named Phase 19's 1.6 additions but omitted Phase 22's 1.7
  additions. [The correction](schema-inventory-correction.json) binds existing
  accepted main code; no new report contract change is introduced here.
- Accepted Phase 23 TypeScript star exports, proved promisify identities,
  independent handler invocation stacks and bounded Zod metadata composition;
  seven-input current-candidate offline CI and deliberate regression rejection;
  reviewed feedback forms, source-rights/privacy guidance and manual weekly review.
- Full existing platform, package, replay, isolation, documentation and dependency
  gates remain. No dependency or service is added. Every dependency lock record
  remains identical except the project's own proposed version.

Canonical Finding, rule meanings, baseline matching, suppression, model contracts
and CLI exit-code semantics remain stable. New default rules can produce new
findings. Consumers requiring an exact native schema must support 1.7.0; SARIF
remains 2.1.0. Source support is bounded, and zero findings are not safety assurance.

## Accepted limitations and evidence

The [technical acceptance receipt](../technical-acceptance-v1/receipt.json) binds
proposal `d153cc83576e21ee22ce1fead0d3c123128dc623cd53b55d90d04fd65fb6bfd9`.
The advisory gate, all 30 hosted CI jobs/docs and 12 native suites, 14 original
advisory compatibility observations, actual deliberate rejection, and 106 non-FAF
reports/53 equal pairs remain verified.

FAF's current 1,800.011759-second timeout stays failed: no report, five unstarted
observations closed. Current FAF detection/support/repeat compatibility is
accepted as unestablished. Proxmox remains unsupported; recovery/optimization,
pilots and paid benchmark remain deferred. Phase 22's accepted audit/limitations
and all original failures remain. Phase 21 and Phase 24/15 gates are unchanged.
The replacement advisory retains 56 unrelated `needs_review` occurrences.

## Version preparation checks

| Check | Result |
| --- | --- |
| Offline wheel and sdist build | Passed using the existing cached backend. |
| Existing archive metadata/resource checks | Passed for both distributions. |
| Packaged scanner bytes | All 134 files match the proposed copy; only the package fallback version differs from the accepted scanner. |
| Dependency lock comparison | Only own package version changes from 1.3.0 to 1.4.0. |
| CLI version, report banner and Action pin tests | Three passed against the proposed installation/copy. |
| Current documentation | Strict build passed after acceptance and inventory correction. |
| New advisory observations or paid calls | Zero. |

Prepared package pin: `portunusmcp-sentinel==1.4.0`.
Proposed Action installation pin: the same exact PyPI version. Final immutable
Action commit and signed version tag will be bound after version selection and
before publication approval; no hash is invented here.

Preparation artifacts (not uploaded):

```text
fc9c0155b08687e2a50e327cca4ebc8b7be759539eaef3e4aa4e08801d23f1af  portunusmcp_sentinel-1.4.0-py3-none-any.whl
794aa8270d5220193cbc8e528a0afd2e33c36e6eeb790ae0624221d69b87b7b3  portunusmcp_sentinel-1.4.0.tar.gz
```

The sdist still contains Unreleased notes. After selection, the dated release
notes and final contents must be sealed and built again before publication review;
these preparation hashes must not be represented as already approved public assets.
The original acceptance proposal, frozen corpora, report schema version literals,
historical captures and historical release pins remain unchanged.

## Publication sequence to finalize after version choice

1. Apply the selected exact version changes, finalize the complete release notes,
   prepare the reviewed commit/tree and build final artifacts. Verify the version
   changes and the required full gates against that exact candidate.
2. Present the final immutable Action pin, package hashes, contents, revision and
   exact proposed push/ready/merge/tag/publication/alias actions for approval.
   Expected current remote main is `dd9101ddfead19d65b7a84b374e4cf7e85462ff7` and
   draft PR40 head is `4bc28d050bdbfcbf675bb0cf0c77c82f855acd7f`; unexpected drift
   stops delivery for review. The read-only snapshots in this packet confirm them.
3. After explicit approval, use the existing verified SSH-signed version tag on
   reviewed main HEAD, full release CI, TestPyPI verification, then PyPI hashes,
   provenance and supported-platform install checks. Failures stop the sequence.
4. Perform the approved GitHub release/assets action and exact Action/v1 proof.
   The package workflow does not automatically perform those external actions.
5. Run seven released-detector regression inputs once, with the same approved
   comparisons and 1,800/10/15-second limits, four-worker maximum and 220-minute
   outer cap plus cleanup, under a separately bound release verification packet.
   The source-checkout identity guard must be preserved for ordinary CI; installed
   wheel identity must be verified explicitly for this published-detector check.
6. Retain actual publication/verification times, artifacts and provenance, then
   obtain explicit final acceptance. Phase 23 remains open until that verified loop.

No observation or publication step in this sequence is authorized by the current
version-selection question. No automatic retry, timeout extension or reference
promotion is proposed.

## Rollback

Return to the previously verified `portunusmcp-sentinel==1.3.0` and exact Action
commit `c45e10cf878cfa0f926687f88a5679729ce9a19f`, accepting the loss of the newer
fixes/coverage. Preserve immutable version tags and uploaded artifacts. Any move
of mutable `v1` back requires explicit approval. Current public PyPI remains
1.3.0 and does not contain 1.4.0, as recorded in `pypi.json`.
