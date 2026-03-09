"""
Document generation service — saves AI-drafted content as a document.
Dev: saves to ./generated-docs/
Production: uploads to Supabase Storage (signed URL).
"""
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

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
    Save a demand letter document. Returns document_id.
    In dev: saves to ./generated-docs/ as a text file.
    In production: would use python-docx + WeasyPrint to generate PDF,
    then upload to Supabase Storage.
    """
    document_id = str(uuid.uuid4())
    output_dir = Path("./generated-docs")

    try:
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{document_id}.txt"
        full_content = f"{DISCLAIMER}\n\n{'='*60}\n\n{content}"
        output_path.write_text(full_content, encoding="utf-8")
        logger.info("Demand letter saved: %s", document_id)
    except OSError as e:
        logger.error("Failed to save demand letter %s: %s", document_id, str(e))
        raise RuntimeError(f"Document generation failed: {e}") from e

    return document_id
