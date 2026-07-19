import json

import httpx
import respx
from click.testing import CliRunner

from freelancer_payment_protection_cli.main import cli

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


@respx.mock
def test_invoice_list_json(logged_in):
    respx.get("https://api.test.invalid/api/v1/invoices").mock(return_value=httpx.Response(200, json=[INVOICE]))

    result = CliRunner().invoke(cli, ["invoice", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["invoiceNumber"] == "INV-2024-022"


@respx.mock
def test_invoice_list_human_readable_table(logged_in):
    respx.get("https://api.test.invalid/api/v1/invoices").mock(return_value=httpx.Response(200, json=[INVOICE]))

    result = CliRunner().invoke(cli, ["invoice", "list"])
    assert result.exit_code == 0
    assert "INV-2024-022" in result.output
    assert "polite_reminder" in result.output


@respx.mock
def test_invoice_list_forwards_status_filter(logged_in):
    route = respx.get("https://api.test.invalid/api/v1/invoices", params={"status": "overdue", "page": "1", "page_size": "20"}).mock(
        return_value=httpx.Response(200, json=[INVOICE])
    )

    result = CliRunner().invoke(cli, ["invoice", "list", "--status", "overdue"])
    assert result.exit_code == 0
    assert route.called


@respx.mock
def test_invoice_show(logged_in):
    respx.get("https://api.test.invalid/api/v1/invoices/inv-1").mock(return_value=httpx.Response(200, json=INVOICE))

    result = CliRunner().invoke(cli, ["invoice", "show", "inv-1", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["id"] == "inv-1"


@respx.mock
def test_invoice_show_not_found(logged_in):
    respx.get("https://api.test.invalid/api/v1/invoices/missing").mock(
        return_value=httpx.Response(404, json={"detail": "Invoice not found"})
    )

    result = CliRunner().invoke(cli, ["invoice", "show", "missing", "--json"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["error"] == "Invoice not found"
    assert data["status_code"] == 404


@respx.mock
def test_invoice_create_sends_camel_case_body(logged_in):
    created = dict(INVOICE, id="inv-2", invoiceNumber="INV-2024-099")
    route = respx.post("https://api.test.invalid/api/v1/invoices").mock(return_value=httpx.Response(201, json=created))

    result = CliRunner().invoke(
        cli,
        [
            "invoice",
            "create",
            "--client-id",
            "client-1",
            "--invoice-number",
            "INV-2024-099",
            "--amount",
            "1500.00",
            "--due-date",
            "2026-08-01T00:00:00Z",
            "--json",
        ],
    )
    assert result.exit_code == 0
    sent_body = json.loads(route.calls.last.request.content)
    assert sent_body["clientId"] == "client-1"
    assert sent_body["invoiceNumber"] == "INV-2024-099"
    assert sent_body["amount"] == 1500.00


@respx.mock
def test_invoice_set_status(logged_in):
    updated = dict(INVOICE, status="paid", escalationStage=None)
    route = respx.patch("https://api.test.invalid/api/v1/invoices/inv-1/status").mock(
        return_value=httpx.Response(200, json=updated)
    )

    result = CliRunner().invoke(cli, ["invoice", "set-status", "inv-1", "paid", "--json"])
    assert result.exit_code == 0
    sent_body = json.loads(route.calls.last.request.content)
    assert sent_body == {"status": "paid"}
    data = json.loads(result.output)
    assert data["status"] == "paid"


def test_invoice_list_requires_login():
    result = CliRunner().invoke(cli, ["invoice", "list", "--json"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert "Not logged in" in data["error"]
