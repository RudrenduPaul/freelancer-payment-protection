"""
client list / show / risk

Wraps apps/api/app/routers/clients.py and risk_scoring.py. ClientResponse
fields (camelCase over the wire, same alias-generator pattern as
InvoiceResponse): id, workspaceId, name, email, company, industry,
country, riskScore, riskLevel, totalInvoiced, totalOutstanding,
paymentTermsDays, averagePaymentDelay, contractUrl, notes, createdAt,
updatedAt.

risk_scoring.py's RiskScoreRequest is a plain (non-aliased) BaseModel with
a single `client_id` field — unlike the other schemas in this repo, it
does NOT accept a camelCase `clientId` key, so the CLI sends snake_case
here specifically.
"""
from __future__ import annotations

import click

from ..api import ApiClient
from ..output import emit, error_boundary, kv_table, simple_table

RISK_LEVELS = {"low", "medium", "high", "critical"}


@click.group()
def client() -> None:
    """Manage clients and client risk scoring."""


@client.command("list")
@click.option("--risk-level", type=click.Choice(sorted(RISK_LEVELS)), help="Filter by risk level.")
@click.option("--search", help="Search by name or company.")
@click.option("--page", default=1, show_default=True, type=int)
@click.option("--page-size", default=20, show_default=True, type=int, help="Max 100 (server-enforced).")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def list_clients(risk_level: str | None, search: str | None, page: int, page_size: int, as_json: bool) -> None:
    """List clients for the current workspace. GET /api/v1/clients"""
    params = {"page": page, "page_size": page_size}
    if risk_level:
        params["risk_level"] = risk_level
    if search:
        params["search"] = search

    with error_boundary(as_json):
        with ApiClient() as api:
            clients = api.get("/api/v1/clients", params=params)

    rows = [
        [c["name"], c.get("company") or "-", c["riskLevel"], f"{c['riskScore']:.0f}", f"{c['totalOutstanding']:.2f}", c["id"]]
        for c in clients
    ]
    human = simple_table(["NAME", "COMPANY", "RISK LEVEL", "RISK SCORE", "OUTSTANDING", "ID"], rows)
    emit(clients, as_json, human=human)


@client.command("show")
@click.argument("client_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def show_client(client_id: str, as_json: bool) -> None:
    """Show a single client. GET /api/v1/clients/{client_id}"""
    with error_boundary(as_json):
        with ApiClient() as api:
            c = api.get(f"/api/v1/clients/{client_id}")

    human = kv_table(
        [
            ("Name", c["name"]),
            ("Company", c.get("company") or "-"),
            ("Email", c["email"]),
            ("Risk level", c["riskLevel"]),
            ("Risk score", c["riskScore"]),
            ("Total invoiced", c["totalInvoiced"]),
            ("Total outstanding", c["totalOutstanding"]),
            ("Payment terms (days)", c["paymentTermsDays"]),
            ("Average payment delay (days)", c["averagePaymentDelay"]),
            ("Client ID", c["id"]),
        ]
    )
    emit(c, as_json, human=human)


@client.command("risk")
@click.argument("client_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def client_risk(client_id: str, as_json: bool) -> None:
    """
    Compute (or re-compute) a client's AI risk score.
    POST /api/v1/risk/score  body: {"client_id": ...}

    Score is 0-100. Thresholds (apps/api/app/services/risk_service.py's
    _compute_heuristic_risk): 0-25 low, 26-50 medium, 51-75 high, 76-100 critical.
    Rate-limited server-side to 30 requests/minute per the @limiter.limit
    decorator on this route.
    """
    with error_boundary(as_json):
        with ApiClient() as api:
            result = api.post("/api/v1/risk/score", json_body={"client_id": client_id})

    factors = result.get("factors") or []
    factor_lines = "\n".join(f"  - {f.get('name', '?')}: {f.get('description', '')}" for f in factors)
    human = kv_table(
        [
            ("Score", result.get("score")),
            ("Level", result.get("level")),
            ("Reasoning", result.get("reasoning") or "-"),
        ]
    )
    if factor_lines:
        human += f"\nFactors:\n{factor_lines}"
    emit(result, as_json, human=human)
