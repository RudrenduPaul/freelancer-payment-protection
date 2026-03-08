from pydantic import BaseModel
from typing import Any


class DashboardOverview(BaseModel):
    total_outstanding: float
    total_clients: int
    overdue_invoices: int
    escalations_active: int
    recovery_rate_this_month: float
    average_days_to_payment: float
    clients_by_risk_level: dict[str, int]


class RecoveryTrendPoint(BaseModel):
    month: str
    recovery_rate: float
    amount_recovered: float
    amount_outstanding: float


class OverdueAgingBucket(BaseModel):
    bucket: str  # "1-7", "8-14", "15-21", "22-30", "30+"
    count: int
    total_amount: float


class EscalationEffectiveness(BaseModel):
    stage: str
    emails_sent: int
    recovery_rate: float
    average_days_to_resolution: float
