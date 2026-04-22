from collections import Counter

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


def exit_code_for_findings(findings: list[Finding], threshold: Severity) -> int:
    if any(finding.severity >= threshold for finding in findings):
        return 1
    return 0
