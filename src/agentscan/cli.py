import click


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
    raise click.ClickException("scan command is not implemented yet")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
