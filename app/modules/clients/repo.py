from sqlalchemy.orm import Session
from .models import Client

class ClientRepo:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, client_id: int):
        return self.db.query(Client).filter(Client.id == client_id).first()

    def get_by_email(self, email: str):
        return self.db.query(Client).filter(Client.email == email).first()

    def create(self, client: Client):
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def list(self, skip: int = 0, limit: int = 10):
        return self.db.query(Client).offset(skip).limit(limit).all()