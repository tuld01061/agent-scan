from __future__ import annotations

from pathlib import Path

from agentscan.discovery import discover_paths
from agentscan.matchers import build_matcher_registry
from agentscan.models import ParseWarning, ScanResult
from agentscan.parser import parse_artifact
from agentscan.rules import load_builtin_rules


class NoSupportedFilesError(RuntimeError):
    """Raised when discovery finds no supported files."""


def scan_path(target: Path | str) -> ScanResult:
    paths = discover_paths(target)
    if not paths:
        raise NoSupportedFilesError(f"No supported files found in {target}")

    rules = load_builtin_rules()
    registry = build_matcher_registry()
    findings = []
    parse_warnings: list[ParseWarning] = []

    for path in paths:
        artifact = parse_artifact(path)
        parse_warnings.extend(artifact.parse_warnings)
        for rule in rules:
            findings.extend(registry[rule.matcher_type](rule, artifact))

    return ScanResult(
        files_scanned=len(paths),
        findings=findings,
        parse_warnings=parse_warnings,
    )
