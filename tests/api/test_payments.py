import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def user_headers(client: TestClient):
    res = client.post("/api/v1/users/register", json={"username": "payuser"})
    return {"Authorization": f"Bearer {res.json()['api_key']}"}

def test_create_payment(client: TestClient, user_headers):
    payload = {
        "amount": 100.0,
        "card_number": "4111111111111111",
        "expiry_month": "12",
        "expiry_year": "25",
        "cvc": "123"
    }
    res = client.post("/api/v1/payments/", json=payload, headers=user_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["amount"] == 100.0
    assert data["status"] == "authorized"
    assert data["card_mask"] == "**** **** **** 1111"

def test_idempotency(client: TestClient, user_headers):
    payload = {
        "amount": 50.0,
        "card_number": "4111111111111111",
        "expiry_month": "12",
        "expiry_year": "25",
        "cvc": "123"
    }
    headers = user_headers.copy()
    headers["Idempotency-Key"] = "test-key-123"
    
    res1 = client.post("/api/v1/payments/", json=payload, headers=headers)
    assert res1.status_code == 201
    payment_id1 = res1.json()["id"]
    
    res2 = client.post("/api/v1/payments/", json=payload, headers=headers)
    assert res2.status_code == 201
    assert res2.json()["id"] == payment_id1

def test_capture_payment(client: TestClient, user_headers):
    res = client.post("/api/v1/payments/", json={"amount": 10, "card_number": "1234", "expiry_month": "1", "expiry_year": "25", "cvc": "1"}, headers=user_headers)
    pid = res.json()["id"]
    
    res_cap = client.post(f"/api/v1/payments/{pid}/capture", headers=user_headers)
    assert res_cap.status_code == 200
    assert res_cap.json()["status"] == "captured"

def test_cancel_payment(client: TestClient, user_headers):
    res = client.post("/api/v1/payments/", json={"amount": 10, "card_number": "1234", "expiry_month": "1", "expiry_year": "25", "cvc": "1"}, headers=user_headers)
    pid = res.json()["id"]
    
    res_can = client.post(f"/api/v1/payments/{pid}/cancel", headers=user_headers)
    assert res_can.status_code == 200
    assert res_can.json()["status"] == "canceled"

def test_refund_payment(client: TestClient, user_headers):
    res = client.post("/api/v1/payments/", json={"amount": 10, "card_number": "1234", "expiry_month": "1", "expiry_year": "25", "cvc": "1"}, headers=user_headers)
    pid = res.json()["id"]
    
    client.post(f"/api/v1/payments/{pid}/capture", headers=user_headers)
    
    res_ref = client.post(f"/api/v1/payments/{pid}/refund", headers=user_headers)
    assert res_ref.status_code == 200
    assert res_ref.json()["status"] == "refunded"
