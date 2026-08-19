from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.cases.schemas import CasoCreate, CasoRead, CasoUpdate
from app.modules.cases.services import CasesService

router = APIRouter(prefix="/casos", tags=["Gestión de Casos"])


@router.get("", response_model=List[CasoRead])
async def list_casos(
    estado: Optional[str] = None,
    prioridad: Optional[str] = None,
    responsable_id: Optional[int] = None,
    aprendiz_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar casos de atención con filtros por estado, prioridad, responsable y aprendiz."""
    return await CasesService.list_casos(
        db, estado=estado, prioridad=prioridad, responsable_id=responsable_id, aprendiz_id=aprendiz_id
    )


@router.get("/{caso_id}", response_model=CasoRead)
async def get_caso(
    caso_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener detalle completo de un caso."""
    return await CasesService.get_caso_by_id(db, caso_id)


@router.post("", response_model=CasoRead, status_code=status.HTTP_201_CREATED)
async def create_caso(
    caso_in: CasoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador", "instructor"]))
):
    """Crear un caso de atención manualmente."""
    return await CasesService.create_caso(db, caso_in)


@router.put("/{caso_id}", response_model=CasoRead)
async def update_caso(
    caso_id: int,
    caso_in: CasoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador", "instructor"]))
):
    """Actualizar estado, prioridad o responsable asignado a un caso."""
    return await CasesService.update_caso(db, caso_id, caso_in)
