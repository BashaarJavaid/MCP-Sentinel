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


class WorkspaceMemberCoverage(ContractModel):
    path: NonEmptyString
    status: Literal["included", "unsupported", "incomplete"]
    python_file_count: int | None = Field(ge=0)
    typescript_file_count: int | None = Field(ge=0)
    recognized_surface_count: int | None = Field(ge=0)
    unresolved_surface_count: int | None = Field(ge=0)
    unsupported_surface_count: int | None = Field(ge=0)
    reasons: tuple[NonEmptyString, ...] = ()
    nested_configurations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_member(self) -> WorkspaceMemberCoverage:
        counts = (
            self.python_file_count,
            self.typescript_file_count,
            self.recognized_surface_count,
            self.unresolved_surface_count,
            self.unsupported_surface_count,
        )
        if self.status != "incomplete" and any(value is None for value in counts):
            raise ValueError("observed workspace members require known counts")
        if self.status != "included" and not self.reasons:
            raise ValueError("unavailable workspace members require a reason")
        return self


class WorkspaceCoverage(ContractModel):
    declarations: tuple[str, ...]
    members: tuple[WorkspaceMemberCoverage, ...]

    @model_validator(mode="after")
    def validate_members(self) -> WorkspaceCoverage:
        paths = [member.path for member in self.members]
        if len(set(paths)) != len(paths):
            raise ValueError("workspace members require unique paths")
        return self


class StaticCoverage(ContractModel):
    surfaces: tuple[StaticSurface, ...]
    total_possible_surfaces: None = None
    excluded_rule_ids: tuple[str, ...]
    file_wide_rule_ids: tuple[str, ...]
    unresolved_flows: tuple[RecognitionReason, ...] = ()
    workspace: WorkspaceCoverage | None = None

    @model_validator(mode="after")
    def validate_workspace_surfaces(self) -> StaticCoverage:
        if self.workspace is not None:
            members = self.workspace.members
            counts = {
                member.path: {
                    status: 0 for status in ("recognized", "unresolved", "unsupported")
                }
                for member in members
            }
            for surface in self.surfaces:
                owners = [
                    member.path
                    for member in members
                    if member.status != "incomplete"
                    and (
                        member.path == "."
                        or surface.location.path.startswith(member.path + "/")
                    )
                ]
                if not owners:
                    raise ValueError("workspace surface has no observed member")
                counts[max(owners, key=len)][surface.status] += 1
            for member in members:
                for status, count in counts[member.path].items():
                    reported = getattr(member, status + "_surface_count")
                    if reported is not None and reported != count:
                        raise ValueError(
                            "workspace surface counts must match inventory"
                        )
        return self


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
    role: Literal["discovery", "baseline", "attack"]
    attempt_id: NonEmptyString | None = None
    tools: tuple[ObservedTool, ...]
    more_pages: bool | None
    tool_total: int | None = Field(ge=0)
    reason: str | None = None


class PlannedProbeBinding(ContractModel):
    probe_id: str
    tool: str | None
    field: str | None
    attempt_id: NonEmptyString | None = None
    argument_path: tuple[str, ...] = ()
    mutation: str | None = None


class CampaignCoverage(ContractModel):
    max_probe_attempts: int = Field(ge=1)
    timeout_seconds: int = Field(ge=1)
    planned_attempts: int = Field(ge=0)
    eligible_attempts: int = Field(ge=0)
    started_attempts: int = Field(ge=0)
    tested_attempts: int = Field(ge=0)
    remaining_eligible_attempts: int = Field(ge=0)
    enumeration_complete: bool
    budget_exhausted: bool
    elapsed_ms: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_counts(self) -> CampaignCoverage:
        if not (
            self.tested_attempts
            <= self.started_attempts
            <= self.eligible_attempts
            <= self.planned_attempts
        ):
            raise ValueError("campaign counts exceed planned eligible attempts")
        if self.started_attempts > self.max_probe_attempts:
            raise ValueError("campaign exceeds its attempt budget")
        if (
            self.remaining_eligible_attempts
            != self.eligible_attempts - self.started_attempts
        ):
            raise ValueError(
                "campaign remainder must include all unstarted eligible attempts"
            )
        return self


class DynamicCoverage(ContractModel):
    discovery: tuple[DiscoverySnapshot, ...]
    planned_bindings: tuple[PlannedProbeBinding, ...] = ()
    campaign: CampaignCoverage | None = None


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
