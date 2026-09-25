"""
Settings loaded from environment variables.
App refuses to start if required vars are missing — fail-fast pattern.
All secrets come from env vars only. Never hardcode credentials.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, SecretStr
from typing import Optional


# Resolved from this file's location, never from the working directory, so a
# process started in another project's root can never pick up that project's .env.
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    # Required — app refuses to start if missing
    anthropic_api_key: SecretStr
    supabase_url: AnyHttpUrl
    supabase_service_role_key: SecretStr
    supabase_anon_key: SecretStr
    jwt_secret: SecretStr
    resend_api_key: SecretStr
    redis_url: str

    # Optional integrations
    freshbooks_client_id: Optional[str] = None
    freshbooks_client_secret: Optional[SecretStr] = None
    quickbooks_client_id: Optional[str] = None
    quickbooks_client_secret: Optional[SecretStr] = None
    wave_api_key: Optional[SecretStr] = None

    # App config
    environment: str = "development"
    allowed_origins: list[str] = ["http://localhost:3000"]
    rate_limit_per_minute: int = 100
    max_evidence_file_size_mb: int = 25

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=False,
    )


settings = Settings()  # Raises ValidationError on startup if any required var is missing
