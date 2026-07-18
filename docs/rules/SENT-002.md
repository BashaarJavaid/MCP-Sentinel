# SENT-002 — Unsafe execution from tool input

- Engine: pinned Semgrep CLI rule.
- Impact: Critical; emitted severity is High while theoretical.
- OWASP: `ASI05:2026 — Unexpected Code Execution`. Dynamic evaluation and
  unsafe deserialization let tool-controlled values become executable behavior.
- Boundary: `eval`, `exec`, `pickle.loads`, unsafe `yaml.load`, and shell-enabled
  subprocess calls in Python.
- False-positive risk: Low. Semgrep reports the concrete unsafe sink.
- Acceptance: the vulnerable fixture passes a tool argument to `eval`; the
  clean fixture uses `ast.literal_eval`.

Remediation: use explicit parsers and fixed command allowlists.
