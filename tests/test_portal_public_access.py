import pytest
from datetime import date
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import AsyncSessionLocal
from app.modules.apprentices.models import Aprendiz, Matricula
from app.modules.academic.models import Ficha, ProgramaFormacion
from app.modules.benefits.models import Beneficio
from app.modules.surveys.models import Encuesta, CorteEncuesta


import uuid

@pytest.mark.asyncio
async def test_portal_public_login_and_flow():
    uid = uuid.uuid4().hex[:6]
    prog_code = f"PROG_{uid}"
    ficha_code = f"FICHA_{uid}"
    doc_num = f"DOC_{uid}"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        async with AsyncSessionLocal() as session:
            # Create test learner & ficha con códigos únicos dinámicos
            prog = ProgramaFormacion(codigo_programa=prog_code, version="1", nombre="Programa Test Portal", nivel_formacion="Tecnólogo")
            session.add(prog)
            await session.flush()

            ficha = Ficha(
                ficha_caracterizacion=ficha_code,
                fecha_inicial=date(2026, 1, 1),
                fecha_final=date(2026, 12, 31),
                estado_ficha="En ejecución",
                centro_id="9210",
                programa_codigo=prog_code,
                programa_version="1",
                departamento="Cundinamarca",
                ciudad="Bogotá"
            )

            session.add(ficha)

            aprendiz = Aprendiz(
                tipo_documento="CC",
                numero_documento=doc_num,
                nombres="Carlos",
                apellidos="Pérez",
                correo=f"carlos_{uid}@test.sena.edu.co",
                celular="3001112233",
                direccion_vivienda="Calle 1 # 2-3",
                ciudad="Bogotá",
                departamento="Cundinamarca",
                centro_id="9210",
                activo=True
            )
            session.add(aprendiz)
            await session.flush()

            mat = Matricula(aprendiz_id=aprendiz.id, ficha_id=ficha_code, estado_matricula="En formación")
            session.add(mat)

            beneficio = Beneficio(codigo=f"BEN_{uid}", nombre="Auxilio Alimenticio Test Portal", tipo_beneficio="APOYO_FINANCIERO", activo=True)
            session.add(beneficio)

            await session.commit()

        # 1. Test Login Fallido (Documento inexistente)
        resp_fail = await ac.post("/api/v1/auth/aprendiz-login", json={
            "numero_documento": "0000000000",
            "ficha_caracterizacion": ficha_code
        })
        assert resp_fail.status_code == 401

        # 2. Test Login Exitoso (Documento + Ficha)
        resp_login = await ac.post("/api/v1/auth/aprendiz-login", json={
            "numero_documento": doc_num,
            "ficha_caracterizacion": ficha_code
        })
        assert resp_login.status_code == 200
        data_login = resp_login.json()
        assert "access_token" in data_login
        assert data_login["aprendiz"]["numero_documento"] == doc_num
        assert data_login["ficha_id"] == ficha_code



        token = data_login["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Test Consultar Perfil
        resp_prof = await ac.get("/api/v1/portal/perfil", headers=headers)
        assert resp_prof.status_code == 200
        assert resp_prof.json()["nombres"] == "Carlos"

        # 4. Test Actualizar Perfil (Verificar inmutabilidad de tipo y numero de documento)
        resp_up_prof = await ac.put("/api/v1/portal/perfil", headers=headers, json={
            "nombres": "Carlos Alberto",
            "celular": "3119998877",
            "tipo_documento": "CE",
            "numero_documento": "9999999999"
        })
        assert resp_up_prof.status_code == 200
        prof_data = resp_up_prof.json()
        assert prof_data["nombres"] == "Carlos Alberto"
        assert prof_data["celular"] == "3119998877"
        # Verificar que tipo y numero de documento NO cambiaron
        assert prof_data["tipo_documento"] == "CC"
        assert prof_data["numero_documento"] == doc_num



        # 5. Test Registrar y Consultar Contrato de Aprendizaje
        resp_add_cont = await ac.post("/api/v1/portal/contratos", headers=headers, json={
            "nombre_empresa": "EMPRESA PRUEBA S.A.S.",
            "departamento": "Cundinamarca",
            "ciudad": "Bogotá",
            "fecha_inicio_contrato": "2026-02-01",
            "estado_contrato": "EN PATROCINIO",
            "observaciones": "Etapa lectiva patrocinada"
        })
        assert resp_add_cont.status_code == 201
        cont_data = resp_add_cont.json()
        assert cont_data["nombre_empresa"] == "EMPRESA PRUEBA S.A.S."

        resp_get_cont = await ac.get("/api/v1/portal/contratos", headers=headers)
        assert resp_get_cont.status_code == 200
        assert len(resp_get_cont.json()) == 1

        # 6. Test Registrar y Consultar Beneficios
        resp_get_ben = await ac.get("/api/v1/portal/beneficios", headers=headers)
        assert resp_get_ben.status_code == 200

        resp_add_ben = await ac.post("/api/v1/portal/beneficios", headers=headers, json={
            "beneficio_id": beneficio.id,
            "observaciones": "Solicitado por aprendiz"
        })
        assert resp_add_ben.status_code == 201

        # 7. Test Encuestas Pendientes
        resp_enc = await ac.get("/api/v1/portal/encuestas-pendientes", headers=headers)
        assert resp_enc.status_code == 200
