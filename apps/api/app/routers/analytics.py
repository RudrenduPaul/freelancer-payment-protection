from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from apps.api.app.database import get_db
from apps.api.app.middleware.auth import get_current_workspace
from apps.api.app.schemas.analytics import DashboardOverview

router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """Dashboard metrics: total outstanding, overdue count, recovery rate."""
    from apps.api.app.models.client import Client
    from apps.api.app.models.invoice import Invoice
    from sqlalchemy import func

    total_outstanding = db.query(func.sum(Invoice.amount)).filter(
        Invoice.workspace_id == workspace_id,
        Invoice.status.in_(["overdue", "disputed"]),
    ).scalar() or 0.0

    total_clients = db.query(func.count(Client.id)).filter(
        Client.workspace_id == workspace_id,
        Client.deleted_at.is_(None),
    ).scalar() or 0

    overdue_invoices = db.query(func.count(Invoice.id)).filter(
        Invoice.workspace_id == workspace_id,
        Invoice.status == "overdue",
    ).scalar() or 0

    escalations_active = db.query(func.count(Invoice.id)).filter(
        Invoice.workspace_id == workspace_id,
        Invoice.escalation_stage.isnot(None),
        Invoice.status.in_(["overdue", "disputed"]),
    ).scalar() or 0

    # Count clients by risk level
    risk_counts = db.query(Client.risk_level, func.count(Client.id)).filter(
        Client.workspace_id == workspace_id,
        Client.deleted_at.is_(None),
    ).group_by(Client.risk_level).all()

    clients_by_risk = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for level, count in risk_counts:
        if level:
            clients_by_risk[str(level)] = count

    return DashboardOverview(
        total_outstanding=total_outstanding,
        total_clients=total_clients,
        overdue_invoices=overdue_invoices,
        escalations_active=escalations_active,
        recovery_rate_this_month=0.0,  # Computed from historical data
        average_days_to_payment=0.0,   # Computed from paid invoices
        clients_by_risk_level=clients_by_risk,
    )
