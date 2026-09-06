"""Authoritative metadata for the four permanent dynamic probes."""

from __future__ import annotations

from sentinel.finding import ContractModel, Impact, NonEmptyString, OwaspCategory
from sentinel.owasp_mapping import category_for_rule


class DynamicRuleDefinition(ContractModel):
    rule_id: NonEmptyString
    title: NonEmptyString
    description: NonEmptyString
    impact: Impact
    remediation: NonEmptyString
    owasp_category: OwaspCategory


def _rule(
    rule_id: str,
    title: str,
    description: str,
    impact: Impact,
    remediation: str,
) -> DynamicRuleDefinition:
    return DynamicRuleDefinition(
        rule_id=rule_id,
        title=title,
        description=description,
        impact=impact,
        remediation=remediation,
        owasp_category=category_for_rule(rule_id),
    )


RULES = (
    _rule(
        "SENT-008",
        "Out-of-scope tool execution",
        "After a successful granted-tool control, the server processed valid "
        "arguments through a listed tool omitted from its declared tool-name grants.",
        Impact.CRITICAL,
        "Reject tool calls that are not granted by the active capability policy.",
    ),
    _rule(
        "SENT-009",
        "Oversized argument violates a limit or crashes the target",
        "After a successful baseline, the server processed an explicit size-limit "
        "violation or suffered an observed OOM/crash on an oversized argument.",
        Impact.MEDIUM,
        "Enforce schema and byte-size limits before invoking tool handlers.",
    ),
    _rule(
        "SENT-010",
        "Injection payload executed",
        "A tool argument caused the Sentinel scratch canary side effect.",
        Impact.CRITICAL,
        "Treat tool arguments as inert data and remove dynamic execution sinks.",
    ),
    _rule(
        "SENT-011",
        "Malformed schema input processed",
        "After a successful baseline, the server processed locally verified "
        "invalid arguments that violate a required-field or type constraint.",
        Impact.LOW,
        "Validate required fields and declared types before handler execution.",
    ),
)

RULE_BY_ID = {rule.rule_id: rule for rule in RULES}
RULE_IDS = tuple(rule.rule_id for rule in RULES)
