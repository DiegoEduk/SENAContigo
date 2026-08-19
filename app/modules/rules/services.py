from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.modules.rules.models import Regla, ReglaAccion, ReglaCondicion
from app.modules.rules.schemas import ReglaCreate


class RulesService:
    @staticmethod
    async def list_reglas(session: AsyncSession) -> List[Regla]:
        stmt = (
            select(Regla)
            .options(
                selectinload(Regla.condiciones),
                selectinload(Regla.acciones)
            )
            .order_by(Regla.prioridad)
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_regla(session: AsyncSession, regla_in: ReglaCreate) -> Regla:
        regla = Regla(
            nombre=regla_in.nombre,
            descripcion=regla_in.descripcion,
            activa=regla_in.activa,
            prioridad=regla_in.prioridad
        )
        session.add(regla)
        await session.flush()

        for cond in regla_in.condiciones:
            c = ReglaCondicion(
                regla_id=regla.id,
                variable_id=cond.variable_id,
                opcion_id=cond.opcion_id,
                operador=cond.operador,
                valor_comparar=cond.valor_comparar
            )
            session.add(c)

        for acc in regla_in.acciones:
            a = ReglaAccion(
                regla_id=regla.id,
                tipo_accion=acc.tipo_accion,
                necesidad_id=acc.necesidad_id,
                prioridad_caso=acc.prioridad_caso,
                titulo_caso=acc.titulo_caso,
                mensaje_notificacion=acc.mensaje_notificacion
            )
            session.add(a)

        await session.commit()
        return await RulesService.get_regla_by_id(session, regla.id)

    @staticmethod
    async def get_regla_by_id(session: AsyncSession, regla_id: int) -> Regla:
        stmt = (
            select(Regla)
            .where(Regla.id == regla_id)
            .options(
                selectinload(Regla.condiciones),
                selectinload(Regla.acciones)
            )
        )
        res = await session.execute(stmt)
        regla = res.scalar_one_or_none()
        if not regla:
            raise NotFoundException("Regla", regla_id)
        return regla

    @staticmethod
    async def evaluate_rules_for_aprendiz(session: AsyncSession, aprendiz_id: int):
        """Evaluate active rules for an aprendiz based on their latest responses and auto-create Cases/Needs."""
        from app.modules.responses.models import Respuesta
        from app.modules.cases.models import Caso, CasoNecesidad
        from app.modules.notifications.models import Notificacion

        # Get active rules
        rules = await RulesService.list_reglas(session)
        active_rules = [r for r in rules if r.activa]

        if not active_rules:
            return

        for r in active_rules:
            rule_matched = True
            for cond in r.condiciones:
                # Find latest response of aprendiz for this variable
                stmt = (
                    select(Respuesta)
                    .where(
                        (Respuesta.aprendiz_id == aprendiz_id) &
                        (Respuesta.variable_id == cond.variable_id)
                    )
                    .order_by(Respuesta.fecha_respuesta.desc())
                    .limit(1)
                )
                res = await session.execute(stmt)
                latest_resp = res.scalar_one_or_none()

                if not latest_resp:
                    rule_matched = False
                    break

                if cond.operador == "EQUALS":
                    if cond.opcion_id and latest_resp.opcion_id != cond.opcion_id:
                        rule_matched = False
                        break

            if rule_matched and r.acciones:
                for acc in r.acciones:
                    if acc.tipo_accion in ["CREAR_CASO", "CREAR_NECESIDAD"]:
                        titulo = acc.titulo_caso or f"Caso generado automáticamente por regla: {r.nombre}"
                        # Check existing open case
                        existing_case = await session.execute(
                            select(Caso).where(
                                (Caso.aprendiz_id == aprendiz_id) &
                                (Caso.tipo == titulo) &
                                (Caso.estado.in_(["NUEVO", "ASIGNADO", "EN_ATENCION"]))
                            )
                        )
                        if not existing_case.scalar_one_or_none():
                            caso = Caso(
                                aprendiz_id=aprendiz_id,
                                tipo=titulo,
                                prioridad=acc.prioridad_caso or "CRITICA",
                                estado="NUEVO",
                                origen="MOTOR_DE_REGLAS"
                            )
                            session.add(caso)
                            await session.flush()

                            if acc.necesidad_id:
                                cn = CasoNecesidad(caso_id=caso.id, necesidad_id=acc.necesidad_id)
                                session.add(cn)

                    elif acc.tipo_accion == "CREAR_NOTIFICACION":
                        notif = Notificacion(
                            aprendiz_id=aprendiz_id,
                            titulo=r.nombre,
                            mensaje=acc.mensaje_notificacion or f"Alerta activada por regla {r.nombre}",
                            tipo="ALERTA"
                        )
                        session.add(notif)

        await session.commit()
