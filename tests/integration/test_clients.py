"""
Integration tests cho clients endpoints.

POST   /api/v1/clients/       → tạo client mới (không yêu cầu auth)
GET    /api/v1/clients/{id}   → lấy client theo id (không yêu cầu auth)
GET    /api/v1/clients/       → danh sách clients (không yêu cầu auth)
"""


class TestCreateClient:
    def test_success_returns_client_data(self, client):
        r = client.post("/api/v1/clients/", json={
            "name": "Acme Corp",
            "email": "acme@example.com",
        })

        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Acme Corp"
        assert data["email"] == "acme@example.com"
        assert "id" in data

    def test_duplicate_email_returns_400(self, client, test_client_record):
        r = client.post("/api/v1/clients/", json={
            "name": "Another Corp",
            "email": test_client_record.email,
        })

        assert r.status_code == 400
        assert "already exists" in r.json()["detail"]

    def test_invalid_email_returns_422(self, client):
        r = client.post("/api/v1/clients/", json={
            "name": "Corp",
            "email": "not-valid-email",
        })

        assert r.status_code == 422

    def test_missing_name_returns_422(self, client):
        r = client.post("/api/v1/clients/", json={
            "email": "corp@example.com",
        })

        assert r.status_code == 422

    def test_missing_email_returns_422(self, client):
        r = client.post("/api/v1/clients/", json={
            "name": "Corp",
        })

        assert r.status_code == 422

    def test_no_auth_required(self, client):
        """Clients endpoint không yêu cầu JWT → request không có token vẫn thành công."""
        r = client.post("/api/v1/clients/", json={
            "name": "Open Corp",
            "email": "open@example.com",
        })

        assert r.status_code == 200


class TestGetClient:
    def test_success_returns_client(self, client, test_client_record):
        r = client.get(f"/api/v1/clients/{test_client_record.id}")

        assert r.status_code == 200
        data = r.json()
        assert data["id"] == test_client_record.id
        assert data["name"] == test_client_record.name
        assert data["email"] == test_client_record.email

    def test_not_found_returns_404(self, client):
        r = client.get("/api/v1/clients/99999")

        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_invalid_id_type_returns_422(self, client):
        r = client.get("/api/v1/clients/not-an-integer")

        assert r.status_code == 422


class TestListClients:
    def test_empty_database_returns_empty_list(self, client):
        r = client.get("/api/v1/clients/")

        assert r.status_code == 200
        assert r.json() == []

    def test_returns_existing_clients(self, client, test_client_record):
        r = client.get("/api/v1/clients/")

        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["id"] == test_client_record.id

    def test_pagination_limit(self, client):
        for i in range(5):
            client.post("/api/v1/clients/", json={
                "name": f"Corp {i}",
                "email": f"corp{i}@example.com",
            })

        r = client.get("/api/v1/clients/?skip=0&limit=3")

        assert r.status_code == 200
        assert len(r.json()) == 3

    def test_pagination_skip(self, client):
        for i in range(4):
            client.post("/api/v1/clients/", json={
                "name": f"Skip Corp {i}",
                "email": f"skipcorp{i}@example.com",
            })

        r = client.get("/api/v1/clients/?skip=3&limit=10")

        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_default_limit_is_10(self, client):
        for i in range(15):
            client.post("/api/v1/clients/", json={
                "name": f"Bulk Corp {i}",
                "email": f"bulk{i}@example.com",
            })

        r = client.get("/api/v1/clients/")

        assert r.status_code == 200
        assert len(r.json()) == 10
