"""Constrained dynamic probes over fresh Docker-backed MCP stdio sessions."""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from datetime import datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, INVALID_REQUEST, METHOD_NOT_FOUND, Tool
from pydantic import JsonValue

from sentinel.dynamic.arguments import (
    InvalidBaseline,
    UnsupportedSchema,
    baseline_arguments,
    resolve_schema,
    schema_errors,
    schema_validator,
)
from sentinel.dynamic.catalog import RULE_BY_ID, RULE_IDS
from sentinel.dynamic.coverage import discovery_snapshot
from sentinel.dynamic.sandbox import (
    CANARY_PATH,
    PROBE_TIMEOUT_SECONDS,
    DependencyImage,
    DockerSandbox,
    ProbeSession,
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
    RuntimeProof,
    make_dedup_key,
)
from sentinel.llm.context import sanitize_text
from sentinel.llm.tools import ToolCatalog, extract_tool_catalog
from sentinel.permissions import PermissionsManifest, load_permissions_manifest
from sentinel.report.coverage import (
    DiscoverySnapshot,
    DynamicCoverage,
    PlannedProbeBinding,
)
from sentinel.report.model import (
    PROBE_IDS,
    DynamicAnalysisSummary,
    DynamicProbeOutcome,
    ReportWarning,
)

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
    observations: tuple[_Observation, ...] = ()

    @property
    def complete(self) -> bool:
        return len(self.observations) == 4 and all(
            item.status == "tested" for item in self.observations
        )

    @property
    def summary(self) -> DynamicAnalysisSummary:
        by_id = {item.probe_id: item for item in self.observations}

        def attempt_id(item: _Observation) -> str:
            return f"{item.probe_id}:" + _identity(
                [item.target_tool, item.argument_path, item.field]
            )

        return DynamicAnalysisSummary(
            coverage=DynamicCoverage(
                discovery=tuple(
                    snapshot.model_copy(update={"attempt_id": attempt_id(item)})
                    for item in self.observations
                    for snapshot in item.discovery
                ),
                planned_bindings=tuple(
                    PlannedProbeBinding(
                        probe_id=item.probe_id, tool=item.target_tool, field=item.field
                    )
                    for item in self.campaign.bindings.values()
                ),
            ),
            probe_outcomes=tuple(
                DynamicProbeOutcome(
                    attempt_id=attempt_id(item),
                    probe_id=probe_id,
                    status=item.status,
                    baseline_attempted=item.baseline_attempted,
                    attack_attempted=item.attack_attempted,
                    verdict=item.verdict,
                    tool=item.target_tool or None,
                    field=item.field,
                    argument_path=item.argument_path,
                    reason=sanitize_text(item.reason),
                    baseline=_sanitize_json_dict(item.baseline),
                    attack={
                        "request": item.request,
                        "response": item.response,
                        "logs": list(item.logs),
                    },
                    schema_checks=tuple(
                        _sanitize_json_dict(check) for check in item.schema_checks
                    ),
                    effects=_sanitize_json_dict(item.effects),
                    timings=item.timings,
                    execution_successful=item.execution_successful,
                )
                for probe_id in PROBE_IDS
                for item in (
                    by_id.get(probe_id)
                    or _Observation(
                        probe_id,
                        "",
                        None,
                        {},
                        {},
                        (),
                        False,
                        status="untested",
                        reason="probe result unavailable",
                    ),
                )
            ),
        )

    @property
    def execution_successful(self) -> bool:
        return all(item.execution_successful for item in self.observations)


@dataclass
class _Observation:
    probe_id: str
    target_tool: str
    field: str | None
    request: dict[str, JsonValue]
    response: dict[str, JsonValue]
    logs: tuple[str, ...]
    vulnerable: bool
    status: Literal["tested", "unsupported", "untested", "inconclusive"] = "tested"
    reason: str = "completed attempt"
    baseline: dict[str, Any] = dataclass_field(default_factory=dict)
    schema_checks: list[dict[str, Any]] = dataclass_field(default_factory=list)
    effects: dict[str, Any] = dataclass_field(default_factory=dict)
    timings: dict[str, float] = dataclass_field(default_factory=dict)
    execution_successful: bool = True
    argument_path: tuple[str, ...] = ()
    baseline_attempted: bool = False
    attack_attempted: bool = False
    discovery: list[DiscoverySnapshot] = dataclass_field(default_factory=list)

    @property
    def verdict(self) -> Literal["violation_observed", "no_violation_observed"] | None:
        if self.status != "tested":
            return None
        return "violation_observed" if self.vulnerable else "no_violation_observed"


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
    warnings += tuple(
        ReportWarning(
            code=f"dynamic_probe_{item.status}",
            message=f"{item.probe_id}: {item.reason}",
        )
        for item in observations
        if item.status != "tested"
    )
    return DynamicScanResult(findings, warnings, image, campaign, observations)


def build_probe_campaign(
    findings: tuple[Finding, ...], catalog: ToolCatalog
) -> tuple[ProbeCampaign, ReportWarning | None]:
    candidates = [
        finding
        for finding in findings
        if finding.status is not FindingStatus.SUPPRESSED
        and finding.review is not None
        and finding.review.probe_plan is not None
    ]
    candidates.sort(key=_primary_plan_key)
    for finding in candidates:
        plan = finding.review.probe_plan if finding.review else None
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
    stopped: str | None = None
    for probe_id in campaign.ordered_probe_ids:
        binding = campaign.bindings[probe_id]
        if stopped or asyncio.get_running_loop().time() >= deadline:
            observations.append(
                _Observation(
                    probe_id,
                    binding.target_tool or "<unbound>",
                    binding.field,
                    {},
                    {},
                    (),
                    False,
                    status="untested",
                    reason=stopped or "campaign deadline exhausted",
                )
            )
            continue
        try:
            observation = await _run_one(
                sandbox,
                image,
                binding,
                manifest,
                {"initialized": False, "deadline": deadline},
            )
        except TimeoutError:
            observation = _Observation(
                probe_id,
                binding.target_tool or "<unbound>",
                binding.field,
                {},
                {"timed_out": True},
                (),
                False,
                status="inconclusive",
                reason="session timeout without decisive process evidence",
            )
        except InfrastructureError as error:
            stopped = sanitize_text(str(error))
            observation = _Observation(
                probe_id,
                binding.target_tool or "<unbound>",
                binding.field,
                {},
                {},
                (),
                False,
                status="inconclusive",
                reason=stopped,
                execution_successful=False,
            )
        observations.append(observation)
        if not observation.execution_successful:
            stopped = observation.reason
    return tuple(observations)


async def _run_one(
    sandbox: DockerSandbox,
    image: str,
    binding: ProbeBinding,
    manifest: PermissionsManifest,
    state: dict[str, Any],
) -> _Observation:
    observation = _Observation(
        binding.probe_id,
        binding.target_tool or "<unbound>",
        binding.field,
        {},
        {},
        (),
        False,
    )
    try:
        await _baseline_and_attack(
            sandbox, image, binding, manifest, state, observation
        )
    except UnsupportedSchema as error:
        observation.status = "unsupported"
        observation.reason = str(error)
    except InvalidBaseline as error:
        observation.status = "inconclusive"
        observation.reason = str(error)
    except TimeoutError:
        observation.status = "inconclusive"
        observation.reason = "campaign deadline exhausted before a decisive result"
    except InfrastructureError as error:
        observation.status = "inconclusive"
        observation.reason = sanitize_text(str(error))
        observation.execution_successful = False
    return observation


def _session_timeout(state: dict[str, Any]) -> float:
    remaining = state.get("deadline", float("inf")) - asyncio.get_running_loop().time()
    if remaining <= 0:
        raise TimeoutError("campaign deadline exhausted")
    return float(min(PROBE_TIMEOUT_SECONDS, remaining))


async def _list_tools(
    probe: ProbeSession, observation: _Observation, role: Literal["baseline", "attack"]
) -> tuple[Tool, ...]:
    try:
        listed = await asyncio.wait_for(
            probe.client.list_tools(),
            timeout=max(0, probe.deadline - asyncio.get_running_loop().time()),
        )
    except Exception as error:
        observation.discovery.append(
            DiscoverySnapshot(
                probe_id=observation.probe_id,
                role=role,
                tools=(),
                more_pages=None,
                tool_total=None,
                reason="runtime tool discovery failed",
            )
        )
        raise InfrastructureError("runtime tool discovery failed") from error
    tools = tuple(listed.tools)
    observation.discovery.append(
        discovery_snapshot(
            observation.probe_id,
            role,
            tools,
            more_pages=listed.nextCursor is not None,
            deadline=probe.deadline,
        )
    )
    if len({tool.name for tool in tools}) != len(tools):
        raise InfrastructureError("runtime tool catalog contains duplicate names")
    return tools


async def _call(
    probe: ProbeSession,
    name: str,
    arguments: dict[str, Any],
    observation: _Observation,
    role: Literal["baseline", "attack"],
) -> dict[str, Any]:
    before = probe.process_state()
    if not before["Running"] or before["Error"] or before["OOMKilled"]:
        raise InfrastructureError("target was not healthy before the tool call")
    try:

        async def send() -> Any:
            setattr(observation, f"{role}_attempted", True)
            return await probe.client.call_tool(name, arguments=arguments)

        result = await asyncio.wait_for(
            send(),
            timeout=max(0, probe.deadline - asyncio.get_running_loop().time()),
        )
        response = _bounded_response(
            result.model_dump(mode="json"), is_error=bool(result.isError)
        )
        response["is_error"] = bool(result.isError)
    except TimeoutError:
        response = {"is_error": True, "timed_out": True}
    except Exception as error:
        response = {
            "is_error": True,
            "protocol_failure": not (
                isinstance(error, McpError)
                and error.error.code
                in {INVALID_PARAMS, INVALID_REQUEST, METHOD_NOT_FOUND}
            ),
            "error": sanitize_text(str(error))[:1024],
        }
    # Sample while stdio is still attached, before scanner shutdown can kill it.
    after = probe.process_state()
    response["process_state"] = after
    if after["Error"]:
        raise InfrastructureError("Docker reported a target process error")
    return response


def _baseline_for(sandbox: DockerSandbox, tool: Tool) -> dict[str, Any]:
    return baseline_arguments(
        tool.inputSchema, sandbox.target.probe_baselines.get(tool.name)
    )


def _resource_failure(response: dict[str, Any]) -> bool:
    state = response["process_state"]
    return bool(
        not state["Running"]
        and not state["Error"]
        and (state["OOMKilled"] or state["ExitCode"] != 0)
    )


async def _baseline_and_attack(
    sandbox: DockerSandbox,
    image: str,
    binding: ProbeBinding,
    manifest: PermissionsManifest,
    state: dict[str, Any],
    observation: _Observation,
) -> None:
    started = asyncio.get_running_loop().time()
    try:
        async with sandbox.probe_session(
            image, binding.probe_id, timeout=_session_timeout(state)
        ) as probe:
            state["initialized"] = True
            tools = await _list_tools(probe, observation, "baseline")
            selected = _select_runtime_binding(binding, tools, manifest)
            observation.target_tool = selected.target_tool or OUT_OF_SCOPE_CANARY
            observation.field = selected.field
            observation.argument_path = tuple(
                part
                for part in (selected.container_field, selected.field)
                if part is not None
            )
            tool = next(
                (item for item in tools if item.name == selected.target_tool), None
            )
            if binding.probe_id == "SENT-008":
                granted = sorted(
                    (item for item in tools if item.name in manifest.tools),
                    key=lambda item: item.name,
                )
                if not granted:
                    raise InvalidBaseline(
                        "no listed granted tool for a legitimate control"
                    )
                control = granted[0]
                arguments = _baseline_for(sandbox, control)
                attack = _baseline_for(sandbox, tool) if tool else {}
                redacted = _sanitize_json(attack)
                observation.effects["policy_sha256"] = _identity(
                    manifest.model_dump(mode="json")
                )
            else:
                if tool is None or selected.field is None:
                    raise UnsupportedSchema("no compatible listed tool/field")
                control = tool
                arguments = _baseline_for(sandbox, control)
                attack, redacted = _probe_arguments(selected, tools, arguments)
            observation.request = _sanitize_json_dict(redacted)
            observation.baseline = {
                "tool": control.name,
                "request": _sanitize_json(arguments),
                "schema_valid": True,
                "schema_sha256": _identity(control.inputSchema),
            }
            observation.effects["request_sha256"] = _identity(attack)
            observation.effects["request_size_bytes"] = len(
                json.dumps(attack, ensure_ascii=False).encode()
            )
            if tool is not None:
                observation.effects["schema_sha256"] = _identity(tool.inputSchema)
                observation.schema_checks = schema_errors(
                    schema_validator(tool.inputSchema), attack
                )
            if binding.probe_id == "SENT-010":
                if probe.canary_exists():
                    raise InvalidBaseline("canary exists before the baseline")
                observation.effects["baseline_canary_before"] = False
            response = await _call(
                probe, control.name, arguments, observation, "baseline"
            )
            observation.baseline["response"] = response
            observation.baseline["logs"] = [
                sanitize_text(item)[:1024] for item in probe.logs()
            ]
            if binding.probe_id == "SENT-010":
                observation.effects["baseline_canary_after"] = probe.canary_exists()
                if observation.effects["baseline_canary_after"]:
                    raise InvalidBaseline("baseline created the canary")
            if response["is_error"] or not response["process_state"]["Running"]:
                raise InvalidBaseline("legitimate runtime baseline did not succeed")
    finally:
        observation.timings["baseline_ms"] = (
            asyncio.get_running_loop().time() - started
        ) * 1000

    started = asyncio.get_running_loop().time()
    try:
        async with sandbox.probe_session(
            image, binding.probe_id, timeout=_session_timeout(state)
        ) as probe:
            listed = await _list_tools(probe, observation, "attack")
            expected = {item.name: item.inputSchema for item in tools}
            if {item.name: item.inputSchema for item in listed} != expected:
                raise InvalidBaseline(
                    "runtime schemas changed between baseline and attack"
                )
            if binding.probe_id == "SENT-010":
                observation.effects["canary_before"] = probe.canary_exists()
                if observation.effects["canary_before"]:
                    raise InvalidBaseline("canary exists before the attack")
            response = await _call(
                probe, observation.target_tool, attack, observation, "attack"
            )
            observation.response = _sanitize_json_dict(response)
            if binding.probe_id == "SENT-010":
                observation.effects["canary_after"] = probe.canary_exists()
            observation.logs = tuple(
                sanitize_text(item)[:1024] for item in probe.logs()
            )
            _conclude(observation, listed_tool=tool is not None)
    finally:
        observation.timings["attack_ms"] = (
            asyncio.get_running_loop().time() - started
        ) * 1000


def _conclude(observation: _Observation, *, listed_tool: bool) -> None:
    response = observation.response
    success = not response["is_error"]
    size_checks = [
        item
        for item in observation.schema_checks
        if item["keyword"] in {"maxLength", "maxItems", "maxProperties"}
    ]
    resource_failure = _resource_failure(response)
    if observation.probe_id == "SENT-010":
        observation.vulnerable = bool(observation.effects.get("canary_after"))
    elif observation.probe_id == "SENT-009":
        observation.vulnerable = (success and bool(size_checks)) or resource_failure
        observation.effects["resource_failure"] = resource_failure
    elif observation.probe_id == "SENT-008":
        observation.vulnerable = success and listed_tool
        if success and not listed_tool:
            observation.status = "inconclusive"
            observation.reason = (
                "unknown-name success does not prove execution of a listed tool"
            )
            return
    else:
        observation.vulnerable = success and bool(observation.schema_checks)
    if observation.vulnerable:
        observation.reason = "security violation observed after a successful baseline"
    elif (
        response.get("timed_out")
        or response.get("protocol_failure")
        or resource_failure
    ):
        observation.status = "inconclusive"
        observation.reason = (
            "attack did not produce a decisive protocol result or security effect"
        )
    else:
        observation.reason = "applicable attempt completed; no violation observed"


def _identity(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()


def _sanitize_json_dict(value: Any) -> dict[str, JsonValue]:
    sanitized = _sanitize_json(value)
    if not isinstance(sanitized, dict):
        raise InfrastructureError("dynamic evidence must be an object")
    return sanitized


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
        if len(containers) == 1 and binding.probe_id != "SENT-011":
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
    binding: ProbeBinding,
    tools: tuple[Tool, ...],
    baseline: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, JsonValue]]:
    tool = next((item for item in tools if item.name == binding.target_tool), None)
    if tool is None:
        raise UnsupportedSchema("probe target is not a listed tool")
    validator = schema_validator(tool.inputSchema)
    arguments = (
        copy.deepcopy(baseline)
        if baseline is not None
        else baseline_arguments(tool.inputSchema)
    )
    if schema_errors(validator, arguments):
        raise InvalidBaseline("baseline must be valid before mutation")
    if binding.field is None:
        return arguments, _sanitize_json_dict(arguments)
    target = arguments
    properties = _properties(tool)
    if binding.container_field is not None:
        nested = arguments.get(binding.container_field)
        if not isinstance(nested, dict):
            raise UnsupportedSchema("runtime object envelope is not an object")
        target = nested
        container_schema = properties.get(binding.container_field, {})
        properties = container_schema.get("properties", {})
    field_schema = resolve_schema(properties.get(binding.field, {}), tool.inputSchema)
    if binding.marker == INJECTION_MARKER:
        target[binding.field] = INJECTION_VALUE
    elif binding.marker == OVERSIZED_MARKER:
        target[binding.field] = _oversized_value(field_schema)
        # Include siblings/envelopes in the wire-size cap, not just the value.
        excess = (
            len(json.dumps(arguments, ensure_ascii=False).encode()) - OVERSIZED_LENGTH
        )
        if excess > 0 and isinstance(target[binding.field], str):
            target[binding.field] = target[binding.field][:-excess]
        if len(json.dumps(arguments, ensure_ascii=False).encode()) > OVERSIZED_LENGTH:
            raise UnsupportedSchema("oversized mutation exceeds the 1 MiB argument cap")
    else:
        if binding.marker == OMIT_MARKER:
            target.pop(binding.field, None)
        else:
            values: tuple[Any, ...] = (
                {"__sentinel_wrong_type__": True},
                "sentinel",
                1,
                False,
                [],
                None,
            )
            for value in values:
                target[binding.field] = value
                errors = schema_errors(validator, arguments)
                if any(error["keyword"] == "type" for error in errors):
                    break
            else:
                # Omission is only useful when the complete schema proves it required.
                target.pop(binding.field, None)
        errors = schema_errors(validator, arguments)
        if not errors or not any(
            error["keyword"] in {"type", "required"} for error in errors
        ):
            raise UnsupportedSchema(
                "no verified type or required-field violation for this binding"
            )
    redacted = copy.deepcopy(arguments)
    redacted_target = (
        redacted[binding.container_field] if binding.container_field else redacted
    )
    if binding.field in target:
        redacted_target[binding.field] = binding.marker
    return arguments, _sanitize_json_dict(redacted)


def _oversized_value(schema: dict[str, Any]) -> Any:
    kind = schema.get("type")
    if isinstance(kind, list):
        kind = next(
            (item for item in kind if item in {"string", "array", "object"}), None
        )
    if kind == "array":
        if "maxItems" in schema:
            count = schema["maxItems"] + 1
            if count > OVERSIZED_LENGTH // 6:
                raise UnsupportedSchema(
                    "maxItems cannot be breached within the payload cap"
                )
            return [None] * count
        return ["A" * (OVERSIZED_LENGTH // 2)]
    if kind == "object":
        if "maxProperties" in schema:
            count = schema["maxProperties"] + 1
            if count > OVERSIZED_LENGTH // 24:
                raise UnsupportedSchema(
                    "maxProperties cannot be breached within the payload cap"
                )
            return {f"sentinel_{i}": None for i in range(count)}
        return {"value": "A" * (OVERSIZED_LENGTH // 2)}
    return "A" * OVERSIZED_LENGTH


def _properties(tool: Tool) -> dict[str, dict[str, Any]]:
    schema_validator(tool.inputSchema)
    schema = resolve_schema(tool.inputSchema, tool.inputSchema)
    raw = schema.get("properties", {})
    if not isinstance(raw, dict):
        return {}
    properties = {
        str(name): resolve_schema(value, tool.inputSchema)
        for name, value in raw.items()
    }
    for name in schema.get("required", []):
        properties.setdefault(name, {})
    return properties


def _compatible_field(
    probe_id: str, tool: Tool, properties: dict[str, dict[str, Any]]
) -> str | None:
    required = resolve_schema(tool.inputSchema, tool.inputSchema).get("required", [])
    for name in sorted(properties):
        kind = properties[name].get("type")
        kinds = set(kind) if isinstance(kind, list) else {kind}
        if probe_id == "SENT-009" and kinds & {"string", "array", "object"}:
            return name
        if probe_id == "SENT-010" and "string" in kinds:
            return name
        if probe_id == "SENT-011" and (name in required or bool(properties)):
            return name
    return None


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
    if not observation.vulnerable:
        raise ValueError("a dynamic finding requires an observed violation")
    definition = RULE_BY_ID[observation.probe_id]
    evidence = DynamicEvidence(
        probe_id=observation.probe_id,
        request=observation.request,
        response=_sanitize_json_dict(
            {
                **observation.response,
                "diagnostics": {"timings": observation.timings},
            }
        ),
        logs=observation.logs,
        proof=RuntimeProof(
            tool=observation.target_tool,
            field=observation.field,
            argument_path=observation.argument_path
            or ((observation.field,) if observation.field is not None else ()),
            baseline=_sanitize_json_dict(observation.baseline),
            schema_checks=tuple(
                _sanitize_json_dict(item) for item in observation.schema_checks
            ),
            effects=_sanitize_json_dict(observation.effects),
        ),
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
        status=FindingStatus.CONFIRMED,
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
