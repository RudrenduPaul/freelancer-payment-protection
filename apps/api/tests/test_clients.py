"""
Tests for client CRUD endpoints.
All external calls mocked. No live API calls.
"""


def test_create_client(test_client):
    response = test_client.post("/api/v1/clients", json={
        "name": "Test Client",
        "email": "testclient@example-domain.com",
        "company": "Test Company",
        "industry": "SaaS",
        "country": "US",
        "paymentTermsDays": 30,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Client"
    assert data["email"] == "testclient@example-domain.com"
    assert data["riskScore"] == 0.0


def test_create_client_invalid_email(test_client):
    response = test_client.post("/api/v1/clients", json={
        "name": "Test Client",
        "email": "this-is-not-an-email",
    })
    assert response.status_code == 422


def test_create_client_name_too_short(test_client):
    response = test_client.post("/api/v1/clients", json={
        "name": "X",
        "email": "short@example-domain.com",
    })
    assert response.status_code == 422


def test_list_clients(test_client):
    response = test_client.get("/api/v1/clients")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_filter_clients_by_risk_level(test_client):
    # Create a client with high risk
    test_client.post("/api/v1/clients", json={
        "name": "Risky Client",
        "email": "risky@example-domain.com",
    })
    response = test_client.get("/api/v1/clients?risk_level=low")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_client_not_found(test_client):
    response = test_client.get("/api/v1/clients/nonexistent-client-id-00000")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_soft_delete_client(test_client):
    create_response = test_client.post("/api/v1/clients", json={
        "name": "Delete Me Client",
        "email": "deleteme@example-domain.com",
    })
    assert create_response.status_code == 201
    client_id = create_response.json()["id"]

    delete_response = test_client.delete(f"/api/v1/clients/{client_id}")
    assert delete_response.status_code == 204

    # Verify it's gone from listing
    get_response = test_client.get(f"/api/v1/clients/{client_id}")
    assert get_response.status_code == 404


def test_update_client(test_client):
    create_response = test_client.post("/api/v1/clients", json={
        "name": "Update Me Client",
        "email": "updateme@example-domain.com",
    })
    assert create_response.status_code == 201
    client_id = create_response.json()["id"]

    update_response = test_client.put(f"/api/v1/clients/{client_id}", json={
        "name": "Updated Client Name",
        "notes": "Updated notes content",
    })
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Client Name"
