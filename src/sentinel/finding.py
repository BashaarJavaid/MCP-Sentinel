"""Canonical immutable Finding contract shared by every Sentinel stage."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    StringConstraints,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Sha256Hex = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
OwaspId = Annotated[str, StringConstraints(pattern=r"^ASI(?:0[1-9]|10):2026$")]


class ContractModel(BaseModel):
    """Strict immutable base for serialized Sentinel contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class Impact(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"


class Severity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"


class Exploitability(str, Enum):
    CONFIRMED = "confirmed"
    LIKELY = "likely"
    THEORETICAL = "theoretical"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FindingStatus(str, Enum):
    NEEDS_REVIEW = "needs_review"
    CONFIRMED = "confirmed"
    LIKELY_FALSE_POSITIVE = "likely_false_positive"
    SUPPRESSED = "suppressed"


class FindingSource(str, Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"


class ReviewStatus(str, Enum):
    CONFIRMED = "confirmed"
    SUPPRESSED = "suppressed"
    NEEDS_REVIEW = "needs_review"


class OwaspCategory(ContractModel):
    id: OwaspId
    name: NonEmptyString


class SourceRange(ContractModel):
    """SARIF-compatible 1-based range with an exclusive end column."""

    start_line: int = Field(ge=1)
    start_column: int = Field(ge=1)
    end_line: int = Field(ge=1)
    end_column: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_order(self) -> SourceRange:
        start = (self.start_line, self.start_column)
        end = (self.end_line, self.end_column)
        if end <= start:
            raise ValueError("end position must be after start position")
        return self


class FileLocation(ContractModel):
    kind: Literal["file"] = "file"
    path: NonEmptyString
    range: SourceRange

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repo_path(value)


class LogicalLocation(ContractModel):
    kind: Literal["logical"] = "logical"
    path: NonEmptyString

    @field_validator("path")
    @classmethod
    def validate_json_pointer(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("logical locations must be JSON Pointers")
        for token in value.split("/")[1:]:
            index = 0
            while index < len(token):
                if token[index] == "~" and (
                    index + 1 >= len(token) or token[index + 1] not in {"0", "1"}
                ):
                    raise ValueError("invalid JSON Pointer escape")
                index += 2 if token[index] == "~" else 1
        return value


FindingLocation = Annotated[FileLocation | LogicalLocation, Field(discriminator="kind")]


class StaticEvidence(ContractModel):
    kind: Literal["static"] = "static"
    snippet: str
    range: SourceRange
    fingerprint: Sha256Hex | None = None


class DynamicEvidence(ContractModel):
    kind: Literal["dynamic"] = "dynamic"
    probe_id: NonEmptyString
    request: dict[str, JsonValue]
    response: dict[str, JsonValue]
    logs: tuple[str, ...] = ()


FindingEvidence = Annotated[
    StaticEvidence | DynamicEvidence, Field(discriminator="kind")
]


class EvidenceReference(ContractModel):
    path: NonEmptyString
    range: SourceRange
    claim: NonEmptyString

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repo_path(value)


class ProbePlan(ContractModel):
    ordered_probe_ids: tuple[NonEmptyString, ...]
    target_tool: NonEmptyString
    argument_bindings: dict[str, dict[str, JsonValue]]


class TokenUsage(ContractModel):
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    reasoning_tokens: int | None = Field(default=None, ge=0)
    cached_tokens: int | None = Field(default=None, ge=0)
    cache_write_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)


class ReviewBase(ContractModel):
    reviewed: bool
    status: ReviewStatus | None = None
    requested_model: str | None = None
    returned_model: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    reasoning: str | None = None
    evidence_refs: tuple[EvidenceReference, ...] | None = None
    probe_plan: ProbePlan | None = None
    suggested_severity_override: Severity | None = None
    usage: TokenUsage | None = None
    latency_ms: int | None = Field(default=None, ge=0)
    reviewed_at: datetime | None = None
    reason: str | None = None

    @field_validator("reviewed_at")
    @classmethod
    def validate_reviewed_at(cls, value: datetime | None) -> datetime | None:
        return ensure_utc(value) if value is not None else None

    @field_serializer("reviewed_at", when_used="json")
    def serialize_reviewed_at(self, value: datetime | None) -> str | None:
        return format_utc(value) if value is not None else None


class NotReviewedReview(ReviewBase):
    mode: Literal["not_reviewed"] = "not_reviewed"
    reviewed: Literal[False] = False


class DegradedReview(ReviewBase):
    mode: Literal["degraded"] = "degraded"
    reviewed: Literal[False] = False
    status: Literal[ReviewStatus.NEEDS_REVIEW] = ReviewStatus.NEEDS_REVIEW
    reason: NonEmptyString
    reviewed_at: datetime


class CompletedReview(ReviewBase):
    reviewed: Literal[True] = True
    status: ReviewStatus
    requested_model: NonEmptyString
    returned_model: NonEmptyString
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: NonEmptyString
    evidence_refs: tuple[EvidenceReference, ...]
    suggested_severity_override: Severity | None = None
    usage: TokenUsage
    latency_ms: int = Field(ge=0)
    reviewed_at: datetime


class LiveReview(CompletedReview):
    mode: Literal["live"] = "live"


class ReplayReview(CompletedReview):
    mode: Literal["replay"] = "replay"


FindingReview = Annotated[
    NotReviewedReview | DegradedReview | LiveReview | ReplayReview,
    Field(discriminator="mode"),
]


class ProvenanceEntry(ContractModel):
    source: FindingSource
    rule_id: NonEmptyString
    evidence: FindingEvidence
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        return ensure_utc(value)

    @field_serializer("timestamp", when_used="json")
    def serialize_timestamp(self, value: datetime) -> str:
        return format_utc(value)


class Finding(ContractModel):
    finding_id: UUID
    dedup_key: Sha256Hex
    rule_id: NonEmptyString
    title: NonEmptyString
    description: NonEmptyString
    impact: Impact
    exploitability: Exploitability = Exploitability.THEORETICAL
    confidence: Confidence = Confidence.HIGH
    status: FindingStatus = FindingStatus.NEEDS_REVIEW
    owasp_category: OwaspCategory
    source: FindingSource
    location: FindingLocation
    evidence: FindingEvidence
    remediation: NonEmptyString
    scan_id: UUID
    timestamp: datetime
    provenance: tuple[ProvenanceEntry, ...]
    review: FindingReview = Field(default_factory=NotReviewedReview)

    @field_validator("finding_id", "scan_id")
    @classmethod
    def validate_uuid4(cls, value: UUID) -> UUID:
        if value.version != 4:
            raise ValueError("identifier must be UUIDv4")
        return value

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        return ensure_utc(value)

    @field_serializer("timestamp", when_used="json")
    def serialize_timestamp(self, value: datetime) -> str:
        return format_utc(value)

    @computed_field(return_type=Severity)  # type: ignore[prop-decorator]
    @property
    def severity(self) -> Severity:
        return calculate_severity(self.impact, self.exploitability)

    @model_validator(mode="after")
    def validate_origin(self) -> Finding:
        if not self.provenance:
            raise ValueError("provenance must contain the originating detector")
        origin = self.provenance[0]
        if origin.source != self.source or origin.rule_id != self.rule_id:
            raise ValueError("first provenance entry must match finding origin")
        return self


_SEVERITY_ORDER = (
    Severity.INFORMATIONAL,
    Severity.LOW,
    Severity.MEDIUM,
    Severity.HIGH,
    Severity.CRITICAL,
)


def calculate_severity(impact: Impact, exploitability: Exploitability) -> Severity:
    """Apply the approved impact/exploitability severity rubric."""

    severity = Severity(impact.value)
    if exploitability is not Exploitability.THEORETICAL:
        return severity
    index = _SEVERITY_ORDER.index(severity)
    return _SEVERITY_ORDER[max(0, index - 1)]


def normalize_repo_path(value: str) -> str:
    """Normalize a relative repository path without resolving the filesystem."""

    normalized = value.replace("\\", "/")
    parts: list[str] = []
    if normalized.startswith("/"):
        raise ValueError("path must be repository-relative")
    for part in normalized.split("/"):
        if part in {"", "."}:
            continue
        if part == "..":
            raise ValueError("path cannot escape the repository root")
        parts.append(part)
    if not parts:
        raise ValueError("path must identify a repository artifact")
    return "/".join(parts)


def make_dedup_key(parts: tuple[str, ...]) -> str:
    """Hash a canonical UTF-8 JSON tuple into a stable deduplication key."""

    payload = json.dumps(parts, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


_ALLOWED_TRANSITIONS: dict[FindingStatus, frozenset[FindingStatus]] = {
    FindingStatus.NEEDS_REVIEW: frozenset(
        {
            FindingStatus.CONFIRMED,
            FindingStatus.LIKELY_FALSE_POSITIVE,
            FindingStatus.SUPPRESSED,
        }
    ),
    FindingStatus.CONFIRMED: frozenset(
        {FindingStatus.NEEDS_REVIEW, FindingStatus.SUPPRESSED}
    ),
    FindingStatus.LIKELY_FALSE_POSITIVE: frozenset({FindingStatus.CONFIRMED}),
    FindingStatus.SUPPRESSED: frozenset(),
}


def transition_status(
    finding: Finding,
    target: FindingStatus,
    *,
    at: datetime,
    reason: str | None = None,
) -> Finding:
    """Return an updated Finding after enforcing the approved lifecycle."""

    if target is finding.status:
        return finding
    if target not in _ALLOWED_TRANSITIONS[finding.status]:
        raise ValueError(f"disallowed status transition: {finding.status} -> {target}")
    needs_reason = target is FindingStatus.SUPPRESSED or (
        finding.status is FindingStatus.CONFIRMED
        and target is FindingStatus.NEEDS_REVIEW
    )
    normalized_reason = reason.strip() if reason is not None else None
    if needs_reason and not normalized_reason:
        raise ValueError("this transition requires a non-empty reason")

    review_data = finding.review.model_dump(mode="python")
    review_data["status"] = (
        ReviewStatus(target.value)
        if target.value in {item.value for item in ReviewStatus}
        else None
    )
    if normalized_reason:
        review_data["reason"] = normalized_reason
    review = type(finding.review).model_validate(review_data)

    data = finding.model_dump(mode="python", exclude={"severity"})
    data.update(status=target, timestamp=ensure_utc(at), review=review)
    return Finding.model_validate(data)


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def format_utc(value: datetime) -> str:
    return ensure_utc(value).isoformat(timespec="microseconds").replace("+00:00", "Z")
