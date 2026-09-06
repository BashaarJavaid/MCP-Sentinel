# Checkpoint 2 — First authorized resumption

The user replied “continue” to the explicit proposal for 30 remaining requests,
36 cumulative attempts, the unchanged $3.72 ceiling, and stopping on the next
failure. `checkpoint2-resume-approval.json` binds that proposal and the original
request packet. No production settings or request contents changed.

Thirteen additional requests ran: twelve were accepted, including the previously
failed request. Cumulative request 19 then failed production validation with
`injection probe requires a string field`. Capture stopped immediately, without
an automatic retry. There are now **17 accepted captures and two failed attempts**.

The new failed fingerprint is
`7cf99e2bdd9215fa1cf8274fc5a75b256e70aae05a2a03ecfd14fa0a232cee58`, for
`excel-boundary-fixed-mutation`, SENT-003 on `create_table` at
`src/excel_mcp/server.py:432`. The native reviewer discarded the rejected response;
its raw response and actual usage are unavailable. The exact prepared request and
native rejection remain evidence. No validator, prompt, probe or detector was tuned.

Accepted usage costs **$0.374996** across 17 unique captures. The original failed
attempt retains its **$0.101505** reservation even though a subsequent attempt for
the same request succeeded. The new failed attempt reserves **$0.101725**.
Cumulative accounting is **$0.578226**, including both uncertain charges; it is
not a statement of exact billing.

The twelve newly accepted responses were inspected against the frozen conditions:

- Ten single-candidate Excel requests suppress generic declared-type-validation
  warnings based on supplied schemas. They do not allege a remote file-boundary
  failure. These suppressions are not incorrect suppression of a matched
  benchmark condition; their whole-repository correctness remains unadjudicated.
- Two Kubernetes requests confirm four HTTP-authentication warnings in
  `src/utils/sse.ts` and `tests/sse.test.ts`. They do not address command execution
  in the labeled `kubectl_get` handler. Shared captures apply to all five
  Kubernetes inputs, without multiplying paid cost.

The first partial replay and repeat evidence remain in `replay-after-first-stop/`
and `replay-after-first-stop-reproducibility.json`. `replay/` is the updated
partial treatment with all 17 accepted captures. Prior summaries describe their
historical capture state. Git has no static review candidates, so its retained
Docker measurement and runtime replay are unchanged; Checkpoint 3 still has zero
new review requests.

`checkpoint2-resume-proposal-2.json` names the **18 remaining exact requests**,
including the new failed request. Completing them would require **37 cumulative
attempts**, with the unchanged **$3.72** cost ceiling. Its conservative cumulative
reservation is **$2.467146**. All accepted captures would be reused. The proposal
is not approval; another live attempt requires a new
user decision under the selected first-failure stop policy.
