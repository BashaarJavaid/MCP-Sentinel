# Checkpoint 2 — Third authorized resumption

The user approved another 18-request resumption by replying “continue” to the
38-cumulative-attempt, $3.72-ceiling proposal. The immutable approval is
`checkpoint2-resume-approval-3.json`.

Cumulative attempt **21** immediately failed production validation with
`injection probe requires a string field`. This is the third consecutive failed
attempt for fingerprint
`7cf99e2bdd9215fa1cf8274fc5a75b256e70aae05a2a03ecfd14fa0a232cee58`
(`excel-boundary-fixed-mutation`, SENT-003, `create_table`). Capture stopped without
an automatic retry or any change to production prompts, probes, validation,
detectors, source or configuration. No new response was accepted.

There remain **17 accepted captures**, now accompanied by **four failed attempts**.
Accepted usage cost is **$0.374996**; uncertain failed-request reservations total
**$0.406680**. Cumulative accounting is **$0.781676**, not an exact billing claim.
All accepted capture hashes still match the ledger, so the existing verified
45-input replay is reused (`resume-3-capture-integrity.json`). Review decisions,
detection outcomes, support, and completion are unchanged.

Repeatedly retrying this request has prevented attempting the remaining requests.
[The new proposal](checkpoint2-resume-proposal-4.json) therefore names only the
**17 never-attempted requests**, preserving their original packet order, source,
settings, request hashes and reservations. It explicitly excludes the repeatedly
rejected request from further paid capture. That request, its findings, and its
input remain visibly incomplete in the 45-input benchmark; no label, denominator,
or finding is removed and no response is manufactured.

The proposed selection fits the already selected **38 cumulative attempts** and
**$3.72** ceiling, with a conservative cumulative reservation of **$2.568871**.
This selection change is **pending user approval**. A subsequent approval must
include the proposal's exact `request_fingerprints` list. The harness validates
that this is a nonempty list of unique fingerprints from the original frozen
packet, then preserves packet order. Tests reject malformed, duplicate and unknown
selections without invoking capture. Existing approvals without a selection retain
their original behavior. First-failure stopping and cumulative accounting remain
unchanged. No call under this new proposal has run.
