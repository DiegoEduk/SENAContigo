from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.identity.schemas import LoginRequest, RolRead, TokenResponse, UsuarioCreate, UsuarioRead, UsuarioUpdate
from app.modules.identity.services import IdentityService

router = APIRouter(prefix="/auth", tags=["Autenticación e Identidad"])
users_router = APIRouter(prefix="/usuarios", tags=["Gestión de Usuarios"])


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Autenticar usuario y generar access token y refresh token."""
    return await IdentityService.authenticate_user(db, login_data)


@router.get("/me", response_model=UsuarioRead)
async def get_me(
    current_user: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    """Obtener datos del usuario actualmente autenticado."""
    return await IdentityService.get_user_by_id(db, current_user.user_id)


@router.post("/seed")
async def run_seed_endpoint():
    """Ejecutar o forzar el poblamiento de datos iniciales en la base de datos."""
    from app.seed import seed_data
    await seed_data()
    return {"status": "ok", "message": "Poblamiento de datos iniciales ejecutado exitosamente."}


@users_router.get("", response_model=List[UsuarioRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Listar usuarios del sistema."""
    return await IdentityService.list_users(db, skip=skip, limit=limit)


@users_router.post("", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion"]))
):
    """Crear un nuevo usuario."""
    return await IdentityService.create_user(db, user_in)


@users_router.get("/{user_id}", response_model=UsuarioRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Obtener usuario por ID."""
    return await IdentityService.get_user_by_id(db, user_id)


@users_router.put("/{user_id}", response_model=UsuarioRead)
async def update_user(
    user_id: int,
    user_in: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion"]))
):
    """Actualizar datos de usuario."""
    return await IdentityService.update_user(db, user_id, user_in)


@users_router.get("/roles/todos", response_model=List[RolRead])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar catálogo de roles."""
    return await IdentityService.list_roles(db)
