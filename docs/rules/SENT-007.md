# SENT-007 — Unverified tool manifest

- Engine: custom AST ordering analysis with strict integrity-sidecar validation.
- Impact: Medium; emitted severity is Low while theoretical.
- OWASP: `ASI04:2026 — Agentic Supply Chain Vulnerabilities`. Registering an
  unverified manifest lets modified supply-chain metadata redefine trusted tools.
- Boundary: JSON/YAML manifest loads and earlier supported SHA-256, constant-time
  digest, or signature-verification calls in the same function.
- False-positive risk: Low. Custom cryptographic wrappers outside the supported
  boundary may require future coverage.
- Acceptance: the vulnerable fixture loads YAML without verification; the clean
  fixture verifies a pinned digest before parsing.

Remediation: verify a pinned SHA-256 digest or trusted detached signature before
parsing and registration.
