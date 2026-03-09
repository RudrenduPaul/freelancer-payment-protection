"""
SQLAlchemy engine + session factory.
Uses SQLite for local development (no credentials needed).
Switches to Supabase PostgreSQL in production via DATABASE_URL env var.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("ENVIRONMENT", "development") == "development",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a DB session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables() -> None:
    """
    Create all tables in the database.
    Used for local dev and tests. In production, use Alembic migrations.
    """
    import apps.api.app.models  # noqa: F401 — registers all models
    from apps.api.app.models.base import Base
    Base.metadata.create_all(bind=engine)
