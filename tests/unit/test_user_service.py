"""
Unit tests cho UserService.

Chiến lược: dùng object.__new__ để tạo service mà không gọi __init__,
sau đó mock repo bằng MagicMock. Tránh phụ thuộc vào DB thật.
"""

from unittest.mock import MagicMock

import pytest

from app.modules.users.models import User
from app.modules.users.service import UserService, pwd_context


def _make_service() -> UserService:
    svc = object.__new__(UserService)
    svc.repo = MagicMock()
    return svc


def _make_user(email="alice@example.com", password="secret", full_name="Alice") -> User:
    user = User(
        email=email,
        password=pwd_context.hash(password),
        full_name=full_name,
    )
    user.id = 1
    return user


class TestCreateUser:
    def test_success_returns_user(self):
        svc = _make_service()
        svc.repo.get_by_email.return_value = None
        svc.repo.create.return_value = _make_user()

        result = svc.create_user("alice@example.com", "secret", "Alice")

        svc.repo.get_by_email.assert_called_once_with("alice@example.com")
        svc.repo.create.assert_called_once()
        assert result.email == "alice@example.com"

    def test_hashes_password_before_storing(self):
        svc = _make_service()
        svc.repo.get_by_email.return_value = None

        captured_user = None

        def capture_create(user):
            nonlocal captured_user
            captured_user = user
            user.id = 1
            return user

        svc.repo.create.side_effect = capture_create

        svc.create_user("alice@example.com", "plain_password", None)

        assert captured_user is not None
        assert captured_user.password != "plain_password"
        assert pwd_context.verify("plain_password", captured_user.password)

    def test_duplicate_email_raises_value_error(self):
        svc = _make_service()
        svc.repo.get_by_email.return_value = _make_user()

        with pytest.raises(ValueError, match="Email already exists"):
            svc.create_user("alice@example.com", "secret", None)

        svc.repo.create.assert_not_called()

    def test_full_name_optional(self):
        svc = _make_service()
        svc.repo.get_by_email.return_value = None
        svc.repo.create.return_value = _make_user(full_name=None)

        result = svc.create_user("alice@example.com", "secret", None)
        assert result.full_name is None


class TestAuthenticate:
    def test_wrong_email_returns_none(self):
        svc = _make_service()
        svc.repo.get_by_email.return_value = None

        result = svc.authenticate("nobody@example.com", "secret")

        assert result is None

    def test_wrong_password_returns_none(self):
        svc = _make_service()
        svc.repo.get_by_email.return_value = _make_user(password="correct")

        result = svc.authenticate("alice@example.com", "wrong_password")

        assert result is None

    def test_correct_credentials_returns_user(self):
        svc = _make_service()
        user = _make_user(password="correct")
        svc.repo.get_by_email.return_value = user

        result = svc.authenticate("alice@example.com", "correct")

        assert result is user

    def test_empty_password_returns_none(self):
        svc = _make_service()
        svc.repo.get_by_email.return_value = _make_user(password="correct")

        result = svc.authenticate("alice@example.com", "")

        assert result is None


class TestGetUser:
    def test_returns_user_when_found(self):
        svc = _make_service()
        user = _make_user()
        svc.repo.get_by_id.return_value = user

        result = svc.get_user(1)

        assert result is user
        svc.repo.get_by_id.assert_called_once_with(1)

    def test_returns_none_when_not_found(self):
        svc = _make_service()
        svc.repo.get_by_id.return_value = None

        result = svc.get_user(999)

        assert result is None


class TestListUsers:
    def test_returns_list(self):
        svc = _make_service()
        users = [_make_user(), _make_user(email="bob@example.com")]
        svc.repo.list.return_value = users

        result = svc.list_users(skip=0, limit=10)

        assert result == users
        svc.repo.list.assert_called_once_with(0, 10)

    def test_passes_pagination_params(self):
        svc = _make_service()
        svc.repo.list.return_value = []

        svc.list_users(skip=5, limit=20)

        svc.repo.list.assert_called_once_with(5, 20)

    def test_empty_returns_empty_list(self):
        svc = _make_service()
        svc.repo.list.return_value = []

        result = svc.list_users()

        assert result == []
