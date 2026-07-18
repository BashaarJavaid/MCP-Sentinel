# SENT-003 — Missing tool input validation

- Engine: custom MCP-aware AST analysis.
- Impact: Medium; emitted severity is Low while theoretical.
- OWASP: `ASI02:2026 — Tool Misuse & Exploitation`. Unvalidated tool arguments
  let callers reach handler behavior outside its intended input contract.
- Boundary: FastMCP decorated tools and official SDK `call_tool` dispatchers;
  concrete types, Pydantic validation, and JSON Schema validation are trusted.
- False-positive risk: Medium. Unrecognized custom validators can be reported.
- Acceptance: the vulnerable fixture consumes a raw dictionary; the clean
  fixture accepts a Pydantic model.

Remediation: validate parameters with concrete handler types, Pydantic, or JSON
Schema before their first use.
