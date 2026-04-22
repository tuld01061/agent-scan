from __future__ import annotations

from collections.abc import Callable

from agentscan.models import CanonicalArtifact, Finding, Rule

Matcher = Callable[[Rule, CanonicalArtifact], list[Finding]]


def regex_matcher(rule: Rule, artifact: CanonicalArtifact) -> list[Finding]:
    return []


def tool_combo_matcher(rule: Rule, artifact: CanonicalArtifact) -> list[Finding]:
    return []


def build_matcher_registry() -> dict[str, Matcher]:
    return {
        "regex": regex_matcher,
        "tool_combo": tool_combo_matcher,
    }
