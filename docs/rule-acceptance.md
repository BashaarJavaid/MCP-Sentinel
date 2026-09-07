# Static rule acceptance record

Phase 1 accepts a rule only when its permanent ID, OWASP Agentic Top 10 2026
justification, false-positive risk, impact rating, remediation, vulnerable
fixture, clean fixture, and no-target-execution boundary are documented and
reviewed. Emitted severity is computed from the recorded impact and the
Finding's exploitability; it is not copied from this table.

| Rule | Engine | OWASP justification | FP risk | Fixture pair | No target execution | Review |
|---|---|---|---|---|---|---|
| SENT-001 | Hybrid | `ASI03:2026`: excess capability expands effective identity authority | Medium | Python + TypeScript pass | Pass | Signed off |
| SENT-002 | Semgrep | `ASI05:2026`: unsafe sinks turn input into executable behavior | Low | Pass | Pass | Signed off |
| SENT-003 | Hybrid | `ASI02:2026`: unchecked arguments permit unintended tool use | Medium | Python + TypeScript pass | Pass | Signed off |
| SENT-004 | Hybrid | `ASI01:2026`: tool text can redirect later model goals | Medium–High | Python + TypeScript pass | Pass | Signed off |
| SENT-005 | Semgrep | `ASI03:2026`: embedded credentials confer their identity and privilege | Low–Medium | Pass | Pass | Signed off |
| SENT-006 | Hybrid | `ASI03:2026`: unauthenticated routes exercise server authority | Low | Python + TypeScript pass | Pass | Signed off |
| SENT-007 | Hybrid | `ASI04:2026`: unverified metadata permits supply-chain substitution | Low | Python + TypeScript pass | Pass | Signed off |

The detailed detection boundaries and exemption mechanisms are versioned in the
[`docs/rules.md`](rules.md) catalog.

This table preserves the original acceptance record. Phase 16 extends
`SENT-002` with bounded same-file flow analysis and corrects safety exemptions
without reassigning rule IDs. Its [verification record](phase16-verification.md)
retains failing-before cases, paired controls, and historical-review compatibility
evidence. Those development cases and code coverage do not measure independent
detection accuracy.

## Phase 22 pending acceptance

The [approved technical contract](phase22-technical.md) reserves SENT-012 through
SENT-016. None is accepted or enabled by this table. Each requires the new
independent development/held-out pairs, safe controls, structural mutations,
applicable Python/TypeScript regressions, actionable remediation and measured
false alarms before technical sign-off.

| Rule | OWASP justification | Required false-positive controls | Review |
| --- | --- | --- | --- |
| SENT-012 | `ASI02:2026`: caller paths escape a tool's intended resource boundary | Enforced canonical containment, relevant guards, safe symlink handling | Pending |
| SENT-013 | `ASI01:2026`: tool metadata explicitly redirects model goals | Benign imperatives and quoted security warnings | Pending |
| SENT-014 | `ASI05:2026`: caller values become executable command options | Enforced option rejection and command-specific safe positions | Pending |
| SENT-015 | `ASI02:2026`: caller URLs redirect server requests beyond intended services | Relevant scheme/destination rejection and authorized requests | Pending |
| SENT-016 | `ASI03:2026`: caller requests inherit unauthorized operator credentials | Explicit authorized operator use and enforced caller rejection | Pending |
