# Security policy

## Report a vulnerability privately

Use GitHub's [Report a vulnerability form](https://github.com/BashaarJavaid/MCP-Sentinel/security/advisories/new)
to contact the maintainers privately. Sign in to GitHub, open this repository's
**Security → Advisories**, then choose **Report a vulnerability**. Avoid public
issues for unpatched vulnerabilities or reports containing sensitive details.

Include the affected Sentinel version or commit, operating system and Python
version, scan mode and configuration, and minimal reproduction steps. Describe
the expected and observed behavior, likely impact, and relevant rule IDs. Attach
sanitized logs or JSON/SARIF evidence and a minimal local target when useful;
remove credentials, personal data, and private source you cannot share.

Please coordinate disclosure with the maintainers in the private advisory so a
fix and release guidance can be prepared. Discuss publication timing and credit
there; this project does not promise response or remediation deadlines. For
vulnerabilities in a scanned third-party server, use that project's security
policy. Ordinary bugs and feature requests belong in public issues.

## Dependency audit exceptions

`pip-audit` is a blocking CI gate with no active advisory exceptions. Do not
add wildcard advisory or package exceptions; resolve or explicitly review every
reported vulnerability before release.
