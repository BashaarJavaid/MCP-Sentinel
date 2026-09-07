"""Select the pinned community comparator offline; never scan a corpus input."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import re
from pathlib import Path
from typing import Any

import yaml

from scripts.phase20_corpus import ROOT, archive_files, digest

REVISION = "40b8c63f75dc7c22c8a77482d73bfb864b146f7e"
VERSION = "1.176.0"
ARCHIVE_SHA256 = "beb4ecfbe2ef6d14942bf58c6805456d802d9380fd894c11de8fde957ff1159c"
METADATA = ROOT / "artifacts/phase20/semgrep-preparation.json"


def select(archive: bytes) -> tuple[dict[str, bytes], list[dict[str, Any]]]:
    files = archive_files(archive, strip_root=True)
    configurations: dict[str, bytes] = {}
    identities = []
    for name, data in sorted(files.items()):
        if not name.endswith((".yaml", ".yml")) or not re.search(rb"(?m)^rules:", data):
            continue
        value = yaml.safe_load(data)
        selected = [
            rule
            for rule in value["rules"]
            if rule.get("metadata", {}).get("category") == "security"
            and set(rule.get("languages", [])) & {"python", "javascript", "typescript"}
        ]
        if not selected:
            continue
        configuration = yaml.safe_dump({"rules": selected}, sort_keys=False).encode()
        configurations[name] = configuration
        for rule in selected:
            identities.append(
                {
                    "id": rule["id"],
                    "source_path": name,
                    "source_file_sha256": digest(data),
                    "rule_sha256": digest(
                        json.dumps(rule, sort_keys=True, ensure_ascii=False).encode()
                    ),
                    "configuration_sha256": digest(configuration),
                    "languages": rule["languages"],
                    "category": "security",
                }
            )
    if not identities:
        raise ValueError("no eligible security rules")
    return configurations, identities


def prepare(archive_path: Path, rules_dir: Path) -> None:
    if importlib.metadata.version("semgrep") != VERSION:
        raise ValueError(f"requires installed Semgrep {VERSION}")
    if rules_dir.resolve().is_relative_to(ROOT) or rules_dir.exists():
        raise ValueError("rules directory must be new and outside the repository")
    archive = archive_path.read_bytes()
    if digest(archive) != ARCHIVE_SHA256:
        raise ValueError("community-rule archive differs from the pinned acquisition")
    configurations, identities = select(archive)
    rules_dir.mkdir(parents=True)
    for name, data in configurations.items():
        destination = rules_dir / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    metadata = {
        "version": 1,
        "status": "prepared_not_evaluated",
        "prepared_on": "2026-09-06",
        "engine_version": VERSION,
        "repository": "semgrep/semgrep-rules",
        "revision": REVISION,
        "revision_date": "2026-07-30T02:46:44Z",
        "archive_sha256": digest(archive),
        "archive_url": f"https://api.github.com/repos/semgrep/semgrep-rules/tarball/{REVISION}",
        "license_url": "https://semgrep.dev/legal/rules-license/",
        "redistributed_rule_bytes": False,
        "selection": (
            "Root rules: YAML configurations; metadata.category exactly security; "
            "languages intersects python/javascript/typescript. Select before scans."
        ),
        "command": [
            "semgrep",
            "scan",
            "--config",
            "<prepared-local-rules-dir>",
            "--json",
            "--metrics=off",
            "--disable-version-check",
            "--no-git-ignore",
            "--exclude",
            ".phase20/**",
            "<same-materialized-scan-root>",
        ],
        "rule_count": len(identities),
        "configuration_count": len(configurations),
        "rules": identities,
    }
    METADATA.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--rules-dir", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.archive, args.rules_dir)


if __name__ == "__main__":
    main()
