from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.benefits.schemas import (
    AprendizBeneficioCreate,
    AprendizBeneficioResponse,
    AprendizBeneficioUpdateState,
    BeneficioCreate,
    BeneficioResponse,
    BeneficioUpdate,
)
from app.modules.benefits.services import (
    assign_automatic_benefits_for_aprendiz,
    assign_beneficio_to_aprendiz,
    create_beneficio,
    get_aprendiz_beneficios,
    get_beneficio_by_id,
    get_beneficios,
    update_aprendiz_beneficio_state,
    update_beneficio,
)

router = APIRouter(prefix="/beneficios", tags=["Beneficios Institucionales del Aprendiz"])


@router.get("", response_model=List[BeneficioResponse])
async def list_beneficios(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar el catálogo de beneficios institucionales activos."""
    return await get_beneficios(db)


@router.post("", response_model=BeneficioResponse, status_code=status.HTTP_201_CREATED)
async def create_new_beneficio(
    data: BeneficioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "lider_bienestar"]))
):
    """Crear un nuevo beneficio en el catálogo institucional."""
    return await create_beneficio(db, data)


@router.get("/aprendiz/{aprendiz_id}", response_model=List[AprendizBeneficioResponse])
async def list_beneficios_aprendiz(
    aprendiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar todos los beneficios institucionales asignados a un aprendiz."""
    return await get_aprendiz_beneficios(db, aprendiz_id)


@router.post("/aprendiz", response_model=AprendizBeneficioResponse, status_code=status.HTTP_201_CREATED)
async def assign_beneficio(
    data: AprendizBeneficioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Asignar un beneficio institucional directamente a un aprendiz."""
    beneficio = await get_beneficio_by_id(db, data.beneficio_id)
    if not beneficio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficio no encontrado.")
    return await assign_beneficio_to_aprendiz(db, data)


@router.post("/aprendiz/{aprendiz_id}/asignar-automaticos", response_model=List[AprendizBeneficioResponse])
async def assign_automatic_benefits(
    aprendiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Asignar de forma masiva/automática los beneficios por matrícula activa SENA a un aprendiz."""
    return await assign_automatic_benefits_for_aprendiz(db, aprendiz_id)


@router.patch("/aprendiz/{aprendiz_beneficio_id}/estado", response_model=AprendizBeneficioResponse)
async def update_assigned_beneficio_state(
    aprendiz_beneficio_id: int,
    data: AprendizBeneficioUpdateState,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Actualizar el estado (ACTIVO, SUSPENDIDO, VENCIDO, FINALIZADO) de un beneficio asignado."""
    updated = await update_aprendiz_beneficio_state(db, aprendiz_beneficio_id, data.estado, data.observaciones)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignación de beneficio no encontrada.")
    return updated
