from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenException, NotFoundException, UnauthorizedException
from app.modules.academic.models import Ficha
from app.modules.apprentices.models import Aprendiz, Matricula
from app.modules.benefits.models import AprendizBeneficio, Beneficio
from app.modules.cases.models import Caso, CasoNecesidad
from app.modules.contracts.models import ContratoAprendizaje

from app.modules.portal.schemas import (
    PerfilAprendizUpdate, PortalBeneficioCreate, PortalContratoCreate, PortalContratoUpdate,
    PortalCasoCreate, PortalCasoUpdate
)

from app.modules.responses.models import Respuesta
from app.modules.responses.schemas import BatchRespuestaCreate
from app.modules.responses.services import ResponsesService
from app.modules.surveys.models import CorteEncuesta, Encuesta, EncuestaVariable
from app.modules.variables.models import OpcionVariable, Variable


class PortalService:
    @staticmethod
    async def get_perfil(session: AsyncSession, aprendiz_id: int) -> Aprendiz:
        stmt = (
            select(Aprendiz)
            .where(Aprendiz.id == aprendiz_id)
            .options(selectinload(Aprendiz.matriculas).selectinload(Matricula.ficha))
        )
        res = await session.execute(stmt)
        aprendiz = res.scalar_one_or_none()
        if not aprendiz:
            raise NotFoundException("Aprendiz", aprendiz_id)
        return aprendiz

    @staticmethod
    async def update_perfil(session: AsyncSession, aprendiz_id: int, perfil_in: PerfilAprendizUpdate) -> Aprendiz:
        aprendiz = await PortalService.get_perfil(session, aprendiz_id)
        
        update_data = perfil_in.model_dump(exclude_unset=True)
        # Bloquear explícitamente cualquier intento de alterar tipo_documento o numero_documento
        update_data.pop("tipo_documento", None)
        update_data.pop("numero_documento", None)

        for field, value in update_data.items():
            if value is not None:
                setattr(aprendiz, field, value)

        await session.commit()
        return await PortalService.get_perfil(session, aprendiz_id)

    @staticmethod
    async def get_beneficios(session: AsyncSession, aprendiz_id: int) -> List[AprendizBeneficio]:
        stmt = (
            select(AprendizBeneficio)
            .where(AprendizBeneficio.aprendiz_id == aprendiz_id)
            .options(selectinload(AprendizBeneficio.beneficio))
            .order_by(desc(AprendizBeneficio.created_at))
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def registrar_beneficio(session: AsyncSession, aprendiz_id: int, ben_in: PortalBeneficioCreate) -> AprendizBeneficio:
        # Verificar que el beneficio exista
        ben_stmt = select(Beneficio).where(Beneficio.id == ben_in.beneficio_id)
        ben_res = await session.execute(ben_stmt)
        beneficio = ben_res.scalar_one_or_none()
        if not beneficio:
            raise NotFoundException("Beneficio", ben_in.beneficio_id)

        nuevo_beneficio = AprendizBeneficio(
            aprendiz_id=aprendiz_id,
            beneficio_id=ben_in.beneficio_id,
            estado="ACTIVO",
            origen="AUTOREGISTRO_APRENDIZ",
            observaciones=ben_in.observaciones
        )
        session.add(nuevo_beneficio)
        await session.commit()

        # Cargar la relación beneficio de forma ansiosa para evitar MissingGreenlet en async
        stmt = (
            select(AprendizBeneficio)
            .where(AprendizBeneficio.id == nuevo_beneficio.id)
            .options(selectinload(AprendizBeneficio.beneficio))
        )
        res = await session.execute(stmt)
        return res.scalar_one()

    @staticmethod
    async def get_contratos(session: AsyncSession, aprendiz_id: int) -> List[ContratoAprendizaje]:
        stmt = (
            select(ContratoAprendizaje)
            .join(Matricula, ContratoAprendizaje.matricula_id == Matricula.id)
            .where(Matricula.aprendiz_id == aprendiz_id)
            .options(selectinload(ContratoAprendizaje.matricula))
            .order_by(desc(ContratoAprendizaje.created_at))
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def registrar_contrato(session: AsyncSession, aprendiz_id: int, contrato_in: PortalContratoCreate) -> ContratoAprendizaje:
        # Buscar la matrícula activa del aprendiz
        mat_stmt = select(Matricula).where(Matricula.aprendiz_id == aprendiz_id)
        mat_res = await session.execute(mat_stmt)
        matricula = mat_res.scalars().first()

        if not matricula:
            raise NotFoundException(f"No se encontró una matrícula activa para el aprendiz {aprendiz_id}")

        nuevo_contrato = ContratoAprendizaje(
            matricula_id=matricula.id,
            nombre_empresa=contrato_in.nombre_empresa,
            departamento=contrato_in.departamento,
            ciudad=contrato_in.ciudad,
            fecha_inicio_contrato=contrato_in.fecha_inicio_contrato,
            fecha_fin_contrato=contrato_in.fecha_fin_contrato,
            estado_contrato=contrato_in.estado_contrato,
            observaciones=contrato_in.observaciones
        )
        session.add(nuevo_contrato)
        await session.commit()

        # Cargar matrícula de forma ansiosa
        stmt = (
            select(ContratoAprendizaje)
            .where(ContratoAprendizaje.id == nuevo_contrato.id)
            .options(selectinload(ContratoAprendizaje.matricula))
        )
        res = await session.execute(stmt)
        return res.scalar_one()


    @staticmethod
    async def update_contrato(
        session: AsyncSession,
        aprendiz_id: int,
        contrato_id: int,
        contrato_in: PortalContratoUpdate
    ) -> ContratoAprendizaje:
        stmt = (
            select(ContratoAprendizaje)
            .join(Matricula, ContratoAprendizaje.matricula_id == Matricula.id)
            .where(ContratoAprendizaje.id == contrato_id, Matricula.aprendiz_id == aprendiz_id)
            .options(selectinload(ContratoAprendizaje.matricula))
        )
        res = await session.execute(stmt)
        contrato = res.scalar_one_or_none()

        if not contrato:
            raise NotFoundException("Contrato de Aprendizaje", contrato_id)

        update_data = contrato_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(contrato, field, value)

        await session.commit()
        await session.refresh(contrato)
        return contrato

    @staticmethod
    async def get_encuestas_pendientes(session: AsyncSession, aprendiz_id: int) -> List[dict]:
        from app.modules.variables.models import VariableVersion
        # Obtener encuestas en estado PUBLICADA o ACTIVA
        stmt = (
            select(Encuesta)
            .where(Encuesta.estado.in_(["PUBLICADA", "ACTIVA"]))
            .options(
                selectinload(Encuesta.variables_asociadas).selectinload(EncuestaVariable.variable).selectinload(Variable.versiones).selectinload(VariableVersion.opciones),
                selectinload(Encuesta.cortes)
            )
        )
        res = await session.execute(stmt)
        encuestas = list(res.scalars().all())

        resultado = []
        for enc in encuestas:
            preguntas = []
            for ev in sorted(enc.variables_asociadas, key=lambda x: x.orden):
                var = ev.variable
                if not var:
                    continue
                v_version = var.versiones[0] if var.versiones else None
                opciones = [
                    {
                        "id": op.id,
                        "texto_opcion": op.texto,
                        "valor_numerico": op.valor_numerico,
                        "nivel_afectacion": op.nivel_afectacion
                    }
                    for op in sorted(v_version.opciones if v_version else [], key=lambda o: o.orden)
                ]
                preguntas.append({
                    "variable_id": var.id,
                    "variable_version_id": v_version.id if v_version else None,
                    "variable_codigo": var.codigo,
                    "nombre": var.nombre,
                    "texto_pregunta": v_version.titulo_pregunta if v_version else (var.descripcion or var.nombre),
                    "tipo_respuesta": var.tipo_respuesta,
                    "opciones": opciones
                })

            from app.modules.responses.models import Respuesta
            from sqlalchemy import func
            resp_check = await session.execute(
                select(func.count(Respuesta.id)).where(
                    (Respuesta.aprendiz_id == aprendiz_id) &
                    (Respuesta.encuesta_id == enc.id)
                )
            )
            count_resp = resp_check.scalar_one_or_none() or 0

            corte_actual = enc.cortes[0] if enc.cortes else None
            resultado.append({
                "id": enc.id,
                "nombre": enc.titulo,
                "titulo": enc.titulo,
                "descripcion": enc.descripcion,
                "tipo": enc.tipo,
                "corte_id": corte_actual.id if corte_actual else None,
                "ya_respondida": count_resp > 0,
                "total_respuestas": count_resp,
                "preguntas": preguntas
            })

        return resultado

    @staticmethod
    async def get_casos(session: AsyncSession, aprendiz_id: int) -> List[Caso]:
        from app.modules.cases.models import Caso, CasoNecesidad
        from app.modules.actions.models import AccionCaso
        from app.modules.followups.models import SeguimientoCaso

        stmt = (
            select(Caso)
            .where(Caso.aprendiz_id == aprendiz_id)
            .options(
                selectinload(Caso.aprendiz).selectinload(Aprendiz.matriculas).selectinload(Matricula.ficha),
                selectinload(Caso.responsable),
                selectinload(Caso.necesidades_asociadas).selectinload(CasoNecesidad.necesidad),
                selectinload(Caso.acciones).selectinload(AccionCaso.responsable),
                selectinload(Caso.seguimientos).selectinload(SeguimientoCaso.usuario)
            )
            .order_by(desc(Caso.fecha_creacion))
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_caso_by_id(session: AsyncSession, aprendiz_id: int, caso_id: int) -> Caso:
        from app.modules.cases.models import Caso, CasoNecesidad
        from app.modules.actions.models import AccionCaso
        from app.modules.followups.models import SeguimientoCaso

        stmt = (
            select(Caso)
            .where(Caso.id == caso_id, Caso.aprendiz_id == aprendiz_id)
            .options(
                selectinload(Caso.aprendiz).selectinload(Aprendiz.matriculas).selectinload(Matricula.ficha),
                selectinload(Caso.responsable),
                selectinload(Caso.necesidades_asociadas).selectinload(CasoNecesidad.necesidad),
                selectinload(Caso.acciones).selectinload(AccionCaso.responsable),
                selectinload(Caso.seguimientos).selectinload(SeguimientoCaso.usuario)
            )
        )

        res = await session.execute(stmt)
        caso = res.scalar_one_or_none()
        if not caso:
            raise NotFoundException("Caso", caso_id)
        return caso

    @staticmethod
    async def registrar_caso(session: AsyncSession, aprendiz_id: int, caso_in: PortalCasoCreate) -> Caso:
        from app.modules.cases.models import Caso, CasoNecesidad
        caso = Caso(
            aprendiz_id=aprendiz_id,
            tipo=caso_in.tipo,
            prioridad=caso_in.prioridad or "MEDIA",
            estado="NUEVO",
            origen="MANUAL_APRENDIZ"
        )
        session.add(caso)
        await session.flush()

        for nec_id in (caso_in.necesidades_ids or []):
            cn = CasoNecesidad(caso_id=caso.id, necesidad_id=nec_id)
            session.add(cn)

        await session.commit()
        return await PortalService.get_caso_by_id(session, aprendiz_id, caso.id)

    @staticmethod
    async def update_caso(
        session: AsyncSession,
        aprendiz_id: int,
        caso_id: int,
        caso_in: PortalCasoUpdate
    ) -> Caso:
        caso = await PortalService.get_caso_by_id(session, aprendiz_id, caso_id)
        update_data = caso_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(caso, field, value)
        await session.commit()
        return await PortalService.get_caso_by_id(session, aprendiz_id, caso_id)

    @staticmethod
    async def agregar_necesidades_caso(
        session: AsyncSession,
        aprendiz_id: int,
        caso_id: int,
        necesidades_ids: List[int]
    ) -> Caso:
        from app.modules.cases.models import CasoNecesidad
        caso = await PortalService.get_caso_by_id(session, aprendiz_id, caso_id)
        
        existentes_ids = {cn.necesidad_id for cn in caso.necesidades_asociadas}
        for nec_id in necesidades_ids:
            if nec_id not in existentes_ids:
                cn = CasoNecesidad(caso_id=caso.id, necesidad_id=nec_id)
                session.add(cn)

        await session.commit()
        session.expire_all()
        return await PortalService.get_caso_by_id(session, aprendiz_id, caso_id)



