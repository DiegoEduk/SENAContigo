from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.identity.schemas import AprendizLoginRequest, AprendizTokenResponse, LoginRequest, RolRead, TokenResponse, UsuarioCreate, UsuarioRead, UsuarioUpdate
from app.modules.identity.services import IdentityService

router = APIRouter(prefix="/auth", tags=["Autenticación e Identidad"])
users_router = APIRouter(prefix="/usuarios", tags=["Gestión de Usuarios"])


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Autenticar usuario administrativo/instructor y generar token de acceso."""
    return await IdentityService.authenticate_user(db, login_data)


@router.post("/aprendiz-login", response_model=AprendizTokenResponse)
async def aprendiz_login(login_data: AprendizLoginRequest, db: AsyncSession = Depends(get_db)):
    """Autenticar aprendiz público mediante su Número de Documento y Ficha de Formación matriculada."""
    return await IdentityService.authenticate_aprendiz(
        db,
        numero_documento=login_data.numero_documento,
        ficha_caracterizacion=login_data.ficha_caracterizacion
    )



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
    centro_id: Optional[str] = None,
    regional_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador"]))
):
    """Listar usuarios del sistema con delimitación territorial según el rol del usuario en sesión."""
    if current_user.rol in ["coordinador", "Coordinador"] and current_user.centro_id:
        centro_id = current_user.centro_id
    elif current_user.rol in ["direccion", "Dirección"] and current_user.regional_id:
        regional_id = current_user.regional_id

    return await IdentityService.list_users(db, skip=skip, limit=limit, centro_id=centro_id, regional_id=regional_id)


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
