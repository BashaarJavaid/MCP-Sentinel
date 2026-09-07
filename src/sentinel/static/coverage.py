"""Inventory metadata over the detector's included files, without executing them."""

from __future__ import annotations

import ast
import re

from sentinel.finding import FileLocation, SourceRange
from sentinel.report.coverage import RecognitionReason, StaticCoverage, StaticSurface
from sentinel.static import typescript as ts
from sentinel.static.ast_utils import (
    decorator_call,
    discover_prompt_functions,
    discover_tool_regions,
    import_aliases,
    literal_string,
    qualified_name,
    range_for_node,
    resolve_name,
)
from sentinel.static.catalog import RULE_IDS
from sentinel.static.execution import check_deadline
from sentinel.static.model import RuleRunState, StaticContext
from sentinel.static.semgrep_ast import source_range as ts_source_range
from sentinel.static.typescript_discovery import TypeScriptBinding
from sentinel.static.typescript_execution import _mask


def inventory(
    context: StaticContext, states: dict[str, RuleRunState]
) -> StaticCoverage:
    surfaces: list[StaticSurface] = []
    bindings = context.python_program.tools()

    def schema_supported(binding: TypeScriptBinding | None) -> bool:
        return bool(
            binding
            and binding.schema
            and ts._zod_object_schema(
                context.typescript_program.text(
                    binding.schema.file, binding.schema.node
                ),
                ts._constant_expressions(binding.schema.file.source),
            )
            is not None
        )

    def add(
        kind: str,
        name: str | None,
        path: str,
        location: SourceRange,
        handler: SourceRange | None,
        code: str | None = None,
        message: str = "",
        *,
        unsupported: bool = False,
        handler_path: str | None = None,
    ) -> None:
        check_deadline(context.deadline)
        where = FileLocation(path=path, range=location)
        visits = tuple(
            rule_id
            for rule_id, state in states.items()
            if state.skip_reason is None
            and any(
                visit_path == path
                and (
                    (visit.start_line, visit.start_column)
                    == (location.start_line, location.start_column)
                    or (
                        handler is not None
                        and (visit.start_line, visit.start_column)
                        == (handler.start_line, handler.start_column)
                    )
                )
                for visit_path, visit in state.visits
            )
        )
        surfaces.append(
            StaticSurface(
                kind=kind,  # type: ignore[arg-type]
                name=name,
                location=where,
                handler=FileLocation(path=handler_path or path, range=handler)
                if handler
                else None,
                status="unsupported"
                if unsupported
                else "unresolved"
                if code
                else "recognized",
                reasons=(RecognitionReason(code=code, message=message, location=where),)
                if code
                else (),
                examined_rule_ids=visits,
            )
        )

    for file in context.files.python_files:
        check_deadline(context.deadline)
        path = file.relative_path
        covered: set[ast.AST] = set()
        imports = import_aliases(file)
        for binding in bindings:
            if binding.registration.file is file and isinstance(
                binding.registration.node, ast.Call
            ):
                covered.add(binding.registration.node)
                add(
                    "tool",
                    binding.name,
                    path,
                    range_for_node(binding.registration.node),
                    range_for_node(binding.handler.node),
                    handler_path=binding.handler.file.relative_path,
                )
        for region in discover_tool_regions(file):
            # A dispatcher branch is its own registration location.
            if region.node is not region.function:
                covered.add(region.node)
                add(
                    "tool",
                    region.name,
                    path,
                    range_for_node(region.node),
                    range_for_node(region.node),
                )
                continue
            for dec in region.function.decorator_list:
                name, call = decorator_call(dec)
                if not name or not name.endswith(".tool") or dec in covered:
                    continue
                covered.add(dec)
                dynamic = call is not None and any(
                    kw.arg == "name" and literal_string(kw.value) is None
                    for kw in call.keywords
                )
                registered_name = region.function.name
                if call:
                    registered_name = next(
                        (
                            literal_string(kw.value) or registered_name
                            for kw in call.keywords
                            if kw.arg == "name"
                        ),
                        registered_name,
                    )
                add(
                    "tool",
                    None if dynamic else registered_name,
                    path,
                    range_for_node(dec),
                    range_for_node(region.node),
                    "computed_name" if dynamic else None,
                    "computed tool name; recognized function body only",
                )
                imported_annotations = [
                    arg
                    for arg in (
                        *region.function.args.posonlyargs,
                        *region.function.args.args,
                        *region.function.args.kwonlyargs,
                    )
                    if arg.annotation is not None
                    and (qualified_name(arg.annotation) or "").split(".")[0] in imports
                ]
                if imported_annotations:
                    surface = surfaces[-1]
                    surfaces[-1] = surface.model_copy(
                        update={
                            "status": "unresolved",
                            "reasons": (
                                *surface.reasons,
                                *(
                                    RecognitionReason(
                                        code="imported_schema",
                                        message="imported schema unresolved",
                                        location=FileLocation(
                                            path=path, range=range_for_node(arg)
                                        ),
                                    )
                                    for arg in imported_annotations
                                ),
                            ),
                        }
                    )
        for function in discover_prompt_functions(file):
            for dec in function.decorator_list:
                name, call = decorator_call(dec)
                if name and name.endswith(".prompt"):
                    covered.add(dec)
                    prompt_name = function.name
                    dynamic = False
                    if call:
                        for kw in call.keywords:
                            if kw.arg == "name":
                                prompt_name = literal_string(kw.value) or function.name
                                dynamic = literal_string(kw.value) is None
                    add(
                        "prompt",
                        None if dynamic else prompt_name,
                        path,
                        range_for_node(dec),
                        range_for_node(function),
                        "computed_name" if dynamic else None,
                        "prompt name is computed",
                    )
        functions = {
            node.name: node
            for node in file.tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        applications = {
            target.id
            for node in file.tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and resolve_name(qualified_name(node.value.func) or "", imports)
            in {"fastapi.FastAPI", "fastapi.APIRouter"}
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        decorators = {
            dec: node
            for node in ast.walk(file.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            for dec in node.decorator_list
        }
        for dec, function in decorators.items():
            name, call = decorator_call(dec)
            if (
                dec not in covered
                and call is None
                and name
                and name.endswith((".tool", ".prompt"))
            ):
                add(
                    "prompt" if name.endswith(".prompt") else "tool",
                    function.name,
                    path,
                    range_for_node(dec),
                    range_for_node(function),
                    "unsupported_registration",
                    "nested or unsupported handler form",
                    unsupported=True,
                )
        for node in ast.walk(file.tree):
            check_deadline(context.deadline)
            if node in covered:
                continue
            call = node if isinstance(node, ast.Call) else None
            if call is None:
                continue
            name = qualified_name(call.func) or ""
            method = name.rsplit(".", 1)[-1]
            route = name.split(".")[
                0
            ] in applications and method in ts._HTTP_METHODS | {"api_route"}
            starlette = resolve_name(name, imports) == "starlette.routing.Route"
            if route or starlette:
                handler_node = (
                    decorators.get(call)
                    if route
                    else functions.get(qualified_name(call.args[1]) or "")
                    if len(call.args) > 1
                    else None
                )
                route_name = literal_string(call.args[0]) if call.args else None
                supported = handler_node in functions.values()
                add(
                    "http_route",
                    route_name,
                    path,
                    range_for_node(node),
                    range_for_node(handler_node) if handler_node else None,
                    "computed_route"
                    if route_name is None
                    else "unresolved_handler"
                    if not supported
                    else None,
                    "route path or handler is outside supported recognition",
                )
            elif (
                method
                in {
                    "tool",
                    "add_tool",
                    "register_tool",
                    "call_tool",
                    "prompt",
                    "add_prompt",
                }
                and "." in name
            ):
                registered_function = decorators.get(call)
                if (
                    method == "call_tool"
                    and registered_function
                    and any(
                        region.function is registered_function
                        for region in discover_tool_regions(file)
                    )
                ):
                    continue
                # Client tool calls are uses, not registrations.
                if method == "call_tool" and registered_function is None:
                    continue
                handler_expr = call.args[0] if call.args else None
                local_handler = (
                    functions.get(qualified_name(handler_expr) or "")
                    if handler_expr
                    else None
                )
                imported = (
                    (qualified_name(handler_expr) or "").split(".")[0] in imports
                    if handler_expr
                    else False
                )
                resolved_handler = registered_function or local_handler
                add(
                    "prompt" if "prompt" in method else "tool",
                    local_handler.name
                    if local_handler
                    else literal_string(handler_expr),
                    path,
                    range_for_node(node),
                    range_for_node(resolved_handler) if resolved_handler else None,
                    "imported_implementation"
                    if imported
                    else "unsupported_registration",
                    "imported implementation is not resolved"
                    if imported
                    else "registration uses an unsupported handler form",
                    unsupported=not imported,
                )

    resolved_ts = (
        context.typescript_program.tools() if context.files.typescript_files else ()
    )
    for ts_file in context.files.typescript_files:
        check_deadline(context.deadline)
        source = ts_file.source
        masked = _mask(source)
        local_bindings = [
            ts_binding
            for ts_binding in resolved_ts
            if ts_binding.registration.file == ts_file
        ]
        handled: set[tuple[int, int]] = set()
        for tool in ts.tools_in_file(ts_file):
            if not masked[tool.start : tool.start + 1].strip():
                continue
            reasons = []
            registration = ts.offset_range(source, tool.start, tool.end)
            key = (registration.start_line, registration.start_column)
            handled.add(key)
            ts_binding = next(
                (
                    item
                    for item in local_bindings
                    if (
                        ts_source_range(item.registration.node, ts_file).start_line,
                        ts_source_range(item.registration.node, ts_file).start_column,
                    )
                    == key
                ),
                None,
            )
            handler_symbol = (
                ts_binding.handler
                if ts_binding and ts_binding.handler and ts_binding.handler.function
                else None
            )
            handler_location = (
                ts_source_range(handler_symbol.node, handler_symbol.file)
                if handler_symbol
                else None
            )
            schema_resolved = schema_supported(ts_binding)
            if tool.name is None:
                reasons.append(("computed_name", "tool name is computed"))
            if not tool.handler_start and handler_symbol is None:
                reasons.append(
                    (
                        "unresolved_handler",
                        "imported or unsupported handler implementation",
                    )
                )
            if (
                tool.schema_present
                and tool.input_schema is None
                and not schema_resolved
            ):
                reasons.append(("unresolved_schema", "imported or unsupported schema"))
            add(
                "tool",
                tool.name,
                ts_file.relative_path,
                registration,
                handler_location
                or (
                    ts.offset_range(
                        source,
                        tool.handler_start,
                        tool.handler_start + len(tool.handler),
                    )
                    if tool.handler
                    else None
                ),
                reasons[0][0] if reasons else None,
                reasons[0][1] if reasons else "",
                handler_path=handler_symbol.file.relative_path
                if handler_symbol
                else None,
            )
            if len(reasons) > 1:
                surfaces[-1] = surfaces[-1].model_copy(
                    update={
                        "reasons": tuple(
                            RecognitionReason(
                                code=code,
                                message=message,
                                location=surfaces[-1].location,
                            )
                            for code, message in reasons
                        )
                    }
                )
        for ts_binding in local_bindings:
            registration = ts_source_range(ts_binding.registration.node, ts_file)
            key = (registration.start_line, registration.start_column)
            if key in handled:
                continue
            handler_symbol = (
                ts_binding.handler
                if ts_binding.handler and ts_binding.handler.function
                else None
            )
            reason = (
                "ambiguous_dispatch"
                if ts_binding.name is None
                else "unresolved_handler"
                if handler_symbol is None
                else "unresolved_schema"
                if not schema_supported(ts_binding)
                else None
            )
            add(
                "tool",
                ts_binding.name,
                ts_file.relative_path,
                registration,
                ts_source_range(handler_symbol.node, handler_symbol.file)
                if handler_symbol
                else None,
                reason,
                "tool dispatch, handler or schema cannot be fully resolved"
                if reason
                else "",
                handler_path=handler_symbol.file.relative_path
                if handler_symbol
                else None,
            )
        receivers = ts._http_receivers(source)
        mcp = ts._mcp_server_receivers(source)
        pattern = re.compile(rf"\b({ts._IDENTIFIER})\s*\.\s*({ts._IDENTIFIER})\s*\(")
        for match in pattern.finditer(masked):
            receiver, method = match[1], match[2]
            route = receiver in receivers and method in ts._HTTP_METHODS
            unsupported = receiver in mcp and method in {
                "registerPrompt",
                "prompt",
                "setRequestHandler",
            }
            if not route and not unsupported:
                continue
            match_location = ts.offset_range(source, match.start(), match.end())
            if method == "setRequestHandler" and any(
                (
                    ts_source_range(item.registration.node, ts_file).start_line,
                    ts_source_range(item.registration.node, ts_file).start_column,
                )
                == (match_location.start_line, match_location.start_column)
                for item in local_bindings
            ):
                continue
            close = ts._matching(source, match.end() - 1, "(", ")")
            if close is None:
                continue
            args = ts._split_top_level(source[match.end() : close])
            name = ts._string_literal(args[0]) if args else None
            handler, _, offset = (
                ts._resolve_handler(args[-1], source, ts._functions(source))
                if args
                else ("", (), 0)
            )
            add(
                "http_route" if route else "prompt" if "rompt" in method else "tool",
                name,
                ts_file.relative_path,
                ts.offset_range(source, match.start(), close + 1),
                ts.offset_range(source, offset, offset + len(handler))
                if handler
                else None,
                "unsupported_registration"
                if unsupported
                else "computed_route"
                if name is None
                else "unresolved_handler"
                if not handler
                else None,
                "registration or handler is outside supported recognition",
                unsupported=unsupported,
            )

    flows = []
    for state in states.values():
        for warning in state.warnings:
            if warning.code != "static_flow_unresolved":
                continue
            location = re.search(r"(?:at )?([^\s:]+):(\d+)", warning.message)
            if location:
                line = int(location[2])
                flows.append(
                    RecognitionReason(
                        code=warning.code,
                        message=warning.message,
                        location=FileLocation(
                            path=location[1],
                            range=SourceRange(
                                start_line=line,
                                start_column=1,
                                end_line=line,
                                end_column=2,
                            ),
                        ),
                    )
                )
    check_deadline(context.deadline)
    return StaticCoverage(
        surfaces=tuple(
            sorted(
                surfaces,
                key=lambda item: (
                    item.location.path,
                    item.location.range.start_line,
                    item.location.range.start_column,
                    item.kind,
                ),
            )
        ),
        excluded_rule_ids=tuple(rule for rule in RULE_IDS if rule not in states),
        file_wide_rule_ids=tuple(
            rule
            for rule, state in states.items()
            if rule in {"SENT-005", "SENT-007"} and state.skip_reason is None
        ),
        unresolved_flows=tuple(flows),
    )
