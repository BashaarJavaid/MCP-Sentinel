"""Source-only branch paths and literal checks used by safety exemptions."""

from __future__ import annotations

import ast
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from sentinel.static.execution import check_deadline


@dataclass(frozen=True)
class Condition:
    test: ast.expr
    truth: bool


def paths(
    body: Sequence[ast.AST], deadline: float
) -> Iterator[tuple[ast.AST | Condition, ...]]:
    # ponytail: enumerate branches; merge proof states if branching hits the deadline.
    pending: list[tuple[tuple[ast.AST | Condition, ...], tuple[ast.AST, ...]]] = [
        ((), tuple(body))
    ]
    while pending:
        check_deadline(deadline)
        prefix, remaining = pending.pop()
        if not remaining:
            yield prefix
            continue
        node, *tail = remaining
        if isinstance(node, ast.If):
            for truth, branch in ((False, node.orelse), (True, node.body)):
                pending.append(
                    ((*prefix, Condition(node.test, truth)), (*branch, *tail))
                )
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            pending.append(((*prefix, node), (*node.body, *tail)))
        elif isinstance(node, (ast.Return, ast.Raise)):
            yield (*prefix, node)
        else:
            pending.append(((*prefix, node), tuple(tail)))


def literal(node: ast.AST | None, constants: dict[str, ast.expr]) -> object:
    seen: set[str] = set()
    while isinstance(node, ast.Name) and node.id in constants and node.id not in seen:
        seen.add(node.id)
        node = constants[node.id]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        left, right = literal(node.left, constants), literal(node.right, constants)
        if isinstance(left, str) and isinstance(right, int) and 0 <= right <= 4096:
            return left * right
    try:
        return ast.literal_eval(node) if node is not None else None
    except (ValueError, TypeError, SyntaxError):
        return None


def constants(tree: ast.Module) -> dict[str, ast.expr]:
    result: dict[str, ast.expr] = {}
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    result[target.id] = node.value
    return result


def reference(node: ast.AST | None, aliases: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        base = reference(node.value, aliases)
        return f"{base}.{node.attr}" if base else None
    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
        base = reference(node.value, aliases)
        return f"{base}.{node.slice.value!s}" if base else None
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
        and node.args
    ):
        base = reference(node.func.value, aliases)
        field = literal(node.args[0], {})
        return f"{base}.{field}" if base and isinstance(field, str) else None
    return None


def type_guard(test: ast.expr, truth: bool, aliases: dict[str, str]) -> set[str]:
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return type_guard(test.operand, not truth, aliases)
    if isinstance(test, ast.BoolOp) and (
        (isinstance(test.op, ast.And) and truth)
        or (isinstance(test.op, ast.Or) and not truth)
    ):
        return set().union(
            *(type_guard(value, truth, aliases) for value in test.values)
        )
    if (
        truth
        and isinstance(test, ast.Call)
        and isinstance(test.func, ast.Name)
        and test.func.id == "isinstance"
        and len(test.args) == 2
        and isinstance(test.args[1], ast.Name)
        and test.args[1].id in {"str", "int", "float", "bool", "bytes"}
    ):
        ref = reference(test.args[0], aliases)
        return {ref} if ref else set()
    if (
        isinstance(test, ast.Compare)
        and len(test.ops) == 1
        and isinstance(test.ops[0], (ast.In, ast.NotIn))
    ):
        values = literal(test.comparators[0], {})
        if (
            truth == isinstance(test.ops[0], ast.In)
            and isinstance(values, (tuple, list, set))
            and values
            and all(isinstance(value, (str, int, float, bool)) for value in values)
        ):
            ref = reference(test.left, aliases)
            return {ref} if ref else set()
    return set()


def trusted(
    node: ast.AST,
    values: dict[str, ast.expr],
    imports: dict[str, str],
    *,
    environment: bool = False,
) -> bool:
    from sentinel.static.ast_utils import qualified_name, resolve_name

    if isinstance(literal(node, values), (str, bytes)) and literal(node, values):
        return True
    if isinstance(node, ast.Name) and node.id in values:
        return trusted(values[node.id], {}, imports, environment=environment)
    if isinstance(node, ast.Call):
        name = resolve_name(qualified_name(node.func) or "", imports)
        if (
            environment
            and name in {"os.getenv", "os.environ.get"}
            and node.args
            and isinstance(literal(node.args[0], values), str)
        ):
            return True
        if isinstance(node.func, ast.Attribute) and node.func.attr in {
            "encode",
            "decode",
            "fromhex",
        }:
            return trusted(
                node.args[0]
                if node.func.attr == "fromhex" and node.args
                else node.func.value,
                values,
                imports,
                environment=environment,
            )
    return (
        environment
        and isinstance(node, ast.Subscript)
        and resolve_name(qualified_name(node.value) or "", imports) == "os.environ"
        and isinstance(literal(node.slice, values), str)
    )


def equal_operands(
    test: ast.expr, truth: bool, imports: dict[str, str]
) -> tuple[ast.expr, ast.expr] | None:
    from sentinel.static.ast_utils import qualified_name, resolve_name

    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return equal_operands(test.operand, not truth, imports)
    if (
        isinstance(test, ast.Compare)
        and len(test.ops) == 1
        and (
            (truth and isinstance(test.ops[0], ast.Eq))
            or (not truth and isinstance(test.ops[0], ast.NotEq))
        )
    ):
        return test.left, test.comparators[0]
    if (
        truth
        and isinstance(test, ast.Call)
        and (qualified_name(test.func) or "").split(".")[0] in imports
        and resolve_name(qualified_name(test.func) or "", imports)
        in {"hmac.compare_digest", "secrets.compare_digest"}
        and len(test.args) == 2
    ):
        return test.args[0], test.args[1]
    return None
