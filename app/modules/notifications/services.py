from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notificacion
from app.modules.notifications.schemas import NotificacionCreate


class NotificationsService:
    @staticmethod
    async def list_user_notifications(session: AsyncSession, user_id: int) -> List[Notificacion]:
        stmt = (
            select(Notificacion)
            .where(Notificacion.usuario_id == user_id)
            .order_by(Notificacion.created_at.desc())
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_notification(session: AsyncSession, notif_in: NotificacionCreate) -> Notificacion:
        notif = Notificacion(**notif_in.model_dump())
        session.add(notif)
        await session.commit()
        await session.refresh(notif)
        return notif
