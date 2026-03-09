from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
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

    # Recovery rate: paid invoices / total invoices this month
    from datetime import datetime, timedelta
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_this_month = db.query(func.count(Invoice.id)).filter(
        Invoice.workspace_id == workspace_id,
        Invoice.created_at >= month_start,
    ).scalar() or 0

    paid_this_month = db.query(func.count(Invoice.id)).filter(
        Invoice.workspace_id == workspace_id,
        Invoice.status == "paid",
        Invoice.updated_at >= month_start,
    ).scalar() or 0

    recovery_rate = (paid_this_month / total_this_month * 100) if total_this_month > 0 else 0.0

    # Average days to payment from paid invoices
    paid_invoices = db.query(Invoice).filter(
        Invoice.workspace_id == workspace_id,
        Invoice.status == "paid",
    ).limit(100).all()

    avg_days = 0.0
    if paid_invoices:
        delays = [
            max(0, (inv.updated_at - inv.due_date).days)
            for inv in paid_invoices
            if inv.updated_at and inv.due_date
        ]
        avg_days = sum(delays) / len(delays) if delays else 0.0

    # Clients by risk level
    risk_counts = db.query(Client.risk_level, func.count(Client.id)).filter(
        Client.workspace_id == workspace_id,
        Client.deleted_at.is_(None),
    ).group_by(Client.risk_level).all()

    clients_by_risk: dict[str, int] = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for level, count in risk_counts:
        if level and str(level) in clients_by_risk:
            clients_by_risk[str(level)] = count

    return DashboardOverview(
        total_outstanding=round(total_outstanding, 2),
        total_clients=total_clients,
        overdue_invoices=overdue_invoices,
        escalations_active=escalations_active,
        recovery_rate_this_month=round(recovery_rate, 1),
        average_days_to_payment=round(avg_days, 1),
        clients_by_risk_level=clients_by_risk,
    )
