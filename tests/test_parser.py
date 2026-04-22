from pathlib import Path

from agentscan.parser import parse_artifact


def test_parse_text_file_creates_raw_and_instruction_fields(tmp_path: Path) -> None:
    target = tmp_path / "prompt.md"
    target.write_text("Follow the safety policy.", encoding="utf-8")

    artifact = parse_artifact(target)

    names = [field.name for field in artifact.fields]

    assert artifact.format == "markdown"
    assert names.count("raw_text") == 1
    assert names.count("instruction_text") == 1
    assert artifact.tools == []


def test_parse_json_file_extracts_system_prompt(tmp_path: Path) -> None:
    target = tmp_path / "agent.json"
    target.write_text('{"system_prompt":"Stay within policy."}', encoding="utf-8")

    artifact = parse_artifact(target)

    assert artifact.format == "json"
    names = [field.name for field in artifact.fields]

    assert names.count("system_prompt") == 1
    assert "instruction_text" not in names
    assert artifact.artifact_type == "skill_definition"


def test_parse_malformed_yaml_records_warning_without_crashing(tmp_path: Path) -> None:
    target = tmp_path / "broken.yml"
    target.write_text("name: [unterminated", encoding="utf-8")

    artifact = parse_artifact(target)

    assert artifact.format == "yaml"
    assert artifact.parse_warnings
    assert artifact.raw_text == "name: [unterminated"
