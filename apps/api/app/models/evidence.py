import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from apps.api.app.models.base import Base


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=False)
    workspace_id = Column(String(36), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    source = Column(String(50), nullable=False)
    filename = Column(String(500), nullable=False)
    storage_url = Column(String(1000), nullable=False)
    file_hash = Column(String(64))
    file_size_bytes = Column(String(20))
    captured_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)

    invoice = relationship("Invoice", back_populates="evidence_items")
