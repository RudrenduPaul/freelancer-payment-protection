"""
Tests for invoice CRUD endpoints.
All external calls mocked. No live API calls.
"""
import pytest
from datetime import datetime, timedelta


@pytest.fixture
def sample_client(test_client):
    """Create a client for use in invoice tests."""
    response = test_client.post("/api/v1/clients", json={
        "name": "Invoice Test Client",
        "email": "invoiceclient@example-domain.com",
    })
    assert response.status_code == 201
    return response.json()


def test_create_invoice(test_client, sample_client):
    due_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    response = test_client.post("/api/v1/invoices", json={
        "clientId": sample_client["id"],
        "invoiceNumber": "INV-TEST-001",
        "amount": 5000.00,
        "currency": "USD",
        "dueDate": due_date,
        "sourceSystem": "manual",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["invoiceNumber"] == "INV-TEST-001"
    assert data["amount"] == 5000.00
    assert data["status"] == "pending"
    assert "evidenceCount" in data


def test_create_invoice_negative_amount(test_client, sample_client):
    due_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    response = test_client.post("/api/v1/invoices", json={
        "clientId": sample_client["id"],
        "invoiceNumber": "INV-BAD",
        "amount": -100,
        "currency": "USD",
        "dueDate": due_date,
    })
    assert response.status_code == 422


def test_list_invoices(test_client):
    response = test_client.get("/api/v1/invoices")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_filter_invoices_by_status(test_client):
    response = test_client.get("/api/v1/invoices?status=paid")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_filter_invoices_invalid_status(test_client):
    response = test_client.get("/api/v1/invoices?status=not_a_real_status")
    assert response.status_code == 400


def test_get_invoice_not_found(test_client):
    response = test_client.get("/api/v1/invoices/nonexistent-invoice-id-00000")
    assert response.status_code == 404


def test_update_invoice_status_to_paid(test_client, sample_client):
    due_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    create_resp = test_client.post("/api/v1/invoices", json={
        "clientId": sample_client["id"],
        "invoiceNumber": "INV-STATUS-TEST",
        "amount": 1000.00,
        "currency": "USD",
        "dueDate": due_date,
    })
    assert create_resp.status_code == 201
    invoice_id = create_resp.json()["id"]

    patch_resp = test_client.patch(f"/api/v1/invoices/{invoice_id}/status", json={
        "status": "paid",
    })
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["status"] == "paid"
    assert data["daysPastDue"] == 0
    assert data["escalationStage"] is None
