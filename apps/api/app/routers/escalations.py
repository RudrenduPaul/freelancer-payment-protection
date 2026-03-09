from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from apps.api.app.database import get_db
from apps.api.app.middleware.auth import get_current_workspace

router = APIRouter()


@router.get("")
async def list_active_escalations(
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """List all active escalations grouped by stage."""
    from apps.api.app.models.invoice import Invoice
    from apps.api.app.models.client import Client

    invoices = db.query(Invoice, Client).join(
        Client, Invoice.client_id == Client.id
    ).filter(
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

    for inv, client in invoices:
        stage = inv.escalation_stage
        if stage in grouped:
            grouped[stage].append({
                "invoiceId": str(inv.id),
                "invoiceNumber": inv.invoice_number,
                "amount": inv.amount,
                "currency": inv.currency,
                "daysPastDue": inv.days_past_due,
                "clientId": str(inv.client_id),
                "clientName": client.name,
                "clientCompany": client.company,
                "nextEscalationDate": inv.next_escalation_date.isoformat() if inv.next_escalation_date else None,
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
    from apps.api.app.services.escalation_service import draft_escalation_email as _draft

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.workspace_id == workspace_id,
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    client = db.query(Client).filter(
        Client.id == invoice.client_id,
        Client.workspace_id == workspace_id,
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return await _draft(invoice=invoice, client=client)


@router.get("/{invoice_id}/history")
async def get_escalation_history(
    invoice_id: str,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """Get full escalation history for an invoice."""
    from apps.api.app.models.invoice import Invoice
    from apps.api.app.models.escalation import EscalationEvent

    # Verify invoice belongs to workspace
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.workspace_id == workspace_id,
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    events = db.query(EscalationEvent).filter(
        EscalationEvent.invoice_id == invoice_id,
        EscalationEvent.workspace_id == workspace_id,
    ).order_by(EscalationEvent.created_at.asc()).all()

    return [
        {
            "id": str(e.id),
            "stage": e.stage,
            "emailSubject": e.email_subject,
            "emailBody": e.email_body,
            "generatedByAI": e.generated_by_ai,
            "aiConfidenceScore": e.ai_confidence_score,
            "sentAt": e.sent_at.isoformat() if e.sent_at else None,
            "openedAt": e.opened_at.isoformat() if e.opened_at else None,
            "outcome": e.outcome,
            "createdAt": e.created_at.isoformat(),
        }
        for e in events
    ]
