"""
Seed script — populates the local SQLite dev database with realistic dummy data.

Run from the repo root:
    python scripts/seed_dev.py

Idempotent: drops and recreates seed data on each run.
No real credentials needed — uses the local SQLite DB only.
"""
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# ── Path setup ──────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# ── Placeholder env vars (satisfy Pydantic Settings — no real keys) ─────────
os.environ.setdefault("ANTHROPIC_API_KEY", "seed-placeholder-not-a-real-key")
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "seed-service-role-placeholder")
os.environ.setdefault("SUPABASE_ANON_KEY", "seed-anon-key-placeholder")
os.environ.setdefault("JWT_SECRET", "seed-jwt-secret-at-least-32-chars-placeholder")
os.environ.setdefault("RESEND_API_KEY", "seed-resend-key-placeholder")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{REPO_ROOT}/apps/api/dev.db")
os.environ.setdefault("ENVIRONMENT", "test")  # suppress SQL echo during seed

from apps.api.app.database import engine, SessionLocal, create_all_tables  # noqa: E402
import apps.api.app.models  # noqa: E402, F401 — registers all models with Base
from apps.api.app.models.base import Base  # noqa: E402
from apps.api.app.models.client import Client  # noqa: E402
from apps.api.app.models.invoice import Invoice  # noqa: E402
from apps.api.app.models.escalation import EscalationEvent  # noqa: E402

# ── Constants ────────────────────────────────────────────────────────────────
DEMO_WORKSPACE_ID = "ws-demo-00000000-0000-0000-0000-000000000001"
NOW = datetime.utcnow()


def days_ago(n: int) -> datetime:
    return NOW - timedelta(days=n)


def days_from_now(n: int) -> datetime:
    return NOW + timedelta(days=n)


# ── Client seed data ─────────────────────────────────────────────────────────
# 8 clients spanning all 4 risk levels
CLIENTS = [
    # Low risk — pay promptly, tech industry
    {
        "name": "Priya Sharma",
        "email": "priya@brightpath.io",
        "company": "BrightPath Technologies",
        "industry": "Technology",
        "country": "US",
        "risk_score": 12.0,
        "risk_level": "low",
        "total_invoiced": 28500.0,
        "total_outstanding": 0.0,
        "payment_terms_days": 14,
        "average_payment_delay": -2.0,  # pays 2 days early on average
        "notes": "Excellent client. Always pays early. Refer to for testimonials.",
    },
    {
        "name": "Tom Hargreaves",
        "email": "tom@novadesign.co.uk",
        "company": "Nova Design Studio",
        "industry": "Design & Creative",
        "country": "GB",
        "risk_score": 18.0,
        "risk_level": "low",
        "total_invoiced": 14750.0,
        "total_outstanding": 0.0,
        "payment_terms_days": 30,
        "average_payment_delay": 3.0,
        "notes": "Reliable. Small agency, occasional 2-3 day delay but always pays.",
    },
    # Medium risk — occasional delays, growing companies
    {
        "name": "Marcus Webb",
        "email": "marcus@scalehq.com",
        "company": "ScaleHQ Inc.",
        "industry": "SaaS",
        "country": "US",
        "risk_score": 38.0,
        "risk_level": "medium",
        "total_invoiced": 52000.0,
        "total_outstanding": 8500.0,
        "payment_terms_days": 30,
        "average_payment_delay": 12.0,
        "notes": "Growing startup. Cash-strapped some months. Usually pays after a reminder.",
    },
    {
        "name": "Anika Patel",
        "email": "anika@founderslab.ca",
        "company": "Founders Lab",
        "industry": "Consulting",
        "country": "CA",
        "risk_score": 45.0,
        "risk_level": "medium",
        "total_invoiced": 31200.0,
        "total_outstanding": 5800.0,
        "payment_terms_days": 30,
        "average_payment_delay": 18.0,
        "notes": "Pays but needs nudging. Prefers email reminders over calls.",
    },
    # High risk — frequent disputes or significant delays
    {
        "name": "Derek Olsson",
        "email": "derek@vitalcommerce.se",
        "company": "Vital Commerce AB",
        "industry": "E-commerce",
        "country": "SE",
        "risk_score": 62.0,
        "risk_level": "high",
        "total_invoiced": 89000.0,
        "total_outstanding": 22400.0,
        "payment_terms_days": 45,
        "average_payment_delay": 34.0,
        "notes": "High volume but payment delays are routine. Always escalate after day 30.",
    },
    {
        "name": "Samira Al-Farouk",
        "email": "samira@meridianmedia.ae",
        "company": "Meridian Media Group",
        "industry": "Media & Entertainment",
        "country": "AE",
        "risk_score": 71.0,
        "risk_level": "high",
        "total_invoiced": 44600.0,
        "total_outstanding": 18700.0,
        "payment_terms_days": 30,
        "average_payment_delay": 45.0,
        "notes": "Multiple invoices currently overdue. Disputes scope frequently. Document everything.",
    },
    # Critical risk — in active dispute / legal proceedings
    {
        "name": "Grant Holloway",
        "email": "grant@nexvault.com",
        "company": "NexVault Financial",
        "industry": "Finance & Insurance",
        "country": "US",
        "risk_score": 88.0,
        "risk_level": "critical",
        "total_invoiced": 67500.0,
        "total_outstanding": 35000.0,
        "payment_terms_days": 30,
        "average_payment_delay": 72.0,
        "notes": "CRITICAL: Invoice #INV-2024-041 in formal dispute. Retain all evidence. Legal demand sent.",
    },
    {
        "name": "Lena Voigt",
        "email": "lena@konstrukt.de",
        "company": "Konstrukt GmbH",
        "industry": "Architecture & Engineering",
        "country": "DE",
        "risk_score": 79.0,
        "risk_level": "critical",
        "total_invoiced": 103000.0,
        "total_outstanding": 41500.0,
        "payment_terms_days": 60,
        "average_payment_delay": 61.0,
        "notes": "Long-term client turned bad. Project disputes. Pursue legal action.",
    },
]

# ── Invoice seed data (keyed by client index) ─────────────────────────────
# invoice_number, amount, currency, status, days_past_due, escalation_stage,
# due_offset (negative = overdue, positive = upcoming), line_items
INVOICES = [
    # Priya Sharma (idx 0) — all paid
    {
        "client_idx": 0,
        "invoice_number": "INV-2024-001",
        "amount": 12500.0,
        "currency": "USD",
        "status": "paid",
        "days_past_due": 0,
        "escalation_stage": None,
        "due_offset": -60,
        "paid": True,
        "line_items": [
            {"description": "UX audit & redesign", "quantity": 1, "unit_price": 12500.0, "total": 12500.0}
        ],
    },
    {
        "client_idx": 0,
        "invoice_number": "INV-2024-019",
        "amount": 8200.0,
        "currency": "USD",
        "status": "paid",
        "days_past_due": 0,
        "escalation_stage": None,
        "due_offset": -20,
        "paid": True,
        "line_items": [
            {"description": "Frontend development — Sprint 4", "quantity": 40, "unit_price": 205.0, "total": 8200.0}
        ],
    },
    # Tom Hargreaves (idx 1) — one paid, one upcoming
    {
        "client_idx": 1,
        "invoice_number": "INV-2024-007",
        "amount": 6750.0,
        "currency": "GBP",
        "status": "paid",
        "days_past_due": 0,
        "escalation_stage": None,
        "due_offset": -45,
        "paid": True,
        "line_items": [
            {"description": "Brand identity package", "quantity": 1, "unit_price": 6750.0, "total": 6750.0}
        ],
    },
    {
        "client_idx": 1,
        "invoice_number": "INV-2024-031",
        "amount": 3200.0,
        "currency": "GBP",
        "status": "pending",
        "days_past_due": 0,
        "escalation_stage": None,
        "due_offset": 12,
        "paid": False,
        "line_items": [
            {"description": "Social media asset pack", "quantity": 1, "unit_price": 3200.0, "total": 3200.0}
        ],
    },
    # Marcus Webb (idx 2) — one overdue (polite_reminder stage), one paid
    {
        "client_idx": 2,
        "invoice_number": "INV-2024-022",
        "amount": 8500.0,
        "currency": "USD",
        "status": "overdue",
        "days_past_due": 18,
        "escalation_stage": "polite_reminder",
        "due_offset": -18,
        "paid": False,
        "line_items": [
            {"description": "Growth strategy consulting", "quantity": 10, "unit_price": 650.0, "total": 6500.0},
            {"description": "Competitive analysis report", "quantity": 1, "unit_price": 2000.0, "total": 2000.0},
        ],
    },
    {
        "client_idx": 2,
        "invoice_number": "INV-2024-011",
        "amount": 14200.0,
        "currency": "USD",
        "status": "paid",
        "days_past_due": 0,
        "escalation_stage": None,
        "due_offset": -90,
        "paid": True,
        "line_items": [
            {"description": "Product roadmap & MVP planning", "quantity": 1, "unit_price": 14200.0, "total": 14200.0}
        ],
    },
    # Anika Patel (idx 3) — overdue (firm_notice), one paid
    {
        "client_idx": 3,
        "invoice_number": "INV-2024-026",
        "amount": 5800.0,
        "currency": "CAD",
        "status": "overdue",
        "days_past_due": 31,
        "escalation_stage": "firm_notice",
        "due_offset": -31,
        "paid": False,
        "line_items": [
            {"description": "Operations consulting — October", "quantity": 1, "unit_price": 5800.0, "total": 5800.0}
        ],
    },
    {
        "client_idx": 3,
        "invoice_number": "INV-2024-014",
        "amount": 7400.0,
        "currency": "CAD",
        "status": "paid",
        "days_past_due": 0,
        "escalation_stage": None,
        "due_offset": -75,
        "paid": True,
        "line_items": [
            {"description": "Process optimisation workshop", "quantity": 2, "unit_price": 3700.0, "total": 7400.0}
        ],
    },
    # Derek Olsson (idx 4) — two overdue at different stages
    {
        "client_idx": 4,
        "invoice_number": "INV-2024-029",
        "amount": 15600.0,
        "currency": "USD",
        "status": "overdue",
        "days_past_due": 42,
        "escalation_stage": "final_warning",
        "due_offset": -42,
        "paid": False,
        "line_items": [
            {"description": "E-commerce platform integration", "quantity": 1, "unit_price": 12000.0, "total": 12000.0},
            {"description": "Performance optimisation audit", "quantity": 1, "unit_price": 3600.0, "total": 3600.0},
        ],
    },
    {
        "client_idx": 4,
        "invoice_number": "INV-2024-034",
        "amount": 6800.0,
        "currency": "USD",
        "status": "overdue",
        "days_past_due": 14,
        "escalation_stage": "polite_reminder",
        "due_offset": -14,
        "paid": False,
        "line_items": [
            {"description": "Monthly retainer — December", "quantity": 1, "unit_price": 6800.0, "total": 6800.0}
        ],
    },
    # Samira Al-Farouk (idx 5) — disputed + overdue at firm_notice
    {
        "client_idx": 5,
        "invoice_number": "INV-2024-033",
        "amount": 18700.0,
        "currency": "USD",
        "status": "disputed",
        "days_past_due": 55,
        "escalation_stage": "legal_demand",
        "due_offset": -55,
        "paid": False,
        "line_items": [
            {"description": "Campaign production — Q4", "quantity": 1, "unit_price": 14000.0, "total": 14000.0},
            {"description": "Talent coordination fee", "quantity": 1, "unit_price": 4700.0, "total": 4700.0},
        ],
    },
    {
        "client_idx": 5,
        "invoice_number": "INV-2024-028",
        "amount": 9400.0,
        "currency": "USD",
        "status": "overdue",
        "days_past_due": 28,
        "escalation_stage": "firm_notice",
        "due_offset": -28,
        "paid": False,
        "line_items": [
            {"description": "Video production — Brand film", "quantity": 1, "unit_price": 9400.0, "total": 9400.0}
        ],
    },
    # Grant Holloway (idx 6) — critical: legal_demand + legal_action
    {
        "client_idx": 6,
        "invoice_number": "INV-2024-041",
        "amount": 35000.0,
        "currency": "USD",
        "status": "disputed",
        "days_past_due": 78,
        "escalation_stage": "legal_action",
        "due_offset": -78,
        "paid": False,
        "line_items": [
            {"description": "Fintech platform architecture — Phase 2", "quantity": 1, "unit_price": 28000.0, "total": 28000.0},
            {"description": "Security audit & penetration testing", "quantity": 1, "unit_price": 7000.0, "total": 7000.0},
        ],
    },
    {
        "client_idx": 6,
        "invoice_number": "INV-2024-018",
        "amount": 12500.0,
        "currency": "USD",
        "status": "paid",
        "days_past_due": 0,
        "escalation_stage": None,
        "due_offset": -120,
        "paid": True,
        "line_items": [
            {"description": "Compliance framework design", "quantity": 1, "unit_price": 12500.0, "total": 12500.0}
        ],
    },
    # Lena Voigt (idx 7) — critical: legal_demand stage, another overdue
    {
        "client_idx": 7,
        "invoice_number": "INV-2024-038",
        "amount": 41500.0,
        "currency": "EUR",
        "status": "overdue",
        "days_past_due": 65,
        "escalation_stage": "legal_demand",
        "due_offset": -65,
        "paid": False,
        "line_items": [
            {"description": "Mixed-use development — architectural drawings", "quantity": 1, "unit_price": 32000.0, "total": 32000.0},
            {"description": "Engineering compliance review", "quantity": 1, "unit_price": 9500.0, "total": 9500.0},
        ],
    },
    {
        "client_idx": 7,
        "invoice_number": "INV-2024-025",
        "amount": 28000.0,
        "currency": "EUR",
        "status": "paid",
        "days_past_due": 0,
        "escalation_stage": None,
        "due_offset": -100,
        "paid": True,
        "line_items": [
            {"description": "Residential complex — concept design", "quantity": 1, "unit_price": 28000.0, "total": 28000.0}
        ],
    },
]

# ── Escalation event seed data ────────────────────────────────────────────
# One or more escalation events per active-escalation invoice
ESCALATION_EVENTS = [
    # INV-2024-022 (Marcus / polite_reminder)
    {
        "invoice_idx": 4,  # index into created invoices list
        "client_idx": 2,
        "stage": "polite_reminder",
        "email_subject": "Friendly reminder — Invoice INV-2024-022 is now overdue",
        "email_body": (
            "Hi Marcus,\n\nI hope you're doing well! Just a quick note that Invoice "
            "INV-2024-022 for $8,500 was due 18 days ago. Could you let me know when "
            "I can expect payment, or if there's anything I can help clarify?\n\n"
            "Thanks so much — I really enjoyed working on the growth strategy with you.\n\n"
            "Best,\n[Freelancer]"
        ),
        "generated_by_ai": True,
        "ai_confidence_score": 0.91,
        "sent_at": days_ago(16),
        "opened_at": days_ago(15),
        "replied_at": None,
        "outcome": None,
    },
    # INV-2024-026 (Anika / firm_notice) — two events
    {
        "invoice_idx": 6,
        "client_idx": 3,
        "stage": "polite_reminder",
        "email_subject": "Payment reminder — Invoice INV-2024-026",
        "email_body": (
            "Hi Anika,\n\nJust a friendly heads-up that Invoice INV-2024-026 for CAD 5,800 "
            "is now overdue. No worries yet — let me know if you need anything from my side.\n\n"
            "Best,\n[Freelancer]"
        ),
        "generated_by_ai": True,
        "ai_confidence_score": 0.88,
        "sent_at": days_ago(28),
        "opened_at": days_ago(27),
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 6,
        "client_idx": 3,
        "stage": "firm_notice",
        "email_subject": "Second notice — Invoice INV-2024-026 — CAD 5,800 outstanding",
        "email_body": (
            "Hi Anika,\n\nI sent a reminder two weeks ago regarding Invoice INV-2024-026 "
            "for CAD 5,800, now 31 days overdue. I need to ask for immediate payment within "
            "7 business days to avoid further action.\n\n"
            "If there's an issue I'm unaware of, please reach out today.\n\n"
            "Regards,\n[Freelancer]"
        ),
        "generated_by_ai": True,
        "ai_confidence_score": 0.85,
        "sent_at": days_ago(7),
        "opened_at": days_ago(7),
        "replied_at": None,
        "outcome": None,
    },
    # INV-2024-029 (Derek / final_warning) — three events
    {
        "invoice_idx": 8,
        "client_idx": 4,
        "stage": "polite_reminder",
        "email_subject": "Friendly reminder — Invoice INV-2024-029",
        "email_body": "Hi Derek, just a reminder that INV-2024-029 for $15,600 is now overdue.",
        "generated_by_ai": True,
        "ai_confidence_score": 0.92,
        "sent_at": days_ago(38),
        "opened_at": days_ago(37),
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 8,
        "client_idx": 4,
        "stage": "firm_notice",
        "email_subject": "Second notice — Invoice INV-2024-029 — $15,600 overdue",
        "email_body": (
            "Hi Derek,\n\nThis is my second notice for Invoice INV-2024-029 ($15,600), now 28 days "
            "overdue. Please arrange payment within 7 days.\n\nRegards,\n[Freelancer]"
        ),
        "generated_by_ai": True,
        "ai_confidence_score": 0.87,
        "sent_at": days_ago(24),
        "opened_at": None,
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 8,
        "client_idx": 4,
        "stage": "final_warning",
        "email_subject": "FINAL WARNING — Invoice INV-2024-029 — Legal action pending",
        "email_body": (
            "Dear Mr. Olsson,\n\nDespite two previous notices, Invoice INV-2024-029 for $15,600 remains "
            "unpaid at 42 days overdue. This is your final notice before I initiate legal proceedings. "
            "Full payment must be received within 5 business days.\n\nAll correspondence is being "
            "retained for evidentiary purposes.\n\nRegards,\n[Freelancer]"
        ),
        "generated_by_ai": True,
        "ai_confidence_score": 0.93,
        "sent_at": days_ago(5),
        "opened_at": days_ago(5),
        "replied_at": None,
        "outcome": None,
    },
    # INV-2024-033 (Samira / legal_demand — disputed)
    {
        "invoice_idx": 10,
        "client_idx": 5,
        "stage": "polite_reminder",
        "email_subject": "Payment reminder — Invoice INV-2024-033",
        "email_body": "Hi Samira, just a reminder that INV-2024-033 for $18,700 is overdue.",
        "generated_by_ai": True,
        "ai_confidence_score": 0.89,
        "sent_at": days_ago(50),
        "opened_at": days_ago(49),
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 10,
        "client_idx": 5,
        "stage": "firm_notice",
        "email_subject": "Second notice — Invoice INV-2024-033 — $18,700 outstanding",
        "email_body": "This is my second notice for Invoice INV-2024-033. Payment required within 7 days.",
        "generated_by_ai": True,
        "ai_confidence_score": 0.86,
        "sent_at": days_ago(38),
        "opened_at": None,
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 10,
        "client_idx": 5,
        "stage": "final_warning",
        "email_subject": "FINAL WARNING — Invoice INV-2024-033",
        "email_body": "Final warning before legal proceedings. Pay within 5 days.",
        "generated_by_ai": True,
        "ai_confidence_score": 0.90,
        "sent_at": days_ago(25),
        "opened_at": days_ago(24),
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 10,
        "client_idx": 5,
        "stage": "legal_demand",
        "email_subject": "LEGAL DEMAND — Invoice INV-2024-033 — Formal demand for payment",
        "email_body": (
            "Dear Ms. Al-Farouk,\n\nThis constitutes a formal legal demand for immediate payment of "
            "$18,700 in respect of Invoice INV-2024-033. Failure to pay within 7 days will result "
            "in proceedings being filed without further notice.\n\nAll evidence and communications "
            "are preserved.\n\n[Freelancer]"
        ),
        "generated_by_ai": True,
        "ai_confidence_score": 0.95,
        "sent_at": days_ago(10),
        "opened_at": days_ago(9),
        "replied_at": days_ago(8),
        "outcome": "disputed",
    },
    # INV-2024-041 (Grant / legal_action — critical)
    {
        "invoice_idx": 12,
        "client_idx": 6,
        "stage": "polite_reminder",
        "email_subject": "Payment reminder — Invoice INV-2024-041",
        "email_body": "Hi Grant, just a reminder that INV-2024-041 for $35,000 is overdue.",
        "generated_by_ai": True,
        "ai_confidence_score": 0.90,
        "sent_at": days_ago(72),
        "opened_at": days_ago(71),
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 12,
        "client_idx": 6,
        "stage": "firm_notice",
        "email_subject": "Second notice — Invoice INV-2024-041",
        "email_body": "Second and final friendly notice. Payment required within 7 days.",
        "generated_by_ai": True,
        "ai_confidence_score": 0.88,
        "sent_at": days_ago(58),
        "opened_at": None,
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 12,
        "client_idx": 6,
        "stage": "final_warning",
        "email_subject": "FINAL WARNING — Invoice INV-2024-041 — $35,000",
        "email_body": "Final warning before legal action. 5 business days to pay.",
        "generated_by_ai": True,
        "ai_confidence_score": 0.92,
        "sent_at": days_ago(44),
        "opened_at": days_ago(44),
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 12,
        "client_idx": 6,
        "stage": "legal_demand",
        "email_subject": "LEGAL DEMAND — Invoice INV-2024-041 — NexVault Financial",
        "email_body": (
            "Dear Mr. Holloway,\n\nFormal demand for payment of $35,000. Legal proceedings will "
            "be initiated without further notice within 7 days.\n\n[Freelancer]"
        ),
        "generated_by_ai": True,
        "ai_confidence_score": 0.94,
        "sent_at": days_ago(30),
        "opened_at": days_ago(29),
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 12,
        "client_idx": 6,
        "stage": "legal_action",
        "email_subject": "Notice of Legal Proceedings — Invoice INV-2024-041",
        "email_body": (
            "Dear Mr. Holloway,\n\nPlease be advised that legal proceedings have been initiated "
            "for recovery of $35,000 under Invoice INV-2024-041. This matter has been referred "
            "to our legal counsel.\n\n[Freelancer]"
        ),
        "generated_by_ai": True,
        "ai_confidence_score": 0.97,
        "sent_at": days_ago(10),
        "opened_at": days_ago(9),
        "replied_at": None,
        "outcome": None,
    },
    # INV-2024-038 (Lena / legal_demand)
    {
        "invoice_idx": 14,
        "client_idx": 7,
        "stage": "polite_reminder",
        "email_subject": "Payment reminder — Invoice INV-2024-038",
        "email_body": "Hi Lena, just a reminder that INV-2024-038 for €41,500 is overdue.",
        "generated_by_ai": True,
        "ai_confidence_score": 0.88,
        "sent_at": days_ago(60),
        "opened_at": days_ago(59),
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 14,
        "client_idx": 7,
        "stage": "firm_notice",
        "email_subject": "Second notice — Invoice INV-2024-038 — €41,500",
        "email_body": "This is my second notice. Please pay within 7 days.",
        "generated_by_ai": True,
        "ai_confidence_score": 0.86,
        "sent_at": days_ago(46),
        "opened_at": None,
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 14,
        "client_idx": 7,
        "stage": "final_warning",
        "email_subject": "FINAL WARNING — Invoice INV-2024-038",
        "email_body": "Final warning. Legal action will follow within 5 business days if not paid.",
        "generated_by_ai": True,
        "ai_confidence_score": 0.91,
        "sent_at": days_ago(32),
        "opened_at": days_ago(31),
        "replied_at": None,
        "outcome": "no_response",
    },
    {
        "invoice_idx": 14,
        "client_idx": 7,
        "stage": "legal_demand",
        "email_subject": "LEGAL DEMAND — Invoice INV-2024-038 — Konstrukt GmbH",
        "email_body": (
            "Dear Ms. Voigt,\n\nFormal demand for payment of €41,500 outstanding under Invoice "
            "INV-2024-038. Failure to pay within 7 days will result in court proceedings.\n\n[Freelancer]"
        ),
        "generated_by_ai": True,
        "ai_confidence_score": 0.96,
        "sent_at": days_ago(15),
        "opened_at": days_ago(14),
        "replied_at": None,
        "outcome": None,
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED = "\033[91m"
ANSI_CYAN = "\033[96m"
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"


def banner(text: str) -> None:
    print(f"\n{ANSI_BOLD}{ANSI_CYAN}{'─' * 60}{ANSI_RESET}")
    print(f"{ANSI_BOLD}{ANSI_CYAN}  {text}{ANSI_RESET}")
    print(f"{ANSI_BOLD}{ANSI_CYAN}{'─' * 60}{ANSI_RESET}")


def ok(text: str) -> None:
    print(f"  {ANSI_GREEN}✓{ANSI_RESET}  {text}")


def warn(text: str) -> None:
    print(f"  {ANSI_YELLOW}⚠{ANSI_RESET}  {text}")


# ── Main seed function ────────────────────────────────────────────────────────
def seed() -> None:
    banner("Step 1 — Create tables")
    create_all_tables()
    ok("Tables created (or already exist)")

    db = SessionLocal()
    try:
        banner("Step 2 — Clear existing seed data")
        deleted = (
            db.query(EscalationEvent)
            .filter(EscalationEvent.workspace_id == DEMO_WORKSPACE_ID)
            .delete(synchronize_session=False)
        )
        ok(f"Removed {deleted} escalation events")

        deleted = (
            db.query(Invoice)
            .filter(Invoice.workspace_id == DEMO_WORKSPACE_ID)
            .delete(synchronize_session=False)
        )
        ok(f"Removed {deleted} invoices")

        deleted = (
            db.query(Client)
            .filter(Client.workspace_id == DEMO_WORKSPACE_ID)
            .delete(synchronize_session=False)
        )
        ok(f"Removed {deleted} clients")
        db.commit()

        banner("Step 3 — Seed clients")
        created_clients: list[Client] = []
        for c in CLIENTS:
            client = Client(
                id=str(uuid.uuid4()),
                workspace_id=DEMO_WORKSPACE_ID,
                name=c["name"],
                email=c["email"],
                company=c.get("company"),
                industry=c.get("industry"),
                country=c.get("country"),
                risk_score=c["risk_score"],
                risk_level=c["risk_level"],
                total_invoiced=c["total_invoiced"],
                total_outstanding=c["total_outstanding"],
                payment_terms_days=c["payment_terms_days"],
                average_payment_delay=c["average_payment_delay"],
                notes=c.get("notes"),
                created_at=days_ago(180),
                updated_at=NOW,
            )
            db.add(client)
            created_clients.append(client)
            risk_color = {"low": ANSI_GREEN, "medium": ANSI_YELLOW, "high": "\033[33m", "critical": ANSI_RED}[c["risk_level"]]
            print(f"  {risk_color}●{ANSI_RESET}  {c['name']:<30} risk={risk_color}{c['risk_level']:<8}{ANSI_RESET} score={c['risk_score']:.0f}")
        db.commit()

        banner("Step 4 — Seed invoices")
        created_invoices: list[Invoice] = []
        for inv in INVOICES:
            client = created_clients[inv["client_idx"]]
            due = days_ago(-inv["due_offset"])  # due_offset negative = overdue
            invoice = Invoice(
                id=str(uuid.uuid4()),
                client_id=client.id,
                workspace_id=DEMO_WORKSPACE_ID,
                invoice_number=inv["invoice_number"],
                amount=inv["amount"],
                currency=inv["currency"],
                due_date=due,
                status=inv["status"],
                days_past_due=inv["days_past_due"],
                escalation_stage=inv.get("escalation_stage"),
                line_items=inv.get("line_items", []),
                created_at=due - timedelta(days=30),
                updated_at=NOW,
            )
            db.add(invoice)
            created_invoices.append(invoice)
            status_color = {
                "paid": ANSI_GREEN,
                "overdue": ANSI_RED,
                "disputed": "\033[35m",
                "pending": ANSI_YELLOW,
            }.get(inv["status"], ANSI_RESET)
            stage_label = inv.get("escalation_stage") or "—"
            print(
                f"  {status_color}●{ANSI_RESET}  {inv['invoice_number']:<20}"
                f"{inv['amount']:>10,.0f} {inv['currency']:<4}"
                f"  {status_color}{inv['status']:<12}{ANSI_RESET}"
                f"  stage={stage_label}"
            )
        db.commit()

        banner("Step 5 — Seed escalation events")
        for ev in ESCALATION_EVENTS:
            invoice = created_invoices[ev["invoice_idx"]]
            client = created_clients[ev["client_idx"]]
            event = EscalationEvent(
                id=str(uuid.uuid4()),
                invoice_id=invoice.id,
                workspace_id=DEMO_WORKSPACE_ID,
                client_id=client.id,
                stage=ev["stage"],
                email_subject=ev["email_subject"],
                email_body=ev["email_body"],
                generated_by_ai=ev["generated_by_ai"],
                ai_confidence_score=ev["ai_confidence_score"],
                sent_at=ev.get("sent_at"),
                opened_at=ev.get("opened_at"),
                replied_at=ev.get("replied_at"),
                outcome=ev.get("outcome"),
                created_at=ev.get("sent_at") or NOW,
            )
            db.add(event)
            ok(f"{invoice.invoice_number:<20}  stage={ev['stage']:<18}  confidence={ev['ai_confidence_score']:.0%}")
        db.commit()

        banner("Seed complete — summary")
        total_outstanding = sum(
            inv["amount"] for inv in INVOICES if not inv["paid"]
        )
        overdue_count = sum(1 for inv in INVOICES if inv["status"] == "overdue")
        disputed_count = sum(1 for inv in INVOICES if inv["status"] == "disputed")
        escalation_count = sum(1 for inv in INVOICES if inv.get("escalation_stage"))

        print(f"  Workspace ID  : {ANSI_CYAN}{DEMO_WORKSPACE_ID}{ANSI_RESET}")
        print(f"  Clients       : {ANSI_BOLD}{len(CLIENTS)}{ANSI_RESET}  (2 low · 2 medium · 2 high · 2 critical)")
        print(f"  Invoices      : {ANSI_BOLD}{len(INVOICES)}{ANSI_RESET}")
        print(f"  Overdue       : {ANSI_RED}{overdue_count}{ANSI_RESET}")
        print(f"  Disputed      : {ANSI_RED}{disputed_count}{ANSI_RESET}")
        print(f"  In escalation : {ANSI_YELLOW}{escalation_count}{ANSI_RESET}")
        print(f"  Outstanding   : {ANSI_BOLD}${total_outstanding:,.0f}{ANSI_RESET}")
        print(f"  Events seeded : {ANSI_BOLD}{len(ESCALATION_EVENTS)}{ANSI_RESET}")
        print()
        print(f"  {ANSI_GREEN}✓  Dev DB ready at apps/api/dev.db{ANSI_RESET}")
        print(f"  {ANSI_CYAN}→  Start the API: cd apps/api && uvicorn app.main:app --reload{ANSI_RESET}")
        print(f"  {ANSI_CYAN}→  Start the web: cd apps/web && npx next dev{ANSI_RESET}")
        print()

    finally:
        db.close()


if __name__ == "__main__":
    seed()
