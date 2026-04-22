from pathlib import Path

from agentscan.matchers import build_matcher_registry
from agentscan.rules import RuleLoadError, load_rules_from_dir


def test_build_matcher_registry_exposes_expected_matcher_types() -> None:
    registry = build_matcher_registry()

    assert set(registry) == {"regex", "tool_combo"}


def test_load_rules_from_dir_builds_rule_objects(tmp_path: Path) -> None:
    rule_path = tmp_path / "sample.yml"
    rule_path.write_text(
        "\n".join(
            [
                "id: AS-INJ-001",
                "category: prompt_injection",
                "severity: HIGH",
                "matcher_type: regex",
                "targets:",
                "  - system_prompt",
                "patterns:",
                "  - '(?i)ignore previous instructions'",
                "message: Detect override",
                "remediation: Remove override phrase.",
                "owasp:",
                "  - LLM01",
            ]
        ),
        encoding="utf-8",
    )

    rules = load_rules_from_dir(tmp_path)

    assert [rule.id for rule in rules] == ["AS-INJ-001"]
    assert rules[0].config["patterns"] == ["(?i)ignore previous instructions"]


def test_load_rules_from_dir_rejects_unknown_matcher_type(tmp_path: Path) -> None:
    rule_path = tmp_path / "bad.yml"
    rule_path.write_text(
        "\n".join(
            [
                "id: AS-BAD-001",
                "category: test",
                "severity: LOW",
                "matcher_type: impossible",
                "targets:",
                "  - raw_text",
                "message: bad",
                "remediation: bad",
                "owasp:",
                "  - LLM01",
            ]
        ),
        encoding="utf-8",
    )

    try:
        load_rules_from_dir(tmp_path)
    except RuleLoadError as exc:
        assert "impossible" in str(exc)
    else:
        raise AssertionError("expected RuleLoadError")


def test_load_rules_from_dir_rejects_unknown_targets(tmp_path: Path) -> None:
    rule_path = tmp_path / "bad-target.yml"
    rule_path.write_text(
        "\n".join(
            [
                "id: AS-BAD-002",
                "category: test",
                "severity: LOW",
                "matcher_type: regex",
                "targets:",
                "  - made_up_field",
                "message: bad",
                "remediation: bad",
                "owasp:",
                "  - LLM01",
            ]
        ),
        encoding="utf-8",
    )

    try:
        load_rules_from_dir(tmp_path)
    except RuleLoadError as exc:
        assert "made_up_field" in str(exc)
    else:
        raise AssertionError("expected RuleLoadError")
