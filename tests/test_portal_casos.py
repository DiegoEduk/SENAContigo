import uuid
import pytest
from datetime import date
from app.modules.academic.models import Ficha, ProgramaFormacion
from app.modules.apprentices.models import Aprendiz, Matricula
from app.modules.needs.models import TipoCaso


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

    # Crear tipos de caso en el catálogo
    tc1 = TipoCaso(codigo=f"TC1_{uid}", nombre="Apoyo Alimentario Test", descripcion="Descripción Tipo 1", activa=True)
    tc2 = TipoCaso(codigo=f"TC2_{uid}", nombre="Conectividad Test", descripcion="Descripción Tipo 2", activa=True)
    session.add(tc1)
    session.add(tc2)

    await session.commit()
    tc1_id = tc1.id
    tc2_id = tc2.id

    ac = client


    # 1. Login del aprendiz
    resp_login = await ac.post("/api/v1/auth/aprendiz-login", json={
        "numero_documento": doc_num,
        "ficha_caracterizacion": ficha_code
    })
    assert resp_login.status_code == 200
    token = resp_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. GET /portal/tipos-caso (Consultar catálogo de tipos de caso)
    resp_tipos = await ac.get("/api/v1/portal/tipos-caso", headers=headers)
    assert resp_tipos.status_code == 200
    assert len(resp_tipos.json()) >= 2

    # 3. GET /portal/casos (Inicialmente 0 casos)
    resp_get_casos = await ac.get("/api/v1/portal/casos", headers=headers)
    assert resp_get_casos.status_code == 200
    assert len(resp_get_casos.json()) == 0

    # 4. POST /portal/casos (Crear nuevo caso con tipo_caso_id y descripcion)
    resp_create_caso = await ac.post("/api/v1/portal/casos", headers=headers, json={
        "tipo_caso_id": tc1_id,
        "descripcion": "Requiero apoyo alimentario urgente por situación económica.",
        "prioridad": "ALTA"
    })
    assert resp_create_caso.status_code == 201


    caso_data = resp_create_caso.json()
    caso_id = caso_data["id"]
    assert caso_data["tipo_caso_id"] == tc1_id
    assert caso_data["descripcion"] == "Requiero apoyo alimentario urgente por situación económica."
    assert caso_data["prioridad"] == "ALTA"
    assert caso_data["estado"] == "NUEVO"

    # 5. GET /portal/casos/{caso_id} (Obtener detalle)
    resp_detail = await ac.get(f"/api/v1/portal/casos/{caso_id}", headers=headers)
    assert resp_detail.status_code == 200
    detail_data = resp_detail.json()
    assert detail_data["id"] == caso_id
    assert detail_data["tipo_caso_id"] == tc1_id

    # 6. PUT /portal/casos/{caso_id} (Editar caso cambiando tipo_caso_id y prioridad)
    resp_update = await ac.put(f"/api/v1/portal/casos/{caso_id}", headers=headers, json={
        "tipo_caso_id": tc2_id,
        "descripcion": "Actualizando mi solicitud a equipo computacional.",
        "prioridad": "CRITICA"
    })
    assert resp_update.status_code == 200
    updated_data = resp_update.json()
    assert updated_data["tipo_caso_id"] == tc2_id
    assert updated_data["prioridad"] == "CRITICA"


    # 7. GET /portal/casos (Verificar lista actualizada)
    resp_get_final = await ac.get("/api/v1/portal/casos", headers=headers)
    assert resp_get_final.status_code == 200
    assert len(resp_get_final.json()) == 1

