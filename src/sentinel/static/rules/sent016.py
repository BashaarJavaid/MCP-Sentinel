"""Caller-to-operator credential selection across discovered HTTP boundaries."""

from __future__ import annotations

import ast
import json
from dataclasses import replace
from typing import Any
from urllib.parse import urljoin, urlsplit

from sentinel.static.ast_utils import (
    match_from_node,
    qualified_name,
    resolve_name,
)
from sentinel.static.discovery import PythonProgram, Symbol
from sentinel.static.model import (
    RuleRunState,
    StaticContext,
    StaticMatch,
    TypeScriptSourceFile,
)
from sentinel.static.path_flow import (
    UNKNOWN_VALUE,
    PathFlow,
    Value,
    _key,
    combine,
    member_label,
)
from sentinel.static.rules.sent012 import analyze
from sentinel.static.typescript_discovery import name_of
from sentinel.static.typescript_path_flow import TypeScriptPathFlow
from sentinel.static.typescript_path_flow import analyze as analyze_typescript


class CredentialFlow(PathFlow):
    rule_id = "SENT-016"
    helper_state_prefixes = (
        *PathFlow.helper_state_prefixes,
        "#absent:",
        "#credential:",
    )

    def __init__(
        self, program: PythonProgram, state: RuleRunState, deadline: float
    ) -> None:
        super().__init__(program, state, deadline)
        self.evaluated: dict[ast.AST, Value] = {}
        self.environment_text: dict[str, tuple[str, str]] = {}
        self.operator_predicates: dict[str, tuple[str, bool]] = {}
        self.basic_auth_fields: dict[str, tuple[str, ...]] = {}

    def function(self, symbol: Symbol, bindings: dict[str, Value]) -> Value:
        if not bindings.get("#credential:http", UNKNOWN_VALUE).contained and any(
            source.startswith("http:")
            for value in bindings.values()
            for source in value.sources
        ):
            bindings["#credential:http"] = Value(contained=True)
        for name, value in bindings.items():
            if value.operator_credential:
                bindings[name] = self.conditioned_credential(value, bindings)
        return super().function(symbol, bindings)

    def conditioned_credential(self, value: Value, env: dict[str, Value]) -> Value:
        if not value.operator_credential:
            return value
        absent = [
            current
            for name, current in env.items()
            if name.startswith(("#absent:", "#credential:excluded:"))
            and current.contained
            and any(source.startswith("http:") for source in current.sources)
        ]
        if absent:
            value = replace(
                value,
                sources=value.sources
                | frozenset().union(*(item.sources for item in absent)),
                locations=value.locations
                | frozenset().union(*(item.locations for item in absent)),
                credential_fallback=True,
            )
        settings = {
            name.removeprefix("#credential:opt-in:"): current
            for name, current in env.items()
            if name.startswith("#credential:opt-in:") and current.contained
        }
        if settings:
            value = replace(
                value,
                operator_opt_in=value.operator_opt_in | frozenset(settings),
                locations=value.locations
                | frozenset().union(
                    *(current.locations for current in settings.values())
                ),
            )
        return value

    def member(self, value: Value, member: object, env: dict[str, Value]) -> Value:
        result = super().member(value, member, env)
        if (
            result.operator_credential
            and value.operator_opt_in
            and "#member:unknown:" + value.key not in env
        ):
            result = replace(
                result,
                operator_opt_in=result.operator_opt_in | value.operator_opt_in,
                locations=result.locations | value.locations,
            )
        return result

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

    def assign(self, target: ast.AST, value: Value, env: dict[str, Value]) -> None:
        if isinstance(target, ast.Name):
            original = env.get(target.id, UNKNOWN_VALUE)
            if (
                value.operator_credential
                and env.get("#absent:" + original.key, UNKNOWN_VALUE).contained
            ):
                value = replace(combine([value, original]), credential_fallback=True)
        super().assign(target, value, env)

    def merge(self, env: dict[str, Value], branches: list[dict[str, Value]]) -> None:
        empty = UNKNOWN_VALUE
        http = [
            branch
            for branch in branches
            if branch.get("#credential:http", empty).contained
        ]
        # ponytail: follow the successful HTTP getter path; exception-prefix
        # correlation needs separate state. Keep the stdio alternative distinct.
        branches = http or branches
        super().merge(env, branches)
        if http:
            env["#credential:http"] = Value(contained=True)
        for name in env:
            if name.startswith(
                ("#absent:", "#credential:excluded:", "#credential:opt-in:")
            ):
                first = branches[0].get(name, empty) if branches else empty
                if all(branch.get(name, empty) is first for branch in branches[1:]):
                    env[name] = first
                    continue
                env[name] = (
                    replace(
                        combine([branch[name] for branch in branches]), contained=True
                    )
                    if all(branch.get(name, empty).contained for branch in branches)
                    else empty
                )

    def guard(
        self, symbol: Symbol, node: ast.AST, env: dict[str, Value], truth: bool
    ) -> None:
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            self.guard(symbol, node.operand, env, not truth)
            return
        if isinstance(node, ast.BoolOp):
            conjunctive = isinstance(node.op, ast.And)
            for child in node.values:
                if truth == conjunctive or all(
                    other is child
                    or self.truth_value(self.evaluated.get(other, UNKNOWN_VALUE), env)
                    is conjunctive
                    for other in node.values
                ):
                    self.guard(symbol, child, env, truth)
        if (
            isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.comparators[0], ast.Constant)
            and node.comparators[0].value is None
        ):
            if isinstance(node.ops[0], (ast.Is, ast.Eq)):
                self.guard(symbol, node.left, env, not truth)
            elif isinstance(node.ops[0], (ast.IsNot, ast.NotEq)):
                self.guard(symbol, node.left, env, truth)
            return
        value = self.evaluated.get(node, UNKNOWN_VALUE)
        http_input = any(source.startswith("http:") for source in value.sources)
        predicate = self.operator_predicates.get(value.key)
        if predicate is not None and truth != predicate[1]:
            env["#credential:opt-in:" + predicate[0]] = Value(
                contained=True,
                locations=value.locations
                | {(symbol.file.relative_path, getattr(node, "lineno", 1))},
            )
        if not isinstance(node, (ast.Name, ast.Attribute, ast.Subscript)):
            if not truth and http_input:
                env["#credential:excluded:" + value.key] = replace(
                    value,
                    contained=True,
                    locations=value.locations
                    | {(symbol.file.relative_path, getattr(node, "lineno", 1))},
                )
            return
        if http_input:
            if not truth:
                env["#absent:" + value.key] = replace(
                    value,
                    contained=True,
                    locations=value.locations
                    | {(symbol.file.relative_path, getattr(node, "lineno", 1))},
                )
            for name, current in env.items():
                if current.key == value.key:
                    env[name] = replace(
                        current,
                        credential_present=truth,
                        locations=current.locations
                        | {(symbol.file.relative_path, getattr(node, "lineno", 1))},
                    )

    def expression(
        self, symbol: Symbol, node: ast.AST | None, env: dict[str, Value]
    ) -> Value:
        result = self.conditioned_credential(self._expression(symbol, node, env), env)
        if node is not None:
            self.evaluated[node] = result
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            selected = self.environment_text.get(
                self.evaluated.get(node.left, UNKNOWN_VALUE).key
            )
            if selected and isinstance(node.ops[0], (ast.In, ast.NotIn)):
                try:
                    accepted = ast.literal_eval(node.comparators[0])
                except (ValueError, TypeError, SyntaxError):
                    accepted = None
                if isinstance(accepted, (tuple, list, set)) and all(
                    isinstance(item, str) for item in accepted
                ):
                    self.operator_predicates[result.key] = (
                        selected[0],
                        (selected[1] in accepted) != isinstance(node.ops[0], ast.NotIn),
                    )
        return result

    def _expression(
        self, symbol: Symbol, node: ast.AST | None, env: dict[str, Value]
    ) -> Value:
        if (
            isinstance(node, ast.Subscript)
            and self.external(symbol, node.value, env) == "os.environ"
            and self.program.external(symbol, node.value) == "os.environ"
        ):
            return Value(
                key=_key(symbol.file.relative_path, str(node.lineno), ast.dump(node)),
                operator_credential=True,
                locations=frozenset({(symbol.file.relative_path, node.lineno)}),
            )
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            values = []
            for expression in node.values:
                value = self.expression(symbol, expression, env)
                values.append(value)
                if value.credential_present or self.truth_value(value, env) is True:
                    break
            result = combine(values)
            if any(v.sources and not v.credential_present for v in values[:-1]) and any(
                v.operator_credential for v in values[1:]
            ):
                result = replace(result, credential_fallback=True)
            return result
        return super().expression(symbol, node, env)

    def call(self, symbol: Symbol, node: ast.Call, env: dict[str, Value]) -> Value:
        external = self.external(symbol, node.func, env)
        if (
            external
            in {"httpx.BasicAuth", "requests.auth.HTTPBasicAuth", "aiohttp.BasicAuth"}
            and self.program.external(symbol, node.func) == external
        ):
            fields: tuple[str, ...] = (
                ("login", "password")
                if external == "aiohttp.BasicAuth"
                else ("username", "password")
            )
            arguments = [self.expression(symbol, arg, env) for arg in node.args]
            keywords = {
                keyword.arg: self.expression(symbol, keyword.value, env)
                for keyword in node.keywords
            }
            value = combine(
                [*arguments, *keywords.values()],
                _key(
                    external,
                    symbol.file.relative_path,
                    str(node.lineno),
                    str(node.col_offset),
                    *self.call_sites,
                ),
            )
            required = fields[:1] if external == "aiohttp.BasicAuth" else fields
            if (
                len(arguments) <= 2
                and not any(isinstance(arg, ast.Starred) for arg in node.args)
                and all(
                    name in fields
                    or (name == "encoding" and external == "aiohttp.BasicAuth")
                    for name in keywords
                )
                and not any(field in keywords for field in fields[: len(arguments)])
                and all(
                    index < len(arguments) or field in keywords
                    for index, field in enumerate(required)
                )
            ):
                self.record_keys.add(value.key)
                for index, field in enumerate(fields):
                    env[self.member_key(value, field)] = (
                        arguments[index]
                        if index < len(arguments)
                        else keywords.get(field, UNKNOWN_VALUE)
                    )
                if external == "httpx.BasicAuth":
                    fields = ("_auth_header",)
                    env[self.member_key(value, fields[0])] = value
                self.basic_auth_fields[value.key] = fields
                return replace(value, maybe_none=False, maybe_missing=False)
            return value
        service_client = external in {"atlassian.Jira", "atlassian.Confluence"} and (
            self.program.external(symbol, node.func) == external
        )
        if external in {"os.getenv", "os.environ.get"} and (
            self.program.external(symbol, node.func) == external
        ):
            args = [self.expression(symbol, arg, env) for arg in node.args]
            result = Value(
                key=_key(
                    symbol.file.relative_path,
                    str(node.lineno),
                    ast.dump(node),
                    *self.call_sites,
                    *(arg.key for arg in args),
                ),
                operator_credential=True,
                locations=frozenset({(symbol.file.relative_path, node.lineno)}),
            )
            if len(args) == 2 and not node.keywords:
                name, default = (member_label(arg) for arg in args)
                if isinstance(name, str) and isinstance(default, str):
                    self.environment_text[result.key] = (name, default)
            return result
        method = node.func.attr if isinstance(node.func, ast.Attribute) else ""
        receiver = self.call_receiver(symbol, node, env)
        client_request = self.http_client(receiver, method, env) and method in {
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "head",
            "options",
            "request",
        }
        if (
            service_client
            or client_request
            or external
            in {
                f"{library}.{method}"
                for library in ("requests", "httpx")
                for method in (
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                    "head",
                    "options",
                    "request",
                )
            }
        ):
            # Shared construction retains the client/session identity and evaluates
            # arguments once. Reuse those values for the credential sink check.
            constructed = super().call(symbol, node, env) if service_client else None
            arguments = [
                self.evaluated.get(argument, UNKNOWN_VALUE)
                if service_client
                else self.expression(symbol, argument, env)
                for argument in node.args
            ]
            keywords = {
                keyword.arg: (
                    self.evaluated.get(keyword.value, UNKNOWN_VALUE)
                    if service_client
                    else self.expression(symbol, keyword.value, env)
                )
                for keyword in node.keywords
            }
            credentials: list[Value] = []
            if service_client:
                credentials.extend(
                    keywords[field]
                    for field in ("token", "password")
                    if field in keywords
                )
            else:
                library = (
                    self.http_clients.get(receiver.key) if client_request else None
                )
                auth = keywords.get("auth")
                if library and (
                    auth is None
                    or (
                        auth.key == "None"
                        and library in {"requests.Session", "aiohttp.ClientSession"}
                    )
                ):
                    auth = self.member(
                        receiver,
                        "_default_auth"
                        if library == "aiohttp.ClientSession"
                        else "auth",
                        env,
                    )
                    if library == "aiohttp.ClientSession":
                        base = member_label(self.member(receiver, "_base_url", env))
                        index = 1 if method == "request" else 0
                        url = member_label(
                            keywords.get(
                                "url",
                                arguments[index]
                                if len(arguments) > index
                                else UNKNOWN_VALUE,
                            )
                        )
                        if (base is None or isinstance(base, str)) and isinstance(
                            url, str
                        ):
                            try:
                                origin, destination = (
                                    urlsplit(base or ""),
                                    urlsplit(urljoin(base or "", url)),
                                )
                                if destination.username is not None or (
                                    base is not None
                                    and (
                                        origin.scheme,
                                        origin.hostname,
                                        origin.port
                                        or (443 if origin.scheme == "https" else 80),
                                    )
                                    != (
                                        destination.scheme,
                                        destination.hostname,
                                        destination.port
                                        or (
                                            443 if destination.scheme == "https" else 80
                                        ),
                                    )
                                ):
                                    auth = Value(key="None")
                            except ValueError:
                                self.unresolved(
                                    symbol, node, "invalid aiohttp request URL"
                                )
                                return UNKNOWN_VALUE
                if auth is not None:
                    if auth.key in self.basic_auth_fields:
                        credentials.append(
                            combine(
                                [
                                    self.member(auth, name, env)
                                    for name in self.basic_auth_fields[auth.key]
                                ]
                            )
                        )
                    else:
                        credentials.append(auth)
                for field in ("headers", "params", "data", "json"):
                    values: dict[str, Value] = {}
                    mappings = []
                    if library and field in {"headers", "params"}:
                        mappings.append(self.member(receiver, field, env))
                    if field in keywords:
                        mappings.append(keywords[field])
                    for mapping in mappings:
                        values.update(
                            (name.lower() if field == "headers" else name, env[marker])
                            for name, marker in self.members.get(
                                mapping.key, {}
                            ).items()
                            if isinstance(name, str) and marker in env
                        )
                    if (
                        field == "headers"
                        and library == "aiohttp.ClientSession"
                        and auth is not None
                        and auth.key != "None"
                        and not auth.maybe_none
                        and not auth.maybe_missing
                        and auth.key in self.basic_auth_fields
                        and "authorization" in values
                    ):
                        self.unresolved(
                            symbol,
                            node,
                            "aiohttp rejects combined auth and Authorization header",
                        )
                        return UNKNOWN_VALUE
                    if (
                        field == "headers"
                        and auth is not None
                        and not auth.maybe_none
                        and not auth.maybe_missing
                        and (
                            (
                                auth.key in self.basic_auth_fields
                                and "#member:unknown:" + auth.key not in env
                            )
                            or (
                                self.sequence_keys.get(auth.key) is False
                                and len(self.sequence_elements(auth, env) or ()) == 2
                                and library != "aiohttp.ClientSession"
                            )
                        )
                    ):
                        values.pop("authorization", None)
                    credentials.extend(
                        value
                        for name, value in values.items()
                        if name.lower()
                        in {"authorization", "x-api-key", "access_token", "api_key"}
                    )
            conditioned = [
                self.conditioned_credential(value, env) for value in credentials
            ]
            crossing = combine(
                [value for value in conditioned if value.credential_fallback]
            )
            if crossing.credential_fallback and any(
                source.startswith("http:") for source in crossing.sources
            ):
                settings = {
                    key.removeprefix("#credential:opt-in:"): value
                    for key, value in env.items()
                    if key.startswith("#credential:opt-in:") and value.contained
                }
                setting_names = settings.keys() | crossing.operator_opt_in
                locations = crossing.locations | frozenset().union(
                    *(value.locations for value in settings.values())
                )
                self.state.matches.append(
                    replace(
                        match_from_node(
                            self.rule_id, symbol.file, node, "credential-fallback"
                        ),
                        captures={
                            "sink_name": qualified_name(node.func) or "request",
                            **(
                                {
                                    "credential_operator_opt_in": json.dumps(
                                        sorted(setting_names)
                                    )
                                }
                                if setting_names
                                else {}
                            ),
                            "flow_locations": json.dumps(
                                sorted(
                                    locations
                                    | {(symbol.file.relative_path, node.lineno)}
                                )
                            ),
                        },
                    )
                )
            return constructed if constructed is not None else UNKNOWN_VALUE
        result = super().call(symbol, node, env)
        if (
            method == "get"
            and receiver.key in self.context_variables
            and result.key == "None"
            and env.get("#credential:http", UNKNOWN_VALUE).contained
            and env.get("#http:no-request", UNKNOWN_VALUE).key != "True"
        ):
            result = replace(
                result,
                key=_key("absent-http-context", receiver.key),
                sources=frozenset({"http:request-context"}),
                locations=result.locations | {(symbol.file.relative_path, node.lineno)},
                maybe_none=True,
            )
            self.path_conditions[result.key] = (frozenset(), None)
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "lower"
            and not node.args
            and not node.keywords
        ):
            original = self.evaluated.get(node.func.value, UNKNOWN_VALUE)
            selected = self.environment_text.get(original.key)
            if selected:
                result = replace(
                    original,
                    key=_key(original.key, "lower"),
                    locations=original.locations
                    | {(symbol.file.relative_path, node.lineno)},
                )
                self.environment_text[result.key] = (selected[0], selected[1].lower())
        if (
            external == "fastmcp.server.dependencies.get_http_request"
            and self.program.external(symbol, node.func) == external
            and not node.args
            and not node.keywords
        ):
            env["#credential:http"] = Value(contained=True)
        return result


def detect(context: StaticContext, state: RuleRunState) -> None:
    program = context.python_program
    flow = CredentialFlow(program, state, context.deadline)
    analyze(
        program,
        state,
        context.deadline,
        flow=flow,
        entries=(*program.tools(), *context.python_http_handlers),
    )
    if context.files.typescript_files:
        analyze_typescript(
            context.typescript_program,
            state,
            flow=TypeScriptCredentialFlow(context.typescript_program, state),
            entries=(
                *context.typescript_program.tools(),
                *context.typescript_http_handlers,
            ),
        )


class TypeScriptCredentialFlow(TypeScriptPathFlow):
    rule_id = "SENT-016"

    def expression(
        self, file: TypeScriptSourceFile, node: Any, env: dict[str, Value]
    ) -> Value:
        name = name_of(node) if isinstance(node, dict) else None
        if (
            name is not None
            and name.startswith("process.env.")
            and "process" not in env
            and "process" not in self.program.bindings[file.relative_path]
        ):
            return Value(
                key=_key(file.relative_path, name),
                operator_credential=True,
                locations=frozenset(
                    {
                        (
                            file.relative_path,
                            self.program.source_range(node, file).start_line,
                        )
                    }
                ),
            )
        result = super().expression(file, node, env)
        if env.get(f"#guard:credential:present:{result.key}", UNKNOWN_VALUE).contained:
            result = replace(result, credential_present=True)
        if result.credential_present:
            result = replace(result, key=_key(result.key, "credential-present"))
            self.conditions[result.key] = (None, frozenset())
        elif result.sources and result.key not in self.conditions:
            self.conditions[result.key] = (
                frozenset({f"#guard:credential:absent:{result.key}"}),
                frozenset({f"#guard:credential:present:{result.key}"}),
            )
        return result

    def member(self, value: Value, name: str, env: dict[str, Value]) -> Value:
        if name in self.object_fields(value, env) and not (
            {value.key, self.record_roots.get(value.key, value.key)}
            & self.invalidated_objects
        ):
            return self.object_fields(value, env)[name]
        return replace(
            super().member(value, name, env),
            credential_present=False,
            credential_fallback=False,
        )

    def pattern(self, node: Any, value: Value, env: dict[str, Value]) -> None:
        name = name_of(node) if isinstance(node, dict) else None
        original = env.get(name or "", UNKNOWN_VALUE)
        if (
            value.operator_credential
            and env.get(
                f"#guard:credential:absent:{original.key}", UNKNOWN_VALUE
            ).contained
        ):
            value = replace(combine([value, original]), credential_fallback=True)
        super().pattern(node, value, env)

    def guard(self, value: Value, env: dict[str, Value], truth: bool) -> None:
        super().guard(value, env, truth)
        for name, current in env.items():
            if env.get(
                f"#guard:credential:present:{current.key}", UNKNOWN_VALUE
            ).contained:
                env[name] = replace(current, credential_present=True)

    def call(
        self, file: TypeScriptSourceFile, node: dict[str, Any], env: dict[str, Value]
    ) -> Value:
        callee, arguments = node["Call"]
        operator = callee.get("Special", [{}])[0]
        if isinstance(operator, dict) and operator.get("Op") in {"Or", "Nullish"}:
            values = []
            for argument in arguments[1]:
                value = self.call_value(file, argument.get("Arg", argument), env)
                values.append(value)
                if value.credential_present or (
                    operator["Op"] == "Or" and self.condition(value)[0] is None
                ):
                    break
            result = combine(values)
            if any(v.sources and not v.credential_present for v in values[:-1]) and any(
                v.operator_credential for v in values[1:]
            ):
                result = replace(result, credential_fallback=True)
            return result
        name = name_of(callee) or ""
        binding = (
            self.callables.get(self.call_value(file, callee, env).key)
            if "Special" not in callee
            else None
        )
        external = binding.external if binding else None
        is_fetch = (
            name == "fetch"
            and "fetch" not in env
            and "fetch" not in self.program.bindings[file.relative_path]
        ) or external in {"node-fetch", "node-fetch.default", "undici.fetch"}
        if is_fetch:
            args = [
                self.call_value(file, argument.get("Arg", argument), env)
                for argument in arguments[1]
            ]
            options = self.object_fields(args[1], env) if len(args) > 1 else {}
            headers = self.object_fields(options.get("headers", UNKNOWN_VALUE), env)
            credentials = [
                value
                for field, value in headers.items()
                if field.lower() in {"authorization", "x-api-key"}
                and value.credential_fallback
            ]
            crossing = combine(credentials)
            if crossing.credential_fallback and any(
                source.startswith("http:") for source in crossing.sources
            ):
                location = self.program.source_range(node, file)
                self.state.matches.append(
                    StaticMatch(
                        self.rule_id,
                        file.relative_path,
                        location,
                        self.program.text(file, node),
                        match_kinds=("credential-fallback",),
                        captures={
                            "sink_name": name,
                            "flow_locations": json.dumps(
                                sorted(
                                    crossing.locations
                                    | {(file.relative_path, location.start_line)}
                                )
                            ),
                        },
                    )
                )
            return UNKNOWN_VALUE
        return super().call(file, node, env)
