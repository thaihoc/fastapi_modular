from sqlalchemy.orm import Session

from .repo import ClientRepo
from .models import Client

class ClientService:

    def __init__(self, db: Session):
        self.repo = ClientRepo(db)

    def create_client(self, name: str, email: str):
        existing = self.repo.get_by_email(email)
        if existing:
            raise ValueError("Email already exists")

        client = Client(
            name=name,
            email=email
        )

        return self.repo.create(client)

    def get_client(self, client_id: int):
        return self.repo.get_by_id(client_id)

    def list_clients(self, skip=0, limit=10):
        return self.repo.list(skip, limit)