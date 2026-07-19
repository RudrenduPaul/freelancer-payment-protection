import json

import httpx
import respx
from click.testing import CliRunner

from freelancer_payment_protection_cli.main import cli

CLIENT = {
    "id": "client-1",
    "workspaceId": "ws-test-001",
    "name": "Marcus Webb",
    "email": "marcus@scalehq.com",
    "company": "ScaleHQ Inc.",
    "industry": "SaaS",
    "country": "US",
    "riskScore": 38.0,
    "riskLevel": "medium",
    "totalInvoiced": 52000.0,
    "totalOutstanding": 8500.0,
    "paymentTermsDays": 30,
    "averagePaymentDelay": 12.0,
    "contractUrl": None,
    "notes": "Growing startup.",
    "createdAt": "2026-01-01T00:00:00",
    "updatedAt": "2026-06-01T00:00:00",
}


@respx.mock
def test_client_list(logged_in):
    respx.get("https://api.test.invalid/api/v1/clients").mock(return_value=httpx.Response(200, json=[CLIENT]))

    result = CliRunner().invoke(cli, ["client", "list"])
    assert result.exit_code == 0
    assert "Marcus Webb" in result.output
    assert "medium" in result.output


@respx.mock
def test_client_list_forwards_risk_level_filter(logged_in):
    route = respx.get(
        "https://api.test.invalid/api/v1/clients", params={"risk_level": "critical", "page": "1", "page_size": "20"}
    ).mock(return_value=httpx.Response(200, json=[]))

    result = CliRunner().invoke(cli, ["client", "list", "--risk-level", "critical", "--json"])
    assert result.exit_code == 0
    assert route.called


@respx.mock
def test_client_show(logged_in):
    respx.get("https://api.test.invalid/api/v1/clients/client-1").mock(return_value=httpx.Response(200, json=CLIENT))

    result = CliRunner().invoke(cli, ["client", "show", "client-1", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["riskLevel"] == "medium"


@respx.mock
def test_client_risk_sends_snake_case_client_id(logged_in):
    risk_result = {
        "score": 38,
        "level": "medium",
        "factors": [{"name": "Payment delay", "impact": "negative", "description": "Averages 12 days late", "weight": 25}],
        "reasoning": "Moderate risk based on payment history.",
    }
    route = respx.post("https://api.test.invalid/api/v1/risk/score").mock(return_value=httpx.Response(200, json=risk_result))

    result = CliRunner().invoke(cli, ["client", "risk", "client-1"])
    assert result.exit_code == 0
    sent_body = json.loads(route.calls.last.request.content)
    assert sent_body == {"client_id": "client-1"}
    assert "medium" in result.output
    assert "Payment delay" in result.output


@respx.mock
def test_client_risk_handles_rate_limit(logged_in):
    respx.post("https://api.test.invalid/api/v1/risk/score").mock(
        return_value=httpx.Response(429, json={"detail": "Rate limit exceeded: 30 per 1 minute"})
    )

    result = CliRunner().invoke(cli, ["client", "risk", "client-1", "--json"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["status_code"] == 429
