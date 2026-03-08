"""
pytest configuration and shared fixtures.
ALL external API calls are mocked — no live services in tests.
No real credentials used anywhere in this file.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

# Use in-memory SQLite for tests — no files, no cleanup needed
TEST_DATABASE_URL = "sqlite:///:memory:"

# Set required env vars to placeholder values before any imports
# These are NOT real credentials — only used to satisfy Pydantic Settings validation
os.environ.setdefault("ANTHROPIC_API_KEY", "test-placeholder-not-a-real-key")
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-placeholder")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key-placeholder")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-at-least-32-chars-placeholder")
os.environ.setdefault("RESEND_API_KEY", "test-resend-key-placeholder")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)
os.environ.setdefault("ENVIRONMENT", "test")


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    return engine


@pytest.fixture(scope="session")
def test_db_session(test_engine):
    from apps.api.app.models.client import Base
    Base.metadata.create_all(test_engine)
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def test_client(test_db_session):
    """FastAPI test client with mocked auth and in-memory DB."""
    from apps.api.app.main import app
    from apps.api.app.database import get_db
    from apps.api.app.middleware.auth import get_current_workspace

    def override_get_db():
        yield test_db_session

    def override_get_workspace():
        return "workspace-test-123"

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_workspace] = override_get_workspace

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_claude():
    """Mock all Claude API calls — no real API calls in tests."""
    with patch("apps.api.app.services.ai_service.call_claude") as mock:
        mock.return_value = '{"score": 50, "level": "medium", "factors": [], "reasoning": "Test"}'
        yield mock


@pytest.fixture
def mock_claude_risk():
    """Mock Claude for risk scoring specifically."""
    with patch("apps.api.app.services.risk_service.compute_client_risk_score") as mock:
        mock.return_value = {
            "score": 42,
            "level": "medium",
            "factors": [{"name": "Industry risk", "impact": "negative", "description": "Test", "weight": 10}],
            "reasoning": "Mock risk assessment for testing",
        }
        yield mock
