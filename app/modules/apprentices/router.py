from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.apprentices.schemas import (
    AprendizCreate, AprendizRead, AprendizUpdate,
    MatriculaCreate, MatriculaRead, MatriculaUpdate
)
from app.modules.apprentices.services import ApprenticesService

aprendices_router = APIRouter(prefix="/aprendices", tags=["Gestión de Aprendices"])
matriculas_router = APIRouter(prefix="/matriculas", tags=["Gestión de Matrículas"])


# Aprendices
@aprendices_router.get("", response_model=List[AprendizRead])
async def list_aprendices(
    skip: int = 0,
    limit: int = 100,
    ficha_id: Optional[int] = None,
    centro_id: Optional[int] = None,
    regional_id: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar aprendices con filtros por ficha, centro, regional y búsqueda textual."""
    return await ApprenticesService.list_aprendices(
        db, skip=skip, limit=limit, ficha_id=ficha_id, centro_id=centro_id, regional_id=regional_id, search=search
    )


@aprendices_router.get("/{aprendiz_id}", response_model=AprendizRead)
async def get_aprendiz(
    aprendiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener detalle de un aprendiz por ID."""
    return await ApprenticesService.get_aprendiz_by_id(db, aprendiz_id)


@aprendices_router.post("", response_model=AprendizRead, status_code=status.HTTP_201_CREATED)
async def create_aprendiz(
    aprendiz_in: AprendizCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador", "instructor"]))
):
    """Registrar un nuevo aprendiz."""
    return await ApprenticesService.create_aprendiz(db, aprendiz_in)


@aprendices_router.put("/{aprendiz_id}", response_model=AprendizRead)
async def update_aprendiz(
    aprendiz_id: int,
    aprendiz_in: AprendizUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador", "instructor"]))
):
    """Actualizar datos de un aprendiz."""
    return await ApprenticesService.update_aprendiz(db, aprendiz_id, aprendiz_in)


# Matrículas
@matriculas_router.post("", response_model=MatriculaRead, status_code=status.HTTP_201_CREATED)
async def create_matricula(
    mat_in: MatriculaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador", "instructor"]))
):
    """Matricular un aprendiz en una ficha."""
    return await ApprenticesService.create_matricula(db, mat_in)


@matriculas_router.put("/{matricula_id}", response_model=MatriculaRead)
async def update_matricula(
    matricula_id: int,
    mat_in: MatriculaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador", "instructor"]))
):
    """Actualizar el estado de matrícula de un aprendiz."""
    return await ApprenticesService.update_matricula(db, matricula_id, mat_in)
