from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from apps.api.app.database import get_db
from apps.api.app.middleware.auth import get_current_workspace
from apps.api.app.middleware.rate_limit import limiter
from apps.api.app.schemas.client import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter()


@router.get("", response_model=list[ClientResponse])
async def list_clients(
    risk_level: Optional[str] = Query(None, description="Filter by risk level: low|medium|high|critical"),
    search: Optional[str] = Query(None, description="Search by name or company"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """List clients for the current workspace, with optional filtering."""
    from apps.api.app.models.client import Client

    query = db.query(Client).filter(
        Client.workspace_id == workspace_id,
        Client.deleted_at.is_(None),
    )

    if risk_level:
        query = query.filter(Client.risk_level == risk_level)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Client.name.ilike(search_term)) | (Client.company.ilike(search_term))
        )

    clients = query.offset((page - 1) * page_size).limit(page_size).all()
    return clients


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """Create a new client."""
    from apps.api.app.models.client import Client
    from datetime import datetime

    client = Client(
        workspace_id=workspace_id,
        name=data.name,
        email=data.email,
        company=data.company,
        industry=data.industry,
        country=data.country,
        payment_terms_days=data.payment_terms_days or 30,
        contract_url=data.contract_url,
        notes=data.notes or "",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """Get a single client by ID."""
    from apps.api.app.models.client import Client

    client = db.query(Client).filter(
        Client.id == client_id,
        Client.workspace_id == workspace_id,
        Client.deleted_at.is_(None),
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    data: ClientUpdate,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """Update a client."""
    from apps.api.app.models.client import Client
    from datetime import datetime

    client = db.query(Client).filter(
        Client.id == client_id,
        Client.workspace_id == workspace_id,
        Client.deleted_at.is_(None),
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    client.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    db: Session = Depends(get_db),
    workspace_id: str = Depends(get_current_workspace),
):
    """Soft-delete a client."""
    from apps.api.app.models.client import Client
    from datetime import datetime

    client = db.query(Client).filter(
        Client.id == client_id,
        Client.workspace_id == workspace_id,
        Client.deleted_at.is_(None),
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client.deleted_at = datetime.utcnow()
    db.commit()
