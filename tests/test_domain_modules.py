import pytest


@pytest.mark.asyncio
async def test_variables_and_responses_flow(client):
    # 1. Login as superadmin
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@senacontigo.edu.co", "password": "Admin123456*"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get categories
    cat_res = await client.get("/api/v1/variables/categorias", headers=headers)
    assert cat_res.status_code == 200
    categories = cat_res.json()
    vivienda_cat = [c for c in categories if c["codigo"] == "VIVIENDA"][0]

    # 3. Create a dynamic variable with version 1 options
    var_res = await client.post(
        "/api/v1/variables",
        headers=headers,
        json={
            "categoria_id": vivienda_cat["id"],
            "codigo": "ESTADO_VIVIENDA",
            "nombre": "Estado de la Vivienda",
            "descripcion": "Identificar el nivel de afectación habitacional",
            "tipo_respuesta": "opcion_unica",
            "titulo_pregunta": "¿En qué estado se encuentra su vivienda actual?",
            "opciones": [
                {"codigo": "NORMAL", "texto": "Sin daños / Normal", "valor_numerico": 0, "nivel_afectacion": 0},
                {"codigo": "AFECTADA", "texto": "Vivienda Afectada", "valor_numerico": 1, "nivel_afectacion": 1},
                {"codigo": "INHABITABLE", "texto": "Vivienda Inhabitable", "valor_numerico": 2, "nivel_afectacion": 3}
            ]
        }
    )
    assert var_res.status_code == 201
    var_data = var_res.json()
    assert var_data["version_actual"] == 1
    version_id = var_data["versiones"][0]["id"]
    inhabitable_op_id = [op["id"] for op in var_data["versiones"][0]["opciones"] if op["codigo"] == "INHABITABLE"][0]

    # 4. Create an Aprendiz
    apr_res = await client.post(
        "/api/v1/aprendices",
        headers=headers,
        json={
            "tipo_documento": "CC",
            "numero_documento": "1098765432",
            "nombres": "Juan Carlos",
            "apellidos": "Pérez Gómez",
            "correo": "juan.perez@misena.edu.co",
            "celular": "3111111111"
        }
    )
    assert apr_res.status_code == 201
    aprendiz_id = apr_res.json()["id"]

    # 5. Submit response 1 (Inhabitable)
    resp1_res = await client.post(
        "/api/v1/respuestas",
        headers=headers,
        json={
            "aprendiz_id": aprendiz_id,
            "respuestas": [
                {
                    "variable_id": var_data["id"],
                    "variable_version_id": version_id,
                    "opcion_id": inhabitable_op_id
                }
            ]
        }
    )
    assert resp1_res.status_code == 201

    # 6. Verify estado actual
    status_res = await client.get(f"/api/v1/respuestas/aprendiz/{aprendiz_id}/estado-actual", headers=headers)
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["total_variables_medidas"] == 1
    assert status_data["nivel_afectacion_global"] == 3

    # 7. Submit response 2 (Evolution -> Normal). Immutability test: History length must be 2
    normal_op_id = [op["id"] for op in var_data["versiones"][0]["opciones"] if op["codigo"] == "NORMAL"][0]
    resp2_res = await client.post(
        "/api/v1/respuestas",
        headers=headers,
        json={
            "aprendiz_id": aprendiz_id,
            "respuestas": [
                {
                    "variable_id": var_data["id"],
                    "variable_version_id": version_id,
                    "opcion_id": normal_op_id
                }
            ]
        }
    )
    assert resp2_res.status_code == 201

    history_res = await client.get(f"/api/v1/respuestas/aprendiz/{aprendiz_id}/historico", headers=headers)
    assert history_res.status_code == 200
    assert len(history_res.json()) == 2  # Complete immutable history preserved!
