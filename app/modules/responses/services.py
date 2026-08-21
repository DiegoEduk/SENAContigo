from typing import List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.modules.apprentices.models import Aprendiz
from app.modules.responses.models import Respuesta
from app.modules.responses.schemas import BatchRespuestaCreate, EstadoActualAprendiz, EstadoActualAprendizItem, RespuestaRead
from app.modules.variables.models import OpcionVariable, Variable


class ResponsesService:
    @staticmethod
    async def record_batch_responses(
        session: AsyncSession,
        batch_in: BatchRespuestaCreate,
        user_id: Optional[int] = None,
        ip_origen: Optional[str] = None
    ) -> List[Respuesta]:
        # Validate aprendiz exists
        aprendiz_stmt = select(Aprendiz).where(Aprendiz.id == batch_in.aprendiz_id)
        aprendiz_res = await session.execute(aprendiz_stmt)
        if not aprendiz_res.scalar_one_or_none():
            raise NotFoundException("Aprendiz", batch_in.aprendiz_id)

        created_responses = []
        for item in batch_in.respuestas:
            version_id = item.variable_version_id
            if not version_id:
                from app.modules.variables.models import VariableVersion
                ver_res = await session.execute(
                    select(VariableVersion.id)
                    .where(VariableVersion.variable_id == item.variable_id)
                    .order_by(desc(VariableVersion.numero_version))
                )
                version_id = ver_res.scalar_one_or_none() or 1

            # Immutability Guarantee: Every submission inserts a NEW record
            resp = Respuesta(
                aprendiz_id=batch_in.aprendiz_id,
                variable_id=item.variable_id,
                variable_version_id=version_id,
                opcion_id=item.opcion_id,
                encuesta_id=batch_in.encuesta_id,
                corte_id=batch_in.corte_id,
                valor_texto=item.valor_texto,
                valor_numero=str(item.valor_numero) if item.valor_numero is not None else None,
                registrado_por_usuario_id=user_id,
                origen=batch_in.origen,
                ip_origen=ip_origen
            )
            session.add(resp)
            created_responses.append(resp)

        await session.commit()

        # Trigger Rules Engine asynchronously or in sequence to detect needs & create cases automatically
        try:
            from app.modules.rules.services import RulesService
            await RulesService.evaluate_rules_for_aprendiz(session, batch_in.aprendiz_id)
        except Exception:
            pass  # Do not block response registration if rules engine evaluation encounters non-fatal issue

        return created_responses

    @staticmethod
    async def get_aprendiz_history(session: AsyncSession, aprendiz_id: int) -> List[Respuesta]:
        stmt = (
            select(Respuesta)
            .where(Respuesta.aprendiz_id == aprendiz_id)
            .order_by(desc(Respuesta.fecha_respuesta))
            .options(
                selectinload(Respuesta.variable),
                selectinload(Respuesta.version),
                selectinload(Respuesta.opcion)
            )
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_estado_actual_aprendiz(session: AsyncSession, aprendiz_id: int) -> EstadoActualAprendiz:
        # Get latest response per variable for this aprendiz
        subq = (
            select(
                Respuesta.variable_id,
                func.max(Respuesta.id).label("max_id")
            )
            .where(Respuesta.aprendiz_id == aprendiz_id)
            .group_by(Respuesta.variable_id)
            .subquery()
        )

        stmt = (
            select(Respuesta)
            .join(subq, Respuesta.id == subq.c.max_id)
            .options(
                selectinload(Respuesta.variable).selectinload(Variable.categoria),
                selectinload(Respuesta.opcion)
            )
        )
        res = await session.execute(stmt)
        latest_responses = list(res.scalars().all())

        items = []
        max_nivel = 0
        total_score = 0.0

        for r in latest_responses:
            op_text = r.opcion.texto if r.opcion else None
            nivel = r.opcion.nivel_afectacion if r.opcion else 0
            if nivel > max_nivel:
                max_nivel = nivel
            total_score += nivel

            items.append(
                EstadoActualAprendizItem(
                    variable_id=r.variable_id,
                    variable_nombre=r.variable.nombre if r.variable else "Variable",
                    categoria_nombre=r.variable.categoria.nombre if r.variable and r.variable.categoria else "General",
                    ultima_medicion_fecha=r.fecha_respuesta,
                    opcion_texto=op_text,
                    nivel_afectacion=nivel,
                    valor_texto=r.valor_texto,
                    valor_numero=float(r.valor_numero) if r.valor_numero else None
                )
            )

        return EstadoActualAprendiz(
            aprendiz_id=aprendiz_id,
            total_variables_medidas=len(latest_responses),
            nivel_afectacion_global=max_nivel,
            indicador_afectacion_score=round(total_score, 2),
            estado_variables=items
        )
