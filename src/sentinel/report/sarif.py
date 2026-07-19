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
    Location,
    Message,
    MultiformatMessageString,
    Notification,
    PhysicalLocation,
    Region,
    ReportingConfiguration,
    ReportingDescriptor,
    Result,
    Run,
    SarifLog,
    Suppression,
    Tool,
    ToolComponent,
)

from sentinel.dynamic.catalog import RULE_BY_ID as DYNAMIC_RULE_BY_ID
from sentinel.finding import (
    FileLocation,
    Finding,
    FindingStatus,
    Severity,
    StaticEvidence,
)
from sentinel.report.model import ScanReport
from sentinel.static.catalog import RULE_BY_ID as STATIC_RULE_BY_ID

SARIF_SCHEMA_URI = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/"
    "schemas/sarif-schema-2.1.0.json"
)


def render_sarif(report: ScanReport) -> str:
    notifications = []
    if not report.analysis_complete:
        notifications.append(
            Notification(
                level="error",
                message=Message(
                    text="Sentinel analysis is incomplete; inspect stages."
                ),
                time_utc=_format_datetime(report.completed_at),
                properties={"code": "analysis_incomplete"},
            )
        )
    if report.gpt_review is not None and report.gpt_review.mode == "replay":
        notifications.append(
            Notification(
                level="note",
                message=Message(
                    text="GPT review used a recorded replay; no live model call ran."
                ),
                time_utc=_format_datetime(report.completed_at),
                properties={"code": "gpt_recorded_replay"},
            )
        )
    invocation = Invocation(
        execution_successful=report.execution_successful,
        exit_code=0 if report.analysis_complete else 3,
        exit_code_description=(
            "Analysis completed" if report.analysis_complete else "Analysis incomplete"
        ),
        start_time_utc=_format_datetime(report.started_at),
        end_time_utc=_format_datetime(report.completed_at),
        tool_execution_notifications=notifications or None,
        properties={
            "analysisComplete": report.analysis_complete,
            "schemaVersion": report.schema_version,
            "findingCount": report.summary.total,
            "staticAnalysis": _model_data(report.static_analysis),
            "gptReview": _model_data(report.gpt_review),
        },
    )
    selected_static = (
        report.static_analysis.selected_rule_ids if report.static_analysis else ()
    )
    reported_rule_ids = tuple(
        dict.fromkeys(
            (*selected_static, *(finding.rule_id for finding in report.findings))
        )
    )
    driver = ToolComponent(
        name="MCP Sentinel",
        full_name="MCP Sentinel build-time MCP security scanner",
        information_uri="https://github.com/BashaarJavaid/MCP-Sentinel",
        semantic_version=report.sentinel_version,
        version=report.sentinel_version,
        rules=[_rule_descriptor(rule_id) for rule_id in reported_rule_ids],
        properties={
            "reportSchemaVersion": report.schema_version,
            "gptReview": _model_data(report.gpt_review),
        },
    )
    run = Run(
        tool=Tool(driver=driver),
        invocations=[invocation],
        original_uri_base_ids={"SRCROOT": ArtifactLocation(uri="./")},
        results=[_result(finding, reported_rule_ids) for finding in report.findings],
        properties={
            "analysisComplete": report.analysis_complete,
            "executionSuccessful": report.execution_successful,
        },
    )
    log = SarifLog(version="2.1.0", schema_uri=SARIF_SCHEMA_URI, runs=[run])
    payload = _serialize_sarif_om(log)
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _rule_descriptor(rule_id: str) -> ReportingDescriptor:
    if rule_id in STATIC_RULE_BY_ID:
        definition = STATIC_RULE_BY_ID[rule_id]
        title = definition.title
        description = definition.description
        impact = definition.impact
        owasp_category = definition.owasp_category
        false_positive_risk = definition.false_positive_risk
        engine = definition.engine.value
        help_uri = definition.help_uri
        help_text = f"{definition.remediation} FP risk: {false_positive_risk}"
    else:
        dynamic_definition = DYNAMIC_RULE_BY_ID[rule_id]
        title = dynamic_definition.title
        description = dynamic_definition.description
        impact = dynamic_definition.impact
        owasp_category = dynamic_definition.owasp_category
        false_positive_risk = "Runtime-confirmed probe observation."
        engine = "dynamic"
        help_uri = (
            "https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/"
            f"docs/rules.md#{rule_id.lower()}"
        )
        help_text = dynamic_definition.remediation
    return ReportingDescriptor(
        id=rule_id,
        name=title,
        short_description=MultiformatMessageString(text=title),
        full_description=MultiformatMessageString(text=description),
        help=MultiformatMessageString(text=help_text),
        help_uri=help_uri,
        default_configuration=ReportingConfiguration(
            level=_sarif_level(Severity(impact.value))
        ),
        properties={
            "impact": impact.value,
            "owaspCategory": owasp_category.model_dump(mode="json"),
            "falsePositiveRisk": false_positive_risk,
            "engine": engine,
        },
    )


def _result(finding: Finding, selected: tuple[str, ...]) -> Result:
    location = _location(finding)
    suppressions = None
    if finding.status is FindingStatus.SUPPRESSED:
        suppressions = [
            Suppression(
                kind="external",
                state="accepted",
                justification=finding.review.reason or "Suppressed by Sentinel review",
            )
        ]
    return Result(
        rule_id=finding.rule_id,
        rule_index=selected.index(finding.rule_id),
        level=_sarif_level(finding.severity),
        message=Message(text=f"{finding.title}: {finding.description}"),
        locations=[location],
        fingerprints={"sentinel/v1": finding.dedup_key},
        suppressions=suppressions,
        properties={
            "findingId": str(finding.finding_id),
            "dedupKey": finding.dedup_key,
            "impact": finding.impact.value,
            "severity": finding.severity.value,
            "exploitability": finding.exploitability.value,
            "confidence": finding.confidence.value,
            "status": finding.status.value,
            "source": finding.source.value,
            "owaspId": finding.owasp_category.id,
            "owaspName": finding.owasp_category.name,
            "evidence": finding.evidence.model_dump(mode="json"),
            "provenance": [item.model_dump(mode="json") for item in finding.provenance],
            "review": finding.review.model_dump(mode="json"),
            "remediation": finding.remediation,
        },
    )


def _location(finding: Finding) -> Location:
    if not isinstance(finding.location, FileLocation):
        return Location(
            message=Message(text=f"Runtime location: {finding.location.path}"),
            physical_location=PhysicalLocation(
                artifact_location=ArtifactLocation(
                    uri="sentinel.target.yaml",
                    uri_base_id="SRCROOT",
                ),
                region=Region(start_line=1),
            ),
        )
    if not isinstance(finding.evidence, StaticEvidence):
        raise TypeError("file findings require static evidence")
    source_range = finding.location.range
    return Location(
        physical_location=PhysicalLocation(
            artifact_location=ArtifactLocation(
                uri=finding.location.path,
                uri_base_id="SRCROOT",
            ),
            region=Region(
                start_line=source_range.start_line,
                start_column=source_range.start_column,
                end_line=source_range.end_line,
                end_column=source_range.end_column,
                snippet=MultiformatMessageString(text=finding.evidence.snippet),
            ),
        )
    )


def _sarif_level(severity: Severity) -> str:
    if severity in {Severity.CRITICAL, Severity.HIGH}:
        return "error"
    if severity is Severity.MEDIUM:
        return "warning"
    return "note"


def _model_data(value: Any) -> Any:
    return value.model_dump(mode="json") if value is not None else None


def _serialize_sarif_om(value: Any) -> Any:
    if attrs.has(type(value)):
        output: dict[str, Any] = {}
        for attribute in attrs.fields(type(value)):
            item = getattr(value, attribute.name)
            if item is None:
                continue
            name = attribute.metadata.get("schema_property_name", attribute.name)
            if isinstance(value, Suppression) and name == "state":
                # sarif-om 1.0.4 uses the pre-standard property name.
                name = "status"
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
