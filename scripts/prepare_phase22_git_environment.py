"""Test a proposed Git SDK environment inside Sentinel's Docker boundary only."""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from scripts.phase20_corpus import digest, materialize, validate
from scripts.phase20_measurements import scanner_identity
from sentinel.config import load_configuration
from sentinel.dynamic.sandbox import SCAN_LABEL, DockerSandbox, _pyproject_dependencies

OUTPUT = Path("artifacts/phase22/git-environment-v1")
SDK_PIN = "mcp==1.29.0"


async def prepare(output: Path = OUTPUT) -> None:
    """Prepare evidence for approval; do not adopt or modify Phase 20 inputs."""
    output.mkdir(parents=True, exist_ok=False)
    manifest = validate()
    snapshots = {s.revision: s for s in manifest.snapshots}
    packet: dict[str, object] = {
        "status": "proposed_not_approved",
        "sdk_pin": SDK_PIN,
        "purpose": "Git startup and tool discovery only; no attack or model calls",
        "scanner": scanner_identity(),
        "inputs": [],
    }
    records: list[dict[str, object]] = []
    packet["inputs"] = records
    for item in manifest.inputs:
        if item.runtime_applicability != "eligible":
            continue
        started = time.monotonic()
        record: dict[str, object] = {
            "input_id": item.id,
            "snapshot": item.snapshot,
            "tree_sha256": item.tree_sha256,
        }
        records.append(record)
        try:
            with TemporaryDirectory(prefix="phase22-git-") as temporary:
                root = materialize(
                    item,
                    snapshots[item.snapshot],
                    Path(temporary).resolve() / "source",
                    manifest.packet,
                )
                configuration = load_configuration(root, environ={})
                assert configuration.target is not None
                requirements = (
                    "\n".join(
                        [*_pyproject_dependencies(root / "pyproject.toml"), SDK_PIN]
                    )
                    + "\n"
                )
                additions = root / ".phase22"
                additions.mkdir()
                (additions / "requirements.txt").write_text(requirements)
                configuration = configuration.model_copy(
                    update={
                        "target": configuration.target.model_copy(
                            update={
                                "install_cmd": (
                                    "pip",
                                    "install",
                                    "-r",
                                    ".phase22/requirements.txt",
                                )
                            }
                        )
                    }
                )
                record["requirements"] = requirements
                record["requirements_sha256"] = digest(requirements.encode())
                assert configuration.target is not None
                record["target"] = configuration.target.model_dump(mode="json")
                sandbox = DockerSandbox(configuration, uuid4())
                sandbox.preflight()
                image = sandbox.prepare_dependency_image()
                record["image"] = image.reference
                record["image_inspect"] = json.loads(
                    sandbox.docker(("image", "inspect", image.reference)).stdout
                )
                async with sandbox.probe_session(
                    image.reference, "phase22-discovery", timeout=30
                ) as session:
                    result = await asyncio.wait_for(session.client.list_tools(), 15)
                    record["tools"] = [
                        tool.model_dump(mode="json") for tool in result.tools
                    ]
                    record["process_state"] = session.process_state()
                    record["logs"] = session.logs()
                    for name, arguments in (
                        ("dependencies", ("python", "-m", "pip", "freeze", "--all")),
                        ("dependency_check", ("python", "-m", "pip", "check")),
                    ):
                        record[name] = sandbox.docker(
                            ("exec", session.container_name, *arguments)
                        ).stdout
                    record["container_inspect"] = json.loads(
                        sandbox.docker(("inspect", session.container_name)).stdout
                    )
                    if not result.tools:
                        raise ValueError("Git startup returned no tools")
                remaining = sandbox.docker(
                    ("ps", "-aq", "--filter", f"label={SCAN_LABEL}={sandbox.scan_id}")
                ).stdout.strip()
                record["cleanup_remaining"] = remaining
                if remaining:
                    raise ValueError("Git discovery left containers behind")
                record["state"] = "completed"
        except Exception as error:
            record.update(state="incomplete", error=str(error))
        record["seconds"] = round(time.monotonic() - started, 3)
        (output / "packet.json").write_text(json.dumps(packet, indent=2) + "\n")
        print(item.id, record["state"], record["seconds"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    asyncio.run(prepare(parser.parse_args().output))
