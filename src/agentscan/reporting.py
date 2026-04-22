from collections import Counter
import json

from agentscan.models import Finding, ParseWarning, Severity


def render_report(
    findings: list[Finding],
    parse_warnings: list[ParseWarning],
    files_scanned: int,
) -> str:
    lines: list[str] = []

    for finding in findings:
        lines.extend(
            [
                f"[{finding.severity.name}] {finding.rule_id}",
                f"File: {finding.path}:{finding.line_start}",
                f"Field: {finding.field_name}",
                f"Message: {finding.message}",
                f"Evidence: {finding.snippet}",
                f"Remediation: {finding.remediation}",
                "",
            ]
        )

    counts = Counter(finding.severity.name for finding in findings)
    lines.extend(
        [
            f"Files scanned: {files_scanned}",
            f"Findings: {len(findings)}",
            f"Warnings: {len(parse_warnings)}",
            f"Severity counts: {dict(sorted(counts.items()))}",
        ]
    )
    return "\n".join(lines).strip()


def render_json_report(
    findings: list[Finding],
    parse_warnings: list[ParseWarning],
    files_scanned: int,
) -> str:
    payload = {
        "files_scanned": files_scanned,
        "findings_count": len(findings),
        "warnings_count": len(parse_warnings),
        "severity_counts": dict(
            sorted(Counter(finding.severity.name for finding in findings).items())
        ),
        "findings": [
            {
                "rule_id": finding.rule_id,
                "severity": finding.severity.name,
                "path": str(finding.path),
                "field_name": finding.field_name,
                "source_path": finding.source_path,
                "line_start": finding.line_start,
                "line_end": finding.line_end,
                "snippet": finding.snippet,
                "message": finding.message,
                "remediation": finding.remediation,
                "owasp_refs": finding.owasp_refs,
            }
            for finding in findings
        ],
        "parse_warnings": [
            {
                "path": str(warning.path),
                "message": warning.message,
            }
            for warning in parse_warnings
        ],
    }

    return json.dumps(payload, indent=2, sort_keys=True)


def exit_code_for_findings(findings: list[Finding], threshold: Severity) -> int:
    if any(finding.severity >= threshold for finding in findings):
        return 1
    return 0
