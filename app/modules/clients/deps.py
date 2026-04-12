from fastapi import Depends
from sqlalchemy.orm import Session

from app.shared.deps import get_db
from .service import ClientService

def get_client_service(db: Session = Depends(get_db)):
    return ClientService(db)