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
async def test_four_dashboard_modules(client):
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@senacontigo.edu.co", "password": "Admin123456*"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Module 1: Tabulación
    res_tab = await client.get("/api/v1/analytics/tabulation", headers=headers)
    assert res_tab.status_code == 200

    # Module 2: Beneficios
    res_ben = await client.get("/api/v1/analytics/beneficios", headers=headers)
    assert res_ben.status_code == 200
    data_ben = res_ben.json()
    assert "total_otorgamientos" in data_ben
    assert "tasa_cobertura_porcentaje" in data_ben

    # Module 3: Casos
    res_cas = await client.get("/api/v1/analytics/casos", headers=headers)
    assert res_cas.status_code == 200
    data_cas = res_cas.json()
    assert "total_casos" in data_cas
    assert "tasa_resolucion_porcentaje" in data_cas

    # Module 4: Contratación
    res_con = await client.get("/api/v1/analytics/contratacion", headers=headers)
    assert res_con.status_code == 200
    data_con = res_con.json()
    assert "total_aprendices" in data_con
    assert "tasa_patrocinio_porcentaje" in data_con


@pytest.mark.asyncio
async def test_module_apprentices_endpoints(client):
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@senacontigo.edu.co", "password": "Admin123456*"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Beneficios aprendices
    res_ben_apr = await client.get("/api/v1/analytics/beneficios/aprendices", headers=headers)
    assert res_ben_apr.status_code == 200
    data_ben_apr = res_ben_apr.json()
    assert "items" in data_ben_apr
    assert "total" in data_ben_apr

    # Casos aprendices
    res_cas_apr = await client.get("/api/v1/analytics/casos/aprendices", headers=headers)
    assert res_cas_apr.status_code == 200
    data_cas_apr = res_cas_apr.json()
    assert "items" in data_cas_apr
    assert "total" in data_cas_apr

    # Contratacion aprendices
    res_con_apr = await client.get("/api/v1/analytics/contratacion/aprendices", headers=headers)
    assert res_con_apr.status_code == 200
    data_con_apr = res_con_apr.json()
    assert "items" in data_con_apr
    assert "total" in data_con_apr

    # Buscador de aprendices por documento o nombre
    res_search = await client.get("/api/v1/analytics/beneficios/aprendices?q=1000", headers=headers)
    assert res_search.status_code == 200
    data_search = res_search.json()
    assert "items" in data_search





