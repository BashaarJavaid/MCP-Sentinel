"""Native JSON report renderer."""

from __future__ import annotations

import json
from typing import Any

from sentinel.report.model import ScanReport


def render_json(report: ScanReport) -> str:
    payload = report.model_dump(mode="json", by_alias=True)
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def report_model_input(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload["analysis_complete"] = payload.pop("analysisComplete", None)
    payload["execution_successful"] = payload.pop("executionSuccessful", None)
    raw_findings = payload.get("findings")
    if isinstance(raw_findings, list):
        findings = []
        for raw in raw_findings:
            if isinstance(raw, dict):
                finding = dict(raw)
                finding.pop("severity", None)
                finding.pop("review_disagrees", None)
                findings.append(finding)
            else:
                findings.append(raw)
        payload["findings"] = findings
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
