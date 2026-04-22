from __future__ import annotations

from pathlib import Path
from typing import Any

import orjson
import yaml

from agentscan.models import CanonicalArtifact, CanonicalField, ParseWarning

FORMAT_BY_SUFFIX = {
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".md": "markdown",
    ".txt": "text",
}


def parse_artifact(path: Path | str) -> CanonicalArtifact:
    target = Path(path)
    raw_text = target.read_text(encoding="utf-8")
    format_name = FORMAT_BY_SUFFIX[target.suffix.lower()]
    parsed_data: Any | None = None
    parse_warnings: list[ParseWarning] = []

    if format_name == "yaml":
        try:
            parsed_data = yaml.safe_load(raw_text)
        except yaml.YAMLError as exc:
            parse_warnings.append(ParseWarning(path=target, message=str(exc)))
    elif format_name == "json":
        try:
            parsed_data = orjson.loads(raw_text)
        except orjson.JSONDecodeError as exc:
            parse_warnings.append(ParseWarning(path=target, message=str(exc)))

    artifact = CanonicalArtifact(
        path=target,
        format=format_name,
        artifact_type=_classify_artifact_type(parsed_data),
        raw_text=raw_text,
        parsed_data=parsed_data,
        parse_warnings=parse_warnings,
    )
    artifact.fields.extend(_extract_fields(raw_text, parsed_data))
    return artifact


def _classify_artifact_type(parsed_data: Any | None) -> str:
    if not isinstance(parsed_data, dict):
        return "unknown"

    if any(
        key in parsed_data
        for key in ("system_prompt", "instruction", "instructions", "prompt", "tools")
    ):
        return "skill_definition"

    return "unknown"


def _extract_fields(raw_text: str, parsed_data: Any | None) -> list[CanonicalField]:
    fields = [
        CanonicalField.from_text(
            name="raw_text",
            value=raw_text,
            line_start=1,
            line_end=max(1, len(raw_text.splitlines()) or 1),
            source_path="$",
            tags=["prompt"],
        )
    ]

    if isinstance(parsed_data, dict):
        for key in ("system_prompt", "instructions", "instruction", "prompt"):
            value = parsed_data.get(key)
            if isinstance(value, str):
                canonical_name = "system_prompt" if key == "system_prompt" else "instruction_text"
                fields.append(
                    CanonicalField.from_text(
                        name=canonical_name,
                        value=value,
                        line_start=1,
                        line_end=max(1, len(value.splitlines()) or 1),
                        source_path=key,
                        tags=["prompt"],
                    )
                )

    if not any(field.name == "instruction_text" for field in fields):
        fields.append(
            CanonicalField.from_text(
                name="instruction_text",
                value=raw_text,
                line_start=1,
                line_end=max(1, len(raw_text.splitlines()) or 1),
                source_path="$",
                tags=["prompt"],
            )
        )

    return fields
