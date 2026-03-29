from sqlalchemy.orm import Session
from .models import User

class UserRepo:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list(self, skip: int = 0, limit: int = 10):
        return self.db.query(User).offset(skip).limit(limit).all()