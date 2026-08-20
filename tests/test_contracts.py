import pytest


@pytest.mark.asyncio
async def test_contracts_full_lifecycle(client):
    # 1. Login as superadmin
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@senacontigo.edu.co", "password": "Admin123456*"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create a new Aprendiz
    apr_res = await client.post(
        "/api/v1/aprendices",
        headers=headers,
        json={
            "tipo_documento": "CC",
            "numero_documento": "1098765999",
            "nombres": "Carlos Alberto",
            "apellidos": "Ramírez Silva",
            "correo": "carlos.ramirez999@misena.edu.co",
            "celular": "3119876543"
        }
    )
    assert apr_res.status_code == 201
    aprendiz = apr_res.json()
    aprendiz_id = aprendiz["id"]

    # 3. Check contracts for newly created apprentice (should be empty list)
    contratos_initial = await client.get(
        f"/api/v1/contratos/aprendiz/{aprendiz_id}",
        headers=headers
    )
    assert contratos_initial.status_code == 200
    assert contratos_initial.json() == []

    # 4. Enroll apprentice in a Ficha (Create Matricula)
    fichas_res = await client.get("/api/v1/fichas", headers=headers)
    assert fichas_res.status_code == 200
    fichas = fichas_res.json()

    if fichas:
        ficha_id = fichas[0]["ficha_caracterizacion"]
    else:
        # Create program and ficha if not seeded
        prog_res = await client.post(
            "/api/v1/programas",
            headers=headers,
            json={"codigo_programa": "228118", "version": "1", "nombre": "ADSO", "nivel_formacion": "TECNÓLOGO"}
        )
        centro_res = await client.post(
            "/api/v1/centros",
            headers=headers,
            json={"codigo_centro": "9201", "nombre": "Centro Prueba", "regional_id": "11"}
        )
        ficha_res = await client.post(
            "/api/v1/fichas",
            headers=headers,
            json={
                "ficha_caracterizacion": "2670123",
                "fecha_inicial": "2024-01-01",
                "fecha_final": "2025-12-31",
                "estado_ficha": "EJECUCION",
                "centro_id": "9201",
                "programa_codigo": "228118",
                "programa_version": "1"
            }
        )
        ficha_id = ficha_res.json()["ficha_caracterizacion"]

    mat_res = await client.post(
        "/api/v1/matriculas",
        headers=headers,
        json={
            "aprendiz_id": aprendiz_id,
            "ficha_id": ficha_id,
            "estado_matricula": "En formación"
        }
    )
    assert mat_res.status_code == 201
    matricula_id = mat_res.json()["id"]

    # 5. Create a new Learning Contract for the matricula (EN PATROCINIO)
    contrato_payload = {
        "matricula_id": matricula_id,
        "nombre_empresa": "DISTRIBUIDORA NACIONAL S.A.S.",
        "departamento": "ANTIOQUIA",
        "ciudad": "MEDELLÍN",
        "fecha_inicio_contrato": "2025-03-01",
        "fecha_fin_contrato": "2025-09-01",
        "estado_contrato": "EN PATROCINIO",
        "observaciones": "Patrocinio en desarrollo de software"
    }

    create_c_res = await client.post(
        "/api/v1/contratos",
        headers=headers,
        json=contrato_payload
    )
    assert create_c_res.status_code == 201
    created_contrato = create_c_res.json()
    contrato_id = created_contrato["id"]
    assert created_contrato["nombre_empresa"] == "DISTRIBUIDORA NACIONAL S.A.S."
    assert created_contrato["departamento"] == "ANTIOQUIA"
    assert created_contrato["ciudad"] == "MEDELLÍN"
    assert created_contrato["estado_contrato"] == "EN PATROCINIO"
    assert created_contrato["aprendiz_id"] == aprendiz_id
    assert created_contrato["ficha_id"] == ficha_id

    # 6. Verify apprentice now has 1 contract registered
    contratos_aprendiz = await client.get(
        f"/api/v1/contratos/aprendiz/{aprendiz_id}",
        headers=headers
    )
    assert contratos_aprendiz.status_code == 200
    list_c = contratos_aprendiz.json()
    assert len(list_c) == 1
    assert list_c[0]["id"] == contrato_id

    # 7. Update contract status to EN ETAPA PRACTICA
    update_res = await client.patch(
        f"/api/v1/contratos/{contrato_id}",
        headers=headers,
        json={"estado_contrato": "EN ETAPA PRACTICA"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["estado_contrato"] == "EN ETAPA PRACTICA"

    # 8. List contracts with search filter
    search_res = await client.get(
        "/api/v1/contratos?search=DISTRIBUIDORA",
        headers=headers
    )
    assert search_res.status_code == 200
    search_list = search_res.json()
    assert len(search_list) >= 1
    assert any(c["id"] == contrato_id for c in search_list)
