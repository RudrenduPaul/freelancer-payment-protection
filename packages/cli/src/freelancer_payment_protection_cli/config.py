"""
Configuration and credential-storage paths.

The API base URL and Supabase project settings are read from environment
variables so the same CLI build works against any deployment (local dev
server, self-hosted, or a hosted instance) without hardcoding a URL that
does not exist for every installer of this package.
"""
from __future__ import annotations

import os
from pathlib import Path

CLI_NAME = "freelancer-payment-protection-cli"

# Backend API base URL. Defaults to the FastAPI dev server's default port
# (apps/api/README instructions: `uvicorn app.main:app --reload` serves on
# http://localhost:8000, with routers mounted under /api/v1).
DEFAULT_API_URL = "http://localhost:8000"


def api_url() -> str:
    return os.environ.get("FPP_API_URL", DEFAULT_API_URL).rstrip("/")


def supabase_url() -> str | None:
    # FPP_SUPABASE_URL takes precedence; falls back to the same SUPABASE_URL
    # name the backend's own .env.example uses, since the anon-key auth
    # endpoint lives on the same Supabase project as the backend.
    return os.environ.get("FPP_SUPABASE_URL") or os.environ.get("SUPABASE_URL")


def supabase_anon_key() -> str | None:
    return os.environ.get("FPP_SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_ANON_KEY")


def config_dir() -> Path:
    override = os.environ.get("FPP_CONFIG_DIR")
    if override:
        return Path(override)
    return Path.home() / ".config" / CLI_NAME


def credentials_path() -> Path:
    return config_dir() / "credentials.json"
