from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.modules.cases.models import Caso, CasoNecesidad
from app.modules.cases.schemas import CasoCreate, CasoUpdate


class CasesService:
    @staticmethod
    async def list_casos(
        session: AsyncSession,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        responsable_id: Optional[int] = None,
        aprendiz_id: Optional[int] = None
    ) -> List[Caso]:
        stmt = (
            select(Caso)
            .options(
                selectinload(Caso.aprendiz),
                selectinload(Caso.responsable),
                selectinload(Caso.necesidades_asociadas).selectinload(CasoNecesidad.necesidad)
            )
            .order_by(Caso.fecha_creacion.desc())
        )
        if estado:
            stmt = stmt.where(Caso.estado == estado)
        if prioridad:
            stmt = stmt.where(Caso.prioridad == prioridad)
        if responsable_id:
            stmt = stmt.where(Caso.responsable_id == responsable_id)
        if aprendiz_id:
            stmt = stmt.where(Caso.aprendiz_id == aprendiz_id)

        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_caso_by_id(session: AsyncSession, caso_id: int) -> Caso:
        stmt = (
            select(Caso)
            .where(Caso.id == caso_id)
            .options(
                selectinload(Caso.aprendiz),
                selectinload(Caso.responsable),
                selectinload(Caso.necesidades_asociadas).selectinload(CasoNecesidad.necesidad),
                selectinload(Caso.acciones),
                selectinload(Caso.seguimientos)
            )
        )
        res = await session.execute(stmt)
        caso = res.scalar_one_or_none()
        if not caso:
            raise NotFoundException("Caso", caso_id)
        return caso

    @staticmethod
    async def create_caso(session: AsyncSession, caso_in: CasoCreate) -> Caso:
        caso = Caso(
            aprendiz_id=caso_in.aprendiz_id,
            tipo=caso_in.tipo,
            prioridad=caso_in.prioridad,
            estado=caso_in.estado,
            responsable_id=caso_in.responsable_id,
            origen=caso_in.origen
        )
        session.add(caso)
        await session.flush()

        for nec_id in caso_in.necesidades_ids:
            cn = CasoNecesidad(caso_id=caso.id, necesidad_id=nec_id)
            session.add(cn)

        await session.commit()
        return await CasesService.get_caso_by_id(session, caso.id)

    @staticmethod
    async def update_caso(session: AsyncSession, caso_id: int, caso_in: CasoUpdate) -> Caso:
        caso = await CasesService.get_caso_by_id(session, caso_id)

        for field, value in caso_in.model_dump(exclude_unset=True).items():
            setattr(caso, field, value)

        if caso.estado in ["RESUELTO", "CERRADO", "CANCELADO"] and not caso.fecha_cierre:
            caso.fecha_cierre = datetime.now(timezone.utc)

        await session.commit()
        return await CasesService.get_caso_by_id(session, caso_id)
