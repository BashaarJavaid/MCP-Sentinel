"""SENT-012: caller-controlled filesystem paths without enforced containment."""

import ast

from sentinel.static.ast_utils import range_for_node
from sentinel.static.discovery import Function, PythonProgram, ToolBinding
from sentinel.static.http_discovery import HTTPBinding
from sentinel.static.launches import for_tool
from sentinel.static.model import RuleRunState, StaticContext
from sentinel.static.path_flow import PathFlow, Value


def analyze(
    program: PythonProgram,
    state: RuleRunState,
    deadline: float = float("inf"),
    *,
    flow: PathFlow | None = None,
    entries: tuple[ToolBinding | HTTPBinding, ...] | None = None,
) -> None:
    flow = flow or PathFlow(program, state, deadline)
    visited: set[tuple[str, int]] = set()
    groups: dict[
        tuple[ast.AST, ...], list[tuple[ToolBinding | HTTPBinding, dict[str, Value]]]
    ] = {}
    for tool in program.tools() if entries is None else entries:
        state.visit(
            tool.registration.file.relative_path, range_for_node(tool.registration.node)
        )
        state.visit(tool.handler.file.relative_path, range_for_node(tool.handler.node))
        node = tool.handler.node
        assert isinstance(node, Function)
        key = (tool.handler.file.relative_path, node.lineno)
        if key in visited:
            continue
        visited.add(key)
        bindings = {
            parameter.arg: Value(
                sources=frozenset(
                    {("http:" if isinstance(tool, HTTPBinding) else "") + parameter.arg}
                ),
                key=f"{tool.handler.file.relative_path}:{node.lineno}:{parameter.arg}",
                locations=frozenset(
                    {
                        (tool.handler.file.relative_path, parameter.lineno),
                        (
                            tool.registration.file.relative_path,
                            range_for_node(tool.registration.node).start_line,
                        ),
                    }
                ),
            )
            for parameter in (
                tool.caller_parameters(program)
                if isinstance(tool, ToolBinding)
                else tool.caller_parameters
            )
        }
        if isinstance(tool, ToolBinding):
            launches = for_tool(program, tool)
            group = tuple(launch.call for launch in launches) or (node,)
            groups.setdefault(group, []).append((tool, bindings))
        else:
            groups[(node,)] = [(tool, bindings)]
    for entries_ in groups.values():
        tools = tuple(
            (tool, bindings)
            for tool, bindings in entries_
            if isinstance(tool, ToolBinding)
        )
        if tools:
            flow.entry_group(tools)
        else:
            for tool, bindings in entries_:
                flow.function(tool.handler, bindings)
    state.warnings.extend(program.warnings)


def detect(context: StaticContext, state: RuleRunState) -> None:
    analyze(context.python_program, state, context.deadline)
    if context.files.typescript_files:
        from sentinel.static.typescript_path_flow import analyze as analyze_typescript

        analyze_typescript(context.typescript_program, state)
