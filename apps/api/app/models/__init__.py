# Import all models so SQLAlchemy registers them with Base metadata.
# Order matters — import Client before Invoice (FK dependency).
from apps.api.app.models.base import Base  # noqa: F401
from apps.api.app.models.client import Client  # noqa: F401
from apps.api.app.models.invoice import Invoice  # noqa: F401
from apps.api.app.models.escalation import EscalationEvent  # noqa: F401
from apps.api.app.models.evidence import EvidenceItem  # noqa: F401

__all__ = ["Base", "Client", "Invoice", "EscalationEvent", "EvidenceItem"]
