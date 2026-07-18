"""Strict model-owned response contract for semantic review."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, StringConstraints, field_validator

from sentinel.finding import ContractModel, Severity, normalize_repo_path

ReviewText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
ReasoningText = Annotated[ReviewText, StringConstraints(max_length=800)]
ClaimText = Annotated[ReviewText, StringConstraints(max_length=300)]


class ReviewEvidenceReference(ContractModel):
    path: ReviewText
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    claim: ClaimText

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repo_path(value)

    @field_validator("end_line")
    @classmethod
    def validate_line_order(cls, value: int, info: object) -> int:
        data = getattr(info, "data", {})
        start = data.get("start_line")
        if isinstance(start, int) and value < start:
            raise ValueError("end_line cannot precede start_line")
        return value


class ReviewArgumentBinding(ContractModel):
    probe_id: Literal["SENT-009", "SENT-010", "SENT-011"]
    field: ReviewText
    value: Literal[
        "__SENTINEL_OVERSIZED__",
        "__SENTINEL_INJECTION__",
        "__SENTINEL_WRONG_TYPE__",
        "__SENTINEL_OMIT__",
    ]


class ReviewProbePlan(ContractModel):
    ordered_probe_ids: tuple[
        Literal["SENT-008", "SENT-009", "SENT-010", "SENT-011"], ...
    ]
    target_tool: ReviewText
    argument_bindings: tuple[ReviewArgumentBinding, ...] = Field(
        min_length=3, max_length=3
    )


class FindingReviewDecision(ContractModel):
    finding_id: UUID
    status: Literal["confirmed", "suppressed", "needs_review"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: ReasoningText
    evidence_refs: tuple[ReviewEvidenceReference, ...] = Field(
        min_length=1, max_length=3
    )
    probe_plan: ReviewProbePlan | None
    suggested_severity_override: Severity | None


class ReviewBatchResponse(ContractModel):
    reviews: tuple[FindingReviewDecision, ...] = Field(min_length=1, max_length=10)
