import pytest


@pytest.mark.asyncio
async def test_lider_bienestar_role_permissions(client):
    # 1. Login as lider_bienestar
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "bienestar@senacontigo.edu.co", "password": "Bienestar123456*"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Access Benefits module (allowed)
    ben_res = await client.get("/api/v1/beneficios", headers=headers)
    assert ben_res.status_code == 200

    create_ben_res = await client.post(
        "/api/v1/beneficios",
        headers=headers,
        json={
            "codigo": "BEN-BIENESTAR-TEST",
            "nombre": "Apoyo de Salud Mental",
            "descripcion": "Atención especializada por psicología",
            "tipo_beneficio": "SALUD_Y_PROTECCION",
            "es_automatico_matricula": False
        }
    )
    assert create_ben_res.status_code == 201

    # 3. Attempt to register a contract (Forbidden for lider_bienestar)
    forbidden_contrato_res = await client.post(
        "/api/v1/contratos",
        headers=headers,
        json={
            "matricula_id": 1,
            "nombre_empresa": "EMPRESA PROHIBIDA",
            "departamento": "CUNDINAMARCA",
            "ciudad": "BOGOTÁ",
            "fecha_inicio_contrato": "2025-01-01",
            "estado_contrato": "EN PATROCINIO"
        }
    )
    assert forbidden_contrato_res.status_code == 403


@pytest.mark.asyncio
async def test_lider_contratacion_role_permissions(client):
    # 1. Login as lider_contratacion
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "contratacion@senacontigo.edu.co", "password": "Contratacion123456*"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Access Contracts module (allowed)
    contratos_res = await client.get("/api/v1/contratos", headers=headers)
    assert contratos_res.status_code == 200

    # 3. Attempt to create a benefit (Forbidden for lider_contratacion)
    forbidden_ben_res = await client.post(
        "/api/v1/beneficios",
        headers=headers,
        json={
            "codigo": "BEN-PROHIBIDO",
            "nombre": "Beneficio No Autorizado",
            "descripcion": "Sin permiso",
            "tipo_beneficio": "APOYO_FINANCIERO",
            "es_automatico_matricula": False
        }
    )
    assert forbidden_ben_res.status_code == 403
