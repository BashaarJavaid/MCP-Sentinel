# Phase 22 paid evaluation — smoke/demo subset approved

The full proposed ceiling is **398 new requests / $66.321920**. Only the
two-request smoke/demo subset was approved and executed; benchmark review remains
unapproved. The original proposal below is retained for its exact request contract. The [packet](packet.json) SHA-256 is
`9fbe33de0f3dda4ccaa2e3a058d96d6c43d0cb7518eeb72547c1c30cf78ef3c1`.
The lossless [request archive](requests.tar.gz) retains every exact production request,
candidate and source context, including reused requests. Its hash, all request
fingerprints, normalized request hashes, input identities and individual token/
dollar reservations are in the packet.


The approved TypeScript smoke and Docker demo requests both succeeded without
retries. Their recorded costs are $0.016947 and $0.054852, **$0.071799 total**.
Exact request hashes, accepted capture hashes and usage remain in
`captures/static/ledger.json` and `captures/runtime/ledger.json`. Both captures
pass the existing production replay parser with accepted-ledger validation.
The packaged additions preserve every historical capture and manifest entry.
No benchmark review, replacement evaluation or Meta amendment was performed.

| Purpose | New requests | Reserved ceiling |
| --- | ---: | ---: |
| Historical 45-input reviewed static tier | 307 | $50.920360 |
| Original 25-input development tier | 87 | $14.791355 |
| Original held-out tier on completed inputs | 2 | $0.210105 |
| Corrected TypeScript smoke capture | 1 | $0.095520 |
| Actual demo dynamic review | 1 | $0.304580 |
| Total | 398 | $66.321920 |

Twenty distinct requests reuse historical captures: 16 have accepted capture
ledger entries and pass exact request/semantic replay checks; four packaged demo
captures successfully review seven static findings. The older packaged payloads
lack normalized request hashes and ledgers, a limitation retained in the packet.
None is represented as a new live measurement. Original captures, ledgers, costs,
source, labels, first held-out results and exposed-case records remain unchanged.

Actual configuration is `gpt-5.6-sol`, medium reasoning, the official OpenAI
Responses endpoint, Standard/default service tier, 30-second request timeout,
serial execution, no retries and no local cache. Requests disable tools, storage,
streaming and background execution. The aggregate reservation is 8,566,272 input
tokens and 1,174,528 output tokens, using full serialized UTF-8 bytes plus a
4096-token framing margin per request, cache-write input prices and full output
caps. Official pricing was checked on September 9, 2026; the packet retains the
source and exact rates, including long-context premiums.

The original corpus remains 45 historical, 25 development and 25 held-out inputs.
Historical and development native scans complete all inputs; held-out scans
complete 10, with 10 unsupported and 5 incomplete. Unavailable inputs receive no
invented review completion. The ten corrected unrelated auth-fetch coordinates
are exposed regressions. The separately proposed replacement five are **excluded**
from this packet and require their own freeze decision before evaluation. The
Meta fixed-label decision and independent human/pilot acceptance remain separate.

Before this subset capture, independent local quality, package, real Docker,
installed onboarding, baseline, pre-commit and network-isolation checks passed. The raw 6e68331 full suite
retains two failures: the stale cost expectation has a passing targeted correction
at d7184d3. The TypeScript replay and Docker demo failures from that source
remain preserved. With the two new captures, the unchanged TypeScript regression
passes and the actual Docker demo exits 0: 20/20 attempts, all seven static and
seven dynamic findings reviewed, and valid JSON/SARIF.

The earlier demo exited 3 for missing dynamic review; that raw result is retained.
The successful local replays do not relabel earlier failed hosted runs as passed.

The [capture driver](phase22-v2-paid-capture-driver.py) defaults to an explicit
`check` command and reuses the existing `scripts.phase20_review.capture_batches`.
Its validation checks source, environment, request and packet identities before
reading a key. Nine offline self-checks pass with a fake capture transport; actual
model transport is forbidden during those checks. No synthetic self-test approval
is user authorization. The expanded `requests.json` remains locally preserved; Git stores its compressed
copy to keep the consolidated diff reviewable. Archive SHA-256:
`9e50d0220978bfc0892da48187d24d31543c46882b35582eaa14bc16e3cb0e23`.
The sole archive member was read back byte-for-byte and its raw SHA-256 matches
the approved packet proposal. Reproduce the packet check in the retained
immutable 6e68331 checkout/environment:

```sh
tar -xzf artifacts/phase22/paid-evaluation-v2/requests.tar.gz \
  -C artifacts/phase22/paid-evaluation-v2
/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python \
  artifacts/phase22/paid-evaluation-v2/phase22-v2-paid-capture-driver.py \
  check artifacts/phase22/paid-evaluation-v2/packet.json
```

Execution requires a separate approval file naming this exact packet hash, the
user decision, unique selected fingerprints and request/dollar ceilings. The separate [smoke/demo approval](approval-smoke-demo.json) authorizes exactly
two fingerprints and a $0.400100 ceiling; it does not approve the full packet. Static and runtime stage ceilings partition the
approved total. Each request is reserved durably before send; stop on the first
failure, missing usage, usage above its reservation, or unaffordable request.
Uncertain charges stay reserved. A failed static stage prevents runtime capture;
a stopped or interrupted run requires a new explicit budget decision. Successful
captures remain reusable without repeating their cost.

A smaller approval can select only the TypeScript smoke and demo requests:
**two requests / $0.400100**. That can unblock packaged replay checks but does not
complete the required benchmark-reviewed tier. The full requested approval is
required by the continuation handoff §15; tool permissions do not authorize spend.
