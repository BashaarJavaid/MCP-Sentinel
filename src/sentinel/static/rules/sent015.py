"""Source-only caller URL flow to supported outbound HTTP clients."""

from __future__ import annotations

import ast
import copy
import ipaddress
import json
from dataclasses import replace
from typing import Any
from urllib.parse import urlsplit

from sentinel.static.ast_utils import match_from_node, qualified_name, resolve_name
from sentinel.static.discovery import Symbol
from sentinel.static.model import (
    RuleRunState,
    StaticContext,
    StaticMatch,
    TypeScriptSourceFile,
)
from sentinel.static.path_flow import PathFlow, Value, _key, combine, member_label
from sentinel.static.rules.sent012 import analyze
from sentinel.static.semgrep_ast import source_range
from sentinel.static.traversal import MAX_STATIC_FILE_BYTES
from sentinel.static.typescript_discovery import TypeScriptSymbol, name_of
from sentinel.static.typescript_path_flow import TypeScriptPathFlow
from sentinel.static.typescript_path_flow import analyze as analyze_typescript

Facts = frozenset[tuple[str, str]]
IP_CHECKS = frozenset(
    f"not:{name}"
    for name in (
        "is_private",
        "is_loopback",
        "is_link_local",
        "is_reserved",
        "is_multicast",
        "is_unspecified",
    )
)


def restricted(checks: frozenset[str]) -> bool:
    return "scheme" in checks and (
        "host" in checks or checks >= IP_CHECKS or "is_global" in checks
    )


def public_host(host: str) -> bool:
    """Judge literal allowlist entries without resolving names or making requests."""
    host = host.lower().rstrip(".")
    if not host or host == "localhost" or host.endswith(".localhost"):
        return False
    try:
        address = ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        # Reject ambiguous integer/hex/short IP notations and local hostnames.
        return (
            "." in host
            and all(label and not label.startswith("0x") for label in host.split("."))
            and not all(char in "0123456789." for char in host)
        )
    address = getattr(address, "ipv4_mapped", None) or address
    return address.is_global and not address.is_multicast


def fixed_destination(prefix: str) -> bool:
    try:
        parsed = urlsplit(prefix)
    except ValueError:
        return False
    return (
        parsed.scheme in {"http", "https"}
        and parsed.hostname is not None
        and public_host(parsed.hostname)
        and "/" in prefix.split("://", 1)[-1]
    )


class URLFlow(PathFlow):
    rule_id = "SENT-015"
    helper_state_prefixes = (
        *PathFlow.helper_state_prefixes,
        "#url-conditional:",
        "#url-truth:",
    )

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.parts: dict[str, tuple[str, str]] = {}
        self.predicates: dict[str, tuple[Facts, Facts]] = {}
        self.ip_lists: dict[str, Value] = {}
        self.return_facts: list[list[tuple[Facts | None, Facts | None]]] = []
        self.fact_keys: dict[str, tuple[str, str]] = {}
        self.evaluated: dict[ast.AST, Value] = {}
        self.expression_depth = 0
        self.conditional_checks: dict[str, frozenset[str]] = {}

    def function(self, symbol: Symbol, bindings: dict[str, Value]) -> Value:
        previous = self.evaluated, self.expression_depth
        self.evaluated, self.expression_depth = {}, 0
        self.return_facts.append([])
        try:
            result = super().function(symbol, bindings)
            returns = self.return_facts[-1]
            if (
                returns
                and any(false or true for false, true in returns)
                and result.key not in self.mapping_keys
                and result.key not in self.record_keys
                and result.key not in self.callables
            ):
                result = replace(
                    result,
                    key=_key(
                        "url-predicate",
                        symbol.file.relative_path,
                        symbol.name,
                        result.key,
                        *sorted(
                            _key(name, value.key) for name, value in bindings.items()
                        ),
                    ),
                )
                facts = []
                for truth in (0, 1):
                    possible = [
                        pair[truth] for pair in returns if pair[truth] is not None
                    ]
                    facts.append(
                        frozenset.intersection(
                            *(item for item in possible if item is not None)
                        )
                        if possible
                        else frozenset()
                    )
                self.predicates[result.key] = (facts[0], facts[1])
            return result
        finally:
            self.return_facts.pop()
            self.evaluated, self.expression_depth = previous

    def merge(self, env: dict[str, Value], branches: list[dict[str, Value]]) -> None:
        conditional = {}
        unknown = Value()
        for marker in set().union(*(branch.keys() for branch in branches)):
            if not marker.startswith("#url-truth:"):
                continue
            origin = marker.removeprefix("#url-truth:")
            possible = [
                branch
                for branch in branches
                if branch.get(marker, unknown).key != "False"
            ]
            if not possible or len(possible) == len(branches):
                continue
            checks = frozenset.intersection(
                *(
                    frozenset().union(
                        *(
                            value.url_checks
                            for value in branch.values()
                            if value.key == origin
                        )
                    )
                    for branch in possible
                )
            )
            if checks:
                conditional[origin] = checks
        super().merge(env, branches)
        for origin, checks in conditional.items():
            key = _key("conditional-url", origin, *sorted(checks))
            self.conditional_checks[key] = checks
            env["#url-conditional:" + origin] = Value(key=key)
        for key in env.keys() & self.fact_keys.keys():
            env[key] = replace(
                env[key],
                contained=all(
                    branch.get(key, unknown).contained for branch in branches
                ),
            )

    def statements(
        self,
        symbol: Symbol,
        body: list[ast.stmt],
        env: dict[str, Value],
        returned: list[Value],
    ) -> bool:
        for node in body:
            if isinstance(node, ast.Return):
                super().statements(symbol, [node], env, returned)
                value = returned[-1]
                checked = [
                    key
                    for key in env.keys() & self.fact_keys.keys()
                    if env[key].contained
                ]
                enforced = frozenset(self.fact_keys[key] for key in checked)
                false, true = self.predicates.get(value.key, (frozenset(), frozenset()))
                known = None
                if isinstance(node.value, ast.Constant):
                    known = bool(node.value.value)
                elif node.value is None:
                    known = False
                elif isinstance(node.value, ast.JoinedStr) and any(
                    isinstance(part, ast.Constant) and bool(part.value)
                    for part in node.value.values
                ):
                    known = True
                self.return_facts[-1].append(
                    (
                        None if known is True else false | enforced,
                        None if known is False else true | enforced,
                    )
                )
                if checked:
                    returned[-1] = replace(
                        value,
                        locations=value.locations
                        | frozenset().union(*(env[key].locations for key in checked)),
                    )
                return False
            if isinstance(node, ast.Try) and len(node.body) == 1:
                assignment = node.body[0]
                expression = (
                    assignment.value
                    if isinstance(assignment, (ast.Assign, ast.AnnAssign))
                    else None
                )
                if isinstance(expression, ast.Call) or (
                    isinstance(expression, ast.List) and len(expression.elts) == 1
                ):
                    call = (
                        expression
                        if isinstance(expression, ast.Call)
                        else expression.elts[0]
                    )
                    if (
                        isinstance(call, ast.Call)
                        and len(call.args) == 1
                        and self.external(symbol, call.func, env)
                        == "ipaddress.ip_address"
                        and self.parts.get(
                            self.expression(symbol, call.args[0], env).key, ("", "")
                        )[1]
                        == "hostname"
                    ):
                        # This rule's destination obligation is literal addresses.
                        # ip_address succeeds on that domain. Hostname resolution
                        # and DNS rebinding are not established by this branch.
                        node = copy.copy(node)
                        node.handlers = []
            if isinstance(node, ast.For):
                iterable = self.expression(symbol, node.iter, env)
                item = self.ip_lists.get(iterable.key)
                if item is not None and not any(
                    isinstance(child, (ast.Break, ast.Continue))
                    for statement in node.body
                    for child in ast.walk(statement)
                ):
                    self.assign(node.target, item, env)
                    if not super().statements(symbol, node.body, env, returned):
                        return False
                    if not super().statements(symbol, node.orelse, env, returned):
                        return False
                    continue
            if not super().statements(symbol, [node], env, returned):
                return False
        return True

    def external(self, symbol: Symbol, node: ast.AST, env: dict[str, Value]) -> str:
        name = qualified_name(node) or ""
        root = name.split(".")[0]
        declarations = self.program.bindings[symbol.file.relative_path].get(root, [])
        if root in env or (
            declarations
            and not (
                len(declarations) == 1
                and isinstance(declarations[0], (ast.Import, ast.ImportFrom))
            )
        ):
            return ""
        return resolve_name(name, self.aliases[symbol.file.relative_path])

    def expression(
        self, symbol: Symbol, node: ast.AST | None, env: dict[str, Value]
    ) -> Value:
        if self.expression_depth == 0:
            self.evaluated = {}
        self.expression_depth += 1
        try:
            result = self.expression_value(symbol, node, env)
            if node is not None:
                self.evaluated[node] = result
            return result
        finally:
            self.expression_depth -= 1

    def expression_value(
        self, symbol: Symbol, node: ast.AST | None, env: dict[str, Value]
    ) -> Value:
        result = super().expression(symbol, node, env)
        if isinstance(node, ast.List) and len(node.elts) == 1:
            item = self.evaluated.get(node.elts[0], Value())
            if self.parts.get(item.key, ("", ""))[1] == "ip":
                result = replace(
                    result,
                    key=_key(
                        "ip-list", symbol.file.relative_path, str(node.lineno), item.key
                    ),
                )
                self.ip_lists[result.key] = item
        if isinstance(node, ast.BoolOp):
            values = [self.evaluated.get(child, Value()) for child in node.values]
            parts = {self.parts[v.key] for v in values if v.key in self.parts}
            if len(parts) == 1 and all(
                not v.sources or v.key in self.parts for v in values
            ):
                self.parts[result.key] = next(iter(parts))
        if isinstance(node, ast.Attribute):
            receiver = self.evaluated.get(node.value, Value())
            if (
                self.parts.get(receiver.key, ("", ""))[1] == "ip"
                and node.attr == "ipv4_mapped"
            ):
                result = replace(receiver, maybe_none=True)
            if self.parts.get(receiver.key, ("", ""))[1] == "parsed":
                self.parts[result.key] = (self.parts[receiver.key][0], node.attr)
        if isinstance(node, (ast.BinOp, ast.JoinedStr)):
            result = replace(result, url_checks=frozenset())
        if isinstance(node, ast.FormattedValue) and (
            node.conversion != -1 or node.format_spec is not None
        ):
            result = replace(result, key=_key("formatted", result.key, ast.dump(node)))
        prefix_nodes = (
            node.values
            if isinstance(node, ast.JoinedStr)
            else [node.left, node.right]
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add)
            else []
        )
        if prefix_nodes:
            first_node = prefix_nodes[0]
            first = self.evaluated.get(first_node, Value())
            suffix = (
                member_label(self.evaluated.get(prefix_nodes[1], Value()))
                if len(prefix_nodes) > 1
                else None
            )
            if (
                restricted(first.url_checks)
                and first.instance is None
                and not (
                    isinstance(first_node, ast.FormattedValue)
                    and (
                        first_node.conversion != -1
                        or first_node.format_spec is not None
                    )
                )
                and (
                    "authority" in first.url_checks
                    or (isinstance(suffix, str) and suffix.startswith("/"))
                )
            ):
                result = replace(result, url_checks=first.url_checks | {"authority"})
        prefix = ""
        for part in prefix_nodes:
            value = self.evaluated.get(part, Value())
            try:
                literal = ast.literal_eval(value.key)
            except (ValueError, SyntaxError):
                break
            if value.sources or not isinstance(literal, str):
                break
            # Bound constant expansion by the existing source-size ceiling.
            if len(prefix) + len(literal) > MAX_STATIC_FILE_BYTES:
                break
            prefix += literal
        else:
            if prefix_nodes:
                result = replace(result, key=repr(prefix))
        if fixed_destination(prefix):
            result = replace(
                result, url_checks=frozenset({"scheme", "host", "authority"})
            )
        if isinstance(node, (ast.Compare, ast.BoolOp, ast.UnaryOp, ast.Attribute)):
            self.predicates[result.key] = (
                self.facts(symbol, node, env, False),
                self.facts(symbol, node, env, True),
            )
        return result

    def literals(self, symbol: Symbol, node: ast.AST) -> tuple[str, ...]:
        if isinstance(node, ast.Name):
            declarations = self.program.bindings[symbol.file.relative_path].get(
                node.id, []
            )
            if len(declarations) == 1 and isinstance(
                declarations[0], (ast.Assign, ast.AnnAssign)
            ):
                node = declarations[0].value or node
        try:
            value = ast.literal_eval(node)
        except (ValueError, TypeError):
            return ()
        if isinstance(value, str):
            return (value,)
        if isinstance(value, (tuple, list, set)) and all(
            isinstance(v, str) for v in value
        ):
            return tuple(value)
        return ()

    def facts(
        self, symbol: Symbol, node: ast.AST, env: dict[str, Value], truth: bool
    ) -> Facts:
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return self.facts(symbol, node.operand, env, not truth)
        if isinstance(node, ast.BoolOp):
            children = [self.facts(symbol, child, env, truth) for child in node.values]
            if (truth and isinstance(node.op, ast.And)) or (
                not truth and isinstance(node.op, ast.Or)
            ):
                return frozenset().union(*children)
            return frozenset.intersection(*children) if children else frozenset()
        if isinstance(node, ast.Attribute):
            value = self.evaluated.get(node.value, Value())
            origin, part = self.parts.get(value.key, ("", ""))
            if part == "ip" and (
                "not:" + node.attr in IP_CHECKS or node.attr == "is_global"
            ):
                return frozenset({(origin, ("" if truth else "not:") + node.attr)})
            return frozenset()
        if isinstance(node, (ast.Call, ast.Name)):
            result = self.evaluated.get(node, Value())
            return self.predicates.get(result.key, (frozenset(), frozenset()))[
                int(truth)
            ]
        if not (isinstance(node, ast.Compare) and len(node.ops) == 1):
            return frozenset()
        operator = node.ops[0]
        if not (
            (truth and isinstance(operator, (ast.In, ast.Eq)))
            or (not truth and isinstance(operator, (ast.NotIn, ast.NotEq)))
        ):
            return frozenset()
        checked = self.evaluated.get(node.left, Value())
        origin, part = self.parts.get(checked.key, ("", ""))
        values = self.literals(symbol, node.comparators[0])
        if not values:
            return frozenset()
        check = (
            "scheme"
            if part == "scheme" and set(values) <= {"http", "https"}
            else (
                "host"
                if part == "hostname" and all(public_host(v) for v in values)
                else ""
            )
        )
        return frozenset({(origin, check)}) if check else frozenset()

    def guard(
        self, symbol: Symbol, node: ast.AST, env: dict[str, Value], truth: bool
    ) -> None:
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            self.guard(symbol, node.operand, env, not truth)
            return
        facts = self.facts(symbol, node, env, truth)
        if isinstance(node, ast.Name):
            value = self.evaluated.get(node, Value())
            if value.sources:
                env["#url-truth:" + value.key] = Value(key=repr(truth))
                if truth:
                    selected = env.get("#url-conditional:" + value.key, Value())
                    facts |= frozenset(
                        (value.key, check)
                        for check in self.conditional_checks.get(selected.key, ())
                    )
        if not facts:
            return
        for origin, check in facts:
            key = "#url:" + _key(origin, check)
            self.fact_keys[key] = (origin, check)
            env[key] = Value(
                contained=True,
                locations=frozenset(
                    {(symbol.file.relative_path, getattr(node, "lineno", 1))}
                ),
            )
        for name, value in env.items():
            checks = frozenset(check for origin, check in facts if value.key == origin)
            if checks:
                env[name] = replace(
                    value,
                    url_checks=value.url_checks | checks,
                    locations=value.locations
                    | {(symbol.file.relative_path, getattr(node, "lineno", 1))},
                )

    def call(self, symbol: Symbol, node: ast.Call, env: dict[str, Value]) -> Value:
        external = self.external(symbol, node.func, env)
        name = qualified_name(node.func) or ""
        receiver = self.call_receiver(symbol, node, env)
        method = name.rsplit(".", 1)[-1]
        if receiver.key in self.ip_lists:
            # A known nonempty validation list ceases to prove iteration after mutation.
            self.ip_lists.pop(receiver.key)
        if (
            method == "strip"
            and not node.args
            and not node.keywords
            and receiver.sources
        ):
            return receiver
        if (
            external == "getattr"
            and len(node.args) == 3
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value == "ipv4_mapped"
        ):
            ip = self.expression(symbol, node.args[0], env)
            if self.parts.get(ip.key, ("", ""))[1] == "ip":
                return ip
        if (
            external in {"urllib.parse.urlparse", "urllib.parse.urlsplit"}
            and len(node.args) == 1
        ):
            argument = self.expression(symbol, node.args[0], env)
            result = replace(argument, key=_key("urlparse", argument.key))
            self.parts[result.key] = (argument.key, "parsed")
            return result
        if external == "ipaddress.ip_address" and len(node.args) == 1:
            argument = self.expression(symbol, node.args[0], env)
            origin, part = self.parts.get(argument.key, ("", ""))
            if part == "hostname":
                result = replace(argument, key=_key("ip", argument.key))
                self.parts[result.key] = (origin, "ip")
                return result
        if (
            method == "lower"
            and not node.args
            and self.parts.get(receiver.key, ("", ""))[1] == "scheme"
        ):
            return receiver
        client = self.http_client(receiver, method, env)
        service = self.http_clients.get(receiver.key, "")
        service_request = client and service in {
            "atlassian.Jira",
            "atlassian.Confluence",
        }
        if service_request:
            named_request = method == "myself" and service == "atlassian.Jira"
            if named_request or method in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "request",
            }:
                args = [self.expression(symbol, arg, env) for arg in node.args]
                keywords = {
                    kw.arg: self.expression(symbol, kw.value, env)
                    for kw in node.keywords
                }
                if (
                    not self.http_client(receiver, "request", env)
                    or (named_request and not self.http_client(receiver, "get", env))
                    or self.member_key(receiver, "url_joiner") in env
                ):
                    self.unresolved(
                        symbol, node, "replaced service request implementation"
                    )
                    return Value()
                if (
                    None in keywords
                    or any(isinstance(arg, ast.Starred) for arg in node.args)
                    or (named_request and (args or keywords))
                ):
                    self.unresolved(
                        symbol, node, "unresolved service request arguments"
                    )
                    return Value()
                url = self.member(receiver, "url", env)
                if not named_request:
                    index = int(method == "request")
                    if (
                        len(args) > index + 1
                        or (
                            method != "request"
                            and len(args) <= index
                            and "path" not in keywords
                        )
                        or (len(args) > index and "path" in keywords)
                    ):
                        self.unresolved(symbol, node, "unresolved service request path")
                        return Value()
                    path = keywords.get(
                        "path", args[index] if len(args) > index else Value()
                    )
                    absolute = self.truth_value(
                        keywords.get("absolute", Value(key="False")), env
                    )
                    if absolute is True:
                        url = path
                    elif absolute is None:
                        url = combine([url, path])
                self.url_sink(symbol, node, url, name)
                return Value()
        request = method in {
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "head",
            "options",
            "request",
        } and (
            (client and not service_request)
            or external in {f"{library}.{method}" for library in ("requests", "httpx")}
        )
        if request or external == "urllib.request.urlopen":
            index = int(method == "request")
            argument_node = next(
                (kw.value for kw in node.keywords if kw.arg == "url"),
                node.args[index] if len(node.args) > index else None,
            )
            url = self.expression(symbol, argument_node, env)
            self.url_sink(symbol, node, url, name)
            return Value()
        result = super().call(symbol, node, env)
        helper = self.program.resolve_in(symbol, name)
        if not helper and not (
            method == "get" and (receiver.sources or receiver.key in self.mapping_keys)
        ):
            result = replace(result, url_checks=frozenset())
        return result

    def url_sink(self, symbol: Symbol, node: ast.Call, url: Value, name: str) -> None:
        if url.sources and not restricted(url.url_checks):
            self.state.matches.append(
                replace(
                    match_from_node(self.rule_id, symbol.file, node, "url-flow"),
                    captures={
                        "sink_name": name,
                        "flow_locations": json.dumps(
                            sorted(
                                url.locations
                                | {(symbol.file.relative_path, node.lineno)}
                            )
                        ),
                    },
                )
            )


def detect(context: StaticContext, state: RuleRunState) -> None:
    analyze(
        context.python_program,
        state,
        context.deadline,
        flow=URLFlow(context.python_program, state, context.deadline),
        entries=(*context.python_program.tools(), *context.python_http_handlers),
    )
    if context.files.typescript_files:
        analyze_typescript(
            context.typescript_program,
            state,
            flow=TypeScriptURLFlow(context.typescript_program, state),
            entries=(
                *context.typescript_program.tools(),
                *context.typescript_http_handlers,
            ),
        )


class TypeScriptURLFlow(TypeScriptPathFlow):
    rule_id = "SENT-015"

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.url_parts: dict[str, tuple[str, str]] = {}

    def expression(
        self, file: TypeScriptSourceFile, node: Any, env: dict[str, Value]
    ) -> Value:
        if isinstance(node, dict) and "New" in node:
            _, type_, _, arguments = node["New"]
            constructor = type_.get("t", {}).get("TyExpr", {})
            name = name_of(constructor) or ""
            symbol = self.program.resolve(file, name)
            if (
                (
                    name == "URL"
                    and name not in env
                    and name not in self.program.bindings[file.relative_path]
                )
                or (
                    symbol
                    and symbol.external in {"node:url.URL", "url.URL"}
                    and name not in env
                )
            ) and len(arguments[1]) == 1:
                argument = self.expression(file, arguments[1][0].get("Arg", {}), env)
                result = replace(argument, key=_key("parsed-url", argument.key))
                self.url_parts[result.key] = (argument.key, "parsed")
                return result
        result = super().expression(file, node, env)
        checks = frozenset(
            check
            for check in ("scheme", "host")
            if env.get(f"#guard:url:{result.key}:{check}", Value()).contained
        )
        return replace(result, url_checks=result.url_checks | checks)

    def member(self, value: Value, name: str) -> Value:
        result = replace(super().member(value, name), url_checks=frozenset())
        origin, part = self.url_parts.get(value.key, ("", ""))
        if part == "parsed" and value.key not in self.invalidated_objects:
            self.url_parts[result.key] = (origin, name)
        return result

    def restriction(self, value: Value, literals: Any) -> frozenset[str]:
        origin, part = self.url_parts.get(value.key, ("", ""))
        if isinstance(literals, str):
            literals = [literals]
        if (
            not isinstance(literals, (list, tuple))
            or not literals
            or not all(isinstance(v, str) for v in literals)
        ):
            return frozenset()
        check = (
            "scheme"
            if part == "protocol" and set(literals) <= {"http:", "https:"}
            else (
                "host"
                if part == "hostname" and all(public_host(v) for v in literals)
                else ""
            )
        )
        return frozenset({f"#guard:url:{origin}:{check}"}) if check else frozenset()

    def call(
        self, file: TypeScriptSourceFile, node: dict[str, Any], env: dict[str, Value]
    ) -> Value:
        callee, arguments = node["Call"]
        name = name_of(callee) or ""
        symbol = (
            self.callables.get(self.call_value(file, callee, env).key)
            if "Special" not in callee
            else None
        )
        external = (symbol.external or "").removeprefix("node:") if symbol else ""
        argument_nodes = [item.get("Arg", item) for item in arguments[1]]
        is_fetch = (
            name == "fetch"
            and "fetch" not in env
            and "fetch" not in self.program.bindings[file.relative_path]
        )
        request = (
            is_fetch
            or external
            in {
                "node-fetch",
                "node-fetch.default",
                "undici.fetch",
                "axios",
                "axios.default",
            }
            or external
            in {
                f"{library}.{method}"
                for library in (
                    "axios",
                    "axios.default",
                    "http",
                    "http.default",
                    "https",
                    "https.default",
                )
                for method in (
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "head",
                    "request",
                )
            }
        )
        if request and argument_nodes:
            url = self.call_value(file, argument_nodes[0], env)
            if url.sources and not restricted(url.url_checks):
                location = source_range(node, file)
                self.state.matches.append(
                    StaticMatch(
                        rule_id=self.rule_id,
                        path=file.relative_path,
                        range=location,
                        snippet=self.program.text(file, node),
                        match_kinds=("url-flow",),
                        captures={
                            "sink_name": name,
                            "flow_locations": json.dumps(
                                sorted(
                                    url.locations
                                    | {(file.relative_path, location.start_line)}
                                )
                            ),
                        },
                    )
                )
            return Value()
        result = super().call(file, node, env)
        operator = callee.get("Special", [{}])[0]
        if (
            isinstance(operator, dict)
            and (operator.get("Op") == "Plus" or "ConcatString" in operator)
            and argument_nodes
        ):
            prefix = ""
            for part in argument_nodes:
                literal = self.program.literal(self.program.resolve_node(file, part))
                if literal is None:
                    break
                prefix += literal
            if fixed_destination(prefix):
                result = replace(result, url_checks=frozenset({"scheme", "host"}))
        if (
            isinstance(operator, dict)
            and operator.get("Op") in {"PhysEq", "NotPhysEq", "Eq", "NotEq"}
            and len(argument_nodes) == 2
        ):
            for index in (0, 1):
                value = self.call_value(file, argument_nodes[index], env)
                literals = self.program.literal(
                    TypeScriptSymbol(file, argument_nodes[1 - index])
                )
                facts = self.restriction(value, literals)
                if facts:
                    self.conditions[result.key] = (
                        (frozenset(), facts)
                        if operator["Op"] in {"PhysEq", "Eq"}
                        else (facts, frozenset())
                    )
        if (
            "DotAccess" in callee
            and name_of(callee["DotAccess"][2]) == "includes"
            and len(argument_nodes) == 1
        ):
            container = callee["DotAccess"][0].get("Container")
            literal_array = (
                [
                    self.program.literal(TypeScriptSymbol(file, item))
                    for item in container[1][1]
                ]
                if container
                else []
            )
            facts = self.restriction(
                self.call_value(file, argument_nodes[0], env), literal_array
            )
            self.conditions[result.key] = (frozenset(), facts)
        return result
