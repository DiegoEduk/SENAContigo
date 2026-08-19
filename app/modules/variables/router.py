from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.variables.schemas import (
    CategoriaVariableCreate, CategoriaVariableRead,
    VariableCreate, VariableRead, VariableUpdate,
    VariableVersionCreate, VariableVersionRead
)
from app.modules.variables.services import VariablesService

router = APIRouter(prefix="/variables", tags=["Motor de Variables Dinámicas"])


# Categorías
@router.get("/categorias", response_model=List[CategoriaVariableRead])
async def list_categorias(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar categorías de variables."""
    return await VariablesService.list_categorias(db)


@router.post("/categorias", response_model=CategoriaVariableRead, status_code=status.HTTP_201_CREATED)
async def create_categoria(
    cat_in: CategoriaVariableCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion"]))
):
    """Crear una nueva categoría de variables."""
    return await VariablesService.create_categoria(db, cat_in)


# Variables
@router.get("", response_model=List[VariableRead])
async def list_variables(
    categoria_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar variables dinámicas activas con sus versiones y opciones."""
    return await VariablesService.list_variables(db, categoria_id=categoria_id)


@router.get("/{variable_id}", response_model=VariableRead)
async def get_variable(
    variable_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener variable por ID."""
    return await VariablesService.get_variable_by_id(db, variable_id)


@router.post("", response_model=VariableRead, status_code=status.HTTP_201_CREATED)
async def create_variable(
    var_in: VariableCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion"]))
):
    """Crear una nueva variable dinámica con su versión inicial 1 y sus opciones."""
    return await VariablesService.create_variable(db, var_in)


@router.post("/{variable_id}/versiones", response_model=VariableVersionRead, status_code=status.HTTP_201_CREATED)
async def create_variable_version(
    variable_id: int,
    version_in: VariableVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion"]))
):
    """Crear una nueva versión para una variable existente sin modificar el historial."""
    return await VariablesService.create_new_version(db, variable_id, version_in)
