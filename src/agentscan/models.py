from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Any

from agentscan.normalize import NormalizedText


class Severity(IntEnum):
    INFO = 10
    LOW = 20
    MEDIUM = 30
    HIGH = 40
    CRITICAL = 50

    @classmethod
    def from_string(cls, value: str) -> "Severity":
        return cls[value.upper()]


@dataclass(slots=True)
class ParseWarning:
    path: Path
    message: str


@dataclass(slots=True)
class CanonicalField:
    name: str
    value_raw: str
    normalized_views: NormalizedText
    line_start: int
    line_end: int
    source_path: str
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_text(
        cls,
        name: str,
        value: str,
        line_start: int,
        line_end: int,
        source_path: str,
        tags: list[str] | None = None,
    ) -> "CanonicalField":
        return cls(
            name=name,
            value_raw=value,
            normalized_views=NormalizedText(value),
            line_start=line_start,
            line_end=line_end,
            source_path=source_path,
            tags=tags or [],
        )


@dataclass(slots=True)
class CanonicalTool:
    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    constraints_detected: list[str] = field(default_factory=list)
    line_start: int = 1
    line_end: int = 1


@dataclass(slots=True)
class CanonicalArtifact:
    path: Path
    format: str
    artifact_type: str
    raw_text: str
    parsed_data: Any | None = None
    fields: list[CanonicalField] = field(default_factory=list)
    tools: list[CanonicalTool] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    parse_warnings: list[ParseWarning] = field(default_factory=list)


@dataclass(slots=True)
class Rule:
    id: str
    category: str
    severity: Severity
    matcher_type: str
    targets: list[str]
    config: dict[str, Any]
    message: str
    remediation: str
    owasp: list[str]


@dataclass(slots=True)
class Finding:
    rule_id: str
    severity: Severity
    path: Path
    field_name: str
    source_path: str
    line_start: int
    line_end: int
    snippet: str
    message: str
    remediation: str
    owasp_refs: list[str]
