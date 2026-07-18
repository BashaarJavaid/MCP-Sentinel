"""Canonical permanent rule-to-OWASP Agentic Top 10 mapping."""

from __future__ import annotations

from sentinel.finding import OwaspCategory

OWASP_CATEGORIES = {
    "ASI01:2026": OwaspCategory(id="ASI01:2026", name="Agent Goal Hijack"),
    "ASI02:2026": OwaspCategory(id="ASI02:2026", name="Tool Misuse & Exploitation"),
    "ASI03:2026": OwaspCategory(id="ASI03:2026", name="Identity & Privilege Abuse"),
    "ASI04:2026": OwaspCategory(
        id="ASI04:2026", name="Agentic Supply Chain Vulnerabilities"
    ),
    "ASI05:2026": OwaspCategory(id="ASI05:2026", name="Unexpected Code Execution"),
    "ASI06:2026": OwaspCategory(id="ASI06:2026", name="Memory & Context Poisoning"),
    "ASI07:2026": OwaspCategory(
        id="ASI07:2026", name="Insecure Inter-Agent Communication"
    ),
    "ASI08:2026": OwaspCategory(id="ASI08:2026", name="Cascading Failures"),
    "ASI09:2026": OwaspCategory(id="ASI09:2026", name="Human-Agent Trust Exploitation"),
    "ASI10:2026": OwaspCategory(id="ASI10:2026", name="Rogue Agents"),
}

RULE_OWASP_IDS = {
    "SENT-001": "ASI03:2026",
    "SENT-002": "ASI05:2026",
    "SENT-003": "ASI02:2026",
    "SENT-004": "ASI01:2026",
    "SENT-005": "ASI03:2026",
    "SENT-006": "ASI03:2026",
    "SENT-007": "ASI04:2026",
}


def category_for_rule(rule_id: str) -> OwaspCategory:
    """Return the pinned OWASP category for a permanent rule ID."""

    return OWASP_CATEGORIES[RULE_OWASP_IDS[rule_id]]
