from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import DuplicateResourceException, NotFoundException
from app.modules.academic.models import Ficha, ProgramaFormacion
from app.modules.academic.schemas import FichaCreate, FichaUpdate, ProgramaFormacionCreate, ProgramaFormacionUpdate


class AcademicService:
    # Programas
    @staticmethod
    async def list_programas(session: AsyncSession) -> List[ProgramaFormacion]:
        stmt = select(ProgramaFormacion)
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_programa_by_id(session: AsyncSession, codigo_programa: str, version: str = "1") -> ProgramaFormacion:
        stmt = select(ProgramaFormacion).where(
            (ProgramaFormacion.codigo_programa == codigo_programa) &
            (ProgramaFormacion.version == version)
        )
        res = await session.execute(stmt)
        prog = res.scalar_one_or_none()
        if not prog:
            raise NotFoundException("Programa de Formación", f"{codigo_programa} v{version}")
        return prog

    @staticmethod
    async def create_programa(session: AsyncSession, prog_in: ProgramaFormacionCreate) -> ProgramaFormacion:
        stmt = select(ProgramaFormacion).where(
            (ProgramaFormacion.codigo_programa == prog_in.codigo_programa) &
            (ProgramaFormacion.version == prog_in.version)
        )
        res = await session.execute(stmt)
        if res.scalar_one_or_none():
            raise DuplicateResourceException(f"Ya existe el programa '{prog_in.codigo_programa}' versión '{prog_in.version}'")

        prog = ProgramaFormacion(**prog_in.model_dump())
        session.add(prog)
        await session.commit()
        await session.refresh(prog)
        return prog

    @staticmethod
    async def update_programa(session: AsyncSession, codigo_programa: str, version: str, prog_in: ProgramaFormacionUpdate) -> ProgramaFormacion:
        prog = await AcademicService.get_programa_by_id(session, codigo_programa, version)
        for field, value in prog_in.model_dump(exclude_unset=True).items():
            setattr(prog, field, value)
        await session.commit()
        await session.refresh(prog)
        return prog

    # Fichas
    @staticmethod
    async def list_fichas(
        session: AsyncSession,
        centro_id: Optional[str] = None,
        programa_codigo: Optional[str] = None
    ) -> List[Ficha]:
        stmt = select(Ficha).options(selectinload(Ficha.programa))
        if centro_id:
            stmt = stmt.where(Ficha.centro_id == centro_id)
        if programa_codigo:
            stmt = stmt.where(Ficha.programa_codigo == programa_codigo)
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_ficha_by_id(session: AsyncSession, ficha_caracterizacion: str) -> Ficha:
        stmt = select(Ficha).where(Ficha.ficha_caracterizacion == ficha_caracterizacion).options(selectinload(Ficha.programa))
        res = await session.execute(stmt)
        ficha = res.scalar_one_or_none()
        if not ficha:
            raise NotFoundException("Ficha", ficha_caracterizacion)
        return ficha

    @staticmethod
    async def create_ficha(session: AsyncSession, ficha_in: FichaCreate) -> Ficha:
        stmt = select(Ficha).where(Ficha.ficha_caracterizacion == ficha_in.ficha_caracterizacion)
        res = await session.execute(stmt)
        if res.scalar_one_or_none():
            raise DuplicateResourceException(f"Ya existe una ficha con caracterización '{ficha_in.ficha_caracterizacion}'")

        ficha = Ficha(**ficha_in.model_dump())
        session.add(ficha)
        await session.commit()
        await session.refresh(ficha)
        return await AcademicService.get_ficha_by_id(session, ficha.ficha_caracterizacion)

    @staticmethod
    async def update_ficha(session: AsyncSession, ficha_caracterizacion: str, ficha_in: FichaUpdate) -> Ficha:
        ficha = await AcademicService.get_ficha_by_id(session, ficha_caracterizacion)
        for field, value in ficha_in.model_dump(exclude_unset=True).items():
            setattr(ficha, field, value)
        await session.commit()
        await session.refresh(ficha)
        return await AcademicService.get_ficha_by_id(session, ficha_caracterizacion)
