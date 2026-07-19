"""Constrained dynamic probes over fresh Docker-backed MCP stdio sessions."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from mcp.types import Tool
from pydantic import JsonValue

from sentinel.dynamic.catalog import RULE_BY_ID, RULE_IDS
from sentinel.dynamic.sandbox import (
    CANARY_PATH,
    PROBE_TIMEOUT_SECONDS,
    DependencyImage,
    DockerSandbox,
)
from sentinel.errors import InfrastructureError
from sentinel.finding import (
    Confidence,
    DynamicEvidence,
    Exploitability,
    Finding,
    FindingSource,
    FindingStatus,
    LogicalLocation,
    NotReviewedReview,
    ProbePlan,
    ProvenanceEntry,
    make_dedup_key,
)
from sentinel.llm.context import sanitize_text
from sentinel.llm.tools import ToolCatalog, extract_tool_catalog
from sentinel.permissions import PermissionsManifest, load_permissions_manifest
from sentinel.report.model import ReportWarning

DEFAULT_ORDER = RULE_IDS
OVERSIZED_MARKER = "__SENTINEL_OVERSIZED__"
INJECTION_MARKER = "__SENTINEL_INJECTION__"
WRONG_TYPE_MARKER = "__SENTINEL_WRONG_TYPE__"
OMIT_MARKER = "__SENTINEL_OMIT__"
OUT_OF_SCOPE_CANARY = "__sentinel_out_of_scope__"
OVERSIZED_LENGTH = 1_048_576
MAX_RESPONSE_EVIDENCE_BYTES = 16_384
INJECTION_VALUE = f'__import__("pathlib").Path("{CANARY_PATH}").touch()'


@dataclass(frozen=True)
class ProbeBinding:
    probe_id: str
    target_tool: str | None
    field: str | None
    marker: str | None
    container_field: str | None = None


@dataclass(frozen=True)
class ProbeCampaign:
    ordered_probe_ids: tuple[str, ...]
    bindings: dict[str, ProbeBinding]
    primary_finding_id: str | None
    used_fallback: bool


@dataclass(frozen=True)
class DynamicScanResult:
    findings: tuple[Finding, ...]
    warnings: tuple[ReportWarning, ...]
    image: DependencyImage
    campaign: ProbeCampaign


@dataclass(frozen=True)
class _Observation:
    probe_id: str
    target_tool: str
    field: str | None
    request: dict[str, JsonValue]
    response: dict[str, JsonValue]
    logs: tuple[str, ...]
    vulnerable: bool


def run_dynamic_scan(
    sandbox: DockerSandbox,
    static_findings: tuple[Finding, ...],
    *,
    scan_id: UUID,
    timestamp: datetime,
) -> DynamicScanResult:
    """Build the target image and execute every approved dynamic probe once."""

    sandbox.preflight()
    image = sandbox.prepare_dependency_image()
    catalog = extract_tool_catalog(
        sandbox.configuration.scan_root,
        sandbox.configuration.scanner.scanner.ignore_paths,
    )
    campaign, warning = build_probe_campaign(static_findings, catalog)
    manifest = load_permissions_manifest(sandbox.configuration.scan_root, required=True)
    if manifest is None:  # pragma: no cover - required=True
        raise InfrastructureError("permissions manifest disappeared before probing")
    observations = asyncio.run(
        _run_campaign(sandbox, image.reference, campaign, manifest)
    )
    findings = tuple(
        _finding_from_observation(item, scan_id, timestamp)
        for item in observations
        if item.vulnerable
    )
    warnings = catalog.warnings + ((warning,) if warning is not None else ())
    return DynamicScanResult(findings, warnings, image, campaign)


def build_probe_campaign(
    findings: tuple[Finding, ...], catalog: ToolCatalog
) -> tuple[ProbeCampaign, ReportWarning | None]:
    candidates = [
        finding
        for finding in findings
        if finding.status is not FindingStatus.SUPPRESSED
        and finding.review.probe_plan is not None
    ]
    candidates.sort(key=_primary_plan_key)
    for finding in candidates:
        plan = finding.review.probe_plan
        if plan is None or not _valid_plan(plan, catalog):
            continue
        bindings: dict[str, ProbeBinding] = {
            "SENT-008": ProbeBinding("SENT-008", None, None, None)
        }
        for probe_id in ("SENT-009", "SENT-010", "SENT-011"):
            raw = plan.argument_bindings[probe_id]
            field, marker = next(iter(raw.items()))
            bindings[probe_id] = ProbeBinding(
                probe_id, plan.target_tool, field, str(marker)
            )
        return (
            ProbeCampaign(
                tuple(plan.ordered_probe_ids),
                bindings,
                str(finding.finding_id),
                False,
            ),
            None,
        )
    bindings = {
        rule_id: ProbeBinding(rule_id, None, None, None) for rule_id in RULE_IDS
    }
    warning = ReportWarning(
        code="dynamic_probe_plan_fallback",
        message=(
            "No valid non-suppressed GPT probe plan was available; "
            "used the fixed safe dynamic probe order and runtime schemas."
        ),
    )
    return ProbeCampaign(DEFAULT_ORDER, bindings, None, True), warning


async def _run_campaign(
    sandbox: DockerSandbox,
    image: str,
    campaign: ProbeCampaign,
    manifest: PermissionsManifest,
) -> tuple[_Observation, ...]:
    observations: list[_Observation] = []
    deadline = asyncio.get_running_loop().time() + 120
    for probe_id in campaign.ordered_probe_ids:
        remaining = deadline - asyncio.get_running_loop().time()
        if remaining <= 0:
            raise InfrastructureError("dynamic pass exceeded its 120-second timeout")
        state = {"initialized": False}
        try:
            observation = await asyncio.wait_for(
                _run_one(
                    sandbox,
                    image,
                    campaign.bindings[probe_id],
                    manifest,
                    state,
                ),
                timeout=min(PROBE_TIMEOUT_SECONDS, remaining),
            )
        except TimeoutError as error:
            if probe_id == "SENT-009" and state["initialized"]:
                observation = _Observation(
                    probe_id=probe_id,
                    target_tool=(
                        campaign.bindings[probe_id].target_tool or "<fallback>"
                    ),
                    field=campaign.bindings[probe_id].field,
                    request={"marker": OVERSIZED_MARKER},
                    response={"timed_out": True},
                    logs=(),
                    vulnerable=True,
                )
            else:
                raise InfrastructureError(
                    f"{probe_id} exceeded its {PROBE_TIMEOUT_SECONDS}-second timeout"
                ) from error
        observations.append(observation)
    return tuple(observations)


async def _run_one(
    sandbox: DockerSandbox,
    image: str,
    binding: ProbeBinding,
    manifest: PermissionsManifest,
    state: dict[str, bool],
) -> _Observation:
    async with sandbox.probe_session(image, binding.probe_id) as probe:
        state["initialized"] = True
        listed = await probe.client.list_tools()
        tools = tuple(listed.tools)
        selected = _select_runtime_binding(binding, tools, manifest)
        arguments, redacted = _probe_arguments(selected, tools)
        try:
            result = await probe.client.call_tool(
                selected.target_tool or OUT_OF_SCOPE_CANARY,
                arguments=arguments,
            )
            is_error = bool(result.isError)
            response = _bounded_response(
                result.model_dump(mode="json"), is_error=is_error
            )
        except Exception as error:
            is_error = True
            response = _bounded_response(
                {"error": sanitize_text(str(error))}, is_error=is_error
            )
        canary = probe.canary_exists() if binding.probe_id == "SENT-010" else False
        vulnerable = _is_vulnerable(binding.probe_id, is_error, canary)
        response["canary_created"] = canary
        return _Observation(
            probe_id=binding.probe_id,
            target_tool=selected.target_tool or OUT_OF_SCOPE_CANARY,
            field=selected.field,
            request=redacted,
            response=response,
            logs=tuple(sanitize_text(item) for item in probe.logs()),
            vulnerable=vulnerable,
        )


def _bounded_response(
    response: dict[str, Any], *, is_error: bool
) -> dict[str, JsonValue]:
    encoded_size = len(
        json.dumps(response, ensure_ascii=False, default=str).encode("utf-8")
    )
    if encoded_size > MAX_RESPONSE_EVIDENCE_BYTES:
        return {
            "truncated": True,
            "original_size_bytes": encoded_size,
            "is_error": is_error,
        }
    sanitized = _sanitize_json(response)
    if not isinstance(sanitized, dict):  # pragma: no cover - input is a dict
        raise InfrastructureError("dynamic response sanitizer changed its shape")
    return sanitized


def _sanitize_json(value: Any) -> JsonValue:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        return value
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list | tuple):
        return [_sanitize_json(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _sanitize_json(item) for key, item in value.items()}
    return sanitize_text(str(value))


def _select_runtime_binding(
    binding: ProbeBinding,
    tools: tuple[Tool, ...],
    manifest: PermissionsManifest,
) -> ProbeBinding:
    if binding.probe_id == "SENT-008":
        ungranted = sorted(
            tool.name for tool in tools if tool.name not in manifest.tools
        )
        return ProbeBinding(
            binding.probe_id,
            ungranted[0] if ungranted else OUT_OF_SCOPE_CANARY,
            None,
            None,
        )
    by_name = {tool.name: tool for tool in tools}
    if binding.target_tool in by_name and binding.field is not None:
        properties = _properties(by_name[binding.target_tool])
        if binding.field in properties:
            return binding
        containers = [
            name
            for name, schema in properties.items()
            if schema.get("type") == "object"
            and schema.get("additionalProperties") is True
        ]
        if len(containers) == 1:
            return ProbeBinding(
                binding.probe_id,
                binding.target_tool,
                binding.field,
                binding.marker,
                containers[0],
            )
    for tool in sorted(tools, key=lambda item: item.name):
        properties = _properties(tool)
        field = _compatible_field(binding.probe_id, tool, properties)
        if field is not None:
            marker = {
                "SENT-009": OVERSIZED_MARKER,
                "SENT-010": INJECTION_MARKER,
                "SENT-011": WRONG_TYPE_MARKER,
            }[binding.probe_id]
            return ProbeBinding(binding.probe_id, tool.name, field, marker)
    fallback = sorted(tools, key=lambda item: item.name)
    return ProbeBinding(
        binding.probe_id,
        fallback[0].name if fallback else OUT_OF_SCOPE_CANARY,
        "__sentinel_argument__",
        {
            "SENT-009": OVERSIZED_MARKER,
            "SENT-010": INJECTION_MARKER,
            "SENT-011": WRONG_TYPE_MARKER,
        }[binding.probe_id],
    )


def _probe_arguments(
    binding: ProbeBinding, tools: tuple[Tool, ...]
) -> tuple[dict[str, Any], dict[str, JsonValue]]:
    tool = next((item for item in tools if item.name == binding.target_tool), None)
    schema = tool.inputSchema if tool is not None else {}
    arguments = _baseline_arguments(schema)
    redacted: dict[str, JsonValue] = _baseline_arguments(schema)
    if binding.field is None:
        return arguments, redacted
    argument_target = arguments
    redacted_target = redacted
    if binding.container_field is not None:
        nested_arguments = arguments.get(binding.container_field)
        nested_redacted = redacted.get(binding.container_field)
        if not isinstance(nested_arguments, dict) or not isinstance(
            nested_redacted, dict
        ):
            raise InfrastructureError("runtime object envelope is not an object")
        argument_target = nested_arguments
        redacted_target = nested_redacted
    if binding.marker == OMIT_MARKER:
        argument_target.pop(binding.field, None)
        redacted_target.pop(binding.field, None)
    elif binding.marker == OVERSIZED_MARKER:
        field_schema = _properties(tool).get(binding.field, {}) if tool else {}
        value = _oversized_value(field_schema)
        argument_target[binding.field] = value
        redacted_target[binding.field] = OVERSIZED_MARKER
    elif binding.marker == INJECTION_MARKER:
        argument_target[binding.field] = INJECTION_VALUE
        redacted_target[binding.field] = INJECTION_MARKER
    else:
        argument_target[binding.field] = {"__sentinel_wrong_type__": True}
        redacted_target[binding.field] = WRONG_TYPE_MARKER
    return arguments, redacted


def _baseline_arguments(schema: dict[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    if not isinstance(properties, dict) or not isinstance(required, list):
        return {}
    result: dict[str, Any] = {}
    for name in required:
        if isinstance(name, str) and isinstance(properties.get(name), dict):
            result[name] = _inert_value(properties[name])
    return result


def _inert_value(schema: dict[str, Any]) -> Any:
    kind = schema.get("type")
    if not isinstance(kind, str):
        return None
    return {
        "string": "sentinel",
        "integer": 1,
        "number": 1.0,
        "boolean": False,
        "array": [],
        "object": {},
    }.get(kind)


def _oversized_value(schema: dict[str, Any]) -> Any:
    kind = schema.get("type")
    payload = "A" * OVERSIZED_LENGTH
    if kind == "array":
        return [payload]
    if kind == "object":
        return {"value": payload}
    return payload


def _properties(tool: Tool) -> dict[str, dict[str, Any]]:
    raw = tool.inputSchema.get("properties", {})
    if not isinstance(raw, dict):
        return {}
    return {str(name): value for name, value in raw.items() if isinstance(value, dict)}


def _compatible_field(
    probe_id: str, tool: Tool, properties: dict[str, dict[str, Any]]
) -> str | None:
    required = tool.inputSchema.get("required", [])
    for name in sorted(properties):
        kind = properties[name].get("type")
        if probe_id == "SENT-009" and kind in {"string", "array", "object"}:
            return name
        if probe_id == "SENT-010" and kind == "string":
            return name
        if probe_id == "SENT-011" and (name in required or bool(properties)):
            return name
    return None


def _is_vulnerable(probe_id: str, is_error: bool, canary: bool) -> bool:
    if probe_id == "SENT-010":
        return canary
    return not is_error


def _valid_plan(plan: ProbePlan, catalog: ToolCatalog) -> bool:
    if tuple(sorted(plan.ordered_probe_ids)) != tuple(sorted(RULE_IDS)):
        return False
    tool = next((item for item in catalog.tools if item.name == plan.target_tool), None)
    if tool is None:
        return False
    properties = tool.input_schema.get("properties", {})
    if not isinstance(properties, dict):
        return False
    expected_markers = {
        "SENT-009": {OVERSIZED_MARKER},
        "SENT-010": {INJECTION_MARKER},
        "SENT-011": {WRONG_TYPE_MARKER, OMIT_MARKER},
    }
    if set(plan.argument_bindings) != set(expected_markers):
        return False
    for probe_id, markers in expected_markers.items():
        binding = plan.argument_bindings[probe_id]
        if len(binding) != 1:
            return False
        field, marker = next(iter(binding.items()))
        if field not in properties or marker not in markers:
            return False
    return True


def _primary_plan_key(finding: Finding) -> tuple[Any, ...]:
    status_rank = 0 if finding.status is FindingStatus.CONFIRMED else 1
    severity_rank = {
        "Critical": 0,
        "High": 1,
        "Medium": 2,
        "Low": 3,
        "Informational": 4,
    }[finding.severity.value]
    confidence_rank = {
        Confidence.HIGH: 0,
        Confidence.MEDIUM: 1,
        Confidence.LOW: 2,
    }[finding.confidence]
    return status_rank, severity_rank, confidence_rank, finding.dedup_key


def _finding_from_observation(
    observation: _Observation, scan_id: UUID, timestamp: datetime
) -> Finding:
    definition = RULE_BY_ID[observation.probe_id]
    evidence = DynamicEvidence(
        probe_id=observation.probe_id,
        request=observation.request,
        response=observation.response,
        logs=observation.logs,
    )
    provenance = ProvenanceEntry(
        source=FindingSource.DYNAMIC,
        rule_id=observation.probe_id,
        evidence=evidence,
        timestamp=timestamp,
    )
    logical = f"/tools/{_pointer_escape(observation.target_tool)}"
    if observation.field is not None:
        logical += f"/inputSchema/{_pointer_escape(observation.field)}"
    return Finding(
        finding_id=uuid4(),
        dedup_key=make_dedup_key((observation.probe_id, logical, observation.probe_id)),
        rule_id=observation.probe_id,
        title=definition.title,
        description=definition.description,
        impact=definition.impact,
        exploitability=Exploitability.CONFIRMED,
        confidence=Confidence.HIGH,
        status=FindingStatus.NEEDS_REVIEW,
        owasp_category=definition.owasp_category,
        source=FindingSource.DYNAMIC,
        location=LogicalLocation(path=logical),
        evidence=evidence,
        remediation=definition.remediation,
        scan_id=scan_id,
        timestamp=timestamp,
        provenance=(provenance,),
        review=NotReviewedReview(),
    )


def _pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")
