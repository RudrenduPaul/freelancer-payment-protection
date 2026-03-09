from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional
from datetime import datetime


class _CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class LineItemSchema(_CamelModel):
    id: str
    description: str
    quantity: float
    unit_price: float
    total: float


class InvoiceCreate(_CamelModel):
    client_id: str
    invoice_number: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    due_date: datetime
    source_system: Optional[str] = Field(None, max_length=50)
    external_id: Optional[str] = Field(None, max_length=255)
    line_items: list[LineItemSchema] = []


class InvoiceStatusUpdate(_CamelModel):
    status: str  # paid | pending | overdue | disputed | written_off


class InvoiceResponse(_CamelModel):
    id: str
    client_id: str
    workspace_id: str
    invoice_number: str
    amount: float
    currency: str
    due_date: datetime
    status: str
    days_past_due: int
    escalation_stage: Optional[str] = None
    source_system: Optional[str] = None
    external_id: Optional[str] = None
    line_items: list[dict] = []
    last_escalated_at: Optional[datetime] = None
    next_escalation_date: Optional[datetime] = None
    evidence_count: int = 0
    created_at: datetime
    updated_at: datetime
