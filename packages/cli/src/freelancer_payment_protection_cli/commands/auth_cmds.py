"""login / logout / whoami — Supabase password-grant auth, cached locally."""
from __future__ import annotations

import click

from .. import auth
from ..output import emit, emit_error, error_boundary, kv_table


@click.command()
def login() -> None:
    """
    Log in with your email and password.

    Calls Supabase's own REST auth endpoint directly
    (POST {SUPABASE_URL}/auth/v1/token?grant_type=password) using your
    project's anon key — the same call the web app's Supabase client
    makes. Requires FPP_SUPABASE_URL (or SUPABASE_URL) and
    FPP_SUPABASE_ANON_KEY (or SUPABASE_ANON_KEY) to be set in your
    environment.

    On success, caches the access_token and refresh_token to
    ~/.config/freelancer-payment-protection-cli/credentials.json (mode
    600). Later commands silently refresh the access token using the
    cached refresh_token once it expires.
    """
    email = click.prompt("Email")
    password = click.prompt("Password", hide_input=True)

    with error_boundary(as_json=False):
        creds = auth.login(email, password)
        path = auth.save_credentials(creds)
    click.echo(f"Logged in as {email}.")
    click.echo(f"Credentials cached at {path}")


@click.command()
def logout() -> None:
    """Delete the locally cached credentials."""
    removed = auth.clear_credentials()
    if removed:
        click.echo("Logged out. Cached credentials removed.")
    else:
        click.echo("Not logged in — nothing to remove.")


@click.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def whoami(as_json: bool) -> None:
    """Show the workspace and session info from the cached access token."""
    creds = auth.load_credentials()
    if creds is None:
        emit_error("Not logged in. Run `fpp login` first.", as_json)
        raise SystemExit(1)

    claims = auth.decode_claims_unverified(creds.access_token)
    workspace_id = claims.get("workspace_id")
    data = {
        "workspace_id": workspace_id,
        "email": claims.get("email"),
        "expires_at": creds.expires_at,
        "expired": creds.is_expired(),
    }

    if not workspace_id:
        note = (
            "Warning: cached token has no workspace_id claim. The backend's "
            "get_current_workspace() dependency requires one — API calls "
            "will fail with 401 until you log in with an account that has "
            "a workspace_id configured on its Supabase JWT."
        )
        if not as_json:
            click.echo(note, err=True)
        else:
            data["warning"] = note

    human = kv_table(
        [
            ("Workspace ID", workspace_id or "(none)"),
            ("Email", claims.get("email", "(unknown)")),
            ("Token expired", data["expired"]),
        ]
    )
    emit(data, as_json, human=human)
