import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from apps.api.app.models.client import Base


class EscalationEvent(Base):
    __tablename__ = "escalation_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=False)
    client_id = Column(String(36), nullable=False)
    stage = Column(String(50), nullable=False)
    email_subject = Column(String(500))
    email_body = Column(String(10000))
    generated_by_ai = Column(Boolean, default=True)
    ai_confidence_score = Column(Float)
    sent_at = Column(DateTime)
    opened_at = Column(DateTime)
    replied_at = Column(DateTime)
    outcome = Column(String(50))
    document_url = Column(String(500))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="escalation_events")
