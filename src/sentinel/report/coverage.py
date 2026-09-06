"""Observed coverage and stage review activity; unknown history stays null."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from sentinel.finding import ContractModel, FileLocation, NonEmptyString, Sha256Hex


class RecognitionReason(ContractModel):
    code: NonEmptyString
    message: NonEmptyString
    location: FileLocation


class StaticSurface(ContractModel):
    kind: Literal["tool", "prompt", "http_route"]
    name: str | None
    location: FileLocation
    handler: FileLocation | None
    status: Literal["recognized", "unresolved", "unsupported"]
    reasons: tuple[RecognitionReason, ...] = ()
    examined_rule_ids: tuple[str, ...] = ()


class StaticCoverage(ContractModel):
    surfaces: tuple[StaticSurface, ...]
    total_possible_surfaces: None = None
    excluded_rule_ids: tuple[str, ...]
    file_wide_rule_ids: tuple[str, ...]
    unresolved_flows: tuple[RecognitionReason, ...] = ()


class UnresolvedFieldSpace(ContractModel):
    path: tuple[str, ...]
    reason: NonEmptyString


class ObservedTool(ContractModel):
    name: str
    schema_sha256: Sha256Hex | None
    field_paths: tuple[tuple[str, ...], ...]
    unresolved: tuple[UnresolvedFieldSpace, ...]


class DiscoverySnapshot(ContractModel):
    probe_id: str
    role: Literal["baseline", "attack"]
    tools: tuple[ObservedTool, ...]
    more_pages: bool | None
    tool_total: int | None = Field(ge=0)
    reason: str | None = None


class PlannedProbeBinding(ContractModel):
    probe_id: str
    tool: str | None
    field: str | None


class DynamicCoverage(ContractModel):
    discovery: tuple[DiscoverySnapshot, ...]
    planned_bindings: tuple[PlannedProbeBinding, ...] = ()


class ReviewActivity(ContractModel):
    state: Literal[
        "not_requested",
        "not_reached",
        "no_candidates",
        "all_suppressed",
        "completed",
        "incomplete",
    ]
    candidate_count: int | None = Field(ge=0)
    excluded_count: int | None = Field(ge=0)
    selected_count: int = Field(ge=0)
    reviewed_count: int = Field(ge=0)
    unreviewed_count: int | None = Field(ge=0)
    modes: tuple[Literal["live", "cached", "replay", "degraded"], ...] = ()
    reason: NonEmptyString

    @model_validator(mode="after")
    def validate_counts(self) -> ReviewActivity:
        if self.candidate_count is not None and self.excluded_count is not None:
            eligible = self.candidate_count - self.excluded_count
            if not 0 <= self.reviewed_count <= self.selected_count <= eligible:
                raise ValueError("review activity counts exceed eligible candidates")
            if self.unreviewed_count != eligible - self.reviewed_count:
                raise ValueError("unreviewed count excludes inline suppressions")
        return self


class StageReviewActivity(ContractModel):
    static: ReviewActivity | None = None
    dynamic: ReviewActivity | None = None
