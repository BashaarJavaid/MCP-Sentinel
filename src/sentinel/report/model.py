"""Native versioned scan-report contract."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import Field, field_serializer, field_validator, model_validator

from sentinel.finding import (
    ContractModel,
    Finding,
    FindingStatus,
    NonEmptyString,
    Severity,
    ensure_utc,
    format_utc,
)


class StageName(str, Enum):
    STATIC = "static"
    GPT_STATIC = "gpt_static"
    DYNAMIC = "dynamic"
    GPT_DYNAMIC = "gpt_dynamic"
    MERGE = "merge"
    REPORTING = "reporting"


class StageStatus(str, Enum):
    PENDING = "pending"
    SKIPPED = "skipped"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class StageRecord(ContractModel):
    name: StageName
    status: StageStatus
    reason: str | None = None


class ReportWarning(ContractModel):
    code: NonEmptyString
    message: NonEmptyString


class ScanTarget(ContractModel):
    display_name: NonEmptyString
    root: Literal["."] = "."


def empty_severity_counts() -> dict[Severity, int]:
    return {item: 0 for item in Severity}


def empty_status_counts() -> dict[FindingStatus, int]:
    return {item: 0 for item in FindingStatus}


class ScanSummary(ContractModel):
    total: int = Field(ge=0)
    by_severity: dict[Severity, int]
    by_status: dict[FindingStatus, int]

    @model_validator(mode="after")
    def validate_counts(self) -> ScanSummary:
        if set(self.by_severity) != set(Severity):
            raise ValueError("severity summary must contain every severity")
        if set(self.by_status) != set(FindingStatus):
            raise ValueError("status summary must contain every status")
        if any(value < 0 for value in self.by_severity.values()):
            raise ValueError("severity counts cannot be negative")
        if any(value < 0 for value in self.by_status.values()):
            raise ValueError("status counts cannot be negative")
        if sum(self.by_severity.values()) != self.total:
            raise ValueError("severity counts must sum to total")
        if sum(self.by_status.values()) != self.total:
            raise ValueError("status counts must sum to total")
        return self


class ScanContext(ContractModel):
    scan_id: UUID
    started_at: datetime
    target: ScanTarget

    @field_validator("scan_id")
    @classmethod
    def validate_uuid4(cls, value: UUID) -> UUID:
        if value.version != 4:
            raise ValueError("scan_id must be UUIDv4")
        return value

    @field_validator("started_at")
    @classmethod
    def validate_started_at(cls, value: datetime) -> datetime:
        return ensure_utc(value)


class ScanReport(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    scan_id: UUID
    sentinel_version: NonEmptyString
    started_at: datetime
    completed_at: datetime
    target: ScanTarget
    analysis_complete: bool = Field(serialization_alias="analysisComplete")
    execution_successful: bool = Field(serialization_alias="executionSuccessful")
    stages: tuple[StageRecord, ...]
    summary: ScanSummary
    warnings: tuple[ReportWarning, ...]
    findings: tuple[Finding, ...]

    @field_validator("scan_id")
    @classmethod
    def validate_uuid4(cls, value: UUID) -> UUID:
        if value.version != 4:
            raise ValueError("scan_id must be UUIDv4")
        return value

    @field_validator("started_at", "completed_at")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        return ensure_utc(value)

    @field_serializer("started_at", "completed_at", when_used="json")
    def serialize_timestamp(self, value: datetime) -> str:
        return format_utc(value)

    @model_validator(mode="after")
    def validate_report(self) -> ScanReport:
        if self.completed_at < self.started_at:
            raise ValueError("completed_at cannot precede started_at")
        if {stage.name for stage in self.stages} != set(StageName):
            raise ValueError("report must contain every pipeline stage exactly once")
        if len(self.stages) != len(StageName):
            raise ValueError("report contains duplicate pipeline stages")
        if any(finding.scan_id != self.scan_id for finding in self.findings):
            raise ValueError("every finding must belong to this scan")
        if self.summary.total != len(self.findings):
            raise ValueError("summary total must equal finding count")
        return self


def summarize(findings: tuple[Finding, ...]) -> ScanSummary:
    severities = empty_severity_counts()
    statuses = empty_status_counts()
    for finding in findings:
        severities[finding.severity] += 1
        statuses[finding.status] += 1
    return ScanSummary(total=len(findings), by_severity=severities, by_status=statuses)
