from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from apps.api.app.middleware.auth import get_current_workspace
from apps.api.app.middleware.rate_limit import limiter
from sqlalchemy.orm import Session
from apps.api.app.database import get_db

router = APIRouter()


class RiskScoreRequest(BaseModel):
    client_id: str


@router.post("/score")
@limiter.limit("30/minute")
async def compute_risk_score(
    request: RiskScoreRequest,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """Compute AI risk score for a client. Returns 0-100 with factor breakdown."""
    from apps.api.app.models.client import Client
    from apps.api.app.services.risk_service import compute_client_risk_score

    client = db.query(Client).filter(
        Client.id == request.client_id,
        Client.workspace_id == workspace_id,
        Client.deleted_at.is_(None),
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    result = await compute_client_risk_score(client=client)
    return result
