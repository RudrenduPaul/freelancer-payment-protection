def test_liveness(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "bad-cop-crm"


def test_readiness(test_client):
    response = test_client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "db" in data


def test_readiness_failure_hides_exception_details(test_client, monkeypatch):
    from apps.api.app.routers import health

    class _BrokenEngine:
        def connect(self):
            raise RuntimeError("secret-dsn-host:5432 refused connection")

    monkeypatch.setattr(health, "engine", _BrokenEngine())
    response = test_client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_ready"
    assert data["db"] == "disconnected"
    assert data["error"] == "database unavailable"
    assert "secret-dsn-host" not in response.text
