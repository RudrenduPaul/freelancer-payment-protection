from fastapi import APIRouter
from sqlalchemy import text
from apps.api.app.database import engine

router = APIRouter()


@router.get("/health")
async def liveness():
    """Liveness probe — returns 200 if app is running."""
    return {"status": "ok", "service": "bad-cop-crm"}


@router.get("/health/ready")
async def readiness():
    """Readiness probe — checks DB connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "db": "connected"}
    except Exception as e:
        return {"status": "not_ready", "db": "disconnected", "error": str(e)}
