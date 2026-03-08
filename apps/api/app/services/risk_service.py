"""
Risk scoring service — AI-powered client payment risk assessment.
"""
from typing import Any


async def compute_client_risk_score(client: Any) -> dict:
    """
    Compute AI risk score for a client.
    Returns {score, level, factors, reasoning}.
    Score is 0-100 where 100 = certain non-payment.
    """
    from apps.api.app.services.ai_service import call_claude
    from packages.legal_ai.prompts.risk_scoring import RISK_SCORING_SYSTEM, build_risk_scoring_prompt
    import json

    prompt = build_risk_scoring_prompt(
        client_name=client.name,
        industry=client.industry or "Unknown",
        country=client.country or "US",
        payment_terms_days=client.payment_terms_days,
        average_payment_delay=client.average_payment_delay,
        total_invoiced=client.total_invoiced,
        total_outstanding=client.total_outstanding,
        has_contract=bool(client.contract_url),
        notes=client.notes or "",
    )

    response_text = await call_claude(
        prompt=prompt,
        system_prompt=RISK_SCORING_SYSTEM,
        max_tokens=1024,
    )

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        # Fallback if Claude returns non-JSON
        result = {
            "score": 50,
            "level": "medium",
            "factors": [],
            "reasoning": response_text,
        }

    return result
