"""Ordered campaign contracts; synthetic sessions do not prove runtime security."""

from __future__ import annotations

import asyncio
from collections import Counter
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any, cast

import pytest
from mcp.types import ListToolsResult, Tool

from sentinel.config import SandboxConfig
from sentinel.dynamic import prober
from sentinel.dynamic.sandbox import DependencyImage, DockerSandbox
from sentinel.errors import InfrastructureError
from sentinel.llm.tools import ToolCatalog
from sentinel.permissions import PermissionsManifest
from tests.test_dynamic_correctness import SyntheticSandbox, _tool

POLICY = PermissionsManifest.model_validate(
    {"version": 1, "tools": {"a_safe": {}, "z_vulnerable": {}}}
)


def tools() -> tuple[Tool, ...]:
    schema = {
        "type": "object",
        "properties": {"first": {"type": "string"}, "second": {"type": "string"}},
        "required": ["first", "second"],
        "additionalProperties": False,
    }
    return tuple(
        Tool(name=name, inputSchema=schema) for name in ("a_safe", "z_vulnerable")
    )


def test_enumeration_rounds_cover_later_tools_and_all_mutations() -> None:
    campaign, _ = prober.build_probe_campaign((), ToolCatalog(tools=(), warnings=()))
    attempts, complete = prober.enumerate_attempts(tools(), POLICY, campaign)
    assert complete
    assert len({item.attempt_id for item in attempts}) == len(attempts)
    assert Counter(item.target_tool for item in attempts)["z_vulnerable"] == 8
    actual = [
        item for item in attempts if item.target_tool != prober.OUT_OF_SCOPE_CANARY
    ]
    assert [item.target_tool for item in actual[:4]] == ["a_safe", "z_vulnerable"] * 2
    assert {item.argument_path for item in actual} == {("first",), ("second",)}
    assert {item.mutation for item in actual if item.probe_id == "SENT-011"} == {
        "wrong_type",
        "omit",
    }
    changed = tuple(
        tool.model_copy(
            update={"inputSchema": {**tool.inputSchema, "description": "drift"}}
        )
        for tool in tools()
    )
    assert [
        item.attempt_id
        for item in prober.enumerate_attempts(changed, POLICY, campaign)[0]
    ] == [item.attempt_id for item in attempts]
    assert prober.enumerate_attempts((), POLICY, campaign) == ((), True)


class CampaignSandbox(SyntheticSandbox):
    def __init__(
        self,
        *,
        limit: int = 24,
        discovery_delay: float = 0,
        empty: bool = False,
        failure: bool = False,
    ) -> None:
        super().__init__(_tool({"type": "string"}))
        self.configuration = SimpleNamespace(
            scanner=SimpleNamespace(
                sandbox=SandboxConfig(
                    max_probe_attempts=limit, campaign_timeout_seconds=1
                )
            )
        )
        self.discovery_delay = discovery_delay
        self.empty = empty
        self.failure = failure
        self.cleaned = 0

    @asynccontextmanager
    async def probe_session(
        self, image: str, probe_id: str, *, timeout: float = 10
    ) -> AsyncIterator[Any]:
        try:
            async with super().probe_session(
                image, probe_id, timeout=timeout
            ) as session:
                if self.sessions == 1:

                    async def listed() -> ListToolsResult:
                        await asyncio.sleep(self.discovery_delay)
                        return ListToolsResult(tools=[] if self.empty else [self.tool])

                    session.list_tools = listed
                elif self.failure:
                    raise InfrastructureError("startup failed")
                yield session
        finally:
            self.cleaned += 1


@pytest.mark.parametrize(
    "case", ["attempt_budget", "discovery_timeout", "empty", "startup"]
)
def test_campaign_budgets_and_honest_discovery(case: str) -> None:
    sandbox = CampaignSandbox(
        limit=1 if case == "attempt_budget" else 24,
        discovery_delay=1.1 if case == "discovery_timeout" else 0,
        empty=case == "empty",
        failure=case == "startup",
    )
    campaign, _ = prober.build_probe_campaign((), ToolCatalog(tools=(), warnings=()))
    observations = asyncio.run(
        prober._run_campaign(
            cast(DockerSandbox, sandbox),
            "synthetic",
            campaign,
            PermissionsManifest.model_validate(
                {"version": 1, "tools": {"process": {}}}
            ),
        )
    )
    assert sandbox.cleaned == sandbox.sessions
    if case in {"empty", "discovery_timeout"}:
        assert not observations
        assert not campaign.bindings
        assert campaign.enumeration_complete is (case == "empty")
    else:
        assert sum(item.started for item in observations) == 1
        assert len(observations) > 1
        assert all(item.status == "untested" for item in observations[1:])
        if case == "startup":
            assert not observations[0].execution_successful
        else:
            assert campaign.budget_exhausted


@pytest.mark.parametrize(
    "schema, supported",
    [
        ({"type": "object", "properties": {}, "additionalProperties": False}, True),
        ({"$schema": "https://example.invalid/dialect", "type": "object"}, False),
        ({"$ref": "https://example.invalid/schema"}, False),
        ({"type": "object", "properties": []}, False),
        ({"$ref": "#/$defs/missing"}, False),
        (
            {"type": "object", "properties": {"value": {"$ref": "#/$defs/missing"}}},
            False,
        ),
        (
            {
                "type": "object",
                "properties": {
                    "aaa": {"type": "string"},
                    "zzz": {"$ref": "#/$defs/missing"},
                },
            },
            False,
        ),
    ],
)
def test_unsupported_schema_cannot_establish_complete_campaign(
    monkeypatch: pytest.MonkeyPatch, schema: dict[str, Any], supported: bool
) -> None:
    async def run_one(
        sandbox: Any,
        image: str,
        binding: prober.ProbeBinding,
        manifest: Any,
        state: Any,
    ) -> prober._Observation:
        return prober._Observation(
            binding.probe_id,
            binding.target_tool or "",
            binding.field,
            {},
            {},
            (),
            False,
        )

    monkeypatch.setattr(prober, "_run_one", run_one)
    sandbox = CampaignSandbox()
    sandbox.tool = Tool(name="process", inputSchema=schema)
    campaign, _ = prober.build_probe_campaign((), ToolCatalog(tools=(), warnings=()))
    observed = asyncio.run(
        prober._run_campaign(
            cast(DockerSandbox, sandbox), "synthetic", campaign, POLICY
        )
    )
    assert observed and all(item.status == "tested" for item in observed)
    assert campaign.enumeration_complete is supported
    assert bool(campaign.failure) is not supported
    assert bool(campaign.discovery[0].tools[0].unresolved) is not supported
    assert sandbox.cleaned == sandbox.sessions
    result = prober.DynamicScanResult(
        (), (), DependencyImage("synthetic", "synthetic", True), campaign, observed
    )
    assert result.complete is supported
    assert result.summary.coverage is not None
    assert result.summary.coverage.campaign is not None
    assert result.summary.coverage.campaign.enumeration_complete is supported
    if "aaa" in schema.get("properties", {}):
        assert any(item.field == "aaa" for item in observed)


def test_nested_mutation_targets_only_the_selected_member() -> None:
    tool = Tool(
        name="nested",
        inputSchema={
            "type": "object",
            "properties": {
                "record": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "keep": {"type": "string"},
                    },
                    "required": ["url", "keep"],
                }
            },
            "required": ["record"],
        },
    )
    binding = prober.ProbeBinding(
        "SENT-011", "nested", "url", prober.OMIT_MARKER, path=("record", "url")
    )
    arguments, _ = prober._probe_arguments(
        binding, (tool,), {"record": {"url": "valid", "keep": "unchanged"}}
    )
    assert arguments == {"record": {"keep": "unchanged"}}


def test_repeated_mutations_retain_each_proof() -> None:
    from sentinel.dynamic.merge import merge_findings
    from sentinel.finding import runtime_evidence
    from tests.test_dynamic_reporting import _proof

    first = _proof(attempt_id="first", mutation="wrong_type")
    second = _proof(attempt_id="second", mutation="omit", request={})
    merged = merge_findings((), (first, second), ToolCatalog(tools=(), warnings=()))
    assert len(merged) == 1
    assert {item.attempt_id for item in runtime_evidence(merged[0])} == {
        "first",
        "second",
    }


def test_merged_dynamic_review_contains_all_attempt_proofs(tmp_path: Any) -> None:
    import json

    from sentinel.dynamic.merge import merge_findings
    from sentinel.llm.context import build_finding_context
    from tests.test_dynamic_reporting import _proof

    merged = merge_findings(
        (),
        (
            _proof(attempt_id="one", mutation="wrong_type"),
            _proof(attempt_id="two", mutation="omit", request={}),
        ),
        ToolCatalog(tools=(), warnings=()),
    )
    context = build_finding_context(tmp_path, merged[0])
    supplied = json.loads(context.blocks[0].text)
    assert isinstance(supplied, list) and len(supplied) == 2
    assert {item["attempt_id"] for item in supplied} == {"one", "two"}


def test_priorities_only_reorder_each_tools_choices() -> None:
    campaign = prober.ProbeCampaign(
        ("SENT-010", "SENT-011", "SENT-009", "SENT-008"),
        (
            prober.ProbeBinding(
                "SENT-010", "z_vulnerable", "second", prober.INJECTION_MARKER
            ),
        ),
        None,
        False,
    )
    reordered, _ = prober.enumerate_attempts(tools(), POLICY, campaign)
    ordinary, _ = prober.enumerate_attempts(
        tools(), POLICY, prober.ProbeCampaign(prober.DEFAULT_ORDER, (), None, True)
    )
    assert {item.attempt_id for item in reordered} == {
        item.attempt_id for item in ordinary
    }
    assert [item.target_tool for item in reordered[:2]] == ["a_safe", "z_vulnerable"]
    assert reordered[1].field == "second" and reordered[1].probe_id == "SENT-010"


@pytest.mark.parametrize("interruption", [asyncio.CancelledError, KeyboardInterrupt])
def test_interruption_preserves_earlier_proof_and_unstarted_remainder(
    monkeypatch: pytest.MonkeyPatch, interruption: type[BaseException]
) -> None:
    calls = 0

    async def run_one(
        sandbox: Any,
        image: str,
        binding: prober.ProbeBinding,
        manifest: Any,
        state: Any,
    ) -> prober._Observation:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise interruption()
        return prober._Observation(
            binding.probe_id, binding.target_tool or "", binding.field, {}, {}, (), True
        )

    monkeypatch.setattr(prober, "_run_one", run_one)
    sandbox = CampaignSandbox()
    campaign, _ = prober.build_probe_campaign((), ToolCatalog(tools=(), warnings=()))
    observed = asyncio.run(
        prober._run_campaign(
            cast(DockerSandbox, sandbox), "synthetic", campaign, POLICY
        )
    )
    assert observed[0].vulnerable
    assert sum(item.started for item in observed) == 2
    assert all(item.status == "untested" for item in observed[2:])
    assert sandbox.cleaned == sandbox.sessions


def test_discovery_schema_drift_prevents_baseline_call() -> None:
    sandbox = CampaignSandbox()
    binding = prober.ProbeBinding(
        "SENT-010",
        sandbox.tool.name,
        "value",
        prober.INJECTION_MARKER,
        schema_sha256="a" * 64,
    )
    observation = asyncio.run(
        prober._run_one(cast(DockerSandbox, sandbox), "synthetic", binding, POLICY, {})
    )
    assert observation.status == "inconclusive"
    assert "changed after" in observation.reason
    assert not sandbox.calls


def test_out_of_scope_attempt_cannot_target_a_granted_tool() -> None:
    sandbox = CampaignSandbox()
    policy = PermissionsManifest.model_validate(
        {"version": 1, "tools": {"process": {}}}
    )
    binding = prober.ProbeBinding("SENT-008", "process", None, None)
    observation = asyncio.run(
        prober._run_one(cast(DockerSandbox, sandbox), "synthetic", binding, policy, {})
    )
    assert observation.status == "unsupported" and not observation.vulnerable
    assert not sandbox.calls
