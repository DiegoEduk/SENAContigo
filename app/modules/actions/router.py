from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.actions.schemas import AccionCasoCreate, AccionCasoRead, AccionCasoUpdate
from app.modules.actions.services import ActionsService

router = APIRouter(prefix="/acciones", tags=["Gestión de Acciones por Caso"])


@router.get("/caso/{caso_id}", response_model=List[AccionCasoRead])
async def list_acciones_by_caso(
    caso_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar acciones asociadas a un caso especifico."""
    return await ActionsService.list_acciones_by_caso(db, caso_id)


@router.post("", response_model=AccionCasoRead, status_code=status.HTTP_201_CREATED)
async def create_accion(
    acc_in: AccionCasoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador", "instructor"]))
):
    """Registrar una acción dentro de un caso de atención."""
    return await ActionsService.create_accion(db, acc_in)


@router.put("/{accion_id}", response_model=AccionCasoRead)
async def update_accion(
    accion_id: int,
    acc_in: AccionCasoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador", "instructor"]))
):
    """Actualizar estado u observaciones de una acción."""
    return await ActionsService.update_accion(db, accion_id, acc_in)
