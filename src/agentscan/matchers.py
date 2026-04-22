from __future__ import annotations

import re
from collections.abc import Callable

from agentscan.models import CanonicalArtifact, Finding, Rule

Matcher = Callable[[Rule, CanonicalArtifact], list[Finding]]


def regex_matcher(rule: Rule, artifact: CanonicalArtifact) -> list[Finding]:
    patterns = [re.compile(pattern) for pattern in rule.config.get("patterns", [])]
    view_name = rule.config.get("view", "raw")
    findings: list[Finding] = []

    for field in artifact.fields:
        if field.name not in rule.targets:
            continue

        value = field.normalized_views.get(view_name)
        for pattern in patterns:
            match = pattern.search(value)
            if not match:
                continue

            findings.append(
                Finding(
                    rule_id=rule.id,
                    severity=rule.severity,
                    path=artifact.path,
                    field_name=field.name,
                    source_path=field.source_path,
                    line_start=field.line_start,
                    line_end=field.line_end,
                    snippet=match.group(0)[:160],
                    message=rule.message,
                    remediation=rule.remediation,
                    owasp_refs=rule.owasp,
                )
            )
            break

    return findings


def tool_combo_matcher(rule: Rule, artifact: CanonicalArtifact) -> list[Finding]:
    return []


def build_matcher_registry() -> dict[str, Matcher]:
    return {
        "regex": regex_matcher,
        "tool_combo": tool_combo_matcher,
    }
