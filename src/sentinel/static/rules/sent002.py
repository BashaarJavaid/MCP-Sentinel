"""SENT-002 Semgrep result adapter."""

from sentinel.static.model import RuleRunState, StaticMatch


def run(matches: list[StaticMatch], state: RuleRunState) -> None:
    state.matches.extend(matches)
