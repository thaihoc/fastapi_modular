from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    password = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.now(datetime.timezone.utc))