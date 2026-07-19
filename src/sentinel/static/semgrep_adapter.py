"""Pinned Semgrep CLI adapter for generic static pattern rules."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import certifi

from sentinel.errors import InfrastructureError
from sentinel.finding import SourceRange
from sentinel.static.model import StaticFileSet, StaticMatch

SEMGREP_VERSION = "1.170.0"
SEMGREP_BATCH_SIZE = 200
SEMGREP_TIMEOUT_SECONDS = 10


def run_semgrep(
    files: StaticFileSet,
    selected_rule_ids: tuple[str, ...],
    scan_root: Path,
    *,
    deadline: float,
) -> dict[str, list[StaticMatch]]:
    """Run selected bundled Semgrep rules over deterministic file batches."""

    rule_ids = tuple(
        rule_id for rule_id in selected_rule_ids if rule_id in {"SENT-002", "SENT-005"}
    )
    results: dict[str, list[StaticMatch]] = {rule_id: [] for rule_id in rule_ids}
    if not rule_ids:
        return results
    _verify_semgrep_version()
    executable = shutil.which("semgrep")
    sibling = Path(sys.executable).with_name("semgrep")
    if executable is None and sibling.is_file():
        executable = str(sibling)
    if executable is None:
        raise InfrastructureError("Semgrep executable is not available")

    paths = sorted(
        (
            *(item.path for item in files.python_files),
            *files.config_files,
        ),
        key=lambda path: path.as_posix(),
    )
    if not paths:
        return results
    configs = [
        Path(__file__).parent / "semgrep" / f"{rule_id.lower().replace('-', '')}.yaml"
        for rule_id in rule_ids
    ]
    environment = os.environ.copy()
    environment.update(
        {
            "SEMGREP_SEND_METRICS": "off",
            "SEMGREP_ENABLE_VERSION_CHECK": "0",
            "SEMGREP_LOG_FILE": os.devnull,
            "SEMGREP_SETTINGS_FILE": os.devnull,
            "SSL_CERT_FILE": certifi.where(),
        }
    )
    for index in range(0, len(paths), SEMGREP_BATCH_SIZE):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise InfrastructureError("static analysis exceeded its 120-second timeout")
        batch = paths[index : index + SEMGREP_BATCH_SIZE]
        with tempfile.TemporaryDirectory(prefix="sentinel-semgrep-") as directory:
            output = Path(directory) / "results.json"
            command = [
                executable,
                "scan",
                "--json",
                "--output",
                str(output),
                "--jobs",
                "1",
                "--timeout",
                str(SEMGREP_TIMEOUT_SECONDS),
                "--metrics",
                "off",
                "--disable-version-check",
                "--disable-nosem",
            ]
            for config in configs:
                command.extend(("--config", str(config)))
            command.extend(str(path) for path in batch)
            try:
                completed = subprocess.run(
                    command,
                    check=False,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=min(SEMGREP_TIMEOUT_SECONDS, remaining),
                    env=environment,
                )
            except (OSError, subprocess.TimeoutExpired) as error:
                raise InfrastructureError(
                    f"Semgrep execution failed: {error}"
                ) from error
            if completed.returncode not in {0, 1}:
                detail = completed.stderr.strip() or "unknown Semgrep failure"
                raise InfrastructureError(f"Semgrep execution failed: {detail}")
            if not output.is_file():
                detail = completed.stderr.strip() or "Semgrep wrote no JSON report"
                raise InfrastructureError(f"Semgrep execution failed: {detail}")
            payload = _parse_payload(output.read_text(encoding="utf-8"))
        _collect_results(payload, results, files, scan_root)
    return results


def _verify_semgrep_version() -> None:
    try:
        installed = version("semgrep")
    except PackageNotFoundError as error:
        raise InfrastructureError("Semgrep 1.170.0 is not installed") from error
    if installed != SEMGREP_VERSION:
        raise InfrastructureError(
            f"Semgrep version mismatch: expected {SEMGREP_VERSION}, found {installed}"
        )


def _parse_payload(raw: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise InfrastructureError("Semgrep returned invalid JSON") from error
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise InfrastructureError("Semgrep returned an unexpected JSON shape")
    if payload.get("errors"):
        raise InfrastructureError(f"Semgrep reported scan errors: {payload['errors']}")
    return payload


def _collect_results(
    payload: dict[str, Any],
    results: dict[str, list[StaticMatch]],
    files: StaticFileSet,
    scan_root: Path,
) -> None:
    for item in payload["results"]:
        if not isinstance(item, dict):
            raise InfrastructureError("Semgrep result entry is not an object")
        extra = item.get("extra", {})
        metadata = extra.get("metadata", {}) if isinstance(extra, dict) else {}
        rule_id = metadata.get("sentinel_rule_id")
        if rule_id not in results:
            continue
        raw_path = Path(str(item.get("path", ""))).resolve()
        relative = _relative_path(raw_path, files, scan_root)
        start = item.get("start", {})
        end = item.get("end", {})
        try:
            source_range = SourceRange(
                start_line=int(start["line"]),
                start_column=int(start["col"]),
                end_line=int(end["line"]),
                end_column=max(int(end["col"]), int(start["col"]) + 1),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise InfrastructureError(
                "Semgrep returned an invalid source range"
            ) from error
        snippet = str(extra.get("lines", ""))
        results[rule_id].append(
            StaticMatch(
                rule_id=rule_id,
                path=relative,
                range=source_range,
                snippet=snippet,
                match_kinds=(str(item.get("check_id", "semgrep")),),
            )
        )


def _relative_path(
    path: Path,
    files: StaticFileSet,
    scan_root: Path,
) -> str:
    for python_file in files.python_files:
        if python_file.path == path:
            return python_file.relative_path
    for config_file in files.config_files:
        if config_file == path:
            return path.relative_to(scan_root).as_posix()
    raise InfrastructureError(f"Semgrep returned an out-of-scope path: {path}")
