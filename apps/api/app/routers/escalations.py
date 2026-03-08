from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from apps.api.app.database import get_db
from apps.api.app.middleware.auth import get_current_workspace
from apps.api.app.middleware.rate_limit import limiter

router = APIRouter()


@router.get("")
async def list_active_escalations(
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """List all active escalations grouped by stage."""
    from apps.api.app.models.invoice import Invoice

    invoices = db.query(Invoice).filter(
        Invoice.workspace_id == workspace_id,
        Invoice.escalation_stage.isnot(None),
        Invoice.status.in_(["overdue", "disputed"]),
    ).all()

    grouped: dict = {
        "polite_reminder": [],
        "firm_notice": [],
        "final_warning": [],
        "legal_demand": [],
        "legal_action": [],
    }

    for inv in invoices:
        if inv.escalation_stage in grouped:
            grouped[inv.escalation_stage].append({
                "invoice_id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "amount": inv.amount,
                "currency": inv.currency,
                "days_past_due": inv.days_past_due,
                "client_id": str(inv.client_id),
            })

    return grouped


@router.post("/{invoice_id}/draft")
async def draft_escalation_email(
    invoice_id: str,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """AI-draft the next escalation email for preview before sending."""
    from apps.api.app.models.invoice import Invoice
    from apps.api.app.models.client import Client
    from apps.api.app.services.escalation_service import draft_escalation_email

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.workspace_id == workspace_id,
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    client = db.query(Client).filter(Client.id == invoice.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    draft = await draft_escalation_email(invoice=invoice, client=client)
    return draft


@router.get("/{invoice_id}/history")
async def get_escalation_history(
    invoice_id: str,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """Get full escalation history for an invoice."""
    from apps.api.app.models.invoice import Invoice
    from apps.api.app.models.escalation import EscalationEvent

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.workspace_id == workspace_id,
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    events = db.query(EscalationEvent).filter(
        EscalationEvent.invoice_id == invoice_id,
    ).order_by(EscalationEvent.created_at.asc()).all()

    return events
