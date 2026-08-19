from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateResourceException, NotFoundException
from app.modules.needs.models import Necesidad
from app.modules.needs.schemas import NecesidadCreate


class NeedsService:
    @staticmethod
    async def list_necesidades(session: AsyncSession) -> List[Necesidad]:
        stmt = select(Necesidad).where(Necesidad.activa.is_(True))
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_necesidad(session: AsyncSession, nec_in: NecesidadCreate) -> Necesidad:
        stmt = select(Necesidad).where(Necesidad.codigo == nec_in.codigo)
        res = await session.execute(stmt)
        if res.scalar_one_or_none():
            raise DuplicateResourceException(f"Ya existe una necesidad con código '{nec_in.codigo}'")

        nec = Necesidad(**nec_in.model_dump())
        session.add(nec)
        await session.commit()
        await session.refresh(nec)
        return nec

    @staticmethod
    async def get_necesidad_by_id(session: AsyncSession, necesidad_id: int) -> Necesidad:
        stmt = select(Necesidad).where(Necesidad.id == necesidad_id)
        res = await session.execute(stmt)
        nec = res.scalar_one_or_none()
        if not nec:
            raise NotFoundException("Necesidad", necesidad_id)
        return nec
