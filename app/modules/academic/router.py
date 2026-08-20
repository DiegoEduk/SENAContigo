from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
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


@programas_router.get("/{codigo_programa}", response_model=ProgramaFormacionRead)
async def get_programa(
    codigo_programa: str,
    version: str = Query("1", description="Versión del programa de formación"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener programa de formación por su código y versión (PK compuesta)."""
    return await AcademicService.get_programa_by_id(db, codigo_programa, version=version)


@programas_router.post("", response_model=ProgramaFormacionRead, status_code=status.HTTP_201_CREATED)
async def create_programa(
    prog_in: ProgramaFormacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Crear nuevo programa de formación."""
    return await AcademicService.create_programa(db, prog_in)


@programas_router.put("/{codigo_programa}", response_model=ProgramaFormacionRead)
async def update_programa(
    codigo_programa: str,
    prog_in: ProgramaFormacionUpdate,
    version: str = Query("1", description="Versión del programa de formación"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Actualizar programa de formación."""
    return await AcademicService.update_programa(db, codigo_programa, version=version, prog_in=prog_in)


# Fichas
@fichas_router.get("", response_model=List[FichaRead])
async def list_fichas(
    centro_id: Optional[str] = None,
    programa_codigo: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar fichas de caracterización."""
    return await AcademicService.list_fichas(db, centro_id=centro_id, programa_codigo=programa_codigo)


@fichas_router.get("/{ficha_caracterizacion}", response_model=FichaRead)
async def get_ficha(
    ficha_caracterizacion: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener ficha por su ficha de caracterización (PK)."""
    return await AcademicService.get_ficha_by_id(db, ficha_caracterizacion)


@fichas_router.post("", response_model=FichaRead, status_code=status.HTTP_201_CREATED)
async def create_ficha(
    ficha_in: FichaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Crear nueva ficha de caracterización."""
    return await AcademicService.create_ficha(db, ficha_in)


@fichas_router.put("/{ficha_caracterizacion}", response_model=FichaRead)
async def update_ficha(
    ficha_caracterizacion: str,
    ficha_in: FichaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Actualizar ficha de caracterización."""
    return await AcademicService.update_ficha(db, ficha_caracterizacion, ficha_in)
