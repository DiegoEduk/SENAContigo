from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateResourceException, NotFoundException
from app.modules.needs.models import TipoCaso
from app.modules.needs.schemas import TipoCasoCreate


class CaseTypesService:
    @staticmethod
    async def list_tipos_caso(session: AsyncSession) -> List[TipoCaso]:
        stmt = select(TipoCaso).where(TipoCaso.activa.is_(True))
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_tipo_caso(session: AsyncSession, tc_in: TipoCasoCreate) -> TipoCaso:
        stmt = select(TipoCaso).where(TipoCaso.codigo == tc_in.codigo)
        res = await session.execute(stmt)
        if res.scalar_one_or_none():
            raise DuplicateResourceException(f"Ya existe un tipo de caso con código '{tc_in.codigo}'")

        tc = TipoCaso(**tc_in.model_dump())
        session.add(tc)
        await session.commit()
        await session.refresh(tc)
        return tc

    @staticmethod
    async def get_tipo_caso_by_id(session: AsyncSession, tipo_caso_id: int) -> TipoCaso:
        stmt = select(TipoCaso).where(TipoCaso.id == tipo_caso_id)
        res = await session.execute(stmt)
        tc = res.scalar_one_or_none()
        if not tc:
            raise NotFoundException("Tipo de Caso", tipo_caso_id)
        return tc

    # Alias para retrocompatibilidad
    list_necesidades = list_tipos_caso
    create_necesidad = create_tipo_caso
    get_necesidad_by_id = get_tipo_caso_by_id


NeedsService = CaseTypesService

