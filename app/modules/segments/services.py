from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.segments.models import Segmento
from app.modules.segments.schemas import SegmentoCreate


class SegmentsService:
    @staticmethod
    async def list_segmentos(session: AsyncSession) -> List[Segmento]:
        stmt = select(Segmento)
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_segmento(session: AsyncSession, seg_in: SegmentoCreate) -> Segmento:
        seg = Segmento(**seg_in.model_dump())
        session.add(seg)
        await session.commit()
        await session.refresh(seg)
        return seg

    @staticmethod
    async def get_segmento_by_id(session: AsyncSession, segmento_id: int) -> Segmento:
        stmt = select(Segmento).where(Segmento.id == segmento_id)
        res = await session.execute(stmt)
        seg = res.scalar_one_or_none()
        if not seg:
            raise NotFoundException("Segmento", segmento_id)
        return seg
