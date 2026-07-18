# Static rule acceptance record

Phase 1 accepts a rule only when its permanent ID, OWASP Agentic Top 10 2026
justification, false-positive risk, impact rating, remediation, vulnerable
fixture, clean fixture, and no-target-execution boundary are documented and
reviewed. Emitted severity is computed from the recorded impact and the
Finding's exploitability; it is not copied from this table.

| Rule | Engine | OWASP justification | FP risk | Fixture pair | No target execution | Review |
|---|---|---|---|---|---|---|
| SENT-001 | AST | `ASI03:2026`: excess capability expands effective identity authority | Medium | Pass | Pass | Signed off |
| SENT-002 | Semgrep | `ASI05:2026`: unsafe sinks turn input into executable behavior | Low | Pass | Pass | Signed off |
| SENT-003 | AST | `ASI02:2026`: unchecked arguments permit unintended tool use | Medium | Pass | Pass | Signed off |
| SENT-004 | AST | `ASI01:2026`: tool text can redirect later model goals | Medium–High | Pass | Pass | Signed off |
| SENT-005 | Semgrep | `ASI03:2026`: embedded credentials confer their identity and privilege | Low–Medium | Pass | Pass | Signed off |
| SENT-006 | AST | `ASI03:2026`: unauthenticated routes exercise server authority | Low | Pass | Pass | Signed off |
| SENT-007 | AST | `ASI04:2026`: unverified metadata permits supply-chain substitution | Low | Pass | Pass | Signed off |

The detailed detection boundaries and exemption mechanisms are versioned in
[`docs/rules/`](rules/).
