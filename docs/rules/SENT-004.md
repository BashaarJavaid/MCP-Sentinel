# SENT-004 — Unsanitized tool content in prompt

- Engine: custom intraprocedural AST taint analysis.
- Impact: High; emitted severity is Medium while theoretical.
- OWASP: `ASI01:2026 — Agent Goal Hijack`. Tool-controlled text inserted into a
  later model prompt can redirect the agent's governing instructions.
- Boundary: direct tool text/description/content flow into prompt returns or
  OpenAI request fields within one function.
- False-positive risk: Medium–High. The rule is deliberately best effort;
  trusted sanitizer names must be configured explicitly.
- Acceptance: the vulnerable fixture interpolates tool content directly; the
  clean fixture passes it through `server.sanitize_tool_text`.

Remediation: pass tool-controlled content through a configured sanitizer before
constructing the next prompt.
