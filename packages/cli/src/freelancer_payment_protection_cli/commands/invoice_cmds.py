"""
invoice list / create / show / set-status

Wraps apps/api/app/routers/invoices.py. Every field name below matches
apps.api.app.schemas.invoice.{InvoiceCreate,InvoiceStatusUpdate,InvoiceResponse}
exactly. Those schemas use a camelCase alias generator with
populate_by_name=True and FastAPI's default response_model_by_alias=True,
so requests accept either casing but responses are camelCase over the wire
(clientId, invoiceNumber, dueDate, daysPastDue, escalationStage,
sourceSystem, externalId, lineItems, lastEscalatedAt, nextEscalationDate,
evidenceCount, createdAt, updatedAt).
"""
from __future__ import annotations

import click

from ..api import ApiClient
from ..output import emit, error_boundary, simple_table

VALID_STATUSES = {"paid", "pending", "overdue", "disputed", "written_off"}


@click.group()
def invoice() -> None:
    """Manage invoices (apps/api/app/routers/invoices.py)."""


@invoice.command("list")
@click.option("--status", "status_filter", type=click.Choice(sorted(VALID_STATUSES)), help="Filter by invoice status.")
@click.option("--client-id", help="Filter by client ID.")
@click.option("--page", default=1, show_default=True, type=int)
@click.option("--page-size", default=20, show_default=True, type=int, help="Max 100 (server-enforced).")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def list_invoices(status_filter: str | None, client_id: str | None, page: int, page_size: int, as_json: bool) -> None:
    """List invoices for the current workspace. GET /api/v1/invoices"""
    params = {"page": page, "page_size": page_size}
    if status_filter:
        params["status"] = status_filter
    if client_id:
        params["client_id"] = client_id

    with error_boundary(as_json):
        with ApiClient() as api:
            invoices = api.get("/api/v1/invoices", params=params)

    rows = [
        [
            inv["invoiceNumber"],
            inv["status"],
            f"{inv['amount']:.2f} {inv['currency']}",
            inv["daysPastDue"],
            inv.get("escalationStage") or "-",
            inv["id"],
        ]
        for inv in invoices
    ]
    human = simple_table(["INVOICE #", "STATUS", "AMOUNT", "DAYS PAST DUE", "STAGE", "ID"], rows)
    emit(invoices, as_json, human=human)


@invoice.command("create")
@click.option("--client-id", required=True)
@click.option("--invoice-number", required=True)
@click.option("--amount", required=True, type=float)
@click.option("--currency", default="USD", show_default=True)
@click.option("--due-date", required=True, help="ISO 8601 datetime, e.g. 2026-08-15T00:00:00Z")
@click.option("--source-system", default=None)
@click.option("--external-id", default=None)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def create_invoice(
    client_id: str,
    invoice_number: str,
    amount: float,
    currency: str,
    due_date: str,
    source_system: str | None,
    external_id: str | None,
    as_json: bool,
) -> None:
    """Create an invoice. POST /api/v1/invoices"""
    body = {
        "clientId": client_id,
        "invoiceNumber": invoice_number,
        "amount": amount,
        "currency": currency,
        "dueDate": due_date,
        "sourceSystem": source_system,
        "externalId": external_id,
        "lineItems": [],
    }

    with error_boundary(as_json):
        with ApiClient() as api:
            created = api.post("/api/v1/invoices", json_body=body)

    human = f"Created invoice {created['invoiceNumber']} ({created['id']}) — {created['amount']:.2f} {created['currency']}"
    emit(created, as_json, human=human)


@invoice.command("show")
@click.argument("invoice_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def show_invoice(invoice_id: str, as_json: bool) -> None:
    """Show a single invoice. GET /api/v1/invoices/{invoice_id}"""
    with error_boundary(as_json):
        with ApiClient() as api:
            inv = api.get(f"/api/v1/invoices/{invoice_id}")

    from ..output import kv_table

    human = kv_table(
        [
            ("Invoice #", inv["invoiceNumber"]),
            ("Status", inv["status"]),
            ("Amount", f"{inv['amount']:.2f} {inv['currency']}"),
            ("Due date", inv["dueDate"]),
            ("Days past due", inv["daysPastDue"]),
            ("Escalation stage", inv.get("escalationStage") or "-"),
            ("Next escalation date", inv.get("nextEscalationDate") or "-"),
            ("Last escalated at", inv.get("lastEscalatedAt") or "-"),
            ("Evidence count", inv["evidenceCount"]),
            ("Client ID", inv["clientId"]),
            ("Invoice ID", inv["id"]),
        ]
    )
    emit(inv, as_json, human=human)


@invoice.command("set-status")
@click.argument("invoice_id")
@click.argument("new_status", type=click.Choice(sorted(VALID_STATUSES)))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def set_invoice_status(invoice_id: str, new_status: str, as_json: bool) -> None:
    """
    Update an invoice's status. PATCH /api/v1/invoices/{invoice_id}/status

    Setting status to "paid" also clears escalationStage and
    nextEscalationDate server-side (see invoices.py update_invoice_status).
    """
    with error_boundary(as_json):
        with ApiClient() as api:
            updated = api.patch(f"/api/v1/invoices/{invoice_id}/status", json_body={"status": new_status})

    human = f"Invoice {updated['invoiceNumber']} status set to {updated['status']}."
    emit(updated, as_json, human=human)
