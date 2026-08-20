import pytest


@pytest.mark.asyncio
async def test_benefits_flow_independent_of_cases(client):
    # 1. Login as superadmin
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@senacontigo.edu.co", "password": "Admin123456*"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get default benefits catalog (populated by seed)
    benefits_res = await client.get("/api/v1/beneficios", headers=headers)
    assert benefits_res.status_code == 200
    catalog = benefits_res.json()
    assert len(catalog) >= 5

    # Check for Apoyo de Sostenimiento
    sostenimiento_ben = next(b for b in catalog if b["codigo"] == "BEN-SOSTENIMIENTO")
    assert sostenimiento_ben["es_automatico_matricula"] is True

    # 3. Create a new custom institutional benefit in the catalog
    new_ben_res = await client.post(
        "/api/v1/beneficios",
        headers=headers,
        json={
            "codigo": "BEN-GIMNASIO",
            "nombre": "Acceso a Gimnasio y Acondicionamiento Físico",
            "descripcion": "Uso libre del gimnasio del centro de formación",
            "tipo_beneficio": "CULTURA_Y_DEPORTE",
            "es_automatico_matricula": False
        }
    )
    assert new_ben_res.status_code == 201
    gimnasio_ben = new_ben_res.json()
    assert gimnasio_ben["codigo"] == "BEN-GIMNASIO"

    # 4. Create an Aprendiz (triggers automatic assignment of default SENA benefits)
    apr_res = await client.post(
        "/api/v1/aprendices",
        headers=headers,
        json={
            "tipo_documento": "CC",
            "numero_documento": "1234567890",
            "nombres": "María Fernanda",
            "apellidos": "Gómez López",
            "correo": "maria.gomez@misena.edu.co",
            "celular": "3001234567"
        }
    )
    assert apr_res.status_code == 201
    aprendiz_id = apr_res.json()["id"]

    # 5. Verify automatic benefits assigned to the aprendiz upon enrollment
    apr_ben_res = await client.get(f"/api/v1/beneficios/aprendiz/{aprendiz_id}", headers=headers)
    assert apr_ben_res.status_code == 200
    assigned_benefits = apr_ben_res.json()
    # Should have assigned all automatic benefits (e.g., sostenimiento, transporte, salud, orientacion, deportes)
    assert len(assigned_benefits) >= 4
    assigned_codes = [ab["beneficio"]["codigo"] for ab in assigned_benefits]
    assert "BEN-SOSTENIMIENTO" in assigned_codes
    assert "BEN-TRANSPORTE" in assigned_codes

    # Verify that case_id is None (completely independent of any case or need)
    for ab in assigned_benefits:
        assert ab["caso_id"] is None
        assert ab["origen"] == "MATRICULA_AUTOMATICA"

    # 6. Assign custom benefit (Gimnasio) directly to the aprendiz without any case or need
    direct_assign_res = await client.post(
        "/api/v1/beneficios/aprendiz",
        headers=headers,
        json={
            "aprendiz_id": aprendiz_id,
            "beneficio_id": gimnasio_ben["id"],
            "origen": "ASIGNACION_DIRECTA",
            "observaciones": "Asignación voluntaria a actividades deportivas"
        }
    )
    assert direct_assign_res.status_code == 201
    assigned_gimnasio = direct_assign_res.json()
    assert assigned_gimnasio["beneficio"]["codigo"] == "BEN-GIMNASIO"
    assert assigned_gimnasio["caso_id"] is None
    assert assigned_gimnasio["estado"] == "ACTIVO"

    # 7. Update status of assigned benefit (e.g., SUSPENDIDO)
    ab_id = assigned_gimnasio["id"]
    update_state_res = await client.patch(
        f"/api/v1/beneficios/aprendiz/{ab_id}/estado",
        headers=headers,
        json={
            "estado": "SUSPENDIDO",
            "observaciones": "Suspendido temporalmente por inasistencia"
        }
    )
    assert update_state_res.status_code == 200
    assert update_state_res.json()["estado"] == "SUSPENDIDO"
