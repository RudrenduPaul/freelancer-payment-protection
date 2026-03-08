"""
Escalation service — determines next stage and drafts escalation emails via Claude.
"""
from typing import Any


STAGE_ORDER = [
    "polite_reminder",
    "firm_notice",
    "final_warning",
    "legal_demand",
    "legal_action",
]


def get_next_stage(current_stage: str | None) -> str | None:
    """Returns the next escalation stage, or None if already at legal_action."""
    if current_stage is None:
        return "polite_reminder"
    try:
        current_index = STAGE_ORDER.index(current_stage)
        if current_index < len(STAGE_ORDER) - 1:
            return STAGE_ORDER[current_index + 1]
        return None
    except ValueError:
        return "polite_reminder"


async def draft_escalation_email(invoice: Any, client: Any) -> dict:
    """
    AI-draft the next escalation email for an invoice.
    Returns structured {subject, body, tone, confidence_score, key_phrases}.
    """
    from apps.api.app.services.ai_service import call_claude
    from packages.legal_ai.prompts.escalation_sequence import (
        ESCALATION_SYSTEM,
        build_escalation_prompt,
    )
    import json

    next_stage = get_next_stage(invoice.escalation_stage)
    if not next_stage:
        return {"error": "Invoice is already at the final escalation stage"}

    previous_attempts = 0  # Count from escalation_events in production

    prompt = build_escalation_prompt(
        stage=next_stage,
        client_name=client.name,
        invoice_number=invoice.invoice_number,
        amount=invoice.amount,
        currency=invoice.currency,
        days_past_due=invoice.days_past_due,
        freelancer_name="[your name]",
        previous_attempts=previous_attempts,
    )

    response_text = await call_claude(
        prompt=prompt,
        system_prompt=ESCALATION_SYSTEM,
        max_tokens=1024,
    )

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        result = {
            "subject": "Follow up on unpaid invoice",
            "body": response_text,
            "tone": next_stage,
            "confidence_score": 70,
            "key_phrases": [],
        }

    result["stage"] = next_stage
    return result
