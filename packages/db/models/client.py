import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from packages.db.models.base import Base


class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    company = Column(String(255))
    industry = Column(String(100))
    country = Column(String(2))  # ISO 3166-1 alpha-2
    risk_score = Column(Float, default=0.0)
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.low)
    total_invoiced = Column(Float, default=0.0)
    total_outstanding = Column(Float, default=0.0)
    payment_terms_days = Column(Integer, default=30)
    average_payment_delay = Column(Float, default=0.0)
    contract_url = Column(String(500))
    notes = Column(String(5000))
    deleted_at = Column(DateTime, nullable=True)  # soft delete
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="clients")
    invoices = relationship("Invoice", back_populates="client", lazy="dynamic")
