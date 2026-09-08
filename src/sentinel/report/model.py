"""Native versioned scan-report contract."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import (
    Field,
    JsonValue,
    field_serializer,
    field_validator,
    model_validator,
)

from sentinel.config import EndpointMode, ReasoningEffort
from sentinel.finding import (
    ContractModel,
    Finding,
    FindingStatus,
    NonEmptyString,
    Severity,
    Sha256Hex,
    TokenUsage,
    ensure_utc,
    format_utc,
    runtime_evidence,
)
from sentinel.report.coverage import (
    DynamicCoverage,
    StageReviewActivity,
    StaticCoverage,
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
    coverage: StaticCoverage | None = None
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
        if self.coverage is not None and self.coverage.workspace is not None:
            file_count = sum(
                (member.python_file_count or 0) + (member.typescript_file_count or 0)
                for member in self.coverage.workspace.members
            )
            if file_count > self.scanned_file_count:
                raise ValueError("workspace file counts exceed scanned files")
        return self


ProbeId = Literal["SENT-008", "SENT-009", "SENT-010", "SENT-011"]
PROBE_IDS: tuple[ProbeId, ...] = ("SENT-008", "SENT-009", "SENT-010", "SENT-011")


class DynamicProbeOutcome(ContractModel):
    attempt_id: NonEmptyString
    legacy_attempt: bool = False
    probe_id: ProbeId
    mutation: str | None = None
    eligible: bool | None = None
    started: bool | None = None
    status: Literal["tested", "unsupported", "untested", "inconclusive"]
    verdict: Literal["violation_observed", "no_violation_observed"] | None
    tool: str | None
    field: str | None
    argument_path: tuple[str, ...] = ()
    reason: NonEmptyString
    baseline_attempted: bool | None = None
    attack_attempted: bool | None = None
    baseline: dict[str, JsonValue] = Field(default_factory=dict)
    attack: dict[str, JsonValue] = Field(default_factory=dict)
    schema_checks: tuple[dict[str, JsonValue], ...] = ()
    effects: dict[str, JsonValue] = Field(default_factory=dict)
    timings: dict[str, float] = Field(default_factory=dict)
    execution_successful: bool = True

    @model_validator(mode="after")
    def validate_verdict(self) -> DynamicProbeOutcome:
        if self.legacy_attempt and (
            self.mutation is not None
            or self.eligible is not None
            or self.started is not None
        ):
            raise ValueError("legacy attempts cannot invent mutation or eligibility")
        if (self.status == "tested") != (self.verdict is not None):
            raise ValueError("only tested probes require a verdict")
        if self.started is False and (
            self.baseline_attempted or self.attack_attempted or self.status == "tested"
        ):
            raise ValueError("unstarted attempts cannot contain executed probes")
        if self.started is True and self.eligible is not True:
            raise ValueError("started attempts must be eligible")
        return self


class DynamicAnalysisSummary(ContractModel):
    coverage: DynamicCoverage | None = None
    probe_outcomes: tuple[DynamicProbeOutcome, ...] = ()

    @model_validator(mode="after")
    def validate_probes(self) -> DynamicAnalysisSummary:
        ids = [item.attempt_id for item in self.probe_outcomes]
        if len(ids) != len(set(ids)):
            raise ValueError("dynamic analysis requires unique attempt IDs")
        if self.coverage is not None and self.coverage.campaign is not None:
            campaign = self.coverage.campaign
            if any(item.legacy_attempt for item in self.probe_outcomes):
                raise ValueError("legacy attempts cannot establish campaign coverage")
            if any(
                item.started is None or item.eligible is None or item.mutation is None
                for item in self.probe_outcomes
            ):
                raise ValueError(
                    "campaign attempts require explicit execution and eligibility"
                )
            if campaign.planned_attempts != len(self.probe_outcomes):
                raise ValueError("every planned attempt requires an outcome")
            if campaign.eligible_attempts != sum(
                item.eligible is True for item in self.probe_outcomes
            ):
                raise ValueError("campaign eligibility must match outcomes")
            if campaign.tested_attempts != sum(
                item.status == "tested" for item in self.probe_outcomes
            ):
                raise ValueError("campaign tested count must match outcomes")
            if campaign.started_attempts != sum(
                item.started is True for item in self.probe_outcomes
            ):
                raise ValueError("campaign started count must match outcomes")
            bindings = self.coverage.planned_bindings
            if [item.attempt_id for item in bindings] != ids:
                raise ValueError("planned bindings must match ordered attempt IDs")
            for binding, outcome in zip(bindings, self.probe_outcomes, strict=True):
                if (
                    binding.probe_id,
                    binding.tool,
                    binding.field,
                    binding.argument_path,
                    binding.mutation,
                ) != (
                    outcome.probe_id,
                    outcome.tool,
                    outcome.field,
                    outcome.argument_path,
                    outcome.mutation,
                ):
                    raise ValueError("binding identity must match its outcome")
        if self.coverage is not None:
            by_id = {item.attempt_id: item for item in self.probe_outcomes}
            for snapshot in self.coverage.discovery:
                if snapshot.role == "discovery":
                    if snapshot.attempt_id is not None:
                        raise ValueError(
                            "campaign discovery does not belong to an attempt"
                        )
                elif snapshot.attempt_id is not None:
                    matched = by_id.get(snapshot.attempt_id)
                    if matched is None or matched.probe_id != snapshot.probe_id:
                        raise ValueError(
                            "discovery must reference its matching attempt"
                        )
                elif self.coverage.campaign is not None:
                    raise ValueError("attempt discovery requires an attempt ID")
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


class BaselineSummary(ContractModel):
    matcher_version: Literal["sentinel-baseline-v1", "sentinel-baseline-v2"] = (
        "sentinel-baseline-v2"
    )
    source_schema_version: Literal["1.3.0", "1.4.0", "1.5.0", "1.6.0", "1.7.0"]
    source_sha256: Sha256Hex
    baseline_finding_count: int = Field(ge=0)
    matched_finding_count: int = Field(ge=0)
    new_finding_count: int = Field(ge=0)
    resolved_finding_count: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_counts(self) -> BaselineSummary:
        if self.resolved_finding_count > self.baseline_finding_count:
            raise ValueError("resolved baseline count exceeds baseline finding count")
        if (
            self.matched_finding_count
            and self.resolved_finding_count == self.baseline_finding_count
        ):
            raise ValueError("matched findings require an unresolved baseline identity")
        return self


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
    endpoint_mode: EndpointMode
    endpoint_url_hash: Sha256Hex
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
    disagreement_count: int | None = Field(default=0, ge=0)
    requested_model: NonEmptyString
    reasoning_effort: ReasoningEffort
    endpoint_mode: EndpointMode
    endpoint_url_hash: Sha256Hex
    mode: Literal["live", "replay", "cached", "degraded", "mixed", "not_run"]
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
    schema_version: Literal["1.7.0"] = "1.7.0"
    review_activity: StageReviewActivity = Field(default_factory=StageReviewActivity)
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
    dynamic_analysis: DynamicAnalysisSummary | None = None
    gpt_review: GptReviewSummary | None
    baseline: BaselineSummary | None = None

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
        if self.dynamic_analysis is not None:
            outcomes = self.dynamic_analysis.probe_outcomes
            coverage = self.dynamic_analysis.coverage
            if (
                self.analysis_complete
                and not outcomes
                and (coverage is None or coverage.campaign is None)
            ):
                raise ValueError("unknown discovery cannot establish complete analysis")
            if coverage is not None and coverage.campaign is not None:
                by_id = {item.attempt_id: item for item in outcomes}
                for finding in self.findings:
                    for evidence in runtime_evidence(finding):
                        outcome = by_id.get(evidence.attempt_id or "")
                        proof = evidence.proof
                        if (
                            outcome is None
                            or proof is None
                            or outcome.verdict != "violation_observed"
                            or (
                                evidence.probe_id,
                                evidence.mutation,
                                proof.tool,
                                proof.field,
                                proof.argument_path,
                            )
                            != (
                                outcome.probe_id,
                                outcome.mutation,
                                outcome.tool,
                                outcome.field,
                                outcome.argument_path,
                            )
                        ):
                            raise ValueError(
                                "runtime proof must reference its observed attempt"
                            )
            if (
                self.analysis_complete
                and coverage is not None
                and coverage.campaign is not None
                and (
                    not coverage.campaign.enumeration_complete
                    or coverage.campaign.remaining_eligible_attempts
                )
            ):
                raise ValueError(
                    "incomplete campaign coverage cannot establish complete analysis"
                )
            if self.analysis_complete and any(
                item.status != "tested" for item in outcomes
            ):
                raise ValueError("incomplete probes cannot establish complete analysis")
            if self.execution_successful and any(
                not item.execution_successful for item in outcomes
            ):
                raise ValueError("probe infrastructure failure must fail execution")
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
        matched = sum(item.baseline_matched is True for item in self.findings)
        new = sum(item.baseline_matched is False for item in self.findings)
        if self.baseline is None:
            if any(item.baseline_matched is not None for item in self.findings):
                raise ValueError(
                    "findings cannot have baseline state without a baseline"
                )
        elif (
            matched != self.baseline.matched_finding_count
            or new != self.baseline.new_finding_count
        ):
            raise ValueError("baseline summary does not match finding annotations")
        if self.baseline is not None and matched + new != len(self.findings):
            raise ValueError(
                "every finding requires baseline state when a baseline is used"
            )
        return self


def summarize(findings: tuple[Finding, ...]) -> ScanSummary:
    severities = empty_severity_counts()
    statuses = empty_status_counts()
    for finding in findings:
        severities[finding.severity] += 1
        statuses[finding.status] += 1
    return ScanSummary(total=len(findings), by_severity=severities, by_status=statuses)
