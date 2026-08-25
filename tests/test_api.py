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


@pytest.mark.asyncio
async def test_get_tabulation(client):
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@senacontigo.edu.co", "password": "Admin123456*"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/analytics/tabulation", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert "categorias" in data
    assert "distribucion_niveles_riesgo" in data


@pytest.mark.asyncio
async def test_export_tabulation_pdf(client):
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@senacontigo.edu.co", "password": "Admin123456*"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/analytics/tabulation/export-pdf", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 0
    assert res.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_allowed_filters(client):
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@senacontigo.edu.co", "password": "Admin123456*"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/analytics/allowed-filters", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "allowed_filters" in data
    assert "user_role" in data
    assert "regional_id" in data["allowed_filters"]
    assert "programa_codigo" in data["allowed_filters"]


@pytest.mark.asyncio
async def test_filter_options(client):
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@senacontigo.edu.co", "password": "Admin123456*"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Sin término o <= 4 caracteres no precarga catalogos extensos
    res_short = await client.get("/api/v1/analytics/filter-options?q=SENA", headers=headers)
    assert res_short.status_code == 200
    data_short = res_short.json()
    assert len(data_short["regionales"]) == 0
    assert len(data_short["programas"]) == 0

    # Con término > 4 caracteres realiza búsqueda flexible por nombre/código
    res_search = await client.get("/api/v1/analytics/filter-options?target=programa&q=DISEÑO", headers=headers)
    assert res_search.status_code == 200
    data_search = res_search.json()
    assert "programas" in data_search


@pytest.mark.asyncio
async def test_search_and_multiselect_filters(client):
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@senacontigo.edu.co", "password": "Admin123456*"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Probar tabulación con múltiples parámetros repetidos (multi-select)
    res = await client.get("/api/v1/analytics/tabulation?regional_id=11&regional_id=12&nivel_riesgo=Bajo&nivel_riesgo=Medio", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert "categorias" in data



