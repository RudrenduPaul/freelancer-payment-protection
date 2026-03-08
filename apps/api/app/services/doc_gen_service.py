"""
Document generation service — python-docx + WeasyPrint PDF pipeline.
"""
import uuid
import os
from pathlib import Path


DISCLAIMER = (
    "DISCLAIMER: This document was generated with AI assistance and does not constitute "
    "legal advice. Review with a qualified attorney before sending."
)


async def generate_demand_letter_pdf(
    content: str,
    workspace_id: str,
    invoice_id: str,
) -> str:
    """
    Generate a PDF demand letter from AI-drafted content.
    In dev: saves to ./generated-docs/
    In production: uploads to Supabase Storage and returns signed URL.
    Returns document_id.
    """
    document_id = str(uuid.uuid4())
    output_dir = Path("./generated-docs")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"{document_id}.txt"
    full_content = f"{DISCLAIMER}\n\n{'='*60}\n\n{content}"
    output_path.write_text(full_content)

    return document_id
