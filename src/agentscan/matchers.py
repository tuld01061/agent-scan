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
            line_start, line_end = _match_line_span(
                text=value,
                base_line_start=field.line_start,
                match_start=match.start(),
                match_end=match.end(),
            )

            findings.append(
                Finding(
                    rule_id=rule.id,
                    severity=rule.severity,
                    path=artifact.path,
                    field_name=field.name,
                    source_path=field.source_path,
                    line_start=line_start,
                    line_end=line_end,
                    snippet=match.group(0)[:160],
                    message=rule.message,
                    remediation=rule.remediation,
                    owasp_refs=rule.owasp,
                )
            )
            break

    return findings


def _match_line_span(
    text: str, base_line_start: int, match_start: int, match_end: int
) -> tuple[int, int]:
    start_offset = text.count("\n", 0, match_start)
    end_offset = text.count("\n", 0, max(match_start, match_end - 1))
    return base_line_start + start_offset, base_line_start + end_offset


def tool_combo_matcher(rule: Rule, artifact: CanonicalArtifact) -> list[Finding]:
    if not artifact.tools:
        return []

    required = {tool_name.lower() for tool_name in rule.config.get("requires_all", [])}
    any_of = {tool_name.lower() for tool_name in rule.config.get("any_of", [])}
    present = {tool.name.lower() for tool in artifact.tools}

    if not required.issubset(present):
        return []

    matched_any = sorted(present.intersection(any_of))
    if not matched_any:
        return []

    snippet = ", ".join(sorted(required.union(matched_any)))
    return [
        Finding(
            rule_id=rule.id,
            severity=rule.severity,
            path=artifact.path,
            field_name="tools",
            source_path="tools",
            line_start=1,
            line_end=1,
            snippet=snippet,
            message=rule.message,
            remediation=rule.remediation,
            owasp_refs=rule.owasp,
        )
    ]


def build_matcher_registry() -> dict[str, Matcher]:
    return {
        "regex": regex_matcher,
        "tool_combo": tool_combo_matcher,
    }
