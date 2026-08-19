from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token
from app.core.security import TokenData
from app.modules.responses.schemas import BatchRespuestaCreate, EstadoActualAprendiz, RespuestaRead
from app.modules.responses.services import ResponsesService

router = APIRouter(prefix="/respuestas", tags=["Respuestas Longitudinales e Histórico"])


@router.post("", response_model=List[RespuestaRead], status_code=status.HTTP_201_CREATED)
async def record_responses(
    batch_in: BatchRespuestaCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Registrar una o varias respuestas de una medición (Registro Inmutable sin sobrescritura)."""
    ip = request.client.host if request.client else None
    return await ResponsesService.record_batch_responses(
        db, batch_in=batch_in, user_id=current_user.user_id, ip_origen=ip
    )


@router.get("/aprendiz/{aprendiz_id}/historico", response_model=List[RespuestaRead])
async def get_aprendiz_history(
    aprendiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener el historial longitudinal completo de respuestas de un aprendiz a lo largo del tiempo."""
    return await ResponsesService.get_aprendiz_history(db, aprendiz_id)


@router.get("/aprendiz/{aprendiz_id}/estado-actual", response_model=EstadoActualAprendiz)
async def get_estado_actual(
    aprendiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Calcular la situación o estado actual del aprendiz basado en la última medición válida de cada variable."""
    return await ResponsesService.get_estado_actual_aprendiz(db, aprendiz_id)
