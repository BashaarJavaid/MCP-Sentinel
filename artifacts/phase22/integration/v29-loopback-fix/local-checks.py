"""Summarize completed local checks at their actual recorded source."""
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path("artifacts/phase22/integration")
OUT = BASE / "v29-loopback-fix"
labels = ["full-suite", "ruff", "format", "mypy", "lock-corrected", "schema", "notices", "artifacts", "production-capture"]
checks = []
for label in labels:
    path = BASE / ("v29-" + label + ".json")
    metadata = json.loads(path.read_text())
    assert metadata["exit_code"] == 0
    checks.append({"label": "v29-" + label, "command": metadata["command"], "source": metadata["source_commit"], "exit_code": metadata["exit_code"], "evidence_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
counts = Counter("skipped" if c.find("skipped") is not None else "failed" if c.find("failure") is not None or c.find("error") is not None else "passed" for c in ET.parse(BASE / "v29-full-suite-junit.xml").iter("testcase"))
assert counts == {"passed": 2242, "skipped": 36}
coverage = json.loads((BASE / "v29-full-suite-coverage.json").read_text())["totals"]["percent_covered"]
path = OUT / "local-checks.json"
assert not path.exists()
path.write_text(json.dumps({"scanner": "f85a90f9ba2d1c43019e8505b977d57f3476a9c9", "checks": checks, "full_suite": dict(counts, branch_coverage_percent=coverage), "source_binding": "local-source-binding.json", "new_paid_calls": 0}, indent=2) + "\n")
print(dict(counts), coverage)
