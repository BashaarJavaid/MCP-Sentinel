"""Frozen-corpus measurements through the production scanner and review batches."""

from __future__ import annotations

import importlib.metadata
import json
import os
import subprocess
import tempfile
import time
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch
from uuid import uuid4

import certifi

from scripts.capture_gpt_reviews import _atomic_json
from scripts.phase20_corpus import (
    CORPUS,
    ROOT,
    Manifest,
    digest,
    materialize,
    tree_digest,
)
from scripts.phase22_corpus import Manifest as Phase22Manifest
from scripts.phase22_corpus import frozen as frozen_phase22
from sentinel.config import LlmConfig, load_configuration
from sentinel.dynamic.prober import run_dynamic_scan
from sentinel.errors import InfrastructureError, TargetError
from sentinel.finding import Finding
from sentinel.llm.semantic_reviewer import SemanticReviewer, _Batch, _BatchResult
from sentinel.orchestrator import run_scan
from sentinel.report.json_report import render_json
from sentinel.report.model import (
    DynamicAnalysisSummary,
    ReportWarning,
    ScanContext,
    ScanTarget,
)
from sentinel.report.sarif import render_sarif
from sentinel.report.validate_json import validate_report_data
from sentinel.report.validate_sarif import validate_sarif_data

ARTIFACTS = ROOT / "artifacts/phase20"
LLM = LlmConfig(retries=0, max_concurrency=1, cache_enabled=False)


def frozen() -> dict[str, Any]:
    record: dict[str, Any] = json.loads((ARTIFACTS / "freeze.json").read_text())
    for key, path in (
        ("manifest_sha256", CORPUS / "manifest.yaml"),
        ("packet_sha256", ARTIFACTS / "checkpoint1-packet.md"),
        ("independent_review_sha256", ARTIFACTS / "checkpoint1-independent-review.md"),
    ):
        if record[key] != digest(path.read_bytes()):
            raise ValueError(f"frozen evidence drift: {key}")
    if record["checkpoint"] != 1 or not record["user_response"]:
        raise ValueError("Checkpoint 1 approval missing")
    return record


def scanner_identity() -> dict[str, Any]:
    return {
        "revision": subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        "source_sha256": tree_digest(
            {
                p.relative_to(ROOT).as_posix(): p.read_bytes()
                for p in (ROOT / "src/sentinel").rglob("*")
                if p.is_file() and "__pycache__" not in p.parts
            }
        ),
        "harness_sha256": tree_digest(
            {p.name: p.read_bytes() for p in (ROOT / "scripts").glob("*phase20*.py")}
        ),
    }


def serialize_batch(batch: _Batch) -> dict[str, Any]:
    return {
        "fingerprint": batch.fingerprint,
        "batch_id": batch.batch_id,
        "request": batch.request,
        "candidates": [
            {
                "finding": c.finding.model_dump(mode="json", exclude={"severity"}),
                "context": c.context.model_dump(mode="json"),
                "tool": c.tool.model_dump(mode="json") if c.tool else None,
            }
            for c in batch.candidates
        ],
    }


def stable_report(report: dict[str, Any]) -> dict[str, Any]:
    """Compare findings and measured coverage, excluding clocks and run identities."""

    def clean(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                k: clean(v)
                for k, v in value.items()
                if k
                not in {
                    "scan_id",
                    "finding_id",
                    "timestamp",
                    "started_at",
                    "completed_at",
                    "duration_ms",
                    "reviewed_at",
                    "applied_at",
                    "latency_ms",
                    "execution_latency_ms",
                    "origin_latency_ms",
                }
            }
        if isinstance(value, list):
            return [clean(v) for v in value]
        return value

    return {
        "findings": sorted(
            (clean(f) for f in report["findings"]),
            key=lambda f: json.dumps(f, sort_keys=True),
        ),
        **{
            k: clean(report[k])
            for k in (
                "analysisComplete",
                "executionSuccessful",
                "stages",
                "static_analysis",
                "dynamic_analysis",
                "review_activity",
            )
            if k in report
        },
    }


def measure(
    manifest: Manifest | Phase22Manifest,
    treatment: str,
    destination: Path,
    *,
    rules_dir: Path | None = None,
) -> dict[str, Any]:
    if isinstance(manifest, Phase22Manifest):
        if treatment != "rules":
            raise ValueError("Phase 22 measurement currently supports rules-only")
        approved = frozen_phase22()
        inputs = {item.id: item for item in approved.inputs}
        if (
            manifest.snapshots != approved.snapshots
            or manifest.packet != approved.packet
            or any(item != inputs.get(item.id) for item in manifest.inputs)
            or len({item.id for item in manifest.inputs}) != len(manifest.inputs)
        ):
            raise ValueError("Phase 22 measurement differs from its authorized inputs")
        approval = {
            "manifest_sha256": digest(
                (ROOT / "artifacts/phase22/corpus-review/manifest.json").read_bytes()
            )
        }
    else:
        approval = frozen()
    if destination.exists():
        raise ValueError(
            "measurement destination exists; use a new directory "
            "for offline verification"
        )
    if treatment == "semgrep":
        if rules_dir is None:
            raise ValueError("semgrep requires --rules-dir (prepared local rules)")
        verify_rules(rules_dir)
    if treatment == "dynamic":
        # A pending static capture must never turn into an unreviewed runtime plan.
        replay = json.loads((ARTIFACTS / "replay/results.json").read_text())
        eligible = {
            i.id for i in manifest.inputs if i.runtime_applicability == "eligible"
        }
        if any(
            o["state"] != "completed"
            for o in replay["outcomes"]
            if o["input_id"] in eligible
        ):
            raise ValueError(
                "eligible static replay must complete before Docker measurement"
            )
        if {o["input_id"] for o in replay["outcomes"]} != {
            i.id for i in manifest.inputs
        }:
            raise ValueError("static replay is missing inputs")
        if replay["manifest_sha256"] != approval["manifest_sha256"]:
            raise ValueError("static replay manifest drift")
        if replay["scanner"]["source_sha256"] != scanner_identity()["source_sha256"]:
            raise ValueError("static replay scanner drift")
    destination.mkdir(parents=True)
    result: dict[str, Any] = {
        "version": 1,
        "treatment": treatment,
        "manifest_sha256": approval["manifest_sha256"],
        "scanner": scanner_identity(),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "outcomes": [],
        "requests": {},
        "model_calls": 0,
    }
    snapshots = {s.revision: s for s in manifest.snapshots}
    for item in manifest.inputs:
        entry: dict[str, Any] = {
            "input_id": item.id,
            "state": "incomplete",
            "reason": None,
        }
        result["outcomes"].append(entry)
        started = time.monotonic()
        output = destination / item.id
        output.mkdir()
        try:
            if (
                treatment in {"dynamic", "runtime-replay"}
                and item.runtime_applicability != "eligible"
            ):
                entry.update(state="unsupported", reason=item.runtime_reason)
                continue
            with tempfile.TemporaryDirectory(prefix="phase20-") as temporary:
                root = materialize(
                    item,
                    snapshots[item.snapshot],
                    Path(temporary).resolve() / "source",
                    manifest.packet,
                )
                if treatment == "semgrep":
                    assert rules_dir is not None
                    entry.update(run_comparator(root, rules_dir, output))
                    continue
                config = load_configuration(
                    root,
                    environ={},
                    static_only=treatment not in {"dynamic", "runtime-replay"},
                    cli_overrides={
                        "rules_only": treatment == "rules",
                        "ignore_paths": [".phase20/**"],
                        "max_findings_per_scan": 500,
                    },
                    llm_cli_overrides={
                        "model": LLM.model,
                        "reasoning_effort": "medium",
                        "retries": 0,
                        "max_concurrency": 1,
                        "cache_enabled": False,
                    },
                )
                configuration = {
                    "scanner": config.scanner.model_dump(mode="json"),
                    "target": config.target.model_dump(mode="json")
                    if config.target
                    else None,
                    "static_only": config.static_only,
                    "language": config.language.value,
                }
                _atomic_json(output / "configuration.json", configuration)
                entry["configuration_sha256"] = digest(
                    (output / "configuration.json").read_bytes()
                )

                class PrepareReviewer(SemanticReviewer):
                    async def _run_batch(
                        self, batch: _Batch, input_id: str = item.id
                    ) -> _BatchResult:
                        if treatment == "dynamic" and all(
                            c.finding.source.value == "static" for c in batch.candidates
                        ):
                            return await super()._run_batch(batch)
                        planned = serialize_batch(batch)
                        previous = result["requests"].get(batch.fingerprint)
                        if previous is None:
                            result["requests"][batch.fingerprint] = {
                                "inputs": [input_id],
                                **planned,
                            }
                        elif input_id not in previous["inputs"]:
                            previous["inputs"].append(input_id)
                        return _BatchResult(
                            batch, None, "offline preparation: review not captured"
                        )

                context = ScanContext(
                    scan_id=uuid4(),
                    started_at=datetime.now(timezone.utc),
                    target=ScanTarget(display_name=item.id),
                )
                reviewer = (
                    PrepareReviewer
                    if treatment in {"prepare-live", "dynamic"}
                    else SemanticReviewer
                )
                from scripts.phase20_review import CheckedCassettes

                def observe_dynamic(
                    *args: Any,
                    output: Path = output,
                    entry: dict[str, Any] = entry,
                    **kwargs: Any,
                ) -> Any:
                    measured = run_dynamic_scan(*args, **kwargs)
                    payload = {
                        "findings": [
                            f.model_dump(mode="json", round_trip=True)
                            for f in measured.findings
                        ],
                        "warnings": [
                            w.model_dump(mode="json") for w in measured.warnings
                        ],
                        "summary": measured.summary.model_dump(mode="json"),
                        "complete": measured.complete,
                        "execution_successful": measured.execution_successful,
                    }
                    _atomic_json(output / "runtime.json", payload)
                    entry["runtime_sha256"] = digest(
                        (output / "runtime.json").read_bytes()
                    )
                    return measured

                with ExitStack() as stack:
                    stack.enter_context(
                        patch("sentinel.orchestrator.SemanticReviewer", reviewer)
                    )
                    if treatment == "dynamic":
                        stack.enter_context(
                            patch(
                                "sentinel.orchestrator.run_dynamic_scan",
                                observe_dynamic,
                            )
                        )
                    elif treatment == "runtime-replay":
                        retained = retained_runtime(item.id)
                        stack.enter_context(patch("sentinel.orchestrator.reap_orphans"))
                        stack.enter_context(
                            patch(
                                "sentinel.orchestrator.run_dynamic_scan",
                                return_value=retained,
                            )
                        )
                    outcome = run_scan(
                        config,
                        context,
                        completed_at=datetime.now(timezone.utc),
                        allow_degraded=False,
                        review_mode="replay",
                        transport=CheckedCassettes(ARTIFACTS / "captures"),
                    )
                native = json.loads(render_json(outcome.report))
                sarif = json.loads(render_sarif(outcome.report))
                validate_report_data(native)
                validate_sarif_data(sarif)
                _atomic_json(output / "report.json", native)
                _atomic_json(output / "report.sarif", sarif)
                entry.update(
                    state="completed" if outcome.exit_code in {0, 1} else "incomplete",
                    exit_code=outcome.exit_code,
                    finding_count=len(native["findings"]),
                    report_sha256=digest((output / "report.json").read_bytes()),
                    stable_sha256=digest(
                        json.dumps(stable_report(native), sort_keys=True).encode()
                    ),
                )
                if outcome.exit_code == 3:
                    entry["reason"] = (
                        "; ".join(
                            s.reason
                            for s in outcome.report.stages
                            if s.reason and s.status.value == "failed"
                        )
                        or "native analysis incomplete"
                    )
                    if (
                        treatment in {"dynamic", "runtime-replay"}
                        and outcome.report.execution_successful
                    ):
                        entry["state"] = "inconclusive"
                if treatment == "prepare-live" and any(
                    item.id in r["inputs"] for r in result["requests"].values()
                ):
                    entry.update(
                        state="review_pending",
                        reason="exact production requests prepared offline",
                    )
        except Exception as error:
            entry.update(
                state="unsupported" if isinstance(error, TargetError) else "incomplete",
                reason=f"{type(error).__name__}: {error}",
            )
        finally:
            entry["wall_duration_ms"] = round((time.monotonic() - started) * 1000)
            _atomic_json(destination / "results.json", result)
            print(f"{treatment}: {item.id}: {entry['state']}", flush=True)
    return result


def retained_runtime(input_id: str) -> SimpleNamespace:
    result = json.loads((ARTIFACTS / "dynamic/results.json").read_text())
    if (
        result["manifest_sha256"] != frozen()["manifest_sha256"]
        or result["scanner"]["source_sha256"] != scanner_identity()["source_sha256"]
    ):
        raise ValueError("runtime measurement source drift")
    outcome = next(o for o in result["outcomes"] if o["input_id"] == input_id)
    path = ARTIFACTS / "dynamic" / input_id / "runtime.json"
    if not path.exists():
        raise InfrastructureError(
            outcome.get("reason") or "no retained runtime observations"
        )
    if digest(path.read_bytes()) != outcome["runtime_sha256"]:
        raise ValueError("retained runtime proof drift")
    payload = json.loads(path.read_text())
    return SimpleNamespace(
        findings=tuple(
            Finding.model_validate_json(json.dumps(f)) for f in payload["findings"]
        ),
        warnings=tuple(ReportWarning.model_validate(w) for w in payload["warnings"]),
        summary=DynamicAnalysisSummary.model_validate_json(
            json.dumps(payload["summary"])
        ),
        complete=payload["complete"],
        execution_successful=payload["execution_successful"],
    )


def verify_repeat(reference: Path, repeated: Path) -> dict[str, Any]:
    from scripts.phase20_review import request_hash

    before = json.loads((reference / "results.json").read_text())
    after = json.loads((repeated / "results.json").read_text())
    for key in ("treatment", "manifest_sha256"):
        if before[key] != after[key]:
            raise ValueError(f"repeated measurement differs: {key}")
    left = {o["input_id"]: o for o in before["outcomes"]}
    right = {o["input_id"]: o for o in after["outcomes"]}
    if left.keys() != right.keys():
        raise ValueError("repeated measurement input coverage differs")
    for input_id, original in left.items():
        if original["state"] != right[input_id]["state"]:
            raise ValueError(f"repeated outcome differs: {input_id}")
        original_path = reference / input_id / "report.json"
        repeat_path = repeated / input_id / "report.json"
        if original_path.exists() != repeat_path.exists():
            raise ValueError(f"repeated native report missing: {input_id}")
        if original_path.exists() and stable_report(
            json.loads(original_path.read_text())
        ) != stable_report(json.loads(repeat_path.read_text())):
            raise ValueError(f"repeated stable findings/coverage differ: {input_id}")
    for fingerprint, request in before["requests"].items():
        candidate = after["requests"].get(fingerprint)
        if (
            candidate is None
            or request["inputs"] != candidate["inputs"]
            or request_hash(request["request"]) != request_hash(candidate["request"])
        ):
            raise ValueError("repeated production request drift")
    if before["requests"].keys() != after["requests"].keys():
        raise ValueError("repeated request coverage differs")
    verification = {
        "reference_sha256": digest((reference / "results.json").read_bytes()),
        "repeat_sha256": digest((repeated / "results.json").read_bytes()),
        "input_count": len(left),
        "stable_findings_and_outcomes_equal": True,
        "request_count": len(before["requests"]),
        "timing_policy": (
            "Repeat wall duration is verification latency, "
            "not live model latency or a new accuracy observation."
        ),
    }
    _atomic_json(repeated / "reproducibility.json", verification)
    return verification


def verify_rules(directory: Path) -> None:
    if importlib.metadata.version("semgrep") != "1.176.0":
        raise ValueError("requires Semgrep 1.176.0")
    metadata = json.loads((ARTIFACTS / "semgrep-preparation.json").read_text())
    expected = {r["source_path"]: r["configuration_sha256"] for r in metadata["rules"]}
    paths = [p for p in directory.rglob("*") if p.is_file()]
    if any(p.is_symlink() for p in directory.rglob("*")) or directory.is_symlink():
        raise ValueError("comparator configuration links forbidden")
    actual = {
        p.relative_to(directory).as_posix(): digest(p.read_bytes()) for p in paths
    }
    if actual != expected:
        raise ValueError("prepared comparator configuration drift")


def run_comparator(root: Path, directory: Path, output: Path) -> dict[str, Any]:
    command = [
        "semgrep",
        "scan",
        "--config",
        str(directory.resolve()),
        "--json",
        "--metrics=off",
        "--disable-version-check",
        "--no-git-ignore",
        "--exclude",
        ".phase20/**",
        str(root),
    ]
    _atomic_json(output / "command.json", {"argv": command, "cwd": str(root)})
    # No registry configs, version checks or telemetry; do not pass ambient tokens.
    environment = {
        k: v
        for k, v in os.environ.items()
        if k in {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "HOME"}
    }
    environment["SEMGREP_SEND_METRICS"] = "off"
    environment["SEMGREP_ENABLE_VERSION_CHECK"] = "0"
    environment["SSL_CERT_FILE"] = certifi.where()
    environment["SEMGREP_SETTINGS_FILE"] = str(output.resolve() / "settings.yml")
    environment["SEMGREP_LOG_FILE"] = str(output.resolve() / "semgrep.log")
    _atomic_json(
        output / "environment.json",
        {
            k: v
            for k, v in environment.items()
            if k.startswith("SEMGREP_") or k == "SSL_CERT_FILE"
        },
    )
    with (
        (output / "raw.json").open("wb") as stdout,
        (output / "stderr.txt").open("wb") as stderr,
    ):
        process = subprocess.run(
            command,
            cwd=root,
            env=environment,
            stdout=stdout,
            stderr=stderr,
            timeout=300,
            check=False,
        )
    _atomic_json(output / "execution.json", {"exit_code": process.returncode})
    data = json.loads((output / "raw.json").read_text())
    if data.get("version") != "1.176.0":
        raise ValueError("executed comparator engine version differs from 1.176.0")
    return {
        "state": "completed"
        if process.returncode == 0 and not data.get("errors")
        else "incomplete",
        "exit_code": process.returncode,
        "finding_count": len(data.get("results", [])),
        "error_count": len(data.get("errors", [])),
        "paths": data.get("paths", {}),
        "raw_sha256": digest((output / "raw.json").read_bytes()),
    }
