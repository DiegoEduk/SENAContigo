from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.followups.schemas import SeguimientoCasoCreate, SeguimientoCasoRead
from app.modules.followups.services import FollowupsService

router = APIRouter(prefix="/seguimientos", tags=["Seguimiento Longitudinal de Casos"])


@router.get("/caso/{caso_id}", response_model=List[SeguimientoCasoRead])
async def list_seguimientos_by_caso(
    caso_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar el historial de seguimientos de un caso."""
    return await FollowupsService.list_seguimientos_by_caso(db, caso_id)


@router.post("", response_model=SeguimientoCasoRead, status_code=status.HTTP_201_CREATED)
async def create_seguimiento(
    seg_in: SeguimientoCasoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador", "instructor"]))
):
    """Registrar una anotación de seguimiento y actualizar opcionalmente el estado del caso."""
    return await FollowupsService.create_seguimiento(db, seg_in, usuario_id=current_user.user_id)
