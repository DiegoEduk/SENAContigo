from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.contracts.schemas import ContratoCreate, ContratoRead, ContratoUpdate
from app.modules.contracts.services import ContractsService

router = APIRouter(prefix="/contratos", tags=["Contratación de Aprendices"])


def _format_contrato_response(c) -> ContratoRead:
    ficha_id = c.matricula.ficha_id if c.matricula else None
    aprendiz_id = c.matricula.aprendiz_id if c.matricula else None
    aprendiz_nombre = ""
    if c.matricula and c.matricula.aprendiz:
        aprendiz_nombre = f"{c.matricula.aprendiz.nombres} {c.matricula.aprendiz.apellidos}"

    return ContratoRead(
        id=c.id,
        matricula_id=c.matricula_id,
        nombre_empresa=c.nombre_empresa,
        departamento=c.departamento,
        ciudad=c.ciudad,
        fecha_inicio_contrato=c.fecha_inicio_contrato,
        fecha_fin_contrato=c.fecha_fin_contrato,
        estado_contrato=c.estado_contrato,
        observaciones=c.observaciones,
        created_at=c.created_at,
        updated_at=c.updated_at,
        ficha_id=ficha_id,
        aprendiz_id=aprendiz_id,
        aprendiz_nombre_completo=aprendiz_nombre
    )


@router.post("", response_model=ContratoRead, status_code=status.HTTP_201_CREATED)
async def create_contrato(
    contrato_in: ContratoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador", "lider_contratacion"]))
):
    """Registrar un nuevo contrato de aprendizaje para una matrícula activa."""
    contrato = await ContractsService.create_contrato(db, contrato_in)
    return _format_contrato_response(contrato)


@router.get("", response_model=List[ContratoRead])
async def list_contratos(
    skip: int = 0,
    limit: int = 100,
    matricula_id: Optional[int] = None,
    aprendiz_id: Optional[int] = None,
    estado: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Listar contratos de aprendizaje con filtros de búsqueda."""
    contratos = await ContractsService.list_contratos(
        db, skip=skip, limit=limit, matricula_id=matricula_id, aprendiz_id=aprendiz_id, estado=estado, search=search
    )
    return [_format_contrato_response(c) for c in contratos]


@router.get("/aprendiz/{aprendiz_id}", response_model=List[ContratoRead])
async def get_contratos_by_aprendiz(
    aprendiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener el histórico completo de contratos de aprendizaje de un aprendiz.
    Si el aprendiz no tiene contratos registrados, retorna una lista vacía.
    """
    contratos = await ContractsService.get_contratos_by_aprendiz(db, aprendiz_id)
    return [_format_contrato_response(c) for c in contratos]


@router.get("/{contrato_id}", response_model=ContratoRead)
async def get_contrato(
    contrato_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener el detalle de un contrato de aprendizaje por ID."""
    contrato = await ContractsService.get_contrato_by_id(db, contrato_id)
    return _format_contrato_response(contrato)


@router.patch("/{contrato_id}", response_model=ContratoRead)
async def update_contrato(
    contrato_id: int,
    contrato_in: ContratoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin", "direccion", "coordinador", "lider_contratacion"]))
):
    """Actualizar datos o el estado de un contrato de aprendizaje registrado."""
    contrato = await ContractsService.update_contrato(db, contrato_id, contrato_in)
    return _format_contrato_response(contrato)
