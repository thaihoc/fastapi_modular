"""
Integration tests cho health endpoints.

GET /api/v1/health       → liveness probe
GET /api/v1/health/ready → readiness probe (kiểm tra DB và Redis)
"""

from unittest.mock import MagicMock, patch

from sqlalchemy.exc import OperationalError


class TestLiveness:
    def test_returns_200_with_ok_status(self, client):
        r = client.get("/api/v1/health")

        assert r.status_code == 200

    def test_response_contains_status_and_timestamp(self, client):
        r = client.get("/api/v1/health")
        data = r.json()

        assert data["status"] == "ok"
        assert "timestamp" in data


class TestReadiness:
    def test_all_ok_without_redis_configured(self, client):
        """Khi không cấu hình Redis, endpoint dùng in-memory cache và báo ok."""
        r = client.get("/api/v1/health/ready")

        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["checks"]["database"]["status"] == "ok"
        assert data["checks"]["redis"]["status"] == "ok"
        assert "not configured" in data["checks"]["redis"]["detail"]

    def test_response_structure(self, client):
        r = client.get("/api/v1/health/ready")
        data = r.json()

        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "redis" in data["checks"]

    def test_database_error_returns_error_status(self, client):
        """Khi DB không thể kết nối, status tổng thể là error."""
        with patch("app.modules.health.api.SessionLocal") as mock_session_cls:
            mock_session = MagicMock()
            mock_session.execute.side_effect = OperationalError(
                "connection refused", params=None, orig=None
            )
            mock_session_cls.return_value = mock_session

            r = client.get("/api/v1/health/ready")

        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "error"
        assert data["checks"]["database"]["status"] == "error"
        assert data["checks"]["database"]["detail"] != ""

    def test_redis_error_returns_error_status(self, client):
        """Khi Redis ping thất bại, status tổng thể là error."""
        mock_redis = MagicMock()
        mock_redis.ping.side_effect = Exception("Connection refused")

        with patch("app.modules.health.api.get_redis_client", return_value=mock_redis):
            r = client.get("/api/v1/health/ready")

        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "error"
        assert data["checks"]["redis"]["status"] == "error"

    def test_redis_ok_when_ping_succeeds(self, client):
        """Khi Redis ping thành công, component redis báo ok."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True

        with patch("app.modules.health.api.get_redis_client", return_value=mock_redis):
            r = client.get("/api/v1/health/ready")

        data = r.json()
        assert data["checks"]["redis"]["status"] == "ok"

    def test_both_errors_returns_overall_error(self, client):
        """Khi cả DB lẫn Redis lỗi, status tổng thể là error."""
        mock_redis = MagicMock()
        mock_redis.ping.side_effect = Exception("Redis down")

        with (
            patch("app.modules.health.api.SessionLocal") as mock_session_cls,
            patch("app.modules.health.api.get_redis_client", return_value=mock_redis),
        ):
            mock_session = MagicMock()
            mock_session.execute.side_effect = OperationalError(
                "DB down", params=None, orig=None
            )
            mock_session_cls.return_value = mock_session

            r = client.get("/api/v1/health/ready")

        data = r.json()
        assert data["status"] == "error"
        assert data["checks"]["database"]["status"] == "error"
        assert data["checks"]["redis"]["status"] == "error"
