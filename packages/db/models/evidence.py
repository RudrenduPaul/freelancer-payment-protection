import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from packages.db.models.base import Base


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # email | slack_message | contract | screenshot | document
    source = Column(String(50), nullable=False)  # gmail | slack | manual_upload | auto_captured
    filename = Column(String(500), nullable=False)
    storage_url = Column(String(1000), nullable=False)
    file_hash = Column(String(64))  # SHA-256 for integrity
    file_size_bytes = Column(String(20))
    captured_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)

    invoice = relationship("Invoice", back_populates="evidence_items")
