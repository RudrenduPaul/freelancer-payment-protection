"""
Shared test fixtures. ALL HTTP calls (to Supabase and to the backend API)
are mocked with respx — no live network calls in this test suite, matching
this monorepo's own backend test suite convention of mocking every
external API call rather than hitting live services.
"""
import base64
import json
import time

import pytest


def _fake_jwt(claims: dict) -> str:
    def b64(obj: dict) -> str:
        raw = json.dumps(obj).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    header = {"alg": "HS256", "typ": "JWT"}
    return f"{b64(header)}.{b64(claims)}.fake-signature-not-verified-by-cli"


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Every test gets its own credentials directory and API/Supabase env."""
    monkeypatch.setenv("FPP_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("FPP_API_URL", "https://api.test.invalid")
    monkeypatch.setenv("FPP_SUPABASE_URL", "https://project.supabase.test")
    monkeypatch.setenv("FPP_SUPABASE_ANON_KEY", "test-anon-key")
    yield


@pytest.fixture
def valid_access_token():
    return _fake_jwt({"workspace_id": "ws-test-001", "email": "freelancer@example.com", "exp": int(time.time()) + 3600})


@pytest.fixture
def logged_in(valid_access_token):
    """Writes a non-expired credentials file so commands don't need to log in."""
    from freelancer_payment_protection_cli import auth

    creds = auth.Credentials(
        access_token=valid_access_token,
        refresh_token="refresh-abc",
        expires_at=time.time() + 3600,
    )
    auth.save_credentials(creds)
    return creds
