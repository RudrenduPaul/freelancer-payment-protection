"""
AI service — all Claude API calls route through here.
Never call the Anthropic SDK directly from routers or workers.
Streaming support for real-time typewriter effect in the UI.
"""
import logging
from typing import AsyncGenerator
from apps.api.app.config import settings

logger = logging.getLogger(__name__)


async def call_claude(
    prompt: str,
    system_prompt: str,
    max_tokens: int = 2048,
) -> str:
    """
    Central wrapper for all Claude API calls.
    All AI features route through this function.
    """
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key.get_secret_value())
    logger.info("Claude API call initiated", extra={"prompt_length": len(prompt)})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text if response.content and response.content[0].type == "text" else ""


async def stream_demand_letter_content(
    client_name: str,
    client_company: str,
    invoice_id: str,
    amount: float,
    currency: str,
    days_past_due: int,
    jurisdiction: str,
    evidence_summary: str,
    previous_contact_dates: list[str],
) -> AsyncGenerator[str, None]:
    """
    Stream demand letter generation from Claude.
    Powers the typewriter effect in DemandLetterPreview component.
    """
    import anthropic
    from packages.legal_ai.prompts.demand_letter import (
        DEMAND_LETTER_SYSTEM,
        build_demand_letter_prompt,
    )

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key.get_secret_value())

    prompt = build_demand_letter_prompt(
        client_name=client_name,
        client_company=client_company,
        invoice_number=invoice_id,
        amount=amount,
        currency=currency,
        due_date="[from invoice record]",
        days_past_due=days_past_due,
        freelancer_name="[from workspace profile]",
        jurisdiction=jurisdiction,
        evidence_summary=evidence_summary,
        previous_contact_dates=previous_contact_dates,
    )

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=DEMAND_LETTER_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text
