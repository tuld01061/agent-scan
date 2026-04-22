from pathlib import Path

from agentscan.models import Finding, ParseWarning, Severity
from agentscan.reporting import exit_code_for_findings, render_json_report, render_report
from agentscan.scanner import NoSupportedFilesError, scan_path


def test_exit_code_for_findings_respects_threshold() -> None:
    findings = [
        Finding(
            rule_id="AS-INJ-001",
            severity=Severity.HIGH,
            path=Path("skill.yml"),
            field_name="system_prompt",
            source_path="system_prompt",
            line_start=1,
            line_end=1,
            snippet="Ignore previous instructions",
            message="Instruction override phrase detected",
            remediation="Remove it.",
            owasp_refs=["LLM01"],
        )
    ]

    assert exit_code_for_findings(findings, Severity.CRITICAL) == 0
    assert exit_code_for_findings(findings, Severity.HIGH) == 1


def test_render_report_includes_findings_and_warning_summary() -> None:
    findings = [
        Finding(
            rule_id="AS-INJ-001",
            severity=Severity.HIGH,
            path=Path("skill.yml"),
            field_name="system_prompt",
            source_path="system_prompt",
            line_start=3,
            line_end=3,
            snippet="Ignore previous instructions",
            message="Instruction override phrase detected",
            remediation="Remove it.",
            owasp_refs=["LLM01"],
        )
    ]
    warnings = [ParseWarning(path=Path("bad.yml"), message="broken yaml")]

    report = render_report(findings=findings, parse_warnings=warnings, files_scanned=2)

    assert "[HIGH] AS-INJ-001" in report
    assert "Warnings: 1" in report
    assert "Files scanned: 2" in report


def test_render_json_report_returns_machine_readable_payload() -> None:
    findings = [
        Finding(
            rule_id="AS-INJ-001",
            severity=Severity.HIGH,
            path=Path("skill.yml"),
            field_name="system_prompt",
            source_path="system_prompt",
            line_start=3,
            line_end=3,
            snippet="Ignore previous instructions",
            message="Instruction override phrase detected",
            remediation="Remove it.",
            owasp_refs=["LLM01"],
        )
    ]
    warnings = [ParseWarning(path=Path("bad.yml"), message="broken yaml")]

    report = render_json_report(findings=findings, parse_warnings=warnings, files_scanned=2)

    assert '"files_scanned": 2' in report
    assert '"rule_id": "AS-INJ-001"' in report
    assert '"parse_warnings"' in report


def test_scan_path_raises_when_no_supported_files_exist(tmp_path: Path) -> None:
    (tmp_path / "README.unsupported").write_text("notes", encoding="utf-8")

    try:
        scan_path(tmp_path)
    except NoSupportedFilesError as exc:
        assert str(exc) == f"No supported files found in {tmp_path}"
    else:
        raise AssertionError("expected NoSupportedFilesError")
