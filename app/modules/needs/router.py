from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.needs.schemas import TipoCasoCreate, TipoCasoRead
from app.modules.needs.services import CaseTypesService

router = APIRouter(prefix="/tipos-caso", tags=["Catálogo de Tipos de Caso"])


@router.get("", response_model=List[TipoCasoRead])
async def list_tipos_caso(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar el catálogo de tipos de caso."""
    return await CaseTypesService.list_tipos_caso(db)


@router.post("", response_model=TipoCasoRead, status_code=status.HTTP_201_CREATED)
async def create_tipo_caso(
    tc_in: TipoCasoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion"]))
):
    """Crear un nuevo tipo de caso en el catálogo."""
    return await CaseTypesService.create_tipo_caso(db, tc_in)

