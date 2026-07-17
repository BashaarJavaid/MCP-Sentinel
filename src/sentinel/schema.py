"""Generate and verify checked-in Sentinel JSON Schemas."""

from __future__ import annotations

import argparse
import json
from importlib import resources
from pathlib import Path
from typing import Any, Protocol, cast

from sentinel.finding import Finding
from sentinel.report.model import ScanReport

SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"


class SchemaResource(Protocol):
    def read_text(self, encoding: str | None = None) -> str: ...


def source_schema_dir() -> Path | None:
    candidate = Path(__file__).resolve().parents[2] / "schemas"
    return candidate if candidate.is_dir() else None


def schema_texts() -> dict[str, str]:
    finding_schema = Finding.model_json_schema(mode="serialization")
    report_schema = ScanReport.model_json_schema(mode="serialization", by_alias=True)
    finding_schema["$schema"] = SCHEMA_DRAFT
    report_schema["$schema"] = SCHEMA_DRAFT
    report_schema = _externalize_finding(report_schema)
    return {
        "finding.schema.json": _dump(finding_schema),
        "report.schema.json": _dump(report_schema),
    }


def generate(schema_dir: Path) -> None:
    schema_dir.mkdir(parents=True, exist_ok=True)
    for name, content in schema_texts().items():
        (schema_dir / name).write_text(content, encoding="utf-8")


def check(schema_dir: Path) -> list[str]:
    drift: list[str] = []
    for name, expected in schema_texts().items():
        path = schema_dir / name
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            drift.append(name)
    return drift


def schema_resource(name: str) -> SchemaResource:
    """Locate a schema in a source checkout or an installed wheel."""

    source = source_schema_dir()
    if source is not None:
        candidate = source / name
        if candidate.is_file():
            return candidate
    return resources.files("sentinel").joinpath("_schemas").joinpath(name)


def _externalize_finding(schema: dict[str, Any]) -> dict[str, Any]:
    definitions = schema.get("$defs", {})
    if "Finding" not in definitions:
        raise RuntimeError("report schema does not contain a Finding definition")
    del definitions["Finding"]

    def replace(value: Any) -> Any:
        if isinstance(value, dict):
            if value.get("$ref") == "#/$defs/Finding":
                return {"$ref": "finding.schema.json"}
            return {key: replace(item) for key, item in value.items()}
        if isinstance(value, list):
            return [replace(item) for item in value]
        return value

    return cast(dict[str, Any], replace(schema))


def _dump(schema: dict[str, Any]) -> str:
    return json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m sentinel.schema")
    parser.add_argument("command", choices=("generate", "check"))
    args = parser.parse_args()

    schema_dir = source_schema_dir()
    if schema_dir is None:
        parser.error("generate/check must run from an editable source checkout")
    if args.command == "generate":
        generate(schema_dir)
        return 0
    drift = check(schema_dir)
    if drift:
        parser.exit(3, f"schema drift detected: {', '.join(drift)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
