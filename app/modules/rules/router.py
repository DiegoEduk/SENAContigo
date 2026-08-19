from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.rules.schemas import ReglaCreate, ReglaRead
from app.modules.rules.services import RulesService

router = APIRouter(prefix="/reglas", tags=["Motor de Reglas Configurables"])


@router.get("", response_model=List[ReglaRead])
async def list_reglas(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar reglas configuradas en el motor de decisiones."""
    return await RulesService.list_reglas(db)


@router.get("/{regla_id}", response_model=ReglaRead)
async def get_regla(
    regla_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener detalle de una regla por ID."""
    return await RulesService.get_regla_by_id(db, regla_id)


@router.post("", response_model=ReglaRead, status_code=status.HTTP_201_CREATED)
async def create_regla(
    regla_in: ReglaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion"]))
):
    """Crear una nueva regla configurable (IF condición THEN acción) en el sistema."""
    return await RulesService.create_regla(db, regla_in)
