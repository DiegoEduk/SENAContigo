import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_login_superadmin(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@senacontigo.edu.co", "password": "Admin123456*"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["usuario"]["correo"] == "admin@senacontigo.edu.co"


@pytest.mark.asyncio
async def test_list_regionales(client):
    # Login first
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@senacontigo.edu.co", "password": "Admin123456*"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/regionales", headers=headers)
    assert res.status_code == 200
    regionales = res.json()
    assert isinstance(regionales, list)
