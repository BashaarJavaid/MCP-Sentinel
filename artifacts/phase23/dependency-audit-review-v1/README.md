# Dependency audit: exact payload and destination review

Approve the existing local dependency gate querying **PyPI** for the pinned package
names and versions in [requests.json](requests.json). There are 84 locked
requirement records, 82 active in this environment;
applicable entries are requested, and cached responses may avoid individual GETs.
Each request uses `https://pypi.org/pypi/<package>/<version>/json`.

The complete exported [requirements.txt](requirements.txt) comes from the unchanged
lockfile, using the same no-dev/no-project export as `make audit`. Package names
and versions appear in GET URLs with ordinary HTTP client/network metadata.
Repository source, credentials, reports and advisory-target code are not uploaded.
No paid model call, target execution, dependency update or publication is included.

Exact [proposal.json](proposal.json) SHA-256:
`0cef9afd8f53d7a9d6aaada8c006b8de3142fe9337e622537deff860b4f1c5ab`

```bash
.venv/bin/pip-audit --vulnerability-service pypi --cache-dir /private/tmp/mcp-sentinel-phase23-pip-audit-cache --no-deps --disable-pip --format json --output artifacts/phase23/callback-engineering-v1/dependency-audit.json -r artifacts/phase23/dependency-audit-review-v1/requirements.txt
```

This is the existing audit with its PyPI destination made explicit, a temporary
cache, and retained JSON output. Automatic approval review rejected the generic
`make audit notices-check docs-check` escalation: it required explicit approval
of the dependency/version payload and external service. The rejected command did
not run. Notices and documentation are being completed separately offline.

All 2,697 tests have passing results across the original full attempt and four
loopback-only reruns, with 36 skips. The original restricted attempt remains failed;
no single uninterrupted full-suite pass is claimed. The dependency gate is still
pending. Candidate advisory execution remains separately unapproved.
