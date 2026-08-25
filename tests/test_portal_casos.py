import uuid
import pytest
from datetime import date
from app.modules.academic.models import Ficha, ProgramaFormacion
from app.modules.apprentices.models import Aprendiz, Matricula
from app.modules.needs.models import Necesidad


@pytest.mark.asyncio
async def test_portal_casos_flow(client, db_session):
    uid = uuid.uuid4().hex[:6]
    prog_code = f"PROG_CASOS_{uid}"
    ficha_code = f"FICHA_CASOS_{uid}"
    doc_num = f"DOC_CASOS_{uid}"

    session = db_session

    prog = ProgramaFormacion(codigo_programa=prog_code, version="1", nombre="Programa Test Casos", nivel_formacion="Tecnólogo")
    session.add(prog)
    await session.flush()

    ficha = Ficha(
        ficha_caracterizacion=ficha_code,
        fecha_inicial=date(2026, 1, 1),
        fecha_final=date(2026, 12, 31),
        estado_ficha="En ejecución",
        centro_id="9201",
        programa_codigo=prog_code,
        programa_version="1",
        departamento="Cundinamarca",
        ciudad="Bogotá"
    )
    session.add(ficha)

    aprendiz = Aprendiz(
        tipo_documento="CC",
        numero_documento=doc_num,
        nombres="Juan",
        apellidos="Valdés",
        correo=f"juan_{uid}@test.sena.edu.co",
        celular="3009998877",
        ciudad="Bogotá",
        departamento="Cundinamarca",
        activo=True
    )
    session.add(aprendiz)
    await session.flush()

    mat = Matricula(aprendiz_id=aprendiz.id, ficha_id=ficha_code, estado_matricula="En formación")
    session.add(mat)

    # Crear necesidades en el catálogo
    nec1 = Necesidad(codigo=f"NEC1_{uid}", nombre="Apoyo Alimentario Test", descripcion="Descripción Nec 1", activa=True)
    nec2 = Necesidad(codigo=f"NEC2_{uid}", nombre="Conectividad Test", descripcion="Descripción Nec 2", activa=True)
    session.add(nec1)
    session.add(nec2)

    await session.commit()

    ac = client

    # 1. Login del aprendiz
    resp_login = await ac.post("/api/v1/auth/aprendiz-login", json={
        "numero_documento": doc_num,
        "ficha_caracterizacion": ficha_code
    })
    assert resp_login.status_code == 200
    token = resp_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. GET /portal/casos (Inicialmente 0 casos)
    resp_get_casos = await ac.get("/api/v1/portal/casos", headers=headers)
    assert resp_get_casos.status_code == 200
    assert len(resp_get_casos.json()) == 0

    # 3. POST /portal/casos (Crear nuevo caso con necesidad 1)
    resp_create_caso = await ac.post("/api/v1/portal/casos", headers=headers, json={
        "tipo": "RIESGO CONTINUIDAD",
        "prioridad": "ALTA",
        "necesidades_ids": [nec1.id]
    })
    assert resp_create_caso.status_code == 201
    caso_data = resp_create_caso.json()
    caso_id = caso_data["id"]
    assert caso_data["tipo"] == "RIESGO CONTINUIDAD"
    assert caso_data["prioridad"] == "ALTA"
    assert caso_data["estado"] == "NUEVO"
    assert len(caso_data["necesidades_asociadas"]) == 1
    assert caso_data["necesidades_asociadas"][0]["necesidad_id"] == nec1.id

    # 4. GET /portal/casos/{caso_id} (Obtener detalle)
    resp_detail = await ac.get(f"/api/v1/portal/casos/{caso_id}", headers=headers)
    assert resp_detail.status_code == 200
    detail_data = resp_detail.json()
    assert detail_data["id"] == caso_id
    assert detail_data["tipo"] == "RIESGO CONTINUIDAD"

    # 5. PUT /portal/casos/{caso_id} (Editar caso)
    resp_update = await ac.put(f"/api/v1/portal/casos/{caso_id}", headers=headers, json={
        "tipo": "SITUACIÓN HABITACIONAL Y VIVIENDA",
        "prioridad": "CRITICA"
    })
    assert resp_update.status_code == 200
    updated_data = resp_update.json()
    assert updated_data["tipo"] == "SITUACIÓN HABITACIONAL Y VIVIENDA"
    assert updated_data["prioridad"] == "CRITICA"

    # 6. POST /portal/casos/{caso_id}/necesidades (Agregar necesidad 2)
    resp_add_nec = await ac.post(f"/api/v1/portal/casos/{caso_id}/necesidades", headers=headers, json={
        "necesidades_ids": [nec2.id]
    })
    assert resp_add_nec.status_code == 200
    nec_data = resp_add_nec.json()
    assert len(nec_data["necesidades_asociadas"]) == 2

    # 7. GET /portal/casos (Verificar lista actualizada)
    resp_get_final = await ac.get("/api/v1/portal/casos", headers=headers)
    assert resp_get_final.status_code == 200
    assert len(resp_get_final.json()) == 1
