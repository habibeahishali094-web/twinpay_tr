import pytest
from fastapi.testclient import TestClient

def test_sandbox_reset(client: TestClient):
    res = client.post("/api/v1/users/register", json={"username": "resetuser"})
    headers = {"Authorization": f"Bearer {res.json()['api_key']}"}
    
    client.post("/api/v1/payments/", json={"amount": 10, "card_number": "1234", "expiry_month": "1", "expiry_year": "25", "cvc": "1"}, headers=headers)
    
    res_reset = client.post("/api/v1/sandbox/reset", headers=headers)
    assert res_reset.status_code == 200
    
    res_get = client.get("/api/v1/payments/1", headers=headers)
    assert res_get.status_code == 404
