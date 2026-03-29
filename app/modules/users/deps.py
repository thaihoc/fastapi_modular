from fastapi import Depends
from sqlalchemy.orm import Session

from app.shared.deps import get_db
from .service import UserService

def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)