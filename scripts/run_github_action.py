"""Run Sentinel for the composite GitHub Action without changing CLI contracts."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from sentinel.errors import InfrastructureError
from sentinel.report.validate_sarif import validate_sarif_data

_SEVERITY_RANK = {
    "informational": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}
_EXPECTED_SCAN_EXITS = frozenset({0, 1, 2, 3})


class ActionUsageError(ValueError):
    """Invalid composite Action input or GitHub event state."""


@dataclass(frozen=True)
class ActionInputs:
    target_path: str
    fail_on: str
    static_only: str


@dataclass(frozen=True)
class SarifMetrics:
    findings_count: int
    highest_severity: str
    analysis_complete: bool
    review: dict[str, Any] | None


@dataclass(frozen=True)
class ActionResult:
    effective_exit_code: int
    sarif_path: Path
    checkout_path: Path
    category: str
    fork_pull_request: bool
    upload_ready: bool
    metrics: SarifMetrics
    message: str | None = None


def execute_action(
    inputs: ActionInputs,
    environ: Mapping[str, str],
    *,
    command_runner: Any = subprocess.run,
) -> ActionResult:
    """Execute one CLI scan and reduce its SARIF into Action-safe metadata."""

    workspace = _required_directory(environ, "GITHUB_WORKSPACE")
    runner_temp = _required_directory(environ, "RUNNER_TEMP")
    report_path = _report_path(runner_temp, environ)
    empty = SarifMetrics(0, "none", False, None)

    try:
        target, relative_target = resolve_target(workspace, inputs.target_path)
        fail_on = _fail_on(inputs.fail_on)
        static_only = _boolean(inputs.static_only, "static-only")
        fork = is_fork_pull_request(environ)
    except ActionUsageError as error:
        return ActionResult(
            effective_exit_code=2,
            sarif_path=report_path,
            checkout_path=workspace,
            category="mcp-sentinel/invalid-target",
            fork_pull_request=False,
            upload_ready=False,
            metrics=empty,
            message=str(error),
        )

    category = sarif_category(relative_target)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.unlink(missing_ok=True)
    command = [
        sys.executable,
        "-m",
        "sentinel",
        "scan",
        str(target),
        "--format",
        "sarif",
        "--output",
        str(report_path),
        "--fail-on",
        fail_on,
    ]
    if static_only:
        command.append("--static-only")
    if fork:
        command.append("--allow-degraded")

    scan_environment = dict(environ)
    scan_environment.pop("OPENAI_API_KEY", None)
    action_key = scan_environment.pop("SENTINEL_ACTION_OPENAI_API_KEY", "")
    if action_key and not fork:
        scan_environment["OPENAI_API_KEY"] = action_key

    completed = command_runner(command, env=scan_environment, check=False)
    raw_exit = int(completed.returncode)
    scan_exit = raw_exit if raw_exit in _EXPECTED_SCAN_EXITS else 3
    message = (
        None
        if raw_exit in _EXPECTED_SCAN_EXITS
        else f"Sentinel returned unexpected exit code {raw_exit}"
    )

    if not report_path.is_file():
        return ActionResult(
            effective_exit_code=3 if scan_exit != 2 else 2,
            sarif_path=report_path,
            checkout_path=target,
            category=category,
            fork_pull_request=fork,
            upload_ready=False,
            metrics=empty,
            message=message or "Sentinel did not produce a SARIF report",
        )

    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        metrics = analyze_sarif(payload)
    except (
        OSError,
        json.JSONDecodeError,
        InfrastructureError,
        ActionUsageError,
    ) as error:
        return ActionResult(
            effective_exit_code=3,
            sarif_path=report_path,
            checkout_path=target,
            category=category,
            fork_pull_request=fork,
            upload_ready=False,
            metrics=empty,
            message=f"SARIF validation failed: {error}",
        )

    upload_ready = scan_exit in {0, 1, 3} and not fork
    return ActionResult(
        effective_exit_code=scan_exit,
        sarif_path=report_path,
        checkout_path=target,
        category=category,
        fork_pull_request=fork,
        upload_ready=upload_ready,
        metrics=metrics,
        message=message,
    )


def resolve_target(workspace: Path, value: str) -> tuple[Path, Path]:
    """Resolve a relative Action target without allowing workspace escape."""

    if not value or any(ord(character) < 32 for character in value):
        raise ActionUsageError("target-path must be a non-empty printable path")
    candidate = Path(value)
    if candidate.is_absolute():
        raise ActionUsageError("target-path must be relative to GITHUB_WORKSPACE")
    try:
        resolved = (workspace / candidate).resolve(strict=True)
    except OSError as error:
        raise ActionUsageError(f"target-path does not exist: {value}") from error
    try:
        relative = resolved.relative_to(workspace)
    except ValueError as error:
        raise ActionUsageError("target-path escapes GITHUB_WORKSPACE") from error
    if not resolved.is_dir():
        raise ActionUsageError("target-path must identify a directory")
    return resolved, relative


def is_fork_pull_request(environ: Mapping[str, str]) -> bool:
    """Return whether the current pull_request event originates from a fork."""

    if environ.get("GITHUB_EVENT_NAME") != "pull_request":
        return False
    event_path = environ.get("GITHUB_EVENT_PATH")
    repository = environ.get("GITHUB_REPOSITORY")
    if not event_path or not repository:
        raise ActionUsageError("pull_request event metadata is incomplete")
    try:
        payload = json.loads(Path(event_path).read_text(encoding="utf-8"))
        head_repository = payload["pull_request"]["head"]["repo"]["full_name"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise ActionUsageError("cannot determine pull_request fork status") from error
    if not isinstance(head_repository, str) or not head_repository:
        raise ActionUsageError("pull_request head repository is invalid")
    return head_repository != repository


def sarif_category(relative_target: Path) -> str:
    normalized = relative_target.as_posix()
    suffix = "root" if normalized in {"", "."} else quote(normalized, safe="/._-")
    return f"mcp-sentinel/{suffix}"


def analyze_sarif(payload: Any) -> SarifMetrics:
    """Validate SARIF and compute the public Action outputs from the same report."""

    validate_sarif_data(payload)
    try:
        run = payload["runs"][0]
        results = run.get("results", [])
        invocation_properties = run["invocations"][0]["properties"]
        declared_count = invocation_properties["findingCount"]
        analysis_complete = invocation_properties["analysisComplete"]
        driver_properties = run["tool"]["driver"].get("properties", {})
        review = driver_properties.get("gptReview")
    except (KeyError, IndexError, TypeError) as error:
        raise ActionUsageError("SARIF lacks Sentinel summary properties") from error
    if not isinstance(results, list) or not isinstance(declared_count, int):
        raise ActionUsageError("SARIF finding count is invalid")
    if declared_count != len(results):
        raise ActionUsageError("SARIF finding count does not match its results")
    if not isinstance(analysis_complete, bool):
        raise ActionUsageError("SARIF analysis state is invalid")
    if review is not None and not isinstance(review, dict):
        raise ActionUsageError("SARIF GPT review summary is invalid")

    severities: list[str] = []
    for result in results:
        if not isinstance(result, dict):
            raise ActionUsageError("SARIF result is invalid")
        properties = result.get("properties", {})
        if not isinstance(properties, dict):
            raise ActionUsageError("SARIF result properties are invalid")
        if properties.get("status") == "suppressed":
            continue
        raw_severity = properties.get("severity")
        if not isinstance(raw_severity, str):
            raise ActionUsageError("SARIF result severity is missing")
        severity = raw_severity.lower()
        if severity not in _SEVERITY_RANK:
            raise ActionUsageError(f"SARIF result severity is invalid: {raw_severity}")
        severities.append(severity)
    highest = max(severities, key=_SEVERITY_RANK.__getitem__) if severities else "none"
    return SarifMetrics(declared_count, highest, analysis_complete, review)


def render_step_summary(result: ActionResult) -> str:
    """Render aggregate telemetry only; never include finding source content."""

    review = result.metrics.review or {}
    candidate_count = _integer(review.get("candidate_count"))
    reviewed_count = _integer(review.get("reviewed_count"))
    skipped_count = max(0, candidate_count - reviewed_count)
    overflow_count = _integer(review.get("overflow_count"))
    batches = review.get("batches", [])
    returned_model_set: set[str] = set()
    if isinstance(batches, list):
        for item in batches:
            if not isinstance(item, dict):
                continue
            returned_model = item.get("returned_model")
            if isinstance(returned_model, str):
                returned_model_set.add(returned_model)
    returned_models = sorted(returned_model_set)
    current_usage = review.get("current_usage", {})
    if not isinstance(current_usage, dict):
        current_usage = {}
    cache_fields = ("cache_hits", "cache_misses", "cache_writes", "cache_errors")

    lines = [
        "## MCP Sentinel",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Analysis complete | {_yes_no(result.metrics.analysis_complete)} |",
        f"| Effective exit code | {result.effective_exit_code} |",
        f"| Findings | {result.metrics.findings_count} |",
        f"| Highest fail-eligible severity | {result.metrics.highest_severity} |",
        f"| SARIF category | `{_markdown(result.category)}` |",
        f"| Fork pull request | {_yes_no(result.fork_pull_request)} |",
        f"| Code-scanning upload eligible | {_yes_no(result.upload_ready)} |",
        "",
        "### GPT review",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Mode | {_markdown(str(review.get('mode', 'none')))} |",
        "| Requested model | "
        f"{_markdown(str(review.get('requested_model', 'none')))} |",
        f"| Returned model(s) | {_markdown(', '.join(returned_models) or 'none')} |",
        f"| Reviewed / skipped | {reviewed_count} / {skipped_count} |",
        f"| Truncated | {_yes_no(overflow_count > 0)} ({overflow_count} overflow) |",
        "| Cache hits / misses / writes / errors | "
        + " / ".join(str(_integer(review.get(name))) for name in cache_fields)
        + " |",
        "| Current tokens (input / output / reasoning / cached / total) | "
        + " / ".join(
            str(_integer(current_usage.get(name)))
            for name in (
                "input_tokens",
                "output_tokens",
                "reasoning_tokens",
                "cached_tokens",
                "total_tokens",
            )
        )
        + " |",
    ]
    if result.fork_pull_request:
        lines.extend(
            (
                "",
                "> Fork pull request: GPT credentials were withheld, degraded "
                "review was enabled, and code-scanning upload was skipped.",
            )
        )
    if result.message:
        lines.extend(("", f"> {_markdown(result.message)}"))
    return "\n".join(lines) + "\n"


def emit_action_state(result: ActionResult, environ: Mapping[str, str]) -> None:
    output_path = environ.get("GITHUB_OUTPUT")
    summary_path = environ.get("GITHUB_STEP_SUMMARY")
    if not output_path or not summary_path:
        raise RuntimeError("GitHub output paths are unavailable")
    outputs = {
        "sarif-path": str(result.sarif_path),
        "checkout-path": str(result.checkout_path),
        "findings-count": str(result.metrics.findings_count),
        "highest-severity": result.metrics.highest_severity,
        "effective-exit-code": str(result.effective_exit_code),
        "upload-ready": str(result.upload_ready).lower(),
        "category": result.category,
        "fork-pull-request": str(result.fork_pull_request).lower(),
    }
    with Path(output_path).open("a", encoding="utf-8") as handle:
        for name, value in outputs.items():
            if "\n" in value or "\r" in value:
                raise RuntimeError(f"unsafe GitHub output value for {name}")
            handle.write(f"{name}={value}\n")
    with Path(summary_path).open("a", encoding="utf-8") as handle:
        handle.write(render_step_summary(result))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-path", default=".")
    parser.add_argument("--fail-on", default="high")
    parser.add_argument("--static-only", default="false")
    args = parser.parse_args(argv)
    environ = dict(os.environ)
    try:
        result = execute_action(
            ActionInputs(args.target_path, args.fail_on, args.static_only), environ
        )
        emit_action_state(result, environ)
    except Exception as error:  # final infrastructure boundary for the Action helper
        print(f"error: GitHub Action helper failed: {error}", file=sys.stderr)
        return 3
    if result.message:
        print(f"warning: {result.message}", file=sys.stderr)
    return 0


def _required_directory(environ: Mapping[str, str], name: str) -> Path:
    raw = environ.get(name)
    if not raw:
        raise RuntimeError(f"{name} is unavailable")
    path = Path(raw).resolve(strict=True)
    if not path.is_dir():
        raise RuntimeError(f"{name} is not a directory")
    return path


def _report_path(runner_temp: Path, environ: Mapping[str, str]) -> Path:
    identity = "-".join(
        environ.get(name, "local")
        for name in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_ACTION")
    )
    safe_identity = re.sub(r"[^A-Za-z0-9_.-]", "-", identity)
    return runner_temp / "mcp-sentinel" / f"results-{safe_identity}.sarif"


def _fail_on(value: str) -> str:
    normalized = value.lower()
    if normalized not in _SEVERITY_RANK:
        raise ActionUsageError(f"invalid fail-on value: {value}")
    return normalized


def _boolean(value: str, name: str) -> bool:
    normalized = value.lower()
    if normalized not in {"true", "false"}:
        raise ActionUsageError(f"{name} must be true or false")
    return normalized == "true"


def _integer(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


if __name__ == "__main__":
    raise SystemExit(main())
