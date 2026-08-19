from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.organization.schemas import (
    CentroFormacionCreate, CentroFormacionRead, CentroFormacionUpdate,
    RegionalCreate, RegionalRead, RegionalUpdate
)
from app.modules.organization.services import OrganizationService

regionales_router = APIRouter(prefix="/regionales", tags=["Estructura SENA - Regionales"])
centros_router = APIRouter(prefix="/centros", tags=["Estructura SENA - Centros"])


# Regionales
@regionales_router.get("", response_model=List[RegionalRead])
async def list_regionales(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar todas las regionales SENA."""
    return await OrganizationService.list_regionales(db)


@regionales_router.get("/{regional_id}", response_model=RegionalRead)
async def get_regional(
    regional_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener regional por ID."""
    return await OrganizationService.get_regional_by_id(db, regional_id)


@regionales_router.post("", response_model=RegionalRead, status_code=status.HTTP_201_CREATED)
async def create_regional(
    reg_in: RegionalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin"]))
):
    """Crear nueva regional SENA."""
    return await OrganizationService.create_regional(db, reg_in)


@regionales_router.put("/{regional_id}", response_model=RegionalRead)
async def update_regional(
    regional_id: int,
    reg_in: RegionalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin"]))
):
    """Actualizar regional SENA."""
    return await OrganizationService.update_regional(db, regional_id, reg_in)


# Centros
@centros_router.get("", response_model=List[CentroFormacionRead])
async def list_centros(
    regional_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar centros de formación (opcionalmente filtrados por regional)."""
    return await OrganizationService.list_centros(db, regional_id=regional_id)


@centros_router.get("/{centro_id}", response_model=CentroFormacionRead)
async def get_centro(
    centro_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener centro de formación por ID."""
    return await OrganizationService.get_centro_by_id(db, centro_id)


@centros_router.post("", response_model=CentroFormacionRead, status_code=status.HTTP_201_CREATED)
async def create_centro(
    centro_in: CentroFormacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion"]))
):
    """Crear nuevo centro de formación SENA."""
    return await OrganizationService.create_centro(db, centro_in)


@centros_router.put("/{centro_id}", response_model=CentroFormacionRead)
async def update_centro(
    centro_id: int,
    centro_in: CentroFormacionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion"]))
):
    """Actualizar centro de formación SENA."""
    return await OrganizationService.update_centro(db, centro_id, centro_in)
