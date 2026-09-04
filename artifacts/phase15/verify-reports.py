"""One-time launch evidence check; run with the installed Sentinel interpreter."""

import json
from pathlib import Path

from sentinel.report.validate_json import validate_report_data
from sentinel.report.validate_sarif import validate_sarif_data

root = Path(__file__).parent
walkthrough = json.loads((root / "walkthrough.json").read_text())
replay = json.loads((root / "replay/report.json").read_text())
for report, sarif_path in (
    (walkthrough, root / "walkthrough.sarif"),
    (replay, root / "replay/report.sarif"),
):
    validate_report_data(report)
    sarif = json.loads(sarif_path.read_text())
    validate_sarif_data(sarif)
    assert report["analysisComplete"] and report["executionSuccessful"]
    assert report["sentinel_version"] == "1.2.1"
    assert {f["rule_id"] for f in report["findings"]} == {
        f["ruleId"] for f in sarif["runs"][0]["results"]
    }
    assert report["gpt_review"]["current_cost_micro_usd"] == 0
assert walkthrough["findings"] == []
assert walkthrough["gpt_review"]["batches"] == []
assert walkthrough["static_analysis"]["scanned_file_count"] == 5
outcomes = walkthrough["static_analysis"]["rule_outcomes"]
assert [r["rule_id"] for r in outcomes] == [f"SENT-{n:03d}" for n in range(1, 8)]
assert outcomes[0]["skip_reason"] == "sentinel.permissions.yaml is absent"
assert all(r["status"] == "evaluated" for r in outcomes[1:])
assert {f["rule_id"] for f in replay["findings"]} == {
    f"SENT-{n:03d}" for n in range(1, 12)
}
assert replay["gpt_review"]["mode"] == "replay"
assert replay["gpt_review"]["current_usage"]["total_tokens"] == 0
assert all(s["status"] == "succeeded" for s in replay["stages"])
assert "PortunusMCP Sentinel 1.2.1" in (root / "replay-console.txt").read_text()
print("Both schemas, walkthrough coverage, installed branding, and Docker replay pass.")
