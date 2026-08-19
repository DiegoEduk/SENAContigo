from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.academic.schemas import (
    FichaCreate, FichaRead, FichaUpdate,
    ProgramaFormacionCreate, ProgramaFormacionRead, ProgramaFormacionUpdate
)
from app.modules.academic.services import AcademicService

programas_router = APIRouter(prefix="/programas", tags=["Gestión Académica - Programas"])
fichas_router = APIRouter(prefix="/fichas", tags=["Gestión Académica - Fichas"])


# Programas
@programas_router.get("", response_model=List[ProgramaFormacionRead])
async def list_programas(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar programas de formación SENA."""
    return await AcademicService.list_programas(db)


@programas_router.get("/{programa_id}", response_model=ProgramaFormacionRead)
async def get_programa(
    programa_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener programa de formación por ID."""
    return await AcademicService.get_programa_by_id(db, programa_id)


@programas_router.post("", response_model=ProgramaFormacionRead, status_code=status.HTTP_201_CREATED)
async def create_programa(
    prog_in: ProgramaFormacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Crear nuevo programa de formación."""
    return await AcademicService.create_programa(db, prog_in)


@programas_router.put("/{programa_id}", response_model=ProgramaFormacionRead)
async def update_programa(
    programa_id: int,
    prog_in: ProgramaFormacionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Actualizar programa de formación."""
    return await AcademicService.update_programa(db, programa_id, prog_in)


# Fichas
@fichas_router.get("", response_model=List[FichaRead])
async def list_fichas(
    centro_id: Optional[int] = None,
    programa_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar fichas de caracterización."""
    return await AcademicService.list_fichas(db, centro_id=centro_id, programa_id=programa_id)


@fichas_router.get("/{ficha_id}", response_model=FichaRead)
async def get_ficha(
    ficha_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener ficha por ID."""
    return await AcademicService.get_ficha_by_id(db, ficha_id)


@fichas_router.post("", response_model=FichaRead, status_code=status.HTTP_201_CREATED)
async def create_ficha(
    ficha_in: FichaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Crear nueva ficha de caracterización."""
    return await AcademicService.create_ficha(db, ficha_in)


@fichas_router.put("/{ficha_id}", response_model=FichaRead)
async def update_ficha(
    ficha_id: int,
    ficha_in: FichaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Actualizar ficha de caracterización."""
    return await AcademicService.update_ficha(db, ficha_id, ficha_in)
