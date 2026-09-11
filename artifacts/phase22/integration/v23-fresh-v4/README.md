# Replacement-v4 execution preparation

**Prepared; approval pending. No fresh observations or paid calls.** This is
version 23 of the Phase 22 integration evidence, not authorization for Phase 23.

The unchanged [operational proposal](../../corpus-replacement-v4/evaluation-proposal.json)
has SHA-256 `28cd716118f71c390a3aeb28c5c541981e9196e50fb909ffa26be1da8a989843`.
The unchanged [freeze checkpoint](../../corpus-replacement-v4/checkpoint-1f3f72f.json)
has SHA-256 `e68cd09a5f9fa177728bfbb6e02b5f78a546350e9ed4f5ddc03df53d239e7c25`.
The manifest hash is `966b8b0578832916c97018316fe890a428b63533242577b8b7cc6f636b59ca7b`.
Measured scanner remains `1f3f72f0f25c597b53c9f833e2e4bec99728d328`.

Approval would authorize one standard Linux dispatch, in this order:

1. `rules-first`: the five named inputs in the proposal.
2. `rules-repeat`: the same five, comparing entire ordered reports.
3. `semgrep-first`: the same five with pinned Semgrep 1.176.0 and 533 rules
   across 511 configurations from the retained comparator selection.

The budget is ten native and five comparator observations, 300 seconds per
whole input, a 120-second native target, at most 15 seconds cleanup per input,
a 90-minute job limit and an 88-minute internal stop. No child starts without
315 seconds remaining. There are no retries, profiles, paid calls, target
execution or detector changes. Execution, identity, schema, cleanup, timeout or
ordered-repeat failure closes the remaining budget. Detection misses and false
alerts remain outcomes; they do not stop collection or permit tuning.

The sources concern initial `auth_fetch` navigation to a hexadecimal IPv4-mapped
loopback address. Private opt-in and hostname allowlist are unset; successful
browser startup is a prerequisite, not tested here. The public mapped-address
control and two reversible helper renames remain correlated with one repository
and one vulnerability. Sources were curated by the implementation agent after
the immutable scanner freeze, with source exposure disclosed. No independent
human review, unseen-source result, DNS/redirect protection or runtime proof is
claimed. Any measured detection limitation needs the user's explicit disposition.

[baseline.json](baseline.json) verifies the handoff, unchanged source/lock/harness,
all 51 seals and every member, the 45 unchanged records, and source-only
materialization/configuration of the five inputs. [preparation.json](preparation.json)
binds the concrete [runner](runner.py), optional workflow and synthetic controls.
The runner reuses `measure()`, `frozen(approval_path=...)`, native/SARIF validators,
and the tested Linux process-group supervisor. It refuses execution without the
new exact approval receipt and final file binding. Existing normal CI jobs have
only mutually exclusive manual-dispatch guards added. A normal PR update cannot
start the fresh measurement job.

After approval, append the actual decision as `authorization.json`, retain the
original proposal unchanged, and freeze `binding.json` over the receipt, runner,
workflow, supervisor and required assets. Stage only verified corpus assets into
a separate checkout of the frozen scanner; do not modify the preserved frozen
worktree. Dispatch CI once with `phase22_fresh_v4=true` and
`phase22_historical=false`, after required candidate quality checks pass. Retain
the dispatch receipt, all hosted artifacts, attempts/unstarted accounting and
source assessments before asking for Phase 22 technical acceptance.

Phase 22 remains incomplete: R66, R88 and R84 are unresolved. The historical
whole-batch gate and all three exposed SSRF regressions retain their passing
source-bound evidence. Full paid evaluation and external pilots remain deferred;
Git's 13 campaigns remain incomplete. Acceptance, subsequent closeout delivery,
merge/release and later phases are distinct decisions; only Phase 22 work and
delivery to existing draft PR #37 are authorized here.
