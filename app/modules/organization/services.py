from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import DuplicateResourceException, NotFoundException
from app.modules.organization.models import CentroFormacion, Regional
from app.modules.organization.schemas import CentroFormacionCreate, CentroFormacionUpdate, RegionalCreate, RegionalUpdate


class OrganizationService:
    # Regionales
    @staticmethod
    async def list_regionales(session: AsyncSession) -> List[Regional]:
        stmt = select(Regional).options(selectinload(Regional.centros))
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_regional_by_id(session: AsyncSession, codigo_regional: str) -> Regional:
        stmt = select(Regional).where(Regional.codigo_regional == codigo_regional).options(selectinload(Regional.centros))
        res = await session.execute(stmt)
        reg = res.scalar_one_or_none()
        if not reg:
            raise NotFoundException("Regional", codigo_regional)
        return reg

    @staticmethod
    async def create_regional(session: AsyncSession, reg_in: RegionalCreate) -> Regional:
        stmt = select(Regional).where(Regional.codigo_regional == reg_in.codigo_regional)
        res = await session.execute(stmt)
        if res.scalar_one_or_none():
            raise DuplicateResourceException(f"Ya existe una regional con código '{reg_in.codigo_regional}'")

        reg = Regional(**reg_in.model_dump())
        session.add(reg)
        await session.commit()
        await session.refresh(reg)
        return await OrganizationService.get_regional_by_id(session, reg.codigo_regional)

    @staticmethod
    async def update_regional(session: AsyncSession, codigo_regional: str, reg_in: RegionalUpdate) -> Regional:
        reg = await OrganizationService.get_regional_by_id(session, codigo_regional)
        for field, value in reg_in.model_dump(exclude_unset=True).items():
            setattr(reg, field, value)
        await session.commit()
        await session.refresh(reg)
        return await OrganizationService.get_regional_by_id(session, codigo_regional)

    # Centros
    @staticmethod
    async def list_centros(session: AsyncSession, regional_id: Optional[str] = None) -> List[CentroFormacion]:
        stmt = select(CentroFormacion)
        if regional_id:
            stmt = stmt.where(CentroFormacion.regional_id == regional_id)
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_centro_by_id(session: AsyncSession, codigo_centro: str) -> CentroFormacion:
        stmt = select(CentroFormacion).where(CentroFormacion.codigo_centro == codigo_centro)
        res = await session.execute(stmt)
        centro = res.scalar_one_or_none()
        if not centro:
            raise NotFoundException("Centro de Formación", codigo_centro)
        return centro

    @staticmethod
    async def create_centro(session: AsyncSession, centro_in: CentroFormacionCreate) -> CentroFormacion:
        stmt = select(CentroFormacion).where(CentroFormacion.codigo_centro == centro_in.codigo_centro)
        res = await session.execute(stmt)
        if res.scalar_one_or_none():
            raise DuplicateResourceException(f"Ya existe un centro con código '{centro_in.codigo_centro}'")

        centro = CentroFormacion(**centro_in.model_dump())
        session.add(centro)
        await session.commit()
        await session.refresh(centro)
        return centro

    @staticmethod
    async def update_centro(session: AsyncSession, codigo_centro: str, centro_in: CentroFormacionUpdate) -> CentroFormacion:
        centro = await OrganizationService.get_centro_by_id(session, codigo_centro)
        for field, value in centro_in.model_dump(exclude_unset=True).items():
            setattr(centro, field, value)
        await session.commit()
        await session.refresh(centro)
        return centro
