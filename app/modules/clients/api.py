from fastapi import APIRouter, Depends, HTTPException

from .schemas import ClientCreate, ClientResponse
from .deps import get_client_service
from .service import ClientService

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("/", response_model=ClientResponse)
def create_client(
    data: ClientCreate,
    service: ClientService = Depends(get_client_service)
):
    try:
        return service.create_client(
            name=data.name,
            email=data.email
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    service: ClientService = Depends(get_client_service)
):
    client = service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return client

@router.get("/", response_model=list[ClientResponse])
def list_clients(
    skip: int = 0,
    limit: int = 10,
    service: ClientService = Depends(get_client_service)
):
    return service.list_clients(skip, limit)