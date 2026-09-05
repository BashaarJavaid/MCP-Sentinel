"""SENT-004: track the sanitizer's result, including overwrites and branches."""

from __future__ import annotations

import ast

from sentinel.static.ast_utils import (
    discover_prompt_functions,
    import_aliases,
    match_from_node,
    module_name,
    qualified_name,
    resolve_name,
)
from sentinel.static.model import RuleRunState, StaticContext
from sentinel.static.safety import Condition, paths


def detect(context: StaticContext, state: RuleRunState) -> None:
    configured = set(context.configuration.scanner.rules.sent004.sanitizers)
    for file in context.files.python_files:
        imports = import_aliases(file)
        module = module_name(context.configuration.scan_root, file)
        prompts = set(discover_prompt_functions(file))
        for function in (
            node
            for node in file.tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ):
            found = False
            for path in paths(function.body, context.deadline):
                tainted: dict[str, bool] = {}

                def value(
                    node: ast.AST | None,
                    tainted: dict[str, bool] = tainted,
                    imports: dict[str, str] = imports,
                    module: str = module,
                ) -> bool:
                    if node is None:
                        return False
                    if isinstance(node, ast.Name):
                        return tainted.get(node.id, False)
                    if isinstance(node, ast.Call):
                        name = qualified_name(node.func) or ""
                        if configured.intersection(
                            {resolve_name(name, imports), f"{module}.{name}"}
                        ):
                            return False
                        if name.endswith(("call_tool", "list_tools")):
                            return True
                    if isinstance(node, ast.Attribute) and node.attr in {
                        "text",
                        "description",
                        "content",
                    }:
                        return True
                    return any(value(child) for child in ast.iter_child_nodes(node))

                for event in path:
                    if isinstance(event, Condition):
                        continue
                    sinks: list[ast.AST] = [
                        node
                        for node in ast.walk(event)
                        if isinstance(node, ast.Call)
                        and (qualified_name(node.func) or "").endswith(
                            ("responses.create", "chat.completions.create")
                        )
                    ]
                    if function in prompts and isinstance(event, ast.Return):
                        sinks.append(event)
                    sink = next((node for node in sinks if value(node)), None)
                    if sink is not None:
                        state.matches.append(
                            match_from_node("SENT-004", file, sink, "prompt-taint")
                        )
                        found = True
                        break
                    if isinstance(event, (ast.Assign, ast.AnnAssign)):
                        targets = (
                            event.targets
                            if isinstance(event, ast.Assign)
                            else [event.target]
                        )
                        for target in targets:
                            if isinstance(target, ast.Name):
                                tainted[target.id] = value(event.value)
                    elif isinstance(event, ast.AugAssign) and isinstance(
                        event.target, ast.Name
                    ):
                        tainted[event.target.id] = tainted.get(
                            event.target.id, False
                        ) or value(event.value)
                if found:
                    break
            if function in prompts and not found:
                state.exempt("sanitizer_or_no_taint")
