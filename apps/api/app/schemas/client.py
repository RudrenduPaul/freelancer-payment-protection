from pydantic import BaseModel, EmailStr, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional
from datetime import datetime


class _CamelModel(BaseModel):
    """Base model with camelCase aliases for frontend compatibility."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class ClientCreate(_CamelModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    payment_terms_days: int = Field(default=30, ge=1, le=365)
    contract_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=5000)


class ClientUpdate(_CamelModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    payment_terms_days: Optional[int] = Field(None, ge=1, le=365)
    contract_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=5000)


class ClientResponse(_CamelModel):
    id: str
    workspace_id: str
    name: str
    email: str
    company: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    risk_score: float
    risk_level: str
    total_invoiced: float
    total_outstanding: float
    payment_terms_days: int
    average_payment_delay: float
    contract_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
