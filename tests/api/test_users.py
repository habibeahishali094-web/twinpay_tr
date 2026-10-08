from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    response = client.post("/api/v1/users/register", json={"username": "testuser"})
    assert response.status_code == 201
    data = response.json()
    assert "api_key" in data
    assert "api_key_prefix" in data
    assert data["username"] == "testuser"
    assert data["api_key"].startswith(data["api_key_prefix"])

def test_get_me(client: TestClient):
    register_res = client.post("/api/v1/users/register", json={"username": "user1"})
    api_key = register_res.json()["api_key"]
    
    res = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {api_key}"})
    assert res.status_code == 200
    assert res.json()["username"] == "user1"

def test_invalid_api_key(client: TestClient):
    res = client.get("/api/v1/users/me", headers={"Authorization": "Bearer invalid_key"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Geçersiz API Anahtarı"

def test_missing_api_key(client: TestClient):
    res = client.get("/api/v1/users/me")
    assert res.status_code == 403

def test_isolation_other_user_data(client: TestClient):
    res1 = client.post("/api/v1/users/register", json={"username": "userA"})
    keyA = res1.json()["api_key"]
    
    res2 = client.post("/api/v1/users/register", json={"username": "userB"})
    keyB = res2.json()["api_key"]
    
    profileA = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {keyA}"})
    assert profileA.json()["username"] == "userA"
    
    profileB = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {keyB}"})
    assert profileB.json()["username"] == "userB"

def test_prefix_length(client: TestClient):
    response = client.post("/api/v1/users/register", json={"username": "prefixuser"})
    data = response.json()
    assert len(data["api_key_prefix"]) == 8
    assert data["api_key_prefix"].startswith("twp_")

def test_login_cookie_flags(client: TestClient):
    register_res = client.post("/api/v1/users/register", json={"username": "cookietest"})
    api_key = register_res.json()["api_key"]
    
    response = client.post("/login", data={"api_key": api_key}, follow_redirects=False)
    assert response.status_code == 302
    
    set_cookie = response.headers.get("set-cookie", "").lower()
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie

def test_logout_deletes_cookie(client: TestClient):
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    set_cookie = response.headers.get("set-cookie", "").lower()
    assert "max-age=0" in set_cookie or "expires=" in set_cookie
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie
