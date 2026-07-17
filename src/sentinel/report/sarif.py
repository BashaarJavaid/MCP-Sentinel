"""SARIF 2.1.0 renderer backed by sarif-om objects."""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

import attrs
from sarif_om import (
    ArtifactLocation,
    Invocation,
    Message,
    Notification,
    Run,
    SarifLog,
    Tool,
    ToolComponent,
)

from sentinel.report.model import ScanReport

SARIF_SCHEMA_URI = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/"
    "schemas/sarif-schema-2.1.0.json"
)


def render_sarif(report: ScanReport) -> str:
    notification = Notification(
        level="error",
        message=Message(
            text="Sentinel Phase 0 report is incomplete because detector stages "
            "are not implemented."
        ),
        time_utc=_format_datetime(report.completed_at),
        properties={"code": "analysis_incomplete"},
    )
    invocation = Invocation(
        execution_successful=False,
        exit_code=3,
        exit_code_description="Analysis incomplete in Phase 0 scaffold",
        start_time_utc=_format_datetime(report.started_at),
        end_time_utc=_format_datetime(report.completed_at),
        tool_execution_notifications=[notification],
        properties={
            "analysisComplete": False,
            "schemaVersion": report.schema_version,
            "findingCount": report.summary.total,
        },
    )
    driver = ToolComponent(
        name="MCP Sentinel",
        full_name="MCP Sentinel build-time MCP security scanner",
        information_uri="https://github.com/BashaarJavaid/MCP-Sentinel",
        semantic_version=report.sentinel_version,
        version=report.sentinel_version,
        rules=[],
    )
    run = Run(
        tool=Tool(driver=driver),
        invocations=[invocation],
        original_uri_base_ids={"SRCROOT": ArtifactLocation(uri="./")},
        results=[],
        properties={
            "analysisComplete": False,
            "executionSuccessful": False,
        },
    )
    log = SarifLog(version="2.1.0", schema_uri=SARIF_SCHEMA_URI, runs=[run])
    payload = _serialize_sarif_om(log)
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _serialize_sarif_om(value: Any) -> Any:
    if attrs.has(type(value)):
        output: dict[str, Any] = {}
        for attribute in attrs.fields(type(value)):
            item = getattr(value, attribute.name)
            if item is None:
                continue
            name = attribute.metadata.get("schema_property_name", attribute.name)
            output[name] = _serialize_sarif_om(item)
        return output
    if isinstance(value, dict):
        return {key: _serialize_sarif_om(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_sarif_om(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return _format_datetime(value)
    return value


def _format_datetime(value: datetime) -> str:
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")
