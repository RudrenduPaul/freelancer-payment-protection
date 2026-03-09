from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from apps.api.app.database import get_db
from apps.api.app.middleware.auth import get_current_workspace
from apps.api.app.schemas.invoice import InvoiceCreate, InvoiceStatusUpdate, InvoiceResponse

router = APIRouter()

VALID_STATUSES = {"paid", "pending", "overdue", "disputed", "written_off"}


def _enrich_invoice(invoice, db: Session) -> dict:
    """Add computed fields (evidence_count) to invoice data."""
    from apps.api.app.models.evidence import EvidenceItem
    evidence_count = db.query(func.count(EvidenceItem.id)).filter(
        EvidenceItem.invoice_id == str(invoice.id)
    ).scalar() or 0

    return {
        "id": str(invoice.id),
        "client_id": str(invoice.client_id),
        "workspace_id": str(invoice.workspace_id),
        "invoice_number": invoice.invoice_number,
        "amount": invoice.amount,
        "currency": invoice.currency,
        "due_date": invoice.due_date,
        "status": invoice.status,
        "days_past_due": invoice.days_past_due,
        "escalation_stage": invoice.escalation_stage,
        "source_system": invoice.source_system,
        "external_id": invoice.external_id,
        "line_items": invoice.line_items or [],
        "last_escalated_at": invoice.last_escalated_at,
        "next_escalation_date": invoice.next_escalation_date,
        "evidence_count": evidence_count,
        "created_at": invoice.created_at,
        "updated_at": invoice.updated_at,
    }


@router.get("", response_model=list[InvoiceResponse])
async def list_invoices(
    status_filter: Optional[str] = Query(None, alias="status"),
    client_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    from apps.api.app.models.invoice import Invoice

    query = db.query(Invoice).filter(Invoice.workspace_id == workspace_id)
    if status_filter:
        if status_filter not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")
        query = query.filter(Invoice.status == status_filter)
    if client_id:
        query = query.filter(Invoice.client_id == client_id)

    invoices = query.order_by(Invoice.due_date.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return [_enrich_invoice(inv, db) for inv in invoices]


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    from apps.api.app.models.invoice import Invoice
    from datetime import datetime

    invoice = Invoice(
        client_id=str(data.client_id),
        workspace_id=workspace_id,
        invoice_number=data.invoice_number,
        amount=data.amount,
        currency=data.currency,
        due_date=data.due_date,
        source_system=data.source_system or "manual",
        external_id=data.external_id,
        line_items=[item.model_dump(by_alias=False) for item in data.line_items],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return _enrich_invoice(invoice, db)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    from apps.api.app.models.invoice import Invoice

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.workspace_id == workspace_id,
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return _enrich_invoice(invoice, db)


@router.patch("/{invoice_id}/status", response_model=InvoiceResponse)
async def update_invoice_status(
    invoice_id: str,
    data: InvoiceStatusUpdate,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    from apps.api.app.models.invoice import Invoice
    from datetime import datetime

    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.workspace_id == workspace_id,
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.status = data.status
    if data.status == "paid":
        invoice.days_past_due = 0
        invoice.escalation_stage = None
        invoice.next_escalation_date = None
    invoice.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(invoice)
    return _enrich_invoice(invoice, db)
