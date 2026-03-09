import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from apps.api.app.models.base import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String(36), ForeignKey("clients.id"), nullable=False)
    workspace_id = Column(String(36), nullable=False, index=True)
    invoice_number = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    due_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")
    days_past_due = Column(Integer, default=0)
    escalation_stage = Column(String(50), nullable=True)
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
