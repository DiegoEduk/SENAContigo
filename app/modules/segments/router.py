from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.segments.schemas import SegmentoCreate, SegmentoRead
from app.modules.segments.services import SegmentsService

router = APIRouter(prefix="/segmentos", tags=["Motor de Segmentación Dinámica"])


@router.get("", response_model=List[SegmentoRead])
async def list_segmentos(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar segmentos de aprendices creados."""
    return await SegmentsService.list_segmentos(db)


@router.post("", response_model=SegmentoRead, status_code=status.HTTP_201_CREATED)
async def create_segmento(
    seg_in: SegmentoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Crear un segmento dinámico para focalizar encuestas o casos."""
    return await SegmentsService.create_segmento(db, seg_in)
