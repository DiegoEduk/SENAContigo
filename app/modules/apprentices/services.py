from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import DuplicateResourceException, NotFoundException
from app.modules.apprentices.models import Aprendiz, Matricula
from app.modules.apprentices.schemas import AprendizCreate, AprendizUpdate, MatriculaCreate, MatriculaUpdate
from app.modules.benefits.services import assign_automatic_benefits_for_aprendiz


class ApprenticesService:
    @staticmethod
    async def list_aprendices(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        ficha_id: Optional[int] = None,
        centro_id: Optional[int] = None,
        regional_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Aprendiz]:
        stmt = select(Aprendiz).options(selectinload(Aprendiz.matriculas))

        if centro_id:
            stmt = stmt.where(Aprendiz.centro_id == centro_id)
        if regional_id:
            stmt = stmt.where(Aprendiz.regional_id == regional_id)
        if ficha_id:
            stmt = stmt.join(Matricula).where(Matricula.ficha_id == ficha_id)
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                (Aprendiz.nombres.ilike(search_pattern)) |
                (Aprendiz.apellidos.ilike(search_pattern)) |
                (Aprendiz.numero_documento.ilike(search_pattern)) |
                (Aprendiz.correo.ilike(search_pattern))
            )

        stmt = stmt.offset(skip).limit(limit)
        res = await session.execute(stmt)
        return list(res.scalars().unique().all())

    @staticmethod
    async def get_aprendiz_by_id(session: AsyncSession, aprendiz_id: int) -> Aprendiz:
        stmt = select(Aprendiz).where(Aprendiz.id == aprendiz_id).options(selectinload(Aprendiz.matriculas))
        res = await session.execute(stmt)
        aprendiz = res.scalar_one_or_none()
        if not aprendiz:
            raise NotFoundException("Aprendiz", aprendiz_id)
        return aprendiz

    @staticmethod
    async def create_aprendiz(session: AsyncSession, aprendiz_in: AprendizCreate) -> Aprendiz:
        stmt = select(Aprendiz).where(
            (Aprendiz.numero_documento == aprendiz_in.numero_documento) |
            (Aprendiz.correo == aprendiz_in.correo)
        )
        res = await session.execute(stmt)
        if res.scalar_one_or_none():
            raise DuplicateResourceException("Ya existe un aprendiz con este documento o correo")

        aprendiz = Aprendiz(**aprendiz_in.model_dump())
        session.add(aprendiz)
        await session.commit()
        await session.refresh(aprendiz)

        # Asignación automática de beneficios por el hecho de registrarse/matricularse en el SENA
        await assign_automatic_benefits_for_aprendiz(session, aprendiz.id)

        return await ApprenticesService.get_aprendiz_by_id(session, aprendiz.id)

    @staticmethod
    async def update_aprendiz(session: AsyncSession, aprendiz_id: int, aprendiz_in: AprendizUpdate) -> Aprendiz:
        aprendiz = await ApprenticesService.get_aprendiz_by_id(session, aprendiz_id)
        for field, value in aprendiz_in.model_dump(exclude_unset=True).items():
            setattr(aprendiz, field, value)
        await session.commit()
        await session.refresh(aprendiz)
        return await ApprenticesService.get_aprendiz_by_id(session, aprendiz_id)

    # Matrículas
    @staticmethod
    async def create_matricula(session: AsyncSession, mat_in: MatriculaCreate) -> Matricula:
        # Check duplicate
        stmt = select(Matricula).where(
            (Matricula.aprendiz_id == mat_in.aprendiz_id) &
            (Matricula.ficha_id == mat_in.ficha_id)
        )
        res = await session.execute(stmt)
        if res.scalar_one_or_none():
            raise DuplicateResourceException("El aprendiz ya se encuentra matriculado en esta ficha")

        mat = Matricula(**mat_in.model_dump())
        session.add(mat)
        await session.commit()
        await session.refresh(mat)
        return mat

    @staticmethod
    async def update_matricula(session: AsyncSession, matricula_id: int, mat_in: MatriculaUpdate) -> Matricula:
        stmt = select(Matricula).where(Matricula.id == matricula_id)
        res = await session.execute(stmt)
        mat = res.scalar_one_or_none()
        if not mat:
            raise NotFoundException("Matrícula", matricula_id)

        for field, value in mat_in.model_dump(exclude_unset=True).items():
            setattr(mat, field, value)
        await session.commit()
        await session.refresh(mat)
        return mat
