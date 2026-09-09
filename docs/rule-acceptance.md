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

The [approved technical contract](phase22-technical.md) governs SENT-012 through
SENT-016. All five are implemented and included in default static selection on the
integration branch. Implementation does not constitute technical sign-off: the
independent condition measurements, fresh holdout, reviewed retention and human
review remain separate gates in the [implementation status](phase22-implementation-status.md).

| Rule | Impact / initial severity | OWASP justification | Required false-positive controls | Review |
| --- | --- | --- | --- | --- |
| [SENT-012](rules.md#sent-012) | High / Medium | `ASI02:2026`: caller paths escape a tool's intended resource boundary | Enforced canonical containment, relevant guards, safe symlink handling | Pending |
| [SENT-013](rules.md#sent-013) | High / Medium | `ASI01:2026`: tool metadata explicitly redirects model goals | Benign imperatives and quoted security warnings | Pending |
| [SENT-014](rules.md#sent-014) | Critical / High | `ASI05:2026`: caller values become command options | Enforced option rejection and command-specific safe positions | Pending |
| [SENT-015](rules.md#sent-015) | High / Medium | `ASI02:2026`: caller URLs redirect server requests beyond intended services | Relevant scheme/destination rejection and authorized requests | Pending |
| [SENT-016](rules.md#sent-016) | High / Medium | `ASI03:2026`: caller requests inherit unauthorized operator credentials | Explicit authorized operator use and enforced caller rejection | Pending |

The initial severity above uses theoretical exploitability. The canonical catalog
owns impact, remediation and false-positive risk; the canonical OWASP map owns the
category. Findings use the shared identity, evidence/provenance, severity,
suppression, baseline and report pipeline. Selecting a rule by ID does not create
a different finding shape or change its meaning.

The durable controls are `test_containment.py`, `test_typescript_containment.py`,
`test_description_poisoning.py`, `test_command_options.py`, `test_ssrf.py` and
`test_credential_fallback.py`. They cover applicable Python and TypeScript flows,
relevant versus unrelated/discarded guards, replacement and mutation, and safe
partners. Shared engine tests check default/explicit selection and SARIF catalog
identity; CLI rule tests check suppression, baselines and severity thresholds.
Imported containment reporting also asserts that a target execution marker is
never created. Static workers operate only on scanner-owned parsed snapshots.

The rule catalog links describe bounded support and actionable remediation.
Unresolved frameworks, command semantics or operator policy remain visible and
need source review; a false alarm or uncertain unrelated candidate is not silently
converted into a condition hit. Frozen development and holdout cases are scored
against their exact named condition and prerequisites. The historical 70-warning
backlog remains distinct from newly reviewed candidates. No row is signed off by
this documentation update or by synthetic fixture success alone.
