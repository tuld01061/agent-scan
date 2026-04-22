from click.testing import CliRunner

from agentscan.cli import cli


def test_cli_help_shows_scan_command() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "scan" in result.output
    assert "AgentScan" in result.output
