from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .repo import UserRepo
from .models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:

    def __init__(self, db: Session):
        self.repo = UserRepo(db)

    def create_user(self, email: str, password: str, full_name: str | None):
        existing = self.repo.get_by_email(email)
        if existing:
            raise ValueError("Email already exists")

        hashed_password = pwd_context.hash(password)

        user = User(
            email=email,
            password=hashed_password,
            full_name=full_name
        )

        return self.repo.create(user)

    def authenticate(self, email: str, password: str):
        user = self.repo.get_by_email(email)
        if not user:
            return None

        if not pwd_context.verify(password, user.password):
            return None

        return user

    def get_user(self, user_id: int):
        return self.repo.get_by_id(user_id)

    def list_users(self, skip=0, limit=10):
        return self.repo.list(skip, limit)