from pathlib import Path

from click.testing import CliRunner

from agentscan.cli import cli


def test_scan_safe_fixture_exits_zero() -> None:
    runner = CliRunner()
    fixture_dir = Path("tests/fixtures/safe")

    result = runner.invoke(cli, ["scan", str(fixture_dir)])

    assert result.exit_code == 0
    assert "Files scanned: 1" in result.output


def test_scan_unsafe_fixture_exits_one_for_high_findings() -> None:
    runner = CliRunner()
    fixture_dir = Path("tests/fixtures/unsafe")

    result = runner.invoke(cli, ["scan", str(fixture_dir)])

    assert result.exit_code == 1
    assert "AS-INJ-001" in result.output
    assert "AS-TOOL-001" in result.output


def test_scan_empty_fixture_exits_two_with_clear_message() -> None:
    runner = CliRunner()
    fixture_dir = Path("tests/fixtures/empty")

    result = runner.invoke(cli, ["scan", str(fixture_dir)])

    assert result.exit_code == 2
    assert f"No supported files found in {fixture_dir}" in result.output


def test_scan_missing_path_exits_two_before_discovery() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["scan", "tests/fixtures/does-not-exist"])

    assert result.exit_code == 2
    assert "does not exist" in result.output.lower()


def test_scan_continues_when_malformed_file_is_present() -> None:
    runner = CliRunner()
    fixture_dir = Path("tests/fixtures")

    result = runner.invoke(cli, ["scan", str(fixture_dir)])

    assert result.exit_code == 1
    assert "Warnings: 1" in result.output
