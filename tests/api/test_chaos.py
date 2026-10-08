import pytest
import time
from fastapi.testclient import TestClient

def test_chaos_delay(client: TestClient):
    res = client.post("/api/v1/users/register", json={"username": "chaosuser"})
    headers = {"Authorization": f"Bearer {res.json()['api_key']}"}
    
    client.put("/api/v1/settings/", json={"chaos_mode_enabled": True, "delay_ms": 1000}, headers=headers)
    
    start_time = time.time()
    res_pay = client.post("/api/v1/payments/", json={"amount": 10, "card_number": "1", "expiry_month": "1", "expiry_year": "25", "cvc": "1"}, headers=headers)
    duration = time.time() - start_time
    
    assert res_pay.status_code == 201
    assert duration >= 1.0

def test_chaos_error_rate_with_seed(client: TestClient):
    res = client.post("/api/v1/users/register", json={"username": "chaosuser2"})
    headers = {"Authorization": f"Bearer {res.json()['api_key']}"}
    
    client.put("/api/v1/settings/", json={"chaos_mode_enabled": True, "error_rate": 100, "seed": "test-seed"}, headers=headers)
    
    res_pay1 = client.post("/api/v1/payments/", json={"amount": 10, "card_number": "1", "expiry_month": "1", "expiry_year": "25", "cvc": "1"}, headers=headers)
    assert res_pay1.status_code == 201
    assert res_pay1.json()["status"] == "failed"
    error1 = res_pay1.json()["error_code"]
    
    res_pay2 = client.post("/api/v1/payments/", json={"amount": 10, "card_number": "1", "expiry_month": "1", "expiry_year": "25", "cvc": "1"}, headers=headers)
    error2 = res_pay2.json()["error_code"]
    
    # Due to same seed applied repeatedly to random.Random, it yields the exact same sequence of choices
    assert error1 == error2
