"""
Integration tests cho users endpoints.

POST   /api/v1/users/        → tạo user mới (yêu cầu JWT)
GET    /api/v1/users/{id}    → lấy user theo id (yêu cầu JWT)
GET    /api/v1/users/        → danh sách users (yêu cầu JWT)

auth_client: validate_token được override → bỏ qua JWT verification.
client:      validate_token không override → kiểm tra hành vi khi không có token.
"""


class TestCreateUser:
    def test_success_returns_user_data(self, auth_client):
        r = auth_client.post("/api/v1/users/", json={
            "email": "newuser@example.com",
            "password": "pass123",
            "full_name": "New User",
        })

        assert r.status_code == 200
        data = r.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "created_at" in data

    def test_password_not_exposed_in_response(self, auth_client):
        r = auth_client.post("/api/v1/users/", json={
            "email": "secure@example.com",
            "password": "s3cr3t",
        })

        assert "password" not in r.json()

    def test_full_name_optional(self, auth_client):
        r = auth_client.post("/api/v1/users/", json={
            "email": "nofullname@example.com",
            "password": "pass123",
        })

        assert r.status_code == 200
        assert r.json()["full_name"] is None

    def test_duplicate_email_returns_400(self, auth_client, test_user):
        r = auth_client.post("/api/v1/users/", json={
            "email": test_user.email,
            "password": "another_pass",
        })

        assert r.status_code == 400
        assert "already exists" in r.json()["detail"]

    def test_invalid_email_returns_422(self, auth_client):
        r = auth_client.post("/api/v1/users/", json={
            "email": "not-an-email",
            "password": "pass123",
        })

        assert r.status_code == 422

    def test_missing_password_returns_422(self, auth_client):
        r = auth_client.post("/api/v1/users/", json={
            "email": "user@example.com",
        })

        assert r.status_code == 422

    def test_missing_email_returns_422(self, auth_client):
        r = auth_client.post("/api/v1/users/", json={
            "password": "pass123",
        })

        assert r.status_code == 422

    def test_no_auth_returns_401(self, client):
        """Không có Authorization header → 401 trước khi xử lý request."""
        r = client.post("/api/v1/users/", json={
            "email": "user@example.com",
            "password": "pass123",
        })

        assert r.status_code == 401


class TestGetUser:
    def test_success_returns_user(self, auth_client, test_user):
        r = auth_client.get(f"/api/v1/users/{test_user.id}")

        assert r.status_code == 200
        data = r.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name

    def test_not_found_returns_404(self, auth_client):
        r = auth_client.get("/api/v1/users/99999")

        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_invalid_id_type_returns_422(self, auth_client):
        r = auth_client.get("/api/v1/users/not-an-integer")

        assert r.status_code == 422

    def test_no_auth_returns_401(self, client, test_user):
        r = client.get(f"/api/v1/users/{test_user.id}")

        assert r.status_code == 401


class TestListUsers:
    def test_empty_database_returns_empty_list(self, auth_client):
        r = auth_client.get("/api/v1/users/")

        assert r.status_code == 200
        assert r.json() == []

    def test_returns_created_users(self, auth_client, test_user):
        r = auth_client.get("/api/v1/users/")

        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["id"] == test_user.id

    def test_pagination_limit(self, auth_client):
        for i in range(5):
            auth_client.post("/api/v1/users/", json={
                "email": f"user{i}@example.com",
                "password": "pass123",
            })

        r = auth_client.get("/api/v1/users/?skip=0&limit=3")

        assert r.status_code == 200
        assert len(r.json()) == 3

    def test_pagination_skip(self, auth_client):
        for i in range(4):
            auth_client.post("/api/v1/users/", json={
                "email": f"paged{i}@example.com",
                "password": "pass123",
            })

        r = auth_client.get("/api/v1/users/?skip=3&limit=10")

        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_no_auth_returns_401(self, client):
        r = client.get("/api/v1/users/")

        assert r.status_code == 401
