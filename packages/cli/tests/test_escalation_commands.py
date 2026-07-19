import json

import httpx
import respx
from click.testing import CliRunner

from freelancer_payment_protection_cli.main import cli

GROUPED = {
    "polite_reminder": [
        {
            "invoiceId": "inv-1",
            "invoiceNumber": "INV-2024-022",
            "amount": 8500.0,
            "currency": "USD",
            "daysPastDue": 18,
            "clientId": "client-1",
            "clientName": "Marcus Webb",
            "clientCompany": "ScaleHQ Inc.",
            "nextEscalationDate": "2026-06-08T00:00:00",
        }
    ],
    "firm_notice": [],
    "final_warning": [],
    "legal_demand": [],
    "legal_action": [],
}

INVOICE = {
    "id": "inv-1",
    "clientId": "client-1",
    "workspaceId": "ws-test-001",
    "invoiceNumber": "INV-2024-022",
    "amount": 8500.0,
    "currency": "USD",
    "dueDate": "2026-06-01T00:00:00",
    "status": "overdue",
    "daysPastDue": 18,
    "escalationStage": "polite_reminder",
    "sourceSystem": "manual",
    "externalId": None,
    "lineItems": [],
    "lastEscalatedAt": None,
    "nextEscalationDate": "2026-06-08T00:00:00",
    "evidenceCount": 0,
    "createdAt": "2026-05-01T00:00:00",
    "updatedAt": "2026-06-01T00:00:00",
}

HISTORY = [
    {
        "id": "evt-1",
        "stage": "polite_reminder",
        "emailSubject": "Friendly reminder",
        "emailBody": "Hi Marcus...",
        "generatedByAI": True,
        "aiConfidenceScore": 0.91,
        "sentAt": "2026-05-20T00:00:00",
        "openedAt": "2026-05-21T00:00:00",
        "outcome": None,
        "createdAt": "2026-05-20T00:00:00",
    }
]


@respx.mock
def test_escalation_list(logged_in):
    respx.get("https://api.test.invalid/api/v1/escalations").mock(return_value=httpx.Response(200, json=GROUPED))

    result = CliRunner().invoke(cli, ["escalation", "list"])
    assert result.exit_code == 0
    assert "polite_reminder" in result.output
    assert "Marcus Webb" in result.output


@respx.mock
def test_escalation_status_combines_invoice_and_history(logged_in):
    respx.get("https://api.test.invalid/api/v1/invoices/inv-1").mock(return_value=httpx.Response(200, json=INVOICE))
    respx.get("https://api.test.invalid/api/v1/escalations/inv-1/history").mock(
        return_value=httpx.Response(200, json=HISTORY)
    )

    result = CliRunner().invoke(cli, ["escalation", "status", "inv-1", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["invoice"]["escalationStage"] == "polite_reminder"
    assert len(data["history"]) == 1


@respx.mock
def test_escalation_advance_drafts_next_stage(logged_in):
    draft = {
        "stage": "firm_notice",
        "stage_label": "Firm Notice",
        "subject": "Second notice",
        "body": "This is my second notice...",
        "tone": "firm_notice",
        "confidence_score": 85,
        "key_phrases": [],
    }
    respx.post("https://api.test.invalid/api/v1/escalations/inv-1/draft").mock(
        return_value=httpx.Response(200, json=draft)
    )

    result = CliRunner().invoke(cli, ["escalation", "advance", "inv-1"])
    assert result.exit_code == 0
    assert "firm_notice" in result.output
    assert "Preview only" in result.output


@respx.mock
def test_escalation_advance_reports_final_stage_error(logged_in):
    draft = {
        "error": "This invoice is already at the final escalation stage (legal_action).",
        "message": "No further escalation is possible. Consider direct legal action.",
    }
    respx.post("https://api.test.invalid/api/v1/escalations/inv-1/draft").mock(
        return_value=httpx.Response(200, json=draft)
    )

    result = CliRunner().invoke(cli, ["escalation", "advance", "inv-1"])
    assert result.exit_code == 0
    assert "already at the final escalation stage" in result.output
