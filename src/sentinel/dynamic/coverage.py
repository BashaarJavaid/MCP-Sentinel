"""Metadata from existing tools/list responses; never fetch another page."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Literal

from mcp.types import Tool

from sentinel.dynamic.arguments import (
    UnsupportedSchema,
    resolve_schema,
    schema_validator,
)
from sentinel.llm.context import sanitize_text
from sentinel.report.coverage import (
    DiscoverySnapshot,
    ObservedTool,
    UnresolvedFieldSpace,
)


def discovery_snapshot(
    probe_id: str,
    role: Literal["baseline", "attack"],
    tools: tuple[Tool, ...],
    *,
    more_pages: bool,
    deadline: float = float("inf"),
) -> DiscoverySnapshot:
    observed = [_observed_tool(tool, deadline) for tool in tools]
    duplicate = len({tool.name for tool in tools}) != len(tools)
    return DiscoverySnapshot(
        probe_id=probe_id,
        role=role,
        tools=tuple(observed),
        more_pages=more_pages,
        tool_total=None if more_pages or duplicate else len(tools),
        reason="duplicate tool names"
        if duplicate
        else "additional pages were not requested"
        if more_pages
        else None,
    )


def _observed_tool(tool: Tool, deadline: float) -> ObservedTool:
    fields: list[tuple[str, ...]] = []
    gaps: list[UnresolvedFieldSpace] = []

    def gap(path: tuple[str, ...], reason: str) -> None:
        gaps.append(UnresolvedFieldSpace(path=path, reason=reason))

    def walk(raw: Any, path: tuple[str, ...], seen: frozenset[int]) -> None:
        if time.monotonic() >= deadline:
            gap(path, "session deadline exhausted during enumeration")
            return
        if len(path) > 8:
            gap(path, "field enumeration stops at depth 8")
            return
        try:
            schema = resolve_schema(raw, tool.inputSchema)
        except UnsupportedSchema as error:
            gap(path, str(error))
            return
        if id(schema) in seen:
            gap(path, "recursive local reference")
            return
        seen = seen | {id(schema)}
        if any(
            key in schema
            for key in (
                "anyOf",
                "oneOf",
                "allOf",
                "if",
                "not",
                "$dynamicRef",
                "$recursiveRef",
            )
        ) or isinstance(schema.get("type"), list):
            gap(path, "schema alternatives or dynamic constraints")
        if schema.get("type") == "array" or "items" in schema:
            gap(path, "array item space is not enumerated")
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            gap(path, "invalid properties schema")
            return
        if schema.get("type") == "object" or "properties" in schema:
            if schema.get("additionalProperties", True) is not False or any(
                key in schema for key in ("patternProperties", "unevaluatedProperties")
            ):
                gap(path, "open-ended object properties")
        elif not schema:
            gap(path, "unconstrained field space")
        for name, child in properties.items():
            child_path = (*path, sanitize_text(name))
            if len(child_path) > 8:
                gap(path, "field enumeration stops at depth 8")
                break
            fields.append(child_path)
            walk(child, child_path, seen)
        # Local reference siblings can add explicit properties in modern dialects.
        if isinstance(raw, dict) and "$ref" in raw and "properties" in raw:
            walk(
                {key: value for key, value in raw.items() if key != "$ref"},
                path,
                seen,
            )

    digest = None
    try:
        encoded = json.dumps(
            tool.inputSchema,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode()
        digest = hashlib.sha256(encoded).hexdigest()
        if len(encoded) > 1_048_576:
            gap((), "runtime schema exceeds 1 MiB")
        else:
            if time.monotonic() < deadline:
                try:
                    schema_validator(tool.inputSchema)
                except UnsupportedSchema as error:
                    gap((), str(error))
            walk(tool.inputSchema, (), frozenset())
    except (ValueError, RecursionError, TypeError):
        gap((), "invalid or excessively recursive runtime schema")
    return ObservedTool(
        name=sanitize_text(tool.name),
        schema_sha256=digest,
        field_paths=tuple(dict.fromkeys(fields)),
        unresolved=tuple(gaps),
    )
