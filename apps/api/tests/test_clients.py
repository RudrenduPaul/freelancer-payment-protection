"""Tests for client CRUD endpoints. All external calls are mocked."""


def test_create_client(test_client):
    response = test_client.post("/api/v1/clients", json={
        "name": "Test Client",
        "email": "testclient@example-domain.com",
        "company": "Test Co",
        "industry": "SaaS",
        "country": "US",
        "payment_terms_days": 30,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Client"
    assert data["email"] == "testclient@example-domain.com"
    assert data["risk_score"] == 0.0


def test_create_client_invalid_email(test_client):
    response = test_client.post("/api/v1/clients", json={
        "name": "Test Client",
        "email": "not-a-valid-email",
    })
    assert response.status_code == 422


def test_create_client_name_too_short(test_client):
    response = test_client.post("/api/v1/clients", json={
        "name": "A",
        "email": "test@example-domain.com",
    })
    assert response.status_code == 422


def test_list_clients_empty(test_client):
    response = test_client.get("/api/v1/clients")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_client_not_found(test_client):
    response = test_client.get("/api/v1/clients/nonexistent-id-00000")
    assert response.status_code == 404


def test_soft_delete_client(test_client):
    create_response = test_client.post("/api/v1/clients", json={
        "name": "Delete Me",
        "email": "deleteme@example-domain.com",
    })
    assert create_response.status_code == 201
    client_id = create_response.json()["id"]

    delete_response = test_client.delete(f"/api/v1/clients/{client_id}")
    assert delete_response.status_code == 204

    get_response = test_client.get(f"/api/v1/clients/{client_id}")
    assert get_response.status_code == 404


def test_update_client(test_client):
    create_response = test_client.post("/api/v1/clients", json={
        "name": "Update Me",
        "email": "updateme@example-domain.com",
    })
    assert create_response.status_code == 201
    client_id = create_response.json()["id"]

    update_response = test_client.put(f"/api/v1/clients/{client_id}", json={
        "name": "Updated Name",
        "notes": "Updated notes",
    })
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Name"
