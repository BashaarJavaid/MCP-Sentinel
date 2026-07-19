"""Probe planning, payload, finding, and merge contract tests."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from mcp.types import Tool

from sentinel.dynamic.merge import merge_findings
from sentinel.dynamic.prober import (
    DEFAULT_ORDER,
    INJECTION_MARKER,
    MAX_RESPONSE_EVIDENCE_BYTES,
    OMIT_MARKER,
    OVERSIZED_LENGTH,
    OVERSIZED_MARKER,
    WRONG_TYPE_MARKER,
    ProbeBinding,
    _bounded_response,
    _finding_from_observation,
    _Observation,
    _probe_arguments,
    _select_runtime_binding,
    build_probe_campaign,
)
from sentinel.finding import (
    Confidence,
    DynamicEvidence,
    EvidenceReference,
    Exploitability,
    FileLocation,
    Finding,
    FindingSource,
    FindingStatus,
    ProbePlan,
    ReplayReview,
    ReviewStatus,
    TokenUsage,
)
from sentinel.llm.tools import ToolCatalog, ToolMetadata
from sentinel.permissions import PermissionsManifest

NOW = datetime(2026, 7, 18, tzinfo=timezone.utc)


def _catalog() -> ToolCatalog:
    return ToolCatalog(
        tools=(
            ToolMetadata(
                name="unsafe_calculator",
                description=None,
                input_schema={
                    "type": "object",
                    "properties": {"expression": {"type": "string"}},
                    "required": ["expression"],
                    "additionalProperties": False,
                },
                path="server.py",
                start_line=10,
                end_line=20,
            ),
        ),
        warnings=(),
    )


def _reviewed_finding(sample_finding: Finding) -> Finding:
    assert isinstance(sample_finding.location, FileLocation)
    plan = ProbePlan(
        ordered_probe_ids=("SENT-010", "SENT-011", "SENT-009", "SENT-008"),
        target_tool="unsafe_calculator",
        argument_bindings={
            "SENT-009": {"expression": OVERSIZED_MARKER},
            "SENT-010": {"expression": INJECTION_MARKER},
            "SENT-011": {"expression": WRONG_TYPE_MARKER},
        },
    )
    review = ReplayReview(
        status=ReviewStatus.CONFIRMED,
        requested_model="gpt-5.6-sol",
        returned_model="gpt-5.6-sol-test",
        confidence=0.9,
        reasoning="The supplied evidence confirms the candidate.",
        evidence_refs=(
            EvidenceReference(
                path="server.py", range=sample_finding.location.range, claim="sink"
            ),
        ),
        probe_plan=plan,
        usage=TokenUsage(),
        latency_ms=1,
        batch_id="batch",
        reviewed_at=NOW,
        applied_at=NOW,
    )
    data = sample_finding.model_dump(mode="python", exclude={"severity"})
    data.update(
        finding_id=uuid4(),
        status=FindingStatus.CONFIRMED,
        confidence=Confidence.HIGH,
        exploitability=Exploitability.LIKELY,
        review=review,
    )
    return Finding.model_validate(data)


def test_valid_gpt_plan_controls_order_and_bindings(sample_finding: Finding) -> None:
    finding = _reviewed_finding(sample_finding)

    campaign, warning = build_probe_campaign((finding,), _catalog())

    assert campaign.ordered_probe_ids == (
        "SENT-010",
        "SENT-011",
        "SENT-009",
        "SENT-008",
    )
    assert campaign.bindings["SENT-010"].target_tool == "unsafe_calculator"
    assert campaign.primary_finding_id == str(finding.finding_id)
    assert campaign.used_fallback is False
    assert warning is None


def test_invalid_or_suppressed_plan_uses_all_four_fixed_probes(
    sample_finding: Finding,
) -> None:
    finding = _reviewed_finding(sample_finding).model_copy(
        update={"status": FindingStatus.SUPPRESSED}
    )

    campaign, warning = build_probe_campaign((finding,), _catalog())

    assert campaign.ordered_probe_ids == DEFAULT_ORDER
    assert set(campaign.bindings) == set(DEFAULT_ORDER)
    assert campaign.used_fallback is True
    assert warning is not None


def test_payloads_are_schema_shaped_and_evidence_is_redacted() -> None:
    tool = Tool(
        name="unsafe_calculator",
        inputSchema={
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    )
    oversized, oversized_evidence = _probe_arguments(
        ProbeBinding("SENT-009", tool.name, "expression", OVERSIZED_MARKER),
        (tool,),
    )
    injected, injection_evidence = _probe_arguments(
        ProbeBinding("SENT-010", tool.name, "expression", INJECTION_MARKER),
        (tool,),
    )
    omitted, omitted_evidence = _probe_arguments(
        ProbeBinding("SENT-011", tool.name, "expression", OMIT_MARKER),
        (tool,),
    )
    wrong_type, wrong_type_evidence = _probe_arguments(
        ProbeBinding("SENT-011", tool.name, "expression", WRONG_TYPE_MARKER),
        (tool,),
    )

    assert len(oversized["expression"]) == OVERSIZED_LENGTH
    assert oversized_evidence["expression"] == OVERSIZED_MARKER
    assert "sent-010-canary" in injected["expression"]
    assert injection_evidence["expression"] == INJECTION_MARKER
    assert omitted == omitted_evidence == {}
    assert wrong_type["expression"] == {"__sentinel_wrong_type__": True}
    assert wrong_type_evidence["expression"] == WRONG_TYPE_MARKER


def test_oversized_response_evidence_is_bounded_without_losing_outcome() -> None:
    response = _bounded_response(
        {"content": [{"text": "A" * OVERSIZED_LENGTH}]},
        is_error=False,
    )

    assert response["truncated"] is True
    assert response["is_error"] is False
    original_size = response["original_size_bytes"]
    assert isinstance(original_size, int)
    assert original_size > OVERSIZED_LENGTH
    assert len(json.dumps(response).encode("utf-8")) < MAX_RESPONSE_EVIDENCE_BYTES


def test_runtime_binding_uses_ungranted_tool_and_schema_fallback() -> None:
    manifest = PermissionsManifest.model_validate(
        {"version": 1, "tools": {"granted": {}}}
    )
    tools = (
        Tool(
            name="granted",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="hidden",
            inputSchema={
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "required": ["value"],
            },
        ),
    )

    scope = _select_runtime_binding(
        ProbeBinding("SENT-008", None, None, None), tools, manifest
    )
    malformed = _select_runtime_binding(
        ProbeBinding("SENT-011", "missing", "missing", None), tools, manifest
    )

    assert scope.target_tool == "hidden"
    assert malformed.target_tool == "hidden"
    assert malformed.field == "value"
    assert malformed.marker == WRONG_TYPE_MARKER


def test_runtime_binding_preserves_logical_field_inside_object_envelope() -> None:
    manifest = PermissionsManifest.model_validate(
        {"version": 1, "tools": {"wrapped": {}}}
    )
    tool = Tool(
        name="wrapped",
        inputSchema={
            "type": "object",
            "properties": {
                "arguments": {
                    "type": "object",
                    "additionalProperties": True,
                }
            },
            "required": ["arguments"],
        },
    )

    binding = _select_runtime_binding(
        ProbeBinding("SENT-011", "wrapped", "record_id", WRONG_TYPE_MARKER),
        (tool,),
        manifest,
    )
    arguments, evidence = _probe_arguments(binding, (tool,))

    assert binding.container_field == "arguments"
    assert arguments == {"arguments": {"record_id": {"__sentinel_wrong_type__": True}}}
    assert evidence == {"arguments": {"record_id": WRONG_TYPE_MARKER}}


def test_dynamic_finding_is_confirmed_and_redacts_pointer_tokens() -> None:
    observation = _Observation(
        probe_id="SENT-009",
        target_tool="unsafe/tool~name",
        field="expression",
        request={"expression": OVERSIZED_MARKER},
        response={"isError": False},
        logs=("accepted",),
        vulnerable=True,
    )

    finding = _finding_from_observation(observation, uuid4(), NOW)

    assert finding.source is FindingSource.DYNAMIC
    assert finding.exploitability is Exploitability.CONFIRMED
    assert finding.location.path == "/tools/unsafe~1tool~0name/inputSchema/expression"
    assert isinstance(finding.evidence, DynamicEvidence)
    assert finding.evidence.request["expression"] == OVERSIZED_MARKER


def test_malformed_dynamic_proof_merges_into_matching_sent003(
    sample_finding: Finding,
) -> None:
    assert isinstance(sample_finding.location, FileLocation)
    static_data = sample_finding.model_dump(mode="python", exclude={"severity"})
    static_data.update(
        finding_id=uuid4(),
        rule_id="SENT-003",
        location=sample_finding.location.model_copy(
            update={
                "range": sample_finding.location.range.model_copy(
                    update={"start_line": 12, "end_line": 12}
                )
            }
        ),
        provenance=(
            sample_finding.provenance[0].model_copy(update={"rule_id": "SENT-003"}),
        ),
    )
    static = Finding.model_validate(static_data)
    dynamic = _finding_from_observation(
        _Observation(
            probe_id="SENT-011",
            target_tool="unsafe_calculator",
            field="expression",
            request={"expression": WRONG_TYPE_MARKER},
            response={"isError": False},
            logs=(),
            vulnerable=True,
        ),
        static.scan_id,
        NOW,
    )

    merged = merge_findings((static,), (dynamic,), _catalog())

    assert len(merged) == 1
    assert merged[0].rule_id == "SENT-003"
    assert merged[0].exploitability is Exploitability.CONFIRMED
    assert [item.rule_id for item in merged[0].provenance] == [
        "SENT-003",
        "SENT-011",
    ]
