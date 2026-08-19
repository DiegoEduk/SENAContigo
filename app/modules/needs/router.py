from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.needs.schemas import NecesidadCreate, NecesidadRead
from app.modules.needs.services import NeedsService

router = APIRouter(prefix="/necesidades", tags=["Catálogo de Necesidades"])


@router.get("", response_model=List[NecesidadRead])
async def list_necesidades(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar el catálogo de necesidades identificables."""
    return await NeedsService.list_necesidades(db)


@router.post("", response_model=NecesidadRead, status_code=status.HTTP_201_CREATED)
async def create_necesidad(
    nec_in: NecesidadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion"]))
):
    """Crear una nueva necesidad en el catálogo."""
    return await NeedsService.create_necesidad(db, nec_in)
