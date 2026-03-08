import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum
from sqlalchemy.orm import relationship
from apps.api.app.database import engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Client(Base):
    __tablename__ = "clients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    company = Column(String(255))
    industry = Column(String(100))
    country = Column(String(2))
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="low")
    total_invoiced = Column(Float, default=0.0)
    total_outstanding = Column(Float, default=0.0)
    payment_terms_days = Column(Integer, default=30)
    average_payment_delay = Column(Float, default=0.0)
    contract_url = Column(String(500))
    notes = Column(String(5000))
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    invoices = relationship("Invoice", back_populates="client", lazy="dynamic")
