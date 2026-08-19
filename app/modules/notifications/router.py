from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token
from app.core.security import TokenData
from app.modules.notifications.schemas import NotificacionCreate, NotificacionRead
from app.modules.notifications.services import NotificationsService

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("", response_model=List[NotificacionRead])
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar notificaciones del usuario autenticado."""
    return await NotificationsService.list_user_notifications(db, current_user.user_id)


@router.post("", response_model=NotificacionRead, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notif_in: NotificacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Emitir una nueva notificación."""
    return await NotificationsService.create_notification(db, notif_in)
