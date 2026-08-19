from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.surveys.schemas import CorteEncuestaCreate, CorteEncuestaRead, EncuestaCreate, EncuestaRead, EncuestaUpdate
from app.modules.surveys.services import SurveysService

router = APIRouter(prefix="/encuestas", tags=["Constructor de Encuestas"])


@router.get("", response_model=List[EncuestaRead])
async def list_encuestas(
    estado: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar encuestas registradas."""
    return await SurveysService.list_encuestas(db, estado=estado)


@router.get("/{encuesta_id}", response_model=EncuestaRead)
async def get_encuesta(
    encuesta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener detalle de encuesta con sus variables y cortes."""
    return await SurveysService.get_encuesta_by_id(db, encuesta_id)


@router.post("", response_model=EncuestaRead, status_code=status.HTTP_201_CREATED)
async def create_encuesta(
    enc_in: EncuestaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Crear nueva encuesta con selección de variables dinámicas."""
    return await SurveysService.create_encuesta(db, enc_in)


@router.post("/{encuesta_id}/cortes", response_model=CorteEncuestaRead, status_code=status.HTTP_201_CREATED)
async def create_corte(
    encuesta_id: int,
    corte_in: CorteEncuestaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Generar un nuevo corte histórico para una encuesta (ej. Medición Antes vs. Después)."""
    return await SurveysService.create_corte(db, encuesta_id, corte_in)
