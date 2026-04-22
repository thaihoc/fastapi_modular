"""
Shared pytest fixtures cho toàn bộ test suite.

Chiến lược DB:
  - SQLite in-memory với StaticPool → toàn bộ session (test setup + HTTP handler)
    dùng chung 1 connection, tránh vấn đề "in-memory DB per connection" của SQLite.
  - Mỗi test function nhận db fixture mới → create_all / drop_all → isolation.

Chiến lược startup events:
  - TestClient KHÔNG dùng context manager → init_cache không chạy.
  - Cache được khởi tạo thủ công với InMemoryBackend trong session fixture.
  - get_db dependency bị override → app dùng test session.
  - validate_token dependency bị override trong auth_client → bỏ qua JWT verification.
"""

# Phải set trước khi import bất kỳ module nào của app
# (Settings() được khởi tạo tại import time, các required fields phải có giá trị)
import os
os.environ.setdefault("DB_URL", "sqlite:///:memory:")
os.environ.setdefault("AUTH_JWKS", "http://localhost/dummy/.well-known/jwks.json")

import pytest
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base

# Import models để chúng register metadata với Base trước khi create_all
import app.modules.users.models   # noqa: F401
import app.modules.clients.models  # noqa: F401


# ── Cache Bootstrap ────────────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def initialize_cache():
    """Khởi tạo FastAPICache với InMemoryBackend cho toàn bộ test session."""
    FastAPICache.init(InMemoryBackend(), prefix="testcache")


# ── DB Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    """
    SQLite in-memory session cho mỗi test.
    StaticPool đảm bảo tất cả connection dùng chung 1 in-memory DB.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


# ── App Client Fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def client(db):
    """
    FastAPI TestClient với get_db overridden về test session.
    Không override validate_token → user endpoints trả 401 nếu không có token.
    """
    from app.main import app
    from app.shared.deps import get_db

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(db):
    """
    FastAPI TestClient với get_db và validate_token đều được override.
    Dùng cho các endpoint yêu cầu JWT auth (users module).
    """
    from app.main import app
    from app.shared.deps import get_db, validate_token

    def override_get_db():
        yield db

    def override_validate_token():
        return {"sub": "test-user"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[validate_token] = override_validate_token
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


# ── Data Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def test_user(db):
    """Tạo user test trực tiếp vào DB (không qua API vì /users/ yêu cầu auth)."""
    from app.modules.users.service import UserService
    return UserService(db).create_user(
        email="user@test.com",
        password="password123",
        full_name="Test User",
    )


@pytest.fixture
def test_client_record(db):
    """Tạo client test trực tiếp vào DB."""
    from app.modules.clients.service import ClientService
    return ClientService(db).create_client(
        name="Test Client",
        email="client@test.com",
    )
