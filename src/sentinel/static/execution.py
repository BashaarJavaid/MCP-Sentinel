"""Same-file execution-flow summaries shared by the two source recognizers."""

from __future__ import annotations

import json
import time
from collections.abc import Iterable, Iterator
from contextlib import suppress
from dataclasses import dataclass, field, replace
from graphlib import CycleError, TopologicalSorter

from sentinel.errors import InfrastructureError
from sentinel.finding import SourceRange
from sentinel.report.model import ReportWarning
from sentinel.static.model import RuleRunState, StaticMatch

Sources = frozenset[str]
UNKNOWN = frozenset({"?"})


def union(values: Iterable[Sources]) -> Sources:
    return frozenset().union(*values)


def substitute(sources: Sources, bindings: dict[str, Sources]) -> Sources:
    return union(bindings.get(name, UNKNOWN) for name in sources)


def check_deadline(deadline: float) -> None:
    if time.monotonic() > deadline:
        raise InfrastructureError("static analysis exceeded its 120-second timeout")


def dependency_order(graph: dict[str, set[str]]) -> Iterator[str]:
    """Summarize acyclic helpers first without Python call-stack depth limits."""
    sorter = TopologicalSorter(graph)
    # A cycle's unavailable return summaries remain explicitly unknown.
    with suppress(CycleError):
        sorter.prepare()
    done: set[str] = set()
    while sorter.is_active():
        ready = sorted(sorter.get_ready())
        for name in ready:
            yield name
            done.add(name)
            sorter.done(name)
    yield from sorted(graph.keys() - done)


@dataclass
class Call:
    site: StaticMatch
    callee: str
    bindings: dict[str, Sources]


@dataclass
class Summary:
    parameters: tuple[str, ...]
    returned: Sources = frozenset()
    sinks: list[tuple[StaticMatch, Sources]] = field(default_factory=list)
    calls: list[Call] = field(default_factory=list)
    issues: list[tuple[StaticMatch, Sources, str]] = field(default_factory=list)
    lines: set[int] = field(default_factory=set)


def emit(
    root: Summary,
    summaries: dict[str, Summary],
    state: RuleRunState,
    *,
    deadline: float,
    first_direct_only: bool = False,
) -> None:
    """Bind summaries to tool inputs; never infer a sink from an unknown call."""
    stack: list[
        tuple[Summary, dict[str, Sources], StaticMatch | None, tuple[int, ...]]
    ] = [(root, {p: frozenset({p}) for p in root.parameters}, None, ())]
    seen: set[tuple[str, SourceRange, tuple[tuple[str, Sources], ...]]] = set()
    helpers: dict[SourceRange, tuple[StaticMatch, set[str], set[int]]] = {}
    direct_indices: list[int] = []
    visited_lines: set[int] = set()
    direct_emitted = False
    while stack:
        check_deadline(deadline)
        summary, bindings, anchor, trace = stack.pop()
        visited_lines.update(summary.lines)
        # ponytail: copied traces; use linked traces if deep scans hit the deadline.
        lines = (*trace, *sorted(summary.lines))
        for site, sources, reason in summary.issues:
            if substitute(sources, bindings) - UNKNOWN:
                state.warnings.append(
                    ReportWarning(
                        code="static_flow_unresolved",
                        message=(
                            f"SENT-002 at {site.path}:{site.range.start_line}: "
                            f"{reason}; this flow is not established as safe."
                        ),
                    )
                )
        for sink, sources in summary.sinks:
            if not substitute(sources, bindings) - UNKNOWN:
                continue
            if anchor is None:
                if not first_direct_only or not direct_emitted:
                    direct_indices.append(len(state.matches))
                    state.matches.append(sink)
                    direct_emitted = True
            else:
                entry = helpers.setdefault(anchor.range, (anchor, set(), set()))
                entry[1].add(
                    f"{sink.captures['sink_name']} at "
                    f"{sink.path}:{sink.range.start_line}"
                )
                entry[2].update(lines)
        for call in reversed(summary.calls):
            bound = {
                name: substitute(sources, bindings)
                for name, sources in call.bindings.items()
            }
            if not union(bound.values()) - UNKNOWN:
                continue
            location = anchor or call.site
            key = (call.callee, location.range, tuple(sorted(bound.items())))
            if key in seen:
                continue
            seen.add(key)
            stack.append((summaries[call.callee], bound, location, lines))
    if seen:
        for index in direct_indices:
            match = state.matches[index]
            state.matches[index] = replace(
                match,
                captures={
                    **match.captures,
                    "flow_lines": json.dumps(sorted(visited_lines)),
                },
            )
    for site, sinks, flow_lines in helpers.values():
        state.matches.append(
            replace(
                site,
                match_kinds=("local-helper-flow",),
                captures={
                    "execution_sinks": "; ".join(sorted(sinks)),
                    "flow_lines": json.dumps(sorted(flow_lines)),
                },
            )
        )
