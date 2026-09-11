# Replacement-v5 source-only checkpoint

Prepared under the [source-only authorization](../integration/v23-source-only-recovery-authorization.json).
**Evaluation is unapproved. Phase 22 remains incomplete.**

The [exact proposal](evaluation-proposal.json) and [checkpoint](checkpoint-1f3f72f.json)
bind scanner `1f3f72f0f25c597b53c9f833e2e4bec99728d328`, frozen before research.
The [source review](review/condition-review.json) and [novelty check](provenance/novelty.json)
record the labels, prerequisites, source exposure and comparisons against all
six earlier manifests and 92 effective trees. The other 45 input records remain
byte-for-byte equal as JSON records. No scanner/comparator outcomes informed selection.

The repository is `priyankark/lighthouse-mcp`, with vulnerable parent
`85a6355bdc0e6e0907a45d8783414b1128958741` and fixed child
`7570c4151fd50c843480cf7106db4c8061a97b35`. All 12 files per revision,
including MIT license and screenshot, are retained. The public source basis is
[upstream issue 23](https://github.com/priyankark/lighthouse-mcp/issues/23) and
[the direct fix](https://github.com/priyankark/lighthouse-mcp/commit/7570c4151fd50c843480cf7106db4c8061a97b35).

Only `run_audit`'s rejection of literal `http://169.254.169.254/` before Chrome
launch is labeled. The vulnerable source has no URL policy at that boundary;
the fixed source checks the literal against a link-local prefix. The public
control uses `http://8.8.8.8/`. Two mutations reversibly rename the argument
predicate and both calls. These are five correlated inputs from one vulnerability.
The same implementation agent curated after freezing the scanner; this is not
independent human review or an unseen-source claim.

The normal upstream SDK compatibility patch remains intact. Startup, temporary
directory access and Chrome availability are unexecuted prerequisites.
Package versions advance 0.1.12 to 0.1.13, while unchanged lock metadata says
0.1.11 and the runtime identity says 0.1.0. Exact revisions and lock bytes govern.
The fixed policy intentionally allows loopback and returns on DNS failure.
Redirects, IPv6, response contents, actual network requests and runtime exploit
proof are outside the narrow labels. No broad SSRF protection claim follows.

Proposed execution order: `rules-first`, `rules-repeat`, `semgrep-first`, each
using the five ordered IDs in the proposal. Approval would permit 10 native and
five Semgrep observations, one standard Linux 90-minute job, a 120-second target
and 300-second whole-input maximum, with zero retries, profiles, target execution
or paid calls. Failures close the unused budget; detection outcomes remain visible
and require disposition where applicable. No prior budget transfers.
