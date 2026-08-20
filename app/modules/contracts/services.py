from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.core.exceptions import NotFoundException
from app.modules.apprentices.models import Aprendiz, Matricula
from app.modules.contracts.models import ContratoAprendizaje
from app.modules.contracts.schemas import ContratoCreate, ContratoUpdate


class ContractsService:
    @staticmethod
    async def create_contrato(session: AsyncSession, contrato_in: ContratoCreate) -> ContratoAprendizaje:
        # Verify matricula exists
        stmt_mat = select(Matricula).where(Matricula.id == contrato_in.matricula_id)
        res_mat = await session.execute(stmt_mat)
        mat = res_mat.scalar_one_or_none()
        if not mat:
            raise NotFoundException("Matrícula", contrato_in.matricula_id)

        contrato = ContratoAprendizaje(**contrato_in.model_dump())
        session.add(contrato)
        await session.commit()
        await session.refresh(contrato)

        return await ContractsService.get_contrato_by_id(session, contrato.id)

    @staticmethod
    async def get_contrato_by_id(session: AsyncSession, contrato_id: int) -> ContratoAprendizaje:
        stmt = (
            select(ContratoAprendizaje)
            .where(ContratoAprendizaje.id == contrato_id)
            .options(
                joinedload(ContratoAprendizaje.matricula).joinedload(Matricula.aprendiz),
                joinedload(ContratoAprendizaje.matricula).joinedload(Matricula.ficha)
            )
        )
        res = await session.execute(stmt)
        contrato = res.scalar_one_or_none()
        if not contrato:
            raise NotFoundException("Contrato de Aprendizaje", contrato_id)
        return contrato

    @staticmethod
    async def list_contratos(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        matricula_id: Optional[int] = None,
        aprendiz_id: Optional[int] = None,
        estado: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[ContratoAprendizaje]:
        stmt = (
            select(ContratoAprendizaje)
            .join(ContratoAprendizaje.matricula)
            .options(
                joinedload(ContratoAprendizaje.matricula).joinedload(Matricula.aprendiz),
                joinedload(ContratoAprendizaje.matricula).joinedload(Matricula.ficha)
            )
        )

        if matricula_id:
            stmt = stmt.where(ContratoAprendizaje.matricula_id == matricula_id)
        if aprendiz_id:
            stmt = stmt.where(Matricula.aprendiz_id == aprendiz_id)
        if estado:
            stmt = stmt.where(ContratoAprendizaje.estado_contrato == estado)
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.join(Matricula.aprendiz).where(
                (ContratoAprendizaje.nombre_empresa.ilike(search_pattern)) |
                (ContratoAprendizaje.departamento.ilike(search_pattern)) |
                (ContratoAprendizaje.ciudad.ilike(search_pattern)) |
                (Aprendiz.nombres.ilike(search_pattern)) |
                (Aprendiz.apellidos.ilike(search_pattern)) |
                (Aprendiz.numero_documento.ilike(search_pattern))
            )

        stmt = stmt.order_by(ContratoAprendizaje.created_at.desc()).offset(skip).limit(limit)
        res = await session.execute(stmt)
        return list(res.scalars().unique().all())

    @staticmethod
    async def get_contratos_by_aprendiz(session: AsyncSession, aprendiz_id: int) -> List[ContratoAprendizaje]:
        stmt = (
            select(ContratoAprendizaje)
            .join(ContratoAprendizaje.matricula)
            .where(Matricula.aprendiz_id == aprendiz_id)
            .options(
                joinedload(ContratoAprendizaje.matricula).joinedload(Matricula.aprendiz),
                joinedload(ContratoAprendizaje.matricula).joinedload(Matricula.ficha)
            )
            .order_by(ContratoAprendizaje.created_at.desc())
        )
        res = await session.execute(stmt)
        return list(res.scalars().unique().all())

    @staticmethod
    async def update_contrato(
        session: AsyncSession, contrato_id: int, contrato_in: ContratoUpdate
    ) -> ContratoAprendizaje:
        contrato = await ContractsService.get_contrato_by_id(session, contrato_id)
        for field, value in contrato_in.model_dump(exclude_unset=True).items():
            setattr(contrato, field, value)
        await session.commit()
        await session.refresh(contrato)
        return await ContractsService.get_contrato_by_id(session, contrato_id)
