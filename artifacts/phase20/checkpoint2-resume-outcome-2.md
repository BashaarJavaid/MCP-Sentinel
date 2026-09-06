# Checkpoint 2 — Second authorized resumption

The user replied “continue” to the explicit proposal for 18 remaining requests,
37 cumulative attempts, the unchanged $3.72 ceiling, and stopping on the next
failure. `checkpoint2-resume-approval-2.json` records that approval against the
unchanged original request packet and the second proposal.

The first resumed request (cumulative attempt **20**) failed production validation
again with `injection probe requires a string field`. This is the same fingerprint
as attempt 19:
`7cf99e2bdd9215fa1cf8274fc5a75b256e70aae05a2a03ecfd14fa0a232cee58`, the SENT-003
`create_table` candidate on `excel-boundary-fixed-mutation`. Capture stopped
immediately. No new response was accepted, and no prompt, probe, detector,
validator, source, or configuration was changed.

There are **17 accepted captures and three failed attempts**. Accepted usage cost
remains **$0.374996**. Uncertain failed-request reservations total **$0.304955**;
cumulative accounting is **$0.679951**. Actual billing for the discarded invalid
responses is unavailable. The duplicate failed attempt remains charged separately.

All accepted capture hashes and the remaining request set match their state
before this resumption (`resume-2-capture-integrity.json`). The verified 45-input
replay is therefore reused without another scan. Detection, review decisions,
coverage, and completion remain unchanged; only paid-failure accounting changed.
The initial full hosted CI matrix at commit `476c2b9` has now passed, as retained
in `hosted-measurement-ci-final.json`. This does not claim that later branch
revisions have finished hosted CI.

[The next proposal](checkpoint2-resume-proposal-3.json) names the same **18 remaining
requests**, including the repeated failure. It would require **38 cumulative
attempts** under the unchanged **$3.72** ceiling, with a conservative cumulative
reservation of **$2.568871**. All accepted captures would be reused and another
failure would stop capture again. This proposal is not approval; a further live
attempt requires a new user decision under the selected stopping policy.
