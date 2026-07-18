"""SENT-004 intraprocedural prompt-flow analysis."""

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


def detect(context: StaticContext, state: RuleRunState) -> None:
    configured = set(context.configuration.scanner.rules.sent004.sanitizers)
    for file in context.files.python_files:
        aliases = import_aliases(file)
        module = module_name(context.configuration.scan_root, file)
        functions = [
            node
            for node in file.tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        prompt_functions = set(discover_prompt_functions(file))
        for function in functions:
            tainted: set[str] = set()
            sanitized: set[str] = set()
            for item in sorted(
                ast.walk(function), key=lambda node: getattr(node, "lineno", 0)
            ):
                if isinstance(item, (ast.Assign, ast.AnnAssign)):
                    value = item.value
                    targets = (
                        item.targets if isinstance(item, ast.Assign) else [item.target]
                    )
                    names = {
                        target.id for target in targets if isinstance(target, ast.Name)
                    }
                    if value is not None and _is_source(value):
                        tainted.update(names)
                    if isinstance(value, ast.Call):
                        call_name = qualified_name(value.func)
                        resolved = resolve_name(call_name, aliases) if call_name else ""
                        local_name = f"{module}.{call_name}" if call_name else ""
                        if configured.intersection({resolved, local_name}) and (
                            _contains_names(value, tainted)
                        ):
                            tainted.update(names)
                            sanitized.update(names)
                        elif _contains_names(value, tainted):
                            tainted.update(names)
                sink = _is_openai_sink(item) or (
                    function in prompt_functions and isinstance(item, ast.Return)
                )
                if sink and _contains_names(item, tainted - sanitized):
                    state.matches.append(
                        match_from_node("SENT-004", file, item, "prompt-taint")
                    )
                    break
            if function in prompt_functions and not any(
                match.path == file.relative_path
                and match.range.start_line >= function.lineno
                and match.range.end_line <= (function.end_lineno or function.lineno)
                for match in state.matches
            ):
                state.exempt("sanitizer_or_no_taint")


def _is_source(node: ast.AST) -> bool:
    if isinstance(node, ast.Attribute) and node.attr in {
        "text",
        "description",
        "content",
    }:
        return True
    if isinstance(node, ast.Call):
        name = qualified_name(node.func) or ""
        return name.endswith(("call_tool", "list_tools"))
    return any(_is_source(child) for child in ast.iter_child_nodes(node))


def _is_openai_sink(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    name = qualified_name(node.func) or ""
    if not name.endswith(("responses.create", "chat.completions.create")):
        return False
    return any(
        keyword.arg in {"input", "instructions", "messages"}
        for keyword in node.keywords
    )


def _contains_names(node: ast.AST, names: set[str]) -> bool:
    return any(
        isinstance(item, ast.Name) and item.id in names for item in ast.walk(node)
    )
