from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime
import uuid


class InvoiceStatus(str, Enum):
    paid = "paid"
    pending = "pending"
    overdue = "overdue"
    disputed = "disputed"
    written_off = "written_off"


class EscalationStage(str, Enum):
    polite_reminder = "polite_reminder"
    firm_notice = "firm_notice"
    final_warning = "final_warning"
    legal_demand = "legal_demand"
    legal_action = "legal_action"


class LineItemSchema(BaseModel):
    id: str
    description: str
    quantity: float
    unit_price: float
    total: float


class InvoiceCreate(BaseModel):
    client_id: uuid.UUID
    invoice_number: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    due_date: datetime
    source_system: Optional[str] = Field(None, max_length=50)
    external_id: Optional[str] = Field(None, max_length=255)
    line_items: list[LineItemSchema] = []


class InvoiceStatusUpdate(BaseModel):
    status: InvoiceStatus


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    workspace_id: uuid.UUID
    invoice_number: str
    amount: float
    currency: str
    due_date: datetime
    status: InvoiceStatus
    days_past_due: int
    escalation_stage: Optional[EscalationStage]
    source_system: Optional[str]
    external_id: Optional[str]
    line_items: list[dict]
    last_escalated_at: Optional[datetime]
    next_escalation_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
