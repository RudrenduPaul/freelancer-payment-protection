"""
FastAPI application factory.
All routers registered here. Middleware applied here.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from apps.api.app.config import settings
from apps.api.app.middleware.rate_limit import limiter
from apps.api.app.routers import (
    clients,
    invoices,
    escalations,
    legal_docs,
    evidence,
    risk_scoring,
    analytics,
    health,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables in development (production uses Alembic migrations)
    if settings.environment == "development" or settings.environment == "test":
        from apps.api.app.database import create_all_tables
        create_all_tables()
    yield


app = FastAPI(
    title="Bad Cop CRM API",
    description="Freelancer payment protection — automated escalation and legal document generation",
    version="1.0.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Register all routers
app.include_router(health.router, tags=["health"])
app.include_router(clients.router, prefix="/api/v1/clients", tags=["clients"])
app.include_router(invoices.router, prefix="/api/v1/invoices", tags=["invoices"])
app.include_router(escalations.router, prefix="/api/v1/escalations", tags=["escalations"])
app.include_router(legal_docs.router, prefix="/api/v1/legal", tags=["legal"])
app.include_router(evidence.router, prefix="/api/v1/evidence", tags=["evidence"])
app.include_router(risk_scoring.router, prefix="/api/v1/risk", tags=["risk"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
