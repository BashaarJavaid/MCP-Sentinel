# Complete the remaining 1.4.0 release steps

**PyPI publication and released-wheel verification are complete.** The remaining
GitHub release command was blocked by automatic approval review before execution.
The reviewer cited older `AGENTS.md` authorization text. Your original publication
approval remains retained; the current status now distinguishes completed actions
from this executor block. No denied action was bypassed.

## Completed and verified

- PR40 merged at `fd10cba1297a32ec35ec647e17f3491dbb3b0979`, exact reviewed tree/parents.
- Main: 30 CI jobs plus deployed documentation; release: all47 jobs including
  TestPyPI/PyPI provenance and all12 public installation jobs.
- SSH-signed immutable `v1.4.0` tag verified by GitHub.
- Public wheel/sdist exactly match approved hashes; signed provenance names the merge.
- All21 approved advisory observations completed. The downloaded wheel's seven
  reports match reviewed references: three detections/four supported negatives,
  31 findings/4,377 warnings retained, 97.037248625 seconds, cleanup verified.
- Original deliberate regression-rejection proof and all accepted limitations remain.

See [publication evidence](../publication-v1/summary.json),
[public artifact verification](../publication-v1/public-artifact-verification.json),
[main gates](../publication-main-v1/summary.json),
[release gates](../publication-release-v1/summary.json), and
[lifecycle](../lifecycle/ghsa-3q26-v20-pypi-published.json).

## Exact remaining actions for approval

1. Create GitHub release `v1.4.0` with the already reviewed notes and the two
   hash-verified public artifacts. The release is currently absent.
2. Push prepared commit `26615d0da25c8af1b9944010397b79765cc365d5` to the absent
   `phase23-1.4.0-release-proof` branch of `BashaarJavaid/mcp-sentinel-action-demo`.
   Run its prepared rules-only exact Action proof once at
   `BashaarJavaid/MCP-Sentinel@d5365dce6184707248dab17a921b3257cc508069`.
3. Only after that proof passes, SSH-sign/update `v1` to the verified release merge,
   using the approved lease against old tag object `089adf0891465ddcb78100e06ecf2a2228566c51`.
   Verify its remote signature and target; run the prepared rules-only alias proof once.
4. Retain all public assets/proofs and request separate final Phase23 acceptance.

[Exact commands](commands.json) are unchanged from the original approved packet.
No new package upload, version tag, advisory observation, paid call, target execution,
source change, main evidence commit or cleanup. Preserve immutable releases and all
historical failures; stop on drift or any failed/incomplete check, with no retries.
The two external proof invocations remain unstarted. Final Phase23 acceptance is separate.

## Why approval is requested again

Automatic review rejected GitHub release creation because it considered the older
repository authorization text controlling. This request explicitly authorizes the
remaining public GitHub release and Action/alias operations above, superseding that
older pending-authorization text. Earlier PyPI approval calls were also rejected;
GitHub subsequently recorded the owner's separate environment approval and the
publication workflow passed. Both rejected calls and the GitHub review history are retained.
