from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from apps.api.app.database import get_db
from apps.api.app.middleware.auth import get_current_workspace

router = APIRouter()

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "message/rfc822",
    "text/plain",
}

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25MB


@router.get("/{invoice_id}")
async def list_evidence(
    invoice_id: str,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    from apps.api.app.models.evidence import EvidenceItem

    items = db.query(EvidenceItem).filter(
        EvidenceItem.invoice_id == invoice_id,
        EvidenceItem.workspace_id == workspace_id,
    ).order_by(EvidenceItem.captured_at.asc()).all()

    return [
        {
            "id": str(item.id),
            "invoiceId": str(item.invoice_id),
            "type": item.type,
            "source": item.source,
            "filename": item.filename,
            "fileHash": item.file_hash,
            "fileSizeBytes": item.file_size_bytes,
            "capturedAt": item.captured_at.isoformat(),
        }
        for item in items
    ]


@router.post("/{invoice_id}/upload")
async def upload_evidence(
    invoice_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    # Validate MIME type before reading content
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not allowed. Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}",
        )

    # Validate file size without reading everything into memory at once
    content = b""
    async for chunk in file:
        content += chunk
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="File exceeds 25MB size limit")

    import hashlib
    import uuid
    from datetime import datetime
    from apps.api.app.models.evidence import EvidenceItem

    file_hash = hashlib.sha256(content).hexdigest()
    storage_url = f"/dev-storage/{uuid.uuid4()}/{file.filename}"

    item = EvidenceItem(
        invoice_id=invoice_id,
        workspace_id=workspace_id,
        type="document",
        source="manual_upload",
        filename=file.filename or "unnamed",
        storage_url=storage_url,
        file_hash=file_hash,
        file_size_bytes=str(len(content)),
        captured_at=datetime.utcnow(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "id": str(item.id),
        "invoiceId": str(item.invoice_id),
        "filename": item.filename,
        "fileHash": item.file_hash,
        "fileSizeBytes": item.file_size_bytes,
        "capturedAt": item.captured_at.isoformat(),
        "message": "Evidence captured and stored. Your case file just got stronger.",
    }


@router.delete("/{item_id}", status_code=204)
async def delete_evidence(
    item_id: str,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    from apps.api.app.models.evidence import EvidenceItem

    item = db.query(EvidenceItem).filter(
        EvidenceItem.id == item_id,
        EvidenceItem.workspace_id == workspace_id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Evidence item not found")
    db.delete(item)
    db.commit()
