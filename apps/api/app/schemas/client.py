from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from datetime import datetime
import uuid


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ClientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    payment_terms_days: int = Field(default=30, ge=1, le=365)
    contract_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=5000)


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    payment_terms_days: Optional[int] = Field(None, ge=1, le=365)
    contract_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=5000)


class ClientResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    email: str
    company: Optional[str]
    industry: Optional[str]
    country: Optional[str]
    risk_score: float
    risk_level: RiskLevel
    total_invoiced: float
    total_outstanding: float
    payment_terms_days: int
    average_payment_delay: float
    contract_url: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
