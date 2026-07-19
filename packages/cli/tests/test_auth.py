import stat
import time

import httpx
import pytest
import respx

from freelancer_payment_protection_cli import auth, config


@respx.mock
def test_login_success_saves_credentials():
    respx.post("https://project.supabase.test/auth/v1/token", params={"grant_type": "password"}).mock(
        return_value=httpx.Response(
            200,
            json={
                "access_token": "access-123",
                "refresh_token": "refresh-456",
                "expires_in": 3600,
                "token_type": "bearer",
            },
        )
    )

    creds = auth.login("freelancer@example.com", "correct-password")
    assert creds.access_token == "access-123"
    assert creds.refresh_token == "refresh-456"

    path = auth.save_credentials(creds)
    assert path.exists()
    mode = stat.S_IMODE(path.stat().st_mode)
    assert mode == 0o600

    loaded = auth.load_credentials()
    assert loaded.access_token == "access-123"


@respx.mock
def test_login_invalid_credentials_raises_auth_error():
    respx.post("https://project.supabase.test/auth/v1/token", params={"grant_type": "password"}).mock(
        return_value=httpx.Response(400, json={"error_description": "Invalid login credentials"})
    )

    with pytest.raises(auth.AuthError, match="Invalid login credentials"):
        auth.login("freelancer@example.com", "wrong-password")


def test_login_without_supabase_url_raises(monkeypatch):
    monkeypatch.delenv("FPP_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    with pytest.raises(auth.AuthError, match="SUPABASE_URL"):
        auth.login("a@b.com", "pw")


@respx.mock
def test_get_valid_access_token_refreshes_when_expired():
    respx.post("https://project.supabase.test/auth/v1/token", params={"grant_type": "refresh_token"}).mock(
        return_value=httpx.Response(
            200,
            json={"access_token": "new-access", "refresh_token": "new-refresh", "expires_in": 3600},
        )
    )

    expired = auth.Credentials(access_token="old-access", refresh_token="old-refresh", expires_at=time.time() - 10)
    auth.save_credentials(expired)

    token = auth.get_valid_access_token()
    assert token == "new-access"

    reloaded = auth.load_credentials()
    assert reloaded.access_token == "new-access"
    assert reloaded.refresh_token == "new-refresh"


def test_get_valid_access_token_without_login_raises():
    with pytest.raises(auth.AuthError, match="Not logged in"):
        auth.get_valid_access_token()


def test_clear_credentials_removes_file():
    creds = auth.Credentials(access_token="a", refresh_token="b", expires_at=time.time() + 3600)
    auth.save_credentials(creds)
    assert config.credentials_path().exists()

    assert auth.clear_credentials() is True
    assert not config.credentials_path().exists()
    assert auth.clear_credentials() is False


def test_decode_claims_unverified_reads_workspace_id():
    from tests.conftest import _fake_jwt

    token = _fake_jwt({"workspace_id": "ws-42", "email": "x@y.com"})
    claims = auth.decode_claims_unverified(token)
    assert claims["workspace_id"] == "ws-42"
    assert claims["email"] == "x@y.com"


def test_decode_claims_unverified_handles_garbage():
    assert auth.decode_claims_unverified("not-a-jwt") == {}
