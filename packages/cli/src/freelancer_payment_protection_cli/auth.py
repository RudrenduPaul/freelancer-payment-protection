"""
Authentication against Supabase's own REST auth API.

The backend (apps/api/app/middleware/auth.py) validates Supabase-issued JWTs
directly — it never mints tokens itself. So this CLI authenticates the same
way the web app's Supabase client does: it calls Supabase's documented
password-grant token endpoint directly, using the project's public anon key
as the `apikey` header. The anon key is safe to ship in a client (that is
its documented purpose in Supabase's own docs); it is not a secret.

Reference: https://supabase.com/docs/reference/auth/token-password-grant
"""
from __future__ import annotations

import json
import os
import stat
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx

from . import config


class AuthError(RuntimeError):
    """Raised when login, token storage, or token refresh fails."""


@dataclass
class Credentials:
    access_token: str
    refresh_token: str
    expires_at: float  # unix timestamp
    token_type: str = "bearer"

    def is_expired(self, skew_seconds: int = 30) -> bool:
        return time.time() >= (self.expires_at - skew_seconds)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Credentials":
        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=float(data["expires_at"]),
            token_type=data.get("token_type", "bearer"),
        )


def _supabase_headers() -> dict:
    anon_key = config.supabase_anon_key()
    if not anon_key:
        raise AuthError(
            "FPP_SUPABASE_ANON_KEY (or SUPABASE_ANON_KEY) is not set. "
            "The CLI needs your Supabase project's anon key to authenticate, "
            "the same public key the web app uses — see README.md 'Login and "
            "authentication'."
        )
    return {"apikey": anon_key, "Content-Type": "application/json"}


def _require_supabase_url() -> str:
    url = config.supabase_url()
    if not url:
        raise AuthError(
            "FPP_SUPABASE_URL (or SUPABASE_URL) is not set. Point it at your "
            "Supabase project URL, e.g. https://your-project.supabase.co."
        )
    return url.rstrip("/")


def login(email: str, password: str, client: httpx.Client | None = None) -> Credentials:
    """
    Calls Supabase's password-grant token endpoint directly:
    POST {SUPABASE_URL}/auth/v1/token?grant_type=password
    Body: {"email": ..., "password": ...}
    Header: apikey: <anon key>
    """
    base = _require_supabase_url()
    headers = _supabase_headers()
    owns_client = client is None
    http = client or httpx.Client(timeout=15.0)
    try:
        response = http.post(
            f"{base}/auth/v1/token",
            params={"grant_type": "password"},
            headers=headers,
            json={"email": email, "password": password},
        )
    except httpx.HTTPError as exc:
        raise AuthError(f"Could not reach Supabase auth endpoint: {exc}") from exc
    finally:
        if owns_client:
            http.close()

    if response.status_code >= 400:
        detail = _extract_error(response)
        raise AuthError(f"Login failed ({response.status_code}): {detail}")

    body = response.json()
    return _credentials_from_token_response(body)


def refresh(refresh_token: str, client: httpx.Client | None = None) -> Credentials:
    """
    Calls Supabase's refresh-token grant:
    POST {SUPABASE_URL}/auth/v1/token?grant_type=refresh_token
    Body: {"refresh_token": ...}
    """
    base = _require_supabase_url()
    headers = _supabase_headers()
    owns_client = client is None
    http = client or httpx.Client(timeout=15.0)
    try:
        response = http.post(
            f"{base}/auth/v1/token",
            params={"grant_type": "refresh_token"},
            headers=headers,
            json={"refresh_token": refresh_token},
        )
    except httpx.HTTPError as exc:
        raise AuthError(f"Could not reach Supabase auth endpoint: {exc}") from exc
    finally:
        if owns_client:
            http.close()

    if response.status_code >= 400:
        detail = _extract_error(response)
        raise AuthError(f"Token refresh failed ({response.status_code}): {detail}")

    body = response.json()
    return _credentials_from_token_response(body)


def _credentials_from_token_response(body: dict) -> Credentials:
    access_token = body.get("access_token")
    refresh_token = body.get("refresh_token")
    expires_in = body.get("expires_in", 3600)
    if not access_token or not refresh_token:
        raise AuthError(f"Unexpected response from Supabase auth endpoint: {body}")
    return Credentials(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=time.time() + float(expires_in),
        token_type=body.get("token_type", "bearer"),
    )


def _extract_error(response: httpx.Response) -> str:
    try:
        data = response.json()
        return data.get("error_description") or data.get("msg") or data.get("error") or response.text
    except (json.JSONDecodeError, ValueError):
        return response.text


def save_credentials(creds: Credentials) -> Path:
    path = config.credentials_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(creds.to_dict(), indent=2))
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # chmod 600
    return path


def load_credentials() -> Credentials | None:
    path = config.credentials_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return Credentials.from_dict(data)
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def clear_credentials() -> bool:
    path = config.credentials_path()
    if path.exists():
        path.unlink()
        return True
    return False


def get_valid_access_token(client: httpx.Client | None = None) -> str:
    """
    Returns a valid access token, transparently refreshing (and persisting
    the refreshed tokens) if the cached one has expired.
    """
    creds = load_credentials()
    if creds is None:
        raise AuthError("Not logged in. Run `fpp login` first.")

    if creds.is_expired():
        creds = refresh(creds.refresh_token, client=client)
        save_credentials(creds)

    return creds.access_token


def decode_claims_unverified(token: str) -> dict[str, Any]:
    """
    Best-effort decode of the JWT payload for display purposes only
    (`whoami`). Does not verify the signature — verification is the
    backend's job (apps/api/app/middleware/auth.py); the CLI only reads
    the claims to show the user which workspace/session is cached.
    """
    import base64

    parts = token.split(".")
    if len(parts) != 3:
        return {}
    payload = parts[1]
    padding = "=" * (-len(payload) % 4)
    try:
        decoded = base64.urlsafe_b64decode(payload + padding)
        return json.loads(decoded)
    except (ValueError, json.JSONDecodeError):
        return {}
