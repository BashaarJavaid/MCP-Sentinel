"""Opt-in real Docker gate: no target code runs on the host, no model calls."""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

import pytest
import yaml

from sentinel.config import load_configuration
from sentinel.dynamic.prober import (
    DEFAULT_ORDER,
    INJECTION_MARKER,
    OVERSIZED_MARKER,
    WRONG_TYPE_MARKER,
    ProbeBinding,
    ProbeCampaign,
    _run_campaign,
    _run_one,
)
from sentinel.dynamic.sandbox import SCAN_LABEL, DependencyImage, DockerSandbox
from sentinel.errors import InfrastructureError
from sentinel.permissions import PermissionsManifest, load_permissions_manifest

pytestmark = [
    pytest.mark.docker,
    pytest.mark.skipif(
        os.environ.get("SENTINEL_RUN_DOCKER_TESTS") != "1",
        reason="select with SENTINEL_RUN_DOCKER_TESTS=1",
    ),
]
FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def dependency_image() -> DependencyImage:
    sandbox = DockerSandbox(
        load_configuration(FIXTURES / "vulnerable_server", environ={}), uuid4()
    )
    sandbox.preflight()  # Selected Docker gates fail, never skip, on unavailability.
    return sandbox.prepare_dependency_image()


def _sandbox(tmp_path: Path, case: str) -> DockerSandbox:
    root = tmp_path / "control"
    root.mkdir()
    shutil.copyfile(FIXTURES / "dynamic_controls" / "server.py", root / "server.py")
    shutil.copyfile(
        FIXTURES / "vulnerable_server" / "requirements.txt", root / "requirements.txt"
    )
    target = yaml.safe_load(
        (FIXTURES / "vulnerable_server" / "sentinel.target.yaml").read_text()
    )
    target.update(env={"CONTROL_CASE": case}, probe_baselines={})
    (root / "sentinel.target.yaml").write_text(yaml.safe_dump(target))
    (root / "sentinel.permissions.yaml").write_text(
        "version: 1\ntools: {process: {}}\n"
    )
    return DockerSandbox(load_configuration(root, environ={}), uuid4())


def _assert_clean(sandbox: DockerSandbox) -> None:
    result = sandbox.docker(
        (
            "ps",
            "--all",
            "--filter",
            f"label={SCAN_LABEL}={sandbox.scan_id}",
            "--format",
            "{{.Names}}",
        )
    )
    assert result.stdout.strip() == ""


@pytest.mark.parametrize(
    ("case", "probe_id", "status", "violation"),
    [
        ("object_safe", "SENT-011", "tested", False),
        ("object_unsafe", "SENT-011", "tested", True),
        ("large_document", "SENT-009", "tested", False),
        ("size_safe", "SENT-009", "tested", False),
        ("size_unsafe", "SENT-009", "tested", True),
        ("array_limit", "SENT-009", "tested", True),
        ("object_limit", "SENT-009", "tested", True),
        ("crash", "SENT-009", "tested", True),
        ("oom", "SENT-009", "tested", True),
        ("failing_baseline", "SENT-009", "inconclusive", False),
        ("slow_baseline", "SENT-009", "inconclusive", False),
        ("missing_prerequisite", "SENT-010", "inconclusive", False),
        ("timeout_attack", "SENT-009", "inconclusive", False),
        ("grant_safe", "SENT-008", "tested", False),
        ("grant_unsafe", "SENT-008", "tested", True),
        ("unknown_rejection", "SENT-008", "tested", False),
        ("unknown_success", "SENT-008", "inconclusive", False),
        ("inert_injection", "SENT-010", "tested", False),
        ("preexisting_canary", "SENT-010", "inconclusive", False),
        ("baseline_canary", "SENT-010", "inconclusive", False),
        ("canary", "SENT-010", "tested", True),
        ("canary_error", "SENT-010", "tested", True),
        ("unsupported_schema", "SENT-011", "unsupported", False),
    ],
)
def test_independent_docker_controls(
    tmp_path: Path,
    dependency_image: DependencyImage,
    case: str,
    probe_id: str,
    status: str,
    violation: bool,
) -> None:
    sandbox = _sandbox(tmp_path, case)
    marker = {
        "SENT-008": None,
        "SENT-009": OVERSIZED_MARKER,
        "SENT-010": INJECTION_MARKER,
        "SENT-011": WRONG_TYPE_MARKER,
    }[probe_id]
    try:
        result = asyncio.run(
            _run_one(
                sandbox,
                dependency_image.reference,
                ProbeBinding(probe_id, "process", "value", marker),
                PermissionsManifest.model_validate(
                    {"version": 1, "tools": {"process": {}}}
                ),
                {},
            )
        )
        print(
            json.dumps(
                {"case": case, "outcome": asdict(result)},
                sort_keys=True,
                default=lambda value: value.model_dump(mode="json"),
            )
        )
        assert result.status == status, result
        assert result.vulnerable is violation, (result.response, result.effects)
        assert (
            result.verdict is None if status != "tested" else result.verdict is not None
        )
        if case in {"oom", "crash"}:
            assert result.effects["resource_failure"] is True
            process_state = result.response["process_state"]
            assert isinstance(process_state, dict)
            assert process_state["Running"] is False
            assert process_state["OOMKilled"] is (case == "oom")
        if case == "canary_error":
            assert result.response["is_error"] is True
            assert result.effects["canary_after"] is True
        if case in {"slow_baseline", "timeout_attack"}:
            stage = "baseline_ms" if case == "slow_baseline" else "attack_ms"
            # Allow bounded Docker-command overhead, not the SDK's two shutdown waits.
            assert result.timings[stage] < 12_500
        if status == "tested":
            assert result.baseline_attempted and result.attack_attempted
            assert [item.role for item in result.discovery] == ["baseline", "attack"]
            assert result.baseline["response"]["is_error"] is False
            assert set(result.timings) == {"baseline_ms", "attack_ms"}
    finally:
        _assert_clean(sandbox)


@pytest.mark.parametrize(
    "fixture,calculator,violation",
    [
        ("vulnerable_server", "unsafe_calculator", True),
        ("clean_server", "safe_calculator", False),
    ],
)
def test_reference_campaigns(
    fixture: str, calculator: str, violation: bool, dependency_image: DependencyImage
) -> None:
    root = FIXTURES / fixture
    sandbox = DockerSandbox(load_configuration(root, environ={}), uuid4())
    manifest = load_permissions_manifest(root, required=True)
    assert manifest is not None
    campaign = ProbeCampaign(
        DEFAULT_ORDER,
        {
            "SENT-008": ProbeBinding("SENT-008", None, None, None),
            "SENT-009": ProbeBinding(
                "SENT-009", calculator, "expression", OVERSIZED_MARKER
            ),
            "SENT-010": ProbeBinding(
                "SENT-010", calculator, "expression", INJECTION_MARKER
            ),
            "SENT-011": ProbeBinding(
                "SENT-011", calculator, "expression", WRONG_TYPE_MARKER
            ),
        },
        None,
        True,
    )
    try:
        results = asyncio.run(
            _run_campaign(sandbox, dependency_image.reference, campaign, manifest)
        )
        print(
            json.dumps(
                {"case": fixture, "outcomes": [asdict(item) for item in results]},
                sort_keys=True,
                default=lambda value: value.model_dump(mode="json"),
            )
        )
        assert len(results) == 4
        assert all(item.status == "tested" for item in results), results
        assert all(item.vulnerable is violation for item in results), results
    finally:
        _assert_clean(sandbox)


@pytest.mark.parametrize("case", ["startup_crash", "startup_slow"])
def test_startup_failure_stops_campaign_and_cleans(
    tmp_path: Path, dependency_image: DependencyImage, case: str
) -> None:
    sandbox = _sandbox(tmp_path, case)
    campaign = ProbeCampaign(
        DEFAULT_ORDER,
        {rule: ProbeBinding(rule, None, None, None) for rule in DEFAULT_ORDER},
        None,
        True,
    )
    manifest = PermissionsManifest.model_validate(
        {"version": 1, "tools": {"process": {}}}
    )
    try:
        results = asyncio.run(
            _run_campaign(sandbox, dependency_image.reference, campaign, manifest)
        )
        assert not results[0].execution_successful
        assert [item.status for item in results[1:]] == ["untested"] * 3
    finally:
        _assert_clean(sandbox)


@pytest.mark.parametrize(
    "interrupt", [False, True], ids=["caller-failure", "cancellation"]
)
def test_session_cleanup_after_interruption(
    tmp_path: Path, dependency_image: DependencyImage, interrupt: bool
) -> None:
    sandbox = _sandbox(tmp_path, "large_document")

    async def interrupted() -> None:
        async with sandbox.probe_session(
            dependency_image.reference, "SENT-009"
        ) as probe:
            assert probe.process_state()["Running"]
            if interrupt:
                raise asyncio.CancelledError()
            raise InfrastructureError("synthetic caller failure")

    try:
        with pytest.raises(
            asyncio.CancelledError if interrupt else InfrastructureError
        ):
            asyncio.run(interrupted())
    finally:
        _assert_clean(sandbox)


@pytest.mark.parametrize("failure", ["inspection", "canary-inspection", "cleanup"])
def test_infrastructure_failure_retains_proof_and_stops_independent_work(
    tmp_path: Path, dependency_image: DependencyImage, failure: str
) -> None:
    sandbox = _sandbox(tmp_path, "grant_unsafe")
    real_runner = sandbox.runner

    def runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        if (
            failure == "inspection"
            and command[1] == "inspect"
            and command[-1].endswith("-009")
        ):
            return subprocess.CompletedProcess(
                command, 125, "", "synthetic inspect failure"
            )
        if failure == "canary-inspection" and command[1] == "exec":
            return subprocess.CompletedProcess(
                command, 125, "", "synthetic canary inspect failure"
            )
        result = real_runner(command)
        if (
            failure == "cleanup"
            and command[1:3] == ("rm", "--force")
            and command[-1].endswith("-009")
        ):
            # Actually clean the test-owned resource, then exercise error propagation.
            return subprocess.CompletedProcess(
                command, 1, "", "synthetic cleanup failure"
            )
        return result

    sandbox.runner = runner
    campaign = ProbeCampaign(
        DEFAULT_ORDER,
        {rule: ProbeBinding(rule, None, None, None) for rule in DEFAULT_ORDER},
        None,
        True,
    )
    manifest = PermissionsManifest.model_validate(
        {"version": 1, "tools": {"process": {}}}
    )
    try:
        results = asyncio.run(
            _run_campaign(sandbox, dependency_image.reference, campaign, manifest)
        )
        print(
            json.dumps(
                {"case": failure, "outcomes": [asdict(item) for item in results]},
                sort_keys=True,
                default=lambda value: value.model_dump(mode="json"),
            )
        )
        assert results[0].vulnerable
        index = 2 if failure == "canary-inspection" else 1
        assert not results[index].execution_successful
        assert all(item.status == "untested" for item in results[index + 1 :])
    finally:
        _assert_clean(sandbox)


def test_multitool_discovery_records_unprobed_fields(
    tmp_path: Path,
    dependency_image: DependencyImage,
) -> None:
    sandbox = _sandbox(tmp_path, "multi_tool")
    try:
        result = asyncio.run(
            _run_one(
                sandbox,
                dependency_image.reference,
                ProbeBinding("SENT-011", "process", "value", WRONG_TYPE_MARKER),
                PermissionsManifest.model_validate(
                    {"version": 1, "tools": {"process": {}}}
                ),
                {},
            )
        )
        assert result.status == "tested"
        assert result.baseline_attempted and result.attack_attempted
        assert result.target_tool == "process" and result.argument_path == ("value",)
        assert len(result.discovery) == 2
        for snapshot in result.discovery:
            assert snapshot.tool_total == 2 and snapshot.more_pages is False
            assert snapshot.tools[1].name == "unprobed"
            assert snapshot.tools[1].field_paths == (("nested",), ("nested", "field"))
        print(
            json.dumps(
                {"phase19_multi_tool": asdict(result)},
                sort_keys=True,
                default=lambda value: value.model_dump(mode="json"),
            )
        )
    finally:
        _assert_clean(sandbox)
