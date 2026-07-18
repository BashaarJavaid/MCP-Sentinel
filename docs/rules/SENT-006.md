# SENT-006 — Missing or ineffective route authentication

- Engine: custom framework-aware AST analysis.
- Impact: High; emitted severity is Medium while theoretical.
- OWASP: `ASI03:2026 — Identity & Privilege Abuse`. An unauthenticated route
  allows callers to exercise server authority without a verified identity.
- Boundary: FastAPI-style route decorators, authentication middleware, and
  dependency functions that read credentials, verify them, and reject failure.
- False-positive risk: Low. Intentional public routes must be listed explicitly
  as `METHOD /path-pattern` values.
- Acceptance: the vulnerable fixture exposes `/admin` without auth; the clean
  fixture uses a verified dependency and explicitly declares `/health` public.

Remediation: verify credentials and reject invalid identities before route code
runs.
