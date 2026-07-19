"""Authoritative static rule metadata."""

from __future__ import annotations

from sentinel.finding import Impact
from sentinel.owasp_mapping import category_for_rule
from sentinel.static.model import RuleDefinition, RuleEngine

_DOC_ROOT = "https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/docs/rules.md"


def _rule(
    rule_id: str,
    title: str,
    description: str,
    impact: Impact,
    remediation: str,
    false_positive_risk: str,
    engine: RuleEngine,
) -> RuleDefinition:
    return RuleDefinition(
        rule_id=rule_id,
        title=title,
        description=description,
        impact=impact,
        remediation=remediation,
        false_positive_risk=false_positive_risk,
        owasp_category=category_for_rule(rule_id),
        engine=engine,
        help_uri=f"{_DOC_ROOT}#{rule_id.lower()}",
    )


RULES = (
    _rule(
        "SENT-001",
        "Overly broad tool permission scope",
        "The tool declares filesystem or network access broader than its handler uses.",
        Impact.HIGH,
        "Narrow each declared scope to the resources the handler actually requires.",
        "Medium: legitimately broad tools require an explicit capability "
        "justification.",
        RuleEngine.AST,
    ),
    _rule(
        "SENT-002",
        "Unsafe execution from tool input",
        "Tool-controlled input reaches an unsafe execution or deserialization sink.",
        Impact.CRITICAL,
        "Replace dynamic execution with explicit parsers and fixed command allowlists.",
        "Low: fixed literal subprocess argument vectors are excluded.",
        RuleEngine.SEMGREP,
    ),
    _rule(
        "SENT-003",
        "Missing tool input validation",
        "A tool handler consumes parameters before framework or explicit validation.",
        Impact.MEDIUM,
        "Use concrete handler types, Pydantic models, or JSON Schema before first use.",
        "Medium: custom validators outside the supported boundary may not be "
        "recognized.",
        RuleEngine.AST,
    ),
    _rule(
        "SENT-004",
        "Unsanitized tool content in prompt",
        "Tool output or description flows into a later model prompt without a "
        "trusted sanitizer.",
        Impact.HIGH,
        "Pass tool-controlled text through a configured sanitizer before prompt "
        "construction.",
        "Medium-High: intraprocedural prompt-flow analysis is intentionally heuristic.",
        RuleEngine.AST,
    ),
    _rule(
        "SENT-005",
        "Hardcoded secret",
        "Source or configuration contains a credential signature or contextual "
        "high-entropy secret.",
        Impact.CRITICAL,
        "Load credentials from an external secret store or environment at runtime.",
        "Low-Medium: high-entropy test values require paired path/fingerprint "
        "allowlisting.",
        RuleEngine.SEMGREP,
    ),
    _rule(
        "SENT-006",
        "Missing or ineffective route authentication",
        "An HTTP route lacks inherited authentication or uses a no-op verifier.",
        Impact.HIGH,
        "Require credential verification and an explicit rejection path before "
        "route execution.",
        "Low: intentional public routes must be explicitly configured.",
        RuleEngine.AST,
    ),
    _rule(
        "SENT-007",
        "Unverified tool manifest",
        "Manifest bytes reach registration without a trusted hash or signature "
        "verification.",
        Impact.MEDIUM,
        "Verify a pinned SHA-256 digest or trusted detached signature before "
        "parsing and use.",
        "Low: custom verification beyond the supported crypto APIs may require "
        "later coverage.",
        RuleEngine.AST,
    ),
)

RULE_BY_ID = {rule.rule_id: rule for rule in RULES}
RULE_IDS = tuple(rule.rule_id for rule in RULES)
