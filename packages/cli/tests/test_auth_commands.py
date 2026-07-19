import json

import httpx
import respx
from click.testing import CliRunner

from freelancer_payment_protection_cli import config
from freelancer_payment_protection_cli.main import cli


@respx.mock
def test_login_command_prompts_and_saves(monkeypatch):
    respx.post("https://project.supabase.test/auth/v1/token", params={"grant_type": "password"}).mock(
        return_value=httpx.Response(
            200, json={"access_token": "tok-1", "refresh_token": "ref-1", "expires_in": 3600}
        )
    )

    result = CliRunner().invoke(cli, ["login"], input="freelancer@example.com\nsecret-pw\n")
    assert result.exit_code == 0
    assert "Logged in as freelancer@example.com" in result.output
    assert config.credentials_path().exists()


def test_logout_command_when_not_logged_in():
    result = CliRunner().invoke(cli, ["logout"])
    assert result.exit_code == 0
    assert "Not logged in" in result.output


def test_whoami_without_login_errors_cleanly():
    result = CliRunner().invoke(cli, ["whoami", "--json"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert "Not logged in" in data["error"]


def test_whoami_reports_workspace_id(logged_in):
    result = CliRunner().invoke(cli, ["whoami", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["workspace_id"] == "ws-test-001"


def test_version_flag():
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "freelancer-payment-protection-cli" in result.output
