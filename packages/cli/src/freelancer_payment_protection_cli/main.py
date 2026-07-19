"""CLI entry point. Registered as console scripts `fpp` and
`freelancer-payment-protection` (see pyproject.toml [project.scripts])."""
from __future__ import annotations

import click

from . import __version__
from .commands.auth_cmds import login, logout, whoami
from .commands.client_cmds import client
from .commands.escalation_cmds import escalation
from .commands.invoice_cmds import invoice


@click.group()
@click.version_option(version=__version__, prog_name="freelancer-payment-protection-cli")
def cli() -> None:
    """
    Command-line client for freelancer-payment-protection: automated
    invoice escalation, legal document generation, and client risk
    scoring for freelancers.

    Every command talks to a real freelancer-payment-protection API
    instance (default http://localhost:8000, override with FPP_API_URL).
    Log in first with `fpp login`.

    Every data-returning command supports --json for scripting/agent use.
    """


cli.add_command(login)
cli.add_command(logout)
cli.add_command(whoami)
cli.add_command(invoice)
cli.add_command(escalation)
cli.add_command(client)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
