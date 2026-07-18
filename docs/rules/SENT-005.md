# SENT-005 — Hardcoded secret

- Engine: pinned Semgrep candidate rule with deterministic signature, entropy,
  redaction, fingerprint, and allowlist post-processing.
- Impact: Critical; emitted severity is High while theoretical.
- OWASP: `ASI03:2026 — Identity & Privilege Abuse`. Embedded credentials let
  anyone with source access assume the credential's identity and privileges.
- Boundary: supported Python and configuration files; provider signatures and
  contextual values of at least 20 characters with entropy at least 4.5.
- False-positive risk: Low–Medium. Exemptions require both a path glob and the
  SHA-256 fingerprint of the matched value; plaintext allowlisting is forbidden.
- Acceptance: the vulnerable fixture contains a GitHub-style token; the clean
  fixture reads its value from the environment.

Remediation: load credentials from an external secret store or environment.
