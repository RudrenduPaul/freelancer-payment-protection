"""
Risk scoring service — AI-powered client payment risk assessment.
Score: 0-100 where 100 = certain non-payment.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Fallback risk scoring when AI is unavailable
def _compute_heuristic_risk(client: Any) -> dict:
    """Simple heuristic risk score when AI is unavailable."""
    score = 0.0

    if client.average_payment_delay > 60:
        score += 40
    elif client.average_payment_delay > 30:
        score += 25
    elif client.average_payment_delay > 14:
        score += 10

    if client.payment_terms_days >= 60:
        score += 15
    elif client.payment_terms_days >= 45:
        score += 8

    if not client.contract_url:
        score += 15

    if client.total_invoiced > 0:
        outstanding_pct = client.total_outstanding / client.total_invoiced
        if outstanding_pct > 0.5:
            score += 20
        elif outstanding_pct > 0.25:
            score += 10

    score = min(100.0, score)

    if score <= 25:
        level = "low"
    elif score <= 50:
        level = "medium"
    elif score <= 75:
        level = "high"
    else:
        level = "critical"

    return {
        "score": round(score, 1),
        "level": level,
        "factors": [{"name": "Heuristic assessment", "impact": "neutral", "description": "AI unavailable — basic scoring applied", "weight": 100}],
        "reasoning": "Computed from payment history and contract status. Run AI scoring for full analysis.",
    }


async def compute_client_risk_score(client: Any) -> dict:
    """
    Compute AI risk score for a client.
    Returns {score, level, factors, reasoning}.
    Falls back to heuristic scoring if AI is unavailable.
    """
    import json
    from apps.api.app.services.ai_service import call_claude
    from packages.legal_ai.prompts.risk_scoring import RISK_SCORING_SYSTEM, build_risk_scoring_prompt

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

    try:
        response_text = await call_claude(
            prompt=prompt,
            system_prompt=RISK_SCORING_SYSTEM,
            max_tokens=1024,
        )
        result = json.loads(response_text)

        # Validate required fields
        if "score" not in result or "level" not in result:
            raise ValueError("Missing required fields in AI response")

        return result

    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("AI risk scoring returned invalid JSON, using heuristic: %s", str(e))
        return _compute_heuristic_risk(client)
    except Exception as e:
        logger.error("AI risk scoring failed, using heuristic fallback: %s", str(e))
        return _compute_heuristic_risk(client)
