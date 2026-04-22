import click

from agentscan.models import Severity
from agentscan.reporting import exit_code_for_findings, render_report
from agentscan.scanner import NoSupportedFilesError, scan_path


@click.group(help="AgentScan static scanner for agent artifacts.")
def cli() -> None:
    """CLI entrypoint for AgentScan."""


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=str))
@click.option(
    "--fail-on",
    type=click.Choice(["low", "medium", "high", "critical"], case_sensitive=False),
    default="high",
    show_default=True,
)
def scan(path: str, fail_on: str) -> None:
    """Scan PATH for supported agent artifacts."""
    threshold = Severity.from_string(fail_on)

    try:
        result = scan_path(path)
    except NoSupportedFilesError as exc:
        raise click.ClickException(str(exc)) from exc

    report = render_report(
        findings=result.findings,
        parse_warnings=result.parse_warnings,
        files_scanned=result.files_scanned,
    )
    click.echo(report)
    raise SystemExit(exit_code_for_findings(result.findings, threshold))


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
