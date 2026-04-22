from __future__ import annotations

from pathlib import Path

import yaml

from agentscan.matchers import build_matcher_registry
from agentscan.models import Rule, Severity


class RuleLoadError(RuntimeError):
    """Raised when rule loading fails."""


COMMON_RULE_KEYS = {
    "id",
    "category",
    "severity",
    "matcher_type",
    "targets",
    "message",
    "remediation",
    "owasp",
}

ALLOWED_RULE_TARGETS = {
    "system_prompt",
    "instruction_text",
    "tool_name",
    "tool_description",
    "raw_text",
    "tools",
}


def load_rules_from_dir(directory: Path | str) -> list[Rule]:
    registry = build_matcher_registry()
    result: list[Rule] = []

    for rule_path in sorted(Path(directory).glob("*.yml")):
        payload = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
        matcher_type = payload["matcher_type"]
        if matcher_type not in registry:
            raise RuleLoadError(f"Unknown matcher_type: {matcher_type}")

        targets = list(payload["targets"])
        invalid_targets = sorted(set(targets) - ALLOWED_RULE_TARGETS)
        if invalid_targets:
            raise RuleLoadError(
                f"Unknown rule target(s): {', '.join(invalid_targets)}"
            )

        config = {
            key: value for key, value in payload.items() if key not in COMMON_RULE_KEYS
        }
        result.append(
            Rule(
                id=payload["id"],
                category=payload["category"],
                severity=Severity.from_string(payload["severity"]),
                matcher_type=matcher_type,
                targets=targets,
                config=config,
                message=payload["message"],
                remediation=payload["remediation"],
                owasp=list(payload["owasp"]),
            )
        )

    return result
