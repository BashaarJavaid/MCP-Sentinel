"""Native versioned scan-report contract."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import Field, field_serializer, field_validator, model_validator

from sentinel.config import ReasoningEffort
from sentinel.finding import (
    ContractModel,
    Finding,
    FindingStatus,
    NonEmptyString,
    Severity,
    TokenUsage,
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


class StaticRuleStatus(str, Enum):
    EVALUATED = "evaluated"
    SKIPPED = "skipped"


class StaticRuleOutcome(ContractModel):
    rule_id: NonEmptyString
    status: StaticRuleStatus
    match_count: int = Field(ge=0)
    exemptions_by_reason: dict[str, int]
    skip_reason: str | None = None

    @model_validator(mode="after")
    def validate_outcome(self) -> StaticRuleOutcome:
        if any(value < 0 for value in self.exemptions_by_reason.values()):
            raise ValueError("static exemption counts cannot be negative")
        if self.status is StaticRuleStatus.SKIPPED and not self.skip_reason:
            raise ValueError("skipped static rules require a reason")
        if self.status is StaticRuleStatus.EVALUATED and self.skip_reason is not None:
            raise ValueError("evaluated static rules cannot have a skip reason")
        return self


class StaticAnalysisSummary(ContractModel):
    selected_rule_ids: tuple[NonEmptyString, ...]
    scanned_file_count: int = Field(ge=0)
    ignored_file_count: int = Field(ge=0)
    total_matches: int = Field(ge=0)
    duration_ms: int = Field(ge=0)
    rule_outcomes: tuple[StaticRuleOutcome, ...]

    @model_validator(mode="after")
    def validate_static_summary(self) -> StaticAnalysisSummary:
        if tuple(item.rule_id for item in self.rule_outcomes) != self.selected_rule_ids:
            raise ValueError("static rule outcomes must match selected rule order")
        if sum(item.match_count for item in self.rule_outcomes) != self.total_matches:
            raise ValueError("static rule matches must sum to total_matches")
        return self


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


class GptPricing(ContractModel):
    model: NonEmptyString
    source: NonEmptyString
    as_of: NonEmptyString
    input_micro_usd_per_million: int = Field(ge=0)
    cached_input_micro_usd_per_million: int = Field(ge=0)
    output_micro_usd_per_million: int = Field(ge=0)
    cache_write_multiplier_millionths: int = Field(ge=0)


class GptBatchRecord(ContractModel):
    batch_id: NonEmptyString
    request_fingerprint: NonEmptyString
    mode: Literal["live", "replay", "cached", "degraded"]
    requested_model: NonEmptyString
    returned_model: str | None
    reasoning_effort: ReasoningEffort
    finding_count: int = Field(ge=0)
    retry_count: int = Field(ge=0)
    status: Literal["accepted", "failed", "skipped"]
    failure: str | None = None
    refusal_count: int = Field(default=0, ge=0)
    incomplete_count: int = Field(default=0, ge=0)
    schema_valid: bool
    current_usage: TokenUsage
    origin_usage: TokenUsage
    current_latency_ms: int = Field(ge=0)
    origin_latency_ms: int = Field(ge=0)
    current_cost_micro_usd: int | None = Field(default=None, ge=0)
    origin_cost_micro_usd: int | None = Field(default=None, ge=0)
    confirmed_count: int = Field(default=0, ge=0)
    suppressed_count: int = Field(default=0, ge=0)
    needs_review_count: int = Field(default=0, ge=0)


class GptReviewSummary(ContractModel):
    requested_model: NonEmptyString
    reasoning_effort: ReasoningEffort
    mode: Literal["live", "replay", "cached", "degraded", "mixed"]
    candidate_count: int = Field(ge=0)
    selected_count: int = Field(ge=0)
    overflow_count: int = Field(ge=0)
    reviewed_count: int = Field(ge=0)
    confirmed_count: int = Field(ge=0)
    suppressed_count: int = Field(ge=0)
    needs_review_count: int = Field(ge=0)
    failure_count: int = Field(ge=0)
    cache_hits: int = Field(ge=0)
    cache_misses: int = Field(ge=0)
    cache_writes: int = Field(ge=0)
    cache_errors: int = Field(ge=0)
    current_usage: TokenUsage
    origin_usage: TokenUsage
    current_latency_ms: int = Field(ge=0)
    origin_latency_ms: int = Field(ge=0)
    current_cost_micro_usd: int | None = Field(default=None, ge=0)
    origin_cost_micro_usd: int | None = Field(default=None, ge=0)
    pricing: GptPricing | None
    batches: tuple[GptBatchRecord, ...]


class ScanReport(ContractModel):
    schema_version: Literal["1.2.0"] = "1.2.0"
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
    static_analysis: StaticAnalysisSummary | None
    gpt_review: GptReviewSummary | None

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
