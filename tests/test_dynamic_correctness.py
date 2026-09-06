"""Phase 17 failing-before contracts; synthetic sessions never execute a target.

These assertions deliberately stay red until the owning implementation checkpoint.
The JSON Schema validator is the independent oracle for payload validity.
"""

from __future__ import annotations

import asyncio
import io
import json
import subprocess
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

import pytest
from jsonschema import Draft202012Validator
from mcp import ClientSession
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, CallToolResult, ErrorData, ListToolsResult, Tool

from sentinel.config import LlmConfig, LoadedConfiguration
from sentinel.dynamic import prober
from sentinel.dynamic.prober import (
    INJECTION_MARKER,
    OVERSIZED_MARKER,
    WRONG_TYPE_MARKER,
    ProbeBinding,
    _finding_from_observation,
    _Observation,
    _probe_arguments,
)
from sentinel.dynamic.sandbox import DockerSandbox, ProbeSession
from sentinel.errors import InfrastructureError
from sentinel.finding import Confidence, FindingStatus
from sentinel.llm.cache import ReviewCache
from sentinel.llm.semantic_reviewer import SemanticReviewer, unavailable_review_outcome
from sentinel.llm.tools import ToolCatalog
from sentinel.permissions import PermissionsManifest
from tests.test_gpt_review import NOW, ROOT, FakeTransport


class SyntheticSandbox:
    """In-memory MCP replies and observable effects, not a Docker substitute."""

    def __init__(
        self,
        tool: Tool,
        *,
        enforce_schema: bool = True,
        baseline_error: bool = False,
        create_canary: bool = False,
        contaminated: bool = False,
        attack_error: bool = False,
    ) -> None:
        self.tool = tool
        self.target = SimpleNamespace(probe_baselines={})
        self.enforce_schema = enforce_schema
        self.baseline_error = baseline_error
        self.create_canary = create_canary
        self.contaminated = contaminated
        self.attack_error = attack_error
        self.sessions = 0
        self.calls: list[tuple[int, str, dict[str, Any]]] = []

    @asynccontextmanager
    async def probe_session(
        self, image: str, probe_id: str, *, timeout: float = 10
    ) -> AsyncIterator[Any]:
        self.sessions += 1
        session_id = self.sessions
        sandbox = self

        class Session:
            client: Session

            def __init__(self) -> None:
                self.client = self
                self.canary = sandbox.contaminated
                self.deadline = asyncio.get_running_loop().time() + timeout

            def process_state(self) -> dict[str, Any]:
                return {"Running": True, "OOMKilled": False, "ExitCode": 0, "Error": ""}

            async def list_tools(self) -> ListToolsResult:
                return ListToolsResult(tools=[sandbox.tool])

            async def call_tool(
                self, name: str, arguments: dict[str, Any]
            ) -> CallToolResult:
                sandbox.calls.append((session_id, name, arguments))
                invalid = not Draft202012Validator(sandbox.tool.inputSchema).is_valid(
                    arguments
                )
                attack = invalid or any(
                    isinstance(value, str)
                    and (len(value) > 4096 or "sent-010-canary" in value)
                    for value in arguments.values()
                )
                if attack and sandbox.create_canary:
                    self.canary = True
                return CallToolResult(
                    content=[],
                    isError=(
                        name != sandbox.tool.name
                        or (sandbox.enforce_schema and invalid)
                        or (sandbox.baseline_error and not attack)
                        or (sandbox.attack_error and attack)
                    ),
                )

            def canary_exists(self) -> bool:
                return self.canary

            def logs(self) -> tuple[str, ...]:
                return ()

        yield Session()


def _tool(field_schema: dict[str, Any]) -> Tool:
    return Tool(
        name="process",
        inputSchema={
            "type": "object",
            "properties": {"value": field_schema},
            "required": ["value"],
            "additionalProperties": False,
        },
    )


def _attempt(sandbox: SyntheticSandbox, probe_id: str, marker: str) -> _Observation:
    return asyncio.run(
        prober._run_one(
            cast(DockerSandbox, sandbox),
            "synthetic:no-target-code",
            ProbeBinding(probe_id, sandbox.tool.name, "value", marker),
            PermissionsManifest.model_validate(
                {"version": 1, "tools": {"process": {}}}
            ),
            {"initialized": False},
        )
    )


@pytest.mark.parametrize("kind", ["object", "string", "integer", "array"])
def test_wrong_type_mutation_is_actually_invalid(kind: str) -> None:
    tool = _tool({"type": kind})
    arguments, _ = _probe_arguments(
        ProbeBinding("SENT-011", tool.name, "value", WRONG_TYPE_MARKER), (tool,)
    )
    assert not Draft202012Validator(tool.inputSchema).is_valid(arguments)


def test_unconstrained_nested_field_is_not_malformed_input() -> None:
    tool = _tool({"type": "object", "additionalProperties": True})
    manifest = PermissionsManifest.model_validate(
        {"version": 1, "tools": {"process": {}}}
    )
    binding = prober._select_runtime_binding(
        ProbeBinding("SENT-011", tool.name, "record_id", WRONG_TYPE_MARKER),
        (tool,),
        manifest,
    )
    arguments, _ = _probe_arguments(binding, (tool,))
    assert not Draft202012Validator(tool.inputSchema).is_valid(arguments)


def test_malformed_mutation_preserves_valid_sibling_arguments() -> None:
    tool = _tool({"type": "string"})
    tool.inputSchema["properties"]["mode"] = {
        "type": "string",
        "enum": ["read"],
        "default": "read",
    }
    tool.inputSchema["required"].append("mode")
    arguments, _ = _probe_arguments(
        ProbeBinding("SENT-011", tool.name, "value", WRONG_TYPE_MARKER), (tool,)
    )
    errors = list(Draft202012Validator(tool.inputSchema).iter_errors(arguments))
    assert errors
    assert all(list(error.path) == ["value"] for error in errors)


@pytest.mark.parametrize("enforce_schema", [True, False], ids=["safe", "unsafe"])
def test_object_schema_distinguishes_safe_and_unsafe_processing(
    enforce_schema: bool,
) -> None:
    sandbox = SyntheticSandbox(_tool({"type": "object"}), enforce_schema=enforce_schema)
    result = _attempt(sandbox, "SENT-011", WRONG_TYPE_MARKER)
    assert result.vulnerable is (not enforce_schema)


@pytest.mark.parametrize(
    ("limit", "enforce_schema", "violation"),
    [(None, True, False), (4096, True, False), (4096, False, True)],
    ids=["legitimate-large-document", "enforced-size-limit", "ignored-size-limit"],
)
def test_large_input_needs_a_policy_breach(
    limit: int | None, enforce_schema: bool, violation: bool
) -> None:
    schema: dict[str, Any] = {"type": "string"}
    if limit is not None:
        schema["maxLength"] = limit
    sandbox = SyntheticSandbox(_tool(schema), enforce_schema=enforce_schema)
    result = _attempt(sandbox, "SENT-009", OVERSIZED_MARKER)
    assert result.vulnerable is violation


def test_successful_baseline_precedes_attack_in_a_separate_session() -> None:
    sandbox = SyntheticSandbox(_tool({"type": "string", "maxLength": 4096}))
    _attempt(sandbox, "SENT-009", OVERSIZED_MARKER)
    assert len(sandbox.calls) == 2
    baseline, attack = sandbox.calls
    assert baseline[0] != attack[0]
    validator = Draft202012Validator(sandbox.tool.inputSchema)
    assert validator.is_valid(baseline[2])
    assert not validator.is_valid(attack[2])


def test_failed_baseline_does_not_establish_a_violation() -> None:
    sandbox = SyntheticSandbox(
        _tool({"type": "string", "maxLength": 4096}),
        enforce_schema=False,
        baseline_error=True,
    )
    result = _attempt(sandbox, "SENT-009", OVERSIZED_MARKER)
    assert not result.vulnerable
    assert len(sandbox.calls) == 1
    assert Draft202012Validator(sandbox.tool.inputSchema).is_valid(sandbox.calls[0][2])


def test_timeout_alone_is_not_proof_and_independent_probes_continue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempted: list[str] = []

    async def timeout_one(
        sandbox: DockerSandbox,
        image: str,
        binding: ProbeBinding,
        manifest: PermissionsManifest,
        state: dict[str, bool],
    ) -> _Observation:
        attempted.append(binding.probe_id)
        state["initialized"] = True
        if binding.probe_id == "SENT-009":
            raise TimeoutError("synthetic call timeout; no process failure evidence")
        return _Observation(binding.probe_id, "process", "value", {}, {}, (), False)

    monkeypatch.setattr(prober, "_run_one", timeout_one)
    campaign, _ = prober.build_probe_campaign((), ToolCatalog(tools=(), warnings=()))
    results = asyncio.run(
        prober._run_campaign(
            cast(DockerSandbox, SyntheticSandbox(_tool({"type": "string"}))),
            "synthetic:no-target-code",
            campaign,
            PermissionsManifest.model_validate(
                {"version": 1, "tools": {"process": {}}}
            ),
        )
    )
    assert attempted == list(prober.DEFAULT_ORDER)
    assert not any(item.vulnerable for item in results)


@pytest.mark.parametrize("failure", ["unsupported", "inconclusive", "infrastructure"])
def test_campaign_preserves_completed_proof_and_stops_only_on_infrastructure(
    monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    attempted: list[str] = []

    async def run_one(
        sandbox: DockerSandbox,
        image: str,
        binding: ProbeBinding,
        manifest: PermissionsManifest,
        state: dict[str, Any],
    ) -> _Observation:
        attempted.append(binding.probe_id)
        observation = _Observation(
            binding.probe_id,
            "process",
            "value",
            {},
            {},
            (),
            binding.probe_id == "SENT-008",
        )
        if binding.probe_id == "SENT-009":
            if failure == "infrastructure":
                raise InfrastructureError("synthetic inspection or cleanup failure")
            observation.status = (
                "unsupported" if failure == "unsupported" else "inconclusive"
            )
        return observation

    monkeypatch.setattr(prober, "_run_one", run_one)
    campaign, _ = prober.build_probe_campaign((), ToolCatalog(tools=(), warnings=()))
    results = asyncio.run(
        prober._run_campaign(
            cast(DockerSandbox, SyntheticSandbox(_tool({"type": "string"}))),
            "synthetic:no-target-code",
            campaign,
            PermissionsManifest.model_validate(
                {"version": 1, "tools": {"process": {}}}
            ),
        )
    )
    assert len(results) == 4
    assert results[0].vulnerable
    if failure == "infrastructure":
        assert attempted == ["SENT-008", "SENT-009"]
        assert not results[1].execution_successful
        assert [item.status for item in results[2:]] == ["untested", "untested"]
    else:
        assert attempted == list(prober.DEFAULT_ORDER)
        assert all(item.execution_successful for item in results)


def test_jsonrpc_invalid_params_is_a_completed_rejection() -> None:
    async def rejected(name: str, arguments: dict[str, Any]) -> None:
        raise McpError(ErrorData(code=INVALID_PARAMS, message="invalid tool arguments"))

    async def call() -> dict[str, Any]:
        probe = SimpleNamespace(
            client=SimpleNamespace(call_tool=rejected),
            deadline=asyncio.get_running_loop().time() + 10,
            process_state=lambda: {
                "Running": True,
                "OOMKilled": False,
                "ExitCode": 0,
                "Error": "",
            },
        )
        return await prober._call(cast(ProbeSession, probe), "process", {})

    response = asyncio.run(call())
    assert response["is_error"] is True
    assert response["protocol_failure"] is False


def test_cleanup_failure_preserves_the_violation_already_observed() -> None:
    class CleanupFailure(SyntheticSandbox):
        @asynccontextmanager
        async def probe_session(
            self, image: str, probe_id: str, *, timeout: float = 10
        ) -> AsyncIterator[Any]:
            async with super().probe_session(image, probe_id, timeout=timeout) as probe:
                yield probe
            if self.sessions == 2:
                raise InfrastructureError("synthetic attack cleanup failure")

    result = _attempt(
        CleanupFailure(
            _tool({"type": "string", "maxLength": 4096}), enforce_schema=False
        ),
        "SENT-009",
        OVERSIZED_MARKER,
    )
    assert result.vulnerable
    assert not result.execution_successful
    finding = _finding_from_observation(result, uuid4(), NOW)
    assert finding.status is FindingStatus.CONFIRMED
    assert finding.evidence.model_dump()["proof"]["verdict"] == "violation_observed"


@pytest.mark.parametrize(
    "returncode", [0, 1, 125], ids=["present", "absent", "failure"]
)
def test_canary_inspection_failure_is_not_absence(
    loaded_config: LoadedConfiguration, returncode: int
) -> None:
    def runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, returncode, "", "")

    session = ProbeSession(
        cast(ClientSession, None),
        "synthetic-container",
        io.StringIO(),
        DockerSandbox(loaded_config, uuid4(), runner=runner),
    )
    if returncode == 125:
        with pytest.raises(InfrastructureError):
            session.canary_exists()
    else:
        assert session.canary_exists() is (returncode == 0)


@pytest.mark.parametrize(
    ("contaminated", "create_canary", "attack_error", "violation"),
    [
        (False, False, False, False),
        (True, False, False, False),
        (False, True, True, True),
    ],
    ids=["inert-input", "pre-existing-canary", "canary-then-error"],
)
def test_canary_requires_a_new_effect_independent_of_protocol_success(
    contaminated: bool, create_canary: bool, attack_error: bool, violation: bool
) -> None:
    sandbox = SyntheticSandbox(
        _tool({"type": "string"}),
        contaminated=contaminated,
        create_canary=create_canary,
        attack_error=attack_error,
    )
    assert _attempt(sandbox, "SENT-010", INJECTION_MARKER).vulnerable is violation


def _observed_canary() -> _Observation:
    return _Observation(
        "SENT-010",
        "process",
        "value",
        {"value": INJECTION_MARKER},
        {
            "canary_before": False,
            "baseline_canary_after": False,
            "canary_created": True,
        },
        (),
        True,
    )


def test_observed_proof_is_confirmed_before_model_review() -> None:
    finding = _finding_from_observation(_observed_canary(), uuid4(), NOW)
    assert finding.status is FindingStatus.CONFIRMED
    assert finding.confidence is Confidence.HIGH


@pytest.mark.parametrize("judgment", ["confirmed", "suppressed", "needs_review"])
def test_model_judgment_cannot_downgrade_observed_proof(
    tmp_path: Path, judgment: str
) -> None:
    class JudgmentTransport(FakeTransport):
        async def create(self, request: dict[str, Any]) -> dict[str, Any]:
            response = await super().create(request)
            content = response["output"][1]["content"][0]
            payload = json.loads(content["text"])
            for review in payload["reviews"]:
                review.update(status=judgment, confidence=0.2, probe_plan=None)
            content["text"] = json.dumps(payload)
            return response

    finding = _finding_from_observation(_observed_canary(), uuid4(), NOW)
    outcome = SemanticReviewer(
        root=ROOT,
        config=LlmConfig(retries=0),
        max_findings=500,
        mode="live",
        transport=JudgmentTransport(),
        cache=ReviewCache(enabled=False, root=tmp_path),
        now=lambda: NOW,
    ).review((finding,), allow_degraded=False)
    assert not outcome.fatal
    reviewed = outcome.findings[0]
    assert reviewed.review.status is not None
    assert reviewed.review.status.value == judgment
    assert reviewed.review.confidence == 0.2
    assert reviewed.review_disagrees is (judgment != "confirmed")
    assert outcome.summary.disagreement_count == (judgment != "confirmed")
    assert outcome.summary.confirmed_count == (judgment == "confirmed")
    assert outcome.summary.suppressed_count == (judgment == "suppressed")
    assert outcome.summary.needs_review_count == (judgment == "needs_review")
    assert reviewed.status is FindingStatus.CONFIRMED
    assert reviewed.confidence is Confidence.HIGH


def test_model_absence_cannot_downgrade_observed_proof() -> None:
    finding = _finding_from_observation(_observed_canary(), uuid4(), NOW)
    outcome = unavailable_review_outcome(
        (finding,),
        config=LlmConfig(),
        reason="OPENAI_API_KEY is required for GPT review",
        allow_degraded=True,
        applied_at=NOW,
    )
    assert outcome.findings[0].status is FindingStatus.CONFIRMED
    assert outcome.findings[0].review.mode == "degraded"
