from pathlib import Path

from agentscan.matchers import tool_combo_matcher
from agentscan.models import CanonicalArtifact, Rule, Severity
from agentscan.parser import parse_artifact


def test_parser_extracts_tools_from_yaml(tmp_path: Path) -> None:
    target = tmp_path / "skill.yml"
    target.write_text(
        "\n".join(
            [
                "tools:",
                "  - name: filesystem_read",
                "    description: Read files",
                "  - name: send_email",
                "    description: Send mail",
            ]
        ),
        encoding="utf-8",
    )

    artifact = parse_artifact(target)

    assert [tool.name for tool in artifact.tools] == ["filesystem_read", "send_email"]
    assert {field.name for field in artifact.fields} >= {"tool_name", "tool_description"}


def test_tool_combo_matcher_returns_empty_list_when_tools_are_missing() -> None:
    artifact = CanonicalArtifact(
        path=Path("prompt.md"),
        format="markdown",
        artifact_type="prompt_template",
        raw_text="hello",
    )
    rule = Rule(
        id="AS-TOOL-001",
        category="tool_abuse",
        severity=Severity.CRITICAL,
        matcher_type="tool_combo",
        targets=["tools"],
        config={"requires_all": ["filesystem_read"], "any_of": ["send_email"]},
        message="Exfiltration tool pair detected",
        remediation="Remove the dangerous tool pair.",
        owasp=["LLM06"],
    )

    assert tool_combo_matcher(rule, artifact) == []


def test_tool_combo_matcher_flags_exfiltration_pair(tmp_path: Path) -> None:
    target = tmp_path / "skill.yml"
    target.write_text(
        "\n".join(
            [
                "tools:",
                "  - name: filesystem_read",
                "    description: Read files",
                "  - name: send_email",
                "    description: Send mail",
            ]
        ),
        encoding="utf-8",
    )

    artifact = parse_artifact(target)
    rule = Rule(
        id="AS-TOOL-001",
        category="tool_abuse",
        severity=Severity.CRITICAL,
        matcher_type="tool_combo",
        targets=["tools"],
        config={"requires_all": ["filesystem_read"], "any_of": ["send_email", "http_post"]},
        message="Exfiltration tool pair detected",
        remediation="Remove the dangerous tool pair.",
        owasp=["LLM06"],
    )

    findings = tool_combo_matcher(rule, artifact)

    assert len(findings) == 1
    assert findings[0].field_name == "tools"
