from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional
from apps.api.app.middleware.auth import get_current_workspace
from apps.api.app.middleware.rate_limit import limiter
from sqlalchemy.orm import Session
from apps.api.app.database import get_db

router = APIRouter()

DISCLAIMER = (
    "DISCLAIMER: This document was generated with AI assistance and does not constitute "
    "legal advice. Review with a qualified attorney before sending."
)


class DemandLetterRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    invoice_id: str
    jurisdiction: str
    client_name: str
    client_company: Optional[str] = None
    amount: float
    currency: str = "USD"
    days_past_due: int
    evidence_summary: Optional[str] = None
    previous_contact_dates: list[str] = []


@router.post("/demand-letter")
@limiter.limit("10/minute")
async def create_demand_letter(
    request: Request,
    body: DemandLetterRequest,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """
    Generate a jurisdiction-aware legal demand letter using Claude.
    Drafts content via AI then stores the document.
    All generated documents include the mandatory AI disclaimer.
    """
    from apps.api.app.services.ai_service import call_claude
    from apps.api.app.services.doc_gen_service import generate_demand_letter_pdf
    from packages.legal_ai.prompts.demand_letter import DEMAND_LETTER_SYSTEM, build_demand_letter_prompt

    prompt = build_demand_letter_prompt(
        client_name=body.client_name,
        client_company=body.client_company or "",
        invoice_number=body.invoice_id,
        amount=body.amount,
        currency=body.currency,
        due_date="[from invoice record]",
        days_past_due=body.days_past_due,
        freelancer_name="[from workspace profile]",
        jurisdiction=body.jurisdiction,
        evidence_summary=body.evidence_summary or "",
        previous_contact_dates=body.previous_contact_dates,
    )

    try:
        content = await call_claude(
            prompt=prompt,
            system_prompt=DEMAND_LETTER_SYSTEM,
            max_tokens=2048,
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="AI service temporarily unavailable. Please try again in a moment.",
        )

    document_id = await generate_demand_letter_pdf(
        content=content,
        workspace_id=workspace_id,
        invoice_id=body.invoice_id,
    )

    return {
        "documentId": document_id,
        "status": "ready",
        "downloadUrl": f"/api/v1/legal/{document_id}/download",
        "disclaimer": DISCLAIMER,
    }


@router.post("/demand-letter/stream")
@limiter.limit("10/minute")
async def stream_demand_letter(
    request: Request,
    body: DemandLetterRequest,
    workspace_id: str = Depends(get_current_workspace),
):
    """
    Stream legal demand letter generation with Server-Sent Events.
    Powers the typewriter effect in the UI.
    """
    from apps.api.app.services.ai_service import stream_demand_letter_content

    async def generate():
        # Always prepend the disclaimer
        yield f"{DISCLAIMER}\n\n{'='*60}\n\n"
        async for chunk in stream_demand_letter_content(
            client_name=body.client_name,
            client_company=body.client_company or "",
            invoice_id=body.invoice_id,
            amount=body.amount,
            currency=body.currency,
            days_past_due=body.days_past_due,
            jurisdiction=body.jurisdiction,
            evidence_summary=body.evidence_summary or "",
            previous_contact_dates=body.previous_contact_dates,
        ):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
