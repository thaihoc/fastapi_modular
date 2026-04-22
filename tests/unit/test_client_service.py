"""
Unit tests cho ClientService.

Chiến lược: dùng object.__new__ để tạo service mà không gọi __init__,
sau đó mock repo bằng MagicMock. Tránh phụ thuộc vào DB thật.
"""

from unittest.mock import MagicMock

import pytest

from app.modules.clients.models import Client
from app.modules.clients.service import ClientService


def _make_service() -> ClientService:
    svc = object.__new__(ClientService)
    svc.repo = MagicMock()
    return svc


def _make_client(name="Acme Corp", email="acme@example.com") -> Client:
    c = Client(name=name, email=email)
    c.id = 1
    return c


class TestCreateClient:
    def test_success_returns_client(self):
        svc = _make_service()
        svc.repo.get_by_email.return_value = None
        svc.repo.create.return_value = _make_client()

        result = svc.create_client("Acme Corp", "acme@example.com")

        svc.repo.get_by_email.assert_called_once_with("acme@example.com")
        svc.repo.create.assert_called_once()
        assert result.name == "Acme Corp"
        assert result.email == "acme@example.com"

    def test_duplicate_email_raises_value_error(self):
        svc = _make_service()
        svc.repo.get_by_email.return_value = _make_client()

        with pytest.raises(ValueError, match="Email already exists"):
            svc.create_client("Acme Corp", "acme@example.com")

        svc.repo.create.assert_not_called()

    def test_passes_correct_fields_to_repo(self):
        svc = _make_service()
        svc.repo.get_by_email.return_value = None

        captured_client = None

        def capture_create(c):
            nonlocal captured_client
            captured_client = c
            c.id = 1
            return c

        svc.repo.create.side_effect = capture_create

        svc.create_client("Beta Inc", "beta@example.com")

        assert captured_client.name == "Beta Inc"
        assert captured_client.email == "beta@example.com"


class TestGetClient:
    def test_returns_client_when_found(self):
        svc = _make_service()
        c = _make_client()
        svc.repo.get_by_id.return_value = c

        result = svc.get_client(1)

        assert result is c
        svc.repo.get_by_id.assert_called_once_with(1)

    def test_returns_none_when_not_found(self):
        svc = _make_service()
        svc.repo.get_by_id.return_value = None

        result = svc.get_client(999)

        assert result is None


class TestListClients:
    def test_returns_list(self):
        svc = _make_service()
        clients = [_make_client(), _make_client(name="Beta Inc", email="beta@example.com")]
        svc.repo.list.return_value = clients

        result = svc.list_clients(skip=0, limit=10)

        assert result == clients
        svc.repo.list.assert_called_once_with(0, 10)

    def test_passes_pagination_params(self):
        svc = _make_service()
        svc.repo.list.return_value = []

        svc.list_clients(skip=3, limit=5)

        svc.repo.list.assert_called_once_with(3, 5)

    def test_empty_returns_empty_list(self):
        svc = _make_service()
        svc.repo.list.return_value = []

        result = svc.list_clients()

        assert result == []
