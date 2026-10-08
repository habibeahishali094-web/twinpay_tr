import pytest
from fastapi.testclient import TestClient

def test_update_settings(client: TestClient):
    res = client.post("/api/v1/users/register", json={"username": "setuser"})
    headers = {"Authorization": f"Bearer {res.json()['api_key']}"}
    
    # get default
    res_get = client.get("/api/v1/settings/", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["language"] == "tr"
    
    # update
    res_put = client.put("/api/v1/settings/", json={"language": "en", "error_rate": 20, "delay_ms": 1000}, headers=headers)
    assert res_put.status_code == 200
    assert res_put.json()["language"] == "en"
    assert res_put.json()["error_rate"] == 20

def test_scenarios(client: TestClient):
    res = client.post("/api/v1/users/register", json={"username": "scenuser"})
    headers = {"Authorization": f"Bearer {res.json()['api_key']}"}
    
    # create scenario
    scen = client.post("/api/v1/settings/scenarios", json={
        "name": "Yüksek Hata",
        "chaos_mode_enabled": True,
        "error_rate": 50,
        "delay_ms": 2000
    }, headers=headers)
    assert scen.status_code == 201
    sid = scen.json()["id"]
    
    # apply scenario
    app = client.post(f"/api/v1/settings/scenarios/{sid}/apply", headers=headers)
    assert app.status_code == 200
    assert app.json()["error_rate"] == 50
    assert app.json()["delay_ms"] == 2000
