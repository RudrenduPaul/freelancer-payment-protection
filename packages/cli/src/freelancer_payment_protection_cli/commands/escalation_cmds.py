"""
escalation list / status / advance

Wraps apps/api/app/routers/escalations.py, which exposes exactly three
routes: GET "" (all active escalations grouped by stage), POST
"/{invoice_id}/draft" (AI-drafts the next stage's email), and GET
"/{invoice_id}/history" (past escalation events for one invoice). There is
no endpoint in this API that persists a stage change — draft_escalation_email
in apps/api/app/services/escalation_service.py only computes and returns
what the next stage's email would say; it never writes escalation_stage
back to the database. `advance` below reflects that honestly: it drafts
the next-stage email and says so, it does not claim to move the invoice
to that stage.

`status` is not a single endpoint either — the closest real equivalent is
the invoice's own escalationStage/daysPastDue/nextEscalationDate fields
(GET /api/v1/invoices/{id}) plus its escalation history
(GET /api/v1/escalations/{id}/history), so this command calls both.

Stage order (apps/api/app/services/escalation_service.py STAGE_ORDER):
  polite_reminder -> firm_notice -> final_warning -> legal_demand -> legal_action
This product's documented policy calls for 7d -> 7d -> 5d -> 7d minimum
waits between stages, but the /draft endpoint itself does not enforce
those waits — it only checks stage order (get_next_stage), so a draft can
be requested at any time regardless of how recently the previous stage
was sent.
"""
from __future__ import annotations

import click

from ..api import ApiClient
from ..output import emit, error_boundary, kv_table, simple_table

STAGE_ORDER = ["polite_reminder", "firm_notice", "final_warning", "legal_demand", "legal_action"]


@click.group()
def escalation() -> None:
    """Manage invoice escalations."""


@escalation.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def list_escalations(as_json: bool) -> None:
    """List every active escalation, grouped by stage. GET /api/v1/escalations"""
    with error_boundary(as_json):
        with ApiClient() as api:
            grouped = api.get("/api/v1/escalations")

    rows = []
    for stage in STAGE_ORDER:
        for item in grouped.get(stage, []):
            rows.append(
                [
                    stage,
                    item["invoiceNumber"],
                    f"{item['amount']:.2f} {item['currency']}",
                    item["daysPastDue"],
                    item["clientName"],
                    item["invoiceId"],
                ]
            )
    human = simple_table(["STAGE", "INVOICE #", "AMOUNT", "DAYS PAST DUE", "CLIENT", "INVOICE ID"], rows)
    emit(grouped, as_json, human=human)


@escalation.command("status")
@click.argument("invoice_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def escalation_status(invoice_id: str, as_json: bool) -> None:
    """
    Show an invoice's current escalation stage and its history.
    Combines GET /api/v1/invoices/{invoice_id} with
    GET /api/v1/escalations/{invoice_id}/history.
    """
    with error_boundary(as_json):
        with ApiClient() as api:
            inv = api.get(f"/api/v1/invoices/{invoice_id}")
            history = api.get(f"/api/v1/escalations/{invoice_id}/history")

    combined = {"invoice": inv, "history": history}

    lines = [
        kv_table(
            [
                ("Invoice #", inv["invoiceNumber"]),
                ("Status", inv["status"]),
                ("Current stage", inv.get("escalationStage") or "(none)"),
                ("Days past due", inv["daysPastDue"]),
                ("Next escalation date", inv.get("nextEscalationDate") or "-"),
                ("Last escalated at", inv.get("lastEscalatedAt") or "-"),
            ]
        )
    ]
    if history:
        rows = [
            [h["stage"], h.get("sentAt") or "-", f"{h.get('aiConfidenceScore', 0):.0%}" if h.get("aiConfidenceScore") is not None else "-", h.get("outcome") or "-"]
            for h in history
        ]
        lines.append("\nHistory:")
        lines.append(simple_table(["STAGE", "SENT AT", "AI CONFIDENCE", "OUTCOME"], rows))
    else:
        lines.append("\nNo escalation history yet.")

    emit(combined, as_json, human="\n".join(lines))


@escalation.command("advance")
@click.argument("invoice_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def escalation_advance(invoice_id: str, as_json: bool) -> None:
    """
    AI-draft the next escalation stage's email for an invoice.
    POST /api/v1/escalations/{invoice_id}/draft

    This previews what the next stage's email would say. It does not
    change the invoice's stored escalation stage: the backend has no
    endpoint that persists that change today, only this preview endpoint.
    Send/record the actual escalation through the product's own workflow.
    """
    with error_boundary(as_json):
        with ApiClient() as api:
            draft = api.post(f"/api/v1/escalations/{invoice_id}/draft")

    if "error" in draft:
        emit(draft, as_json, human=f"{draft['error']}\n{draft.get('message', '')}")
        return

    human = kv_table(
        [
            ("Next stage", f"{draft.get('stage')} ({draft.get('stage_label', '')})"),
            ("Subject", draft.get("subject")),
            ("Confidence", draft.get("confidence_score")),
        ]
    )
    human += f"\n\n{draft.get('body', '')}"
    human += (
        "\n\n(Preview only — no stage change was persisted. This API does not "
        "expose an endpoint that writes the stage back to the invoice.)"
    )
    emit(draft, as_json, human=human)
