import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from packages.db.models.base import Base


class InvoiceStatus(str, enum.Enum):
    paid = "paid"
    pending = "pending"
    overdue = "overdue"
    disputed = "disputed"
    written_off = "written_off"


class EscalationStage(str, enum.Enum):
    polite_reminder = "polite_reminder"
    firm_notice = "firm_notice"
    final_warning = "final_warning"
    legal_demand = "legal_demand"
    legal_action = "legal_action"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    invoice_number = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.pending)
    days_past_due = Column(Integer, default=0)
    escalation_stage = Column(Enum(EscalationStage), nullable=True)
    source_system = Column(String(50))
    external_id = Column(String(255))
    line_items = Column(JSON, default=list)
    last_escalated_at = Column(DateTime)
    next_escalation_date = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", back_populates="invoices")
    escalation_events = relationship("EscalationEvent", back_populates="invoice")
    evidence_items = relationship("EvidenceItem", back_populates="invoice")
