# Approve the reviewed 1.4.0 publication

All **30 CI jobs, documentation and 12 platform suites passed** for candidate
`d5365dce6184707248dab17a921b3257cc508069`. Seven offline advisory reports match the reviewed
references; both distribution hashes match the reviewed local builds.

- [Complete contents, limits and release path](README.md).
- [Exact commands and conditions](commands.json).
- [Sealed proposal](proposal.json).
- Proposal SHA-256: `40cf8a21f0576c062a9016a650b5e980fee268c033926de1fde0d56bb01fcc30`.
- [Hosted evidence](../release-hosted-v1/summary.json).

## Requested approval

Approve the complete proposed sequence: mark PR40 ready, merge its exact reviewed
contents, run the existing main gates, create/push the verified SSH-signed
`v1.4.0` tag, follow the full TestPyPI/PyPI/provenance path, verify seven downloaded
released-wheel inputs, publish GitHub release assets, and verify the exact Action
pin and signed compatible `v1` alias using the prepared separate external branch.

This includes **21 new advisory observations** across main CI, release CI and
released-wheel verification, plus two rules-only clean Action proof invocations.
Normal limits and every required check remain. Zero paid calls or advisory-target
execution; no retries, timeout extensions, extra source changes or branch cleanup.
Stop on identity drift or any failed/incomplete required stage.

Your plan explicitly reserves merge/tag/publication for this review. Version
selection and the earlier draft-delivery approval did not authorize publication.
Phase 23 remains open until the release is verified and you explicitly accept
the final evidence.
