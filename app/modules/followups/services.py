from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.cases.models import Caso
from app.modules.followups.models import SeguimientoCaso
from app.modules.followups.schemas import SeguimientoCasoCreate


class FollowupsService:
    @staticmethod
    async def list_seguimientos_by_caso(session: AsyncSession, caso_id: int) -> List[SeguimientoCaso]:
        stmt = (
            select(SeguimientoCaso)
            .where(SeguimientoCaso.caso_id == caso_id)
            .options(selectinload(SeguimientoCaso.usuario))
            .order_by(SeguimientoCaso.created_at.desc())
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_seguimiento(session: AsyncSession, seg_in: SeguimientoCasoCreate, usuario_id: int) -> SeguimientoCaso:
        seg = SeguimientoCaso(
            caso_id=seg_in.caso_id,
            usuario_id=usuario_id,
            observacion=seg_in.observacion,
            estado_caso_resultante=seg_in.estado_caso_resultante
        )
        session.add(seg)

        # Update case status if provided
        if seg_in.estado_caso_resultante:
            caso_stmt = select(Caso).where(Caso.id == seg_in.caso_id)
            caso_res = await session.execute(caso_stmt)
            caso = caso_res.scalar_one_or_none()
            if caso:
                caso.estado = seg_in.estado_caso_resultante

        await session.commit()
        await session.refresh(seg)
        return seg
