# Review the 1.4.0 draft delivery

The selected release is prepared and locally verified: **2,766 tests passed /
36 skipped**, all `make check` targets passed, and 52 focused checks passed.
The original eight mocked-version failures and five-line test correction remain
retained. Detector logic, production comparison rules and frozen reports are unchanged.

- Exact candidate: `d5365dce6184707248dab17a921b3257cc508069`.
- Tree: `a736214212f90dbfec34f4b6362b4e3c741a3922`.
- Reviewed changed files: 1533; all blob bytes verified.
- Proposal: [delivery-proposal.json](delivery-proposal.json).
- Proposal SHA-256: `02580e2ecac97b630b72adbe4ecec7442deb5f09bd889f2c78431fa0f72b1666`.
- Release contents and limitations: [README.md](README.md).
- Local results: [local-checks.json](local-checks.json).

## Requested approval

Approve updating existing **draft PR40** to this exact candidate, updating its
reviewed title/description, and running its normal hosted CI/docs once. This
includes seven current-candidate advisory observations in the existing Linux
network namespace, with unchanged input/Semgrep/cleanup/worker bounds and
220-minute helper cap. Every existing required gate remains. Stop on remote
drift or failed/incomplete checks. No historical retry or paid call.

The exact prospective Action pin is
`BashaarJavaid/MCP-Sentinel@d5365dce6184707248dab17a921b3257cc508069`; package pin is
`portunusmcp-sentinel==1.4.0`. Their publication remains unapproved.

This is a delivery checkpoint before the final publication review: the plan
requires hosted verification and exact artifact/revision review before approval
of merge, signed tag, publication and Action alias actions. The version choice
does not authorize those actions. PR40 stays draft. Phase 23 remains open.

The commit was prepared with an isolated index; main HEAD and the user's index
are unchanged. This delivery proposal and commit receipt are post-commit review
records, outside the candidate they identify. No remote write has occurred.
