# SENT-001 — Overly broad tool permission scope

- Engine: custom MCP-aware AST analysis plus `sentinel.permissions.yaml`.
- Impact: High; emitted severity is reduced to Medium while theoretical.
- OWASP: `ASI03:2026 — Identity & Privilege Abuse`. A capability grant wider
  than the handler's observed need expands the identity's effective authority.
- Boundary: official SDK/FastMCP tool handlers; literal filesystem paths and
  network hosts; dynamic paths are treated as broad.
- False-positive risk: Medium. Legitimately broad tools must record a
  per-capability `broad_scope_justification`.
- Acceptance: the vulnerable fixture grants `**` for one literal file read;
  the clean fixture records an explicit justification for the broad reader.

Remediation: narrow each declared capability to the resources the handler
actually uses, or document why a broad capability is required.
