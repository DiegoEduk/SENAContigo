from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.modules.surveys.models import CorteEncuesta, Encuesta, EncuestaVariable
from app.modules.surveys.schemas import CorteEncuestaCreate, EncuestaCreate, EncuestaUpdate


class SurveysService:
    @staticmethod
    async def list_encuestas(session: AsyncSession, estado: Optional[str] = None) -> List[Encuesta]:
        stmt = (
            select(Encuesta)
            .options(
                selectinload(Encuesta.variables_asociadas).selectinload(EncuestaVariable.variable),
                selectinload(Encuesta.cortes)
            )
        )
        if estado:
            stmt = stmt.where(Encuesta.estado == estado)
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_encuesta_by_id(session: AsyncSession, encuesta_id: int) -> Encuesta:
        stmt = (
            select(Encuesta)
            .where(Encuesta.id == encuesta_id)
            .options(
                selectinload(Encuesta.variables_asociadas).selectinload(EncuestaVariable.variable),
                selectinload(Encuesta.cortes)
            )
        )
        res = await session.execute(stmt)
        enc = res.scalar_one_or_none()
        if not enc:
            raise NotFoundException("Encuesta", encuesta_id)
        return enc

    @staticmethod
    async def create_encuesta(session: AsyncSession, enc_in: EncuestaCreate) -> Encuesta:
        enc = Encuesta(
            titulo=enc_in.titulo,
            descripcion=enc_in.descripcion,
            tipo=enc_in.tipo,
            fecha_inicio=enc_in.fecha_inicio,
            fecha_fin=enc_in.fecha_fin,
            estado=enc_in.estado,
            segmento_id=enc_in.segmento_id
        )
        session.add(enc)
        await session.flush()

        for idx, var_id in enumerate(enc_in.variables_ids):
            ev = EncuestaVariable(encuesta_id=enc.id, variable_id=var_id, orden=idx)
            session.add(ev)

        # Crear corte inicial automático
        corte = CorteEncuesta(encuesta_id=enc.id, nombre_corte=f"Corte Inicial - {enc.titulo}")
        session.add(corte)

        await session.commit()
        return await SurveysService.get_encuesta_by_id(session, enc.id)

    @staticmethod
    async def create_corte(session: AsyncSession, encuesta_id: int, corte_in: CorteEncuestaCreate) -> CorteEncuesta:
        enc = await SurveysService.get_encuesta_by_id(session, encuesta_id)
        corte = CorteEncuesta(
            encuesta_id=enc.id,
            nombre_corte=corte_in.nombre_corte,
            descripcion=corte_in.descripcion
        )
        session.add(corte)
        await session.commit()
        await session.refresh(corte)
        return corte
