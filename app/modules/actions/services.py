from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.actions.models import AccionCaso
from app.modules.actions.schemas import AccionCasoCreate, AccionCasoUpdate


class ActionsService:
    @staticmethod
    async def list_acciones_by_caso(session: AsyncSession, caso_id: int) -> List[AccionCaso]:
        stmt = select(AccionCaso).where(AccionCaso.caso_id == caso_id).order_by(AccionCaso.created_at.desc())
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_accion(session: AsyncSession, acc_in: AccionCasoCreate) -> AccionCaso:
        accion = AccionCaso(**acc_in.model_dump())
        session.add(accion)
        await session.commit()
        await session.refresh(accion)
        return accion

    @staticmethod
    async def update_accion(session: AsyncSession, accion_id: int, acc_in: AccionCasoUpdate) -> AccionCaso:
        stmt = select(AccionCaso).where(AccionCaso.id == accion_id)
        res = await session.execute(stmt)
        acc = res.scalar_one_or_none()
        if not acc:
            raise NotFoundException("Acción de Caso", accion_id)

        for field, value in acc_in.model_dump(exclude_unset=True).items():
            setattr(acc, field, value)

        await session.commit()
        await session.refresh(acc)
        return acc
