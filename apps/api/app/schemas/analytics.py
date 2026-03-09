from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class DashboardOverview(_CamelModel):
    total_outstanding: float
    total_clients: int
    overdue_invoices: int
    escalations_active: int
    recovery_rate_this_month: float
    average_days_to_payment: float
    clients_by_risk_level: dict[str, int]


class RecoveryTrendPoint(_CamelModel):
    month: str
    recovery_rate: float
    amount_recovered: float
    amount_outstanding: float


class OverdueAgingBucket(_CamelModel):
    bucket: str
    count: int
    total_amount: float


class EscalationEffectiveness(_CamelModel):
    stage: str
    emails_sent: int
    recovery_rate: float
    average_days_to_resolution: float


class RiskScoreResponse(_CamelModel):
    score: float
    level: str
    factors: list[dict]
    reasoning: str


class DemandLetterResponse(_CamelModel):
    document_id: str
    status: str
    estimated_ready_seconds: Optional[int] = None
    download_url: Optional[str] = None
    disclaimer: str
