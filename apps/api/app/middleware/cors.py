"""
CORS configuration — allowlist only, no wildcard in production.
"""
from apps.api.app.config import settings


def get_cors_origins() -> list[str]:
    return settings.allowed_origins
