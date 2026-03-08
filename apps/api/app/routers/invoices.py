from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from apps.api.app.database import get_db
from apps.api.app.middleware.auth import get_current_workspace
from apps.api.app.schemas.invoice import InvoiceCreate, InvoiceStatusUpdate, InvoiceResponse

router = APIRouter()


@router.get("", response_model=list[InvoiceResponse])
async def list_invoices(
    status_filter: Optional[str] = Query(None, alias="status"),
    client_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """List invoices for the current workspace."""
    from apps.api.app.models.invoice import Invoice

    query = db.query(Invoice).filter(Invoice.workspace_id == workspace_id)

    if status_filter:
        query = query.filter(Invoice.status == status_filter)
    if client_id:
        query = query.filter(Invoice.client_id == client_id)

    return query.order_by(Invoice.due_date.asc()).offset((page - 1) * page_size).limit(page_size).all()


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """Create a new invoice manually."""
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
        line_items=[item.model_dump() for item in data.line_items],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """Get invoice detail."""
    from apps.api.app.models.invoice import Invoice

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.workspace_id == workspace_id,
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.patch("/{invoice_id}/status", response_model=InvoiceResponse)
async def update_invoice_status(
    invoice_id: str,
    data: InvoiceStatusUpdate,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """Update invoice status (e.g., mark as paid)."""
    from apps.api.app.models.invoice import Invoice
    from datetime import datetime

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.workspace_id == workspace_id,
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.status = data.status.value
    if data.status.value == "paid":
        invoice.days_past_due = 0
        invoice.escalation_stage = None
        invoice.next_escalation_date = None
    invoice.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(invoice)
    return invoice
