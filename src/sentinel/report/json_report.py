"""Native JSON report renderer."""

from __future__ import annotations

import json

from sentinel.report.model import ScanReport


def render_json(report: ScanReport) -> str:
    payload = report.model_dump(mode="json", by_alias=True)
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
