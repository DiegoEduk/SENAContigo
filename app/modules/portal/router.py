from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import TokenData
from app.modules.apprentices.schemas import AprendizRead
from app.modules.benefits.schemas import AprendizBeneficioResponse
from app.modules.contracts.schemas import ContratoCreate, ContratoRead, ContratoUpdate
from app.modules.contracts.services import ContractsService
from app.modules.portal.schemas import PerfilAprendizUpdate, PortalBeneficioCreate, PortalContratoCreate, PortalContratoUpdate
from app.modules.portal.services import PortalService
from app.modules.responses.schemas import BatchRespuestaCreate, RespuestaHistorialRead, RespuestaRead
from app.modules.responses.services import ResponsesService

router = APIRouter(prefix="/portal", tags=["Portal del Aprendiz"])


def _resolve_aprendiz_id(current_user: TokenData) -> int:
    aprendiz_id = current_user.aprendiz_id or current_user.user_id
    if not aprendiz_id:
        raise UnauthorizedException("No se encontró la identidad de aprendiz asociada a la sesión.")
    return aprendiz_id


# 1. Perfil del Aprendiz
@router.get("/perfil", response_model=AprendizRead)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener datos del perfil del aprendiz en sesión."""
    aprendiz_id = _resolve_aprendiz_id(current_user)
    return await PortalService.get_perfil(db, aprendiz_id)


@router.put("/perfil", response_model=AprendizRead)
async def update_my_profile(
    perfil_in: PerfilAprendizUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Actualizar información de contacto del aprendiz (Tipo y Número de documento permanecen inmutables)."""
    aprendiz_id = _resolve_aprendiz_id(current_user)
    return await PortalService.update_perfil(db, aprendiz_id, perfil_in)


# 2. Beneficios Institucionales
@router.get("/beneficios")
async def get_my_benefits(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Consultar los beneficios institucionales asignados al aprendiz."""
    aprendiz_id = _resolve_aprendiz_id(current_user)
    beneficios = await PortalService.get_beneficios(db, aprendiz_id)
    return [
        {
            "id": b.id,
            "beneficio_id": b.beneficio_id,
            "beneficio_nombre": b.beneficio.nombre if b.beneficio else "Beneficio SENA",
            "estado": b.estado,
            "origen": b.origen,
            "observaciones": b.observaciones,
            "created_at": b.created_at
        }
        for b in beneficios
    ]


@router.post("/beneficios", status_code=status.HTTP_201_CREATED)
async def registrar_my_benefit(
    ben_in: PortalBeneficioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Registrar o reportar un beneficio institucional desde el portal del aprendiz."""
    aprendiz_id = _resolve_aprendiz_id(current_user)
    b = await PortalService.registrar_beneficio(db, aprendiz_id, ben_in)
    return {
        "id": b.id,
        "beneficio_id": b.beneficio_id,
        "beneficio_nombre": b.beneficio.nombre if b.beneficio else "Beneficio SENA",
        "estado": b.estado,
        "origen": b.origen,
        "observaciones": b.observaciones,
        "created_at": b.created_at
    }


# 3. Contratos de Aprendizaje
@router.get("/contratos")
async def get_my_contracts(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Consultar los contratos de aprendizaje registrados para el aprendiz."""
    aprendiz_id = _resolve_aprendiz_id(current_user)
    contratos = await PortalService.get_contratos(db, aprendiz_id)
    return [
        {
            "id": c.id,
            "matricula_id": c.matricula_id,
            "nombre_empresa": c.nombre_empresa,
            "departamento": c.departamento,
            "ciudad": c.ciudad,
            "fecha_inicio_contrato": str(c.fecha_inicio_contrato),
            "fecha_fin_contrato": str(c.fecha_fin_contrato) if c.fecha_fin_contrato else None,
            "estado_contrato": c.estado_contrato,
            "observaciones": c.observaciones,
            "created_at": c.created_at
        }
        for c in contratos
    ]


@router.post("/contratos", status_code=status.HTTP_201_CREATED)
async def registrar_my_contract(
    contrato_in: PortalContratoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Registrar o diligenciar un nuevo contrato de aprendizaje desde el portal del aprendiz."""
    aprendiz_id = _resolve_aprendiz_id(current_user)
    c = await PortalService.registrar_contrato(db, aprendiz_id, contrato_in)
    return {
        "id": c.id,
        "matricula_id": c.matricula_id,
        "nombre_empresa": c.nombre_empresa,
        "departamento": c.departamento,
        "ciudad": c.ciudad,
        "fecha_inicio_contrato": str(c.fecha_inicio_contrato),
        "fecha_fin_contrato": str(c.fecha_fin_contrato) if c.fecha_fin_contrato else None,
        "estado_contrato": c.estado_contrato,
        "observaciones": c.observaciones,
        "created_at": c.created_at
    }


@router.put("/contratos/{contrato_id}")
async def update_my_contract(
    contrato_id: int,
    contrato_in: PortalContratoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Actualizar la información de un contrato de aprendizaje propio."""
    aprendiz_id = _resolve_aprendiz_id(current_user)
    c = await PortalService.update_contrato(db, aprendiz_id, contrato_id, contrato_in)
    return {
        "id": c.id,
        "matricula_id": c.matricula_id,
        "nombre_empresa": c.nombre_empresa,
        "departamento": c.departamento,
        "ciudad": c.ciudad,
        "fecha_inicio_contrato": str(c.fecha_inicio_contrato),
        "fecha_fin_contrato": str(c.fecha_fin_contrato) if c.fecha_fin_contrato else None,
        "estado_contrato": c.estado_contrato,
        "observaciones": c.observaciones,
        "created_at": c.created_at
    }


# 4. Encuestas Dinámicas y Respuestas Longitudinales
@router.get("/encuestas-pendientes")
async def get_encuestas_pendientes(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener dinámicamente las encuestas institucionales activas y pendientes para el aprendiz."""
    aprendiz_id = _resolve_aprendiz_id(current_user)
    return await PortalService.get_encuestas_pendientes(db, aprendiz_id)


@router.post("/responder", response_model=List[RespuestaRead], status_code=status.HTTP_201_CREATED)
async def responder_encuesta(
    batch_in: BatchRespuestaCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Diligenciar respuestas de encuesta. Registra las respuestas en formato longitudinal inmutable."""
    aprendiz_id = _resolve_aprendiz_id(current_user)
    batch_in.aprendiz_id = aprendiz_id
    batch_in.origen = "PORTAL_APRENDIZ"
    ip = request.client.host if request.client else None

    return await ResponsesService.record_batch_responses(
        db, batch_in=batch_in, user_id=None, ip_origen=ip
    )


@router.get("/mi-historial", response_model=List[RespuestaHistorialRead])
async def get_mi_historial(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener el historial longitudinal de respuestas del aprendiz en el tiempo."""
    aprendiz_id = _resolve_aprendiz_id(current_user)
    return await ResponsesService.get_aprendiz_history(db, aprendiz_id)
