from datetime import datetime
from typing import Any, List, Optional, Union
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user_token
from app.core.security import TokenData
from app.modules.analytics.schemas import (
    DashboardSummary, TabulacionResponse, AllowedFiltersResponse, FilterOptionsResponse,
    BeneficiosAnalyticsResponse, CasosAnalyticsResponse, ContratacionAnalyticsResponse,
    ApprenticeListResponse, Apprentice360Response
)
from app.modules.analytics.services import AnalyticsService
from app.core.pdf_generator import generate_tabulation_pdf

router = APIRouter(prefix="/analytics", tags=["Dashboard y Analítica"])


@router.get("/allowed-filters", response_model=AllowedFiltersResponse)
async def get_allowed_filters(
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener la configuración de filtros autorizados según el rol del usuario."""
    return AnalyticsService.get_allowed_filters(current_user)


@router.get("/filter-options", response_model=FilterOptionsResponse)
async def get_filter_options(
    target: Optional[str] = None,
    q: Optional[str] = None,
    regional_id: Optional[List[str]] = Query(None),
    centro_id: Optional[List[str]] = Query(None),
    programa_codigo: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener las opciones dinámicas de selección de filtros con búsqueda (>4 caracteres) y en cascada."""
    return await AnalyticsService.get_filter_options(
        db,
        current_user,
        regional_id=regional_id,
        centro_id=centro_id,
        programa_codigo=programa_codigo,
        q=q,
        target=target
    )


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    regional_id: Optional[List[str]] = Query(None),
    centro_id: Optional[List[str]] = Query(None),
    ficha_id: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener resumen general de métricas para el Dashboard institucional (SENA, Regional, Centro o Ficha)."""
    # Enforce scoping if restricted
    if current_user.rol in ["direccion", "Dirección"] and current_user.regional_id:
        regional_id = [current_user.regional_id]
    elif current_user.rol in ["coordinador", "Coordinador", "instructor", "lider_bienestar", "lider_contratacion"] and current_user.centro_id:
        centro_id = [current_user.centro_id]

    return await AnalyticsService.get_dashboard_summary(
        db, regional_id=regional_id, centro_id=centro_id, ficha_id=ficha_id
    )


@router.get("/tabulation", response_model=TabulacionResponse)
async def get_tabulation_data(
    regional_id: Optional[List[str]] = Query(None),
    centro_id: Optional[List[str]] = Query(None),
    ficha_id: Optional[List[str]] = Query(None),
    programa_codigo: Optional[List[str]] = Query(None),
    nivel_riesgo: Optional[List[str]] = Query(None),
    categoria_id: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener la tabulación detallada de las 20 preguntas y 7 categorías con filtros autorizados por rol."""
    # Enforce scoping según el rol
    if current_user.rol in ["direccion", "Dirección"] and current_user.regional_id:
        regional_id = [current_user.regional_id]
    elif current_user.rol in ["coordinador", "Coordinador", "instructor", "lider_bienestar", "lider_contratacion"] and current_user.centro_id:
        centro_id = [current_user.centro_id]

    return await AnalyticsService.get_tabulation(
        db,
        regional_id=regional_id,
        centro_id=centro_id,
        ficha_id=ficha_id,
        programa_codigo=programa_codigo,
        nivel_riesgo=nivel_riesgo,
        categoria_id=categoria_id
    )


@router.get("/tabulation/export-pdf")
async def export_tabulation_pdf(
    regional_id: Optional[List[str]] = Query(None),
    centro_id: Optional[List[str]] = Query(None),
    ficha_id: Optional[List[str]] = Query(None),
    programa_codigo: Optional[List[str]] = Query(None),
    nivel_riesgo: Optional[List[str]] = Query(None),
    categoria_id: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Generar y descargar el informe institucional de tabulación en formato PDF."""
    # Enforce scoping según el rol
    if current_user.rol in ["direccion", "Dirección"] and current_user.regional_id:
        regional_id = [current_user.regional_id]
    elif current_user.rol in ["coordinador", "Coordinador", "instructor", "lider_bienestar", "lider_contratacion"] and current_user.centro_id:
        centro_id = [current_user.centro_id]

    tabulation_obj = await AnalyticsService.get_tabulation(
        db,
        regional_id=regional_id,
        centro_id=centro_id,
        ficha_id=ficha_id,
        programa_codigo=programa_codigo,
        nivel_riesgo=nivel_riesgo,
        categoria_id=categoria_id
    )

    tabulation_dict = tabulation_obj.model_dump()

    # Nombres legibles para el informe
    regional_nombre = "Todas las Regionales"
    centro_nombre = "Todos los Centros"
    ficha_nombre = ficha_id or "Todas las Fichas"

    if regional_id:
        from app.modules.organization.models import Regional
        res_r = await db.execute(select(Regional).where(Regional.codigo_regional == regional_id))
        reg_obj = res_r.scalar_one_or_none()
        if reg_obj:
            regional_nombre = reg_obj.nombre

    if centro_id:
        from app.modules.organization.models import CentroFormacion
        res_c = await db.execute(select(CentroFormacion).where(CentroFormacion.codigo_centro == centro_id))
        c_obj = res_c.scalar_one_or_none()
        if c_obj:
            centro_nombre = c_obj.nombre

    try:
        pdf_bytes = generate_tabulation_pdf(
            tabulation_data=tabulation_dict,
            regional_nombre=regional_nombre,
            centro_nombre=centro_nombre,
            ficha_codigo=ficha_nombre,
            generado_por=f"{current_user.correo} ({current_user.rol})"
        )
    except Exception as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error al generar el informe en PDF: {str(exc)}")

    filename = f"Informe_Tabulacion_SENAContigo_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/beneficios", response_model=BeneficiosAnalyticsResponse)
async def get_beneficios_analytics(
    regional_id: Optional[List[str]] = Query(None),
    centro_id: Optional[List[str]] = Query(None),
    ficha_id: Optional[List[str]] = Query(None),
    programa_codigo: Optional[List[str]] = Query(None),
    nivel_riesgo: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener el análisis estadístico de otorgamiento y cobertura de beneficios institucionales."""
    if current_user.rol in ["direccion", "Dirección"] and current_user.regional_id:
        regional_id = [current_user.regional_id]
    elif current_user.rol in ["coordinador", "Coordinador", "instructor", "lider_bienestar", "lider_contratacion"] and current_user.centro_id:
        centro_id = [current_user.centro_id]

    return await AnalyticsService.get_beneficios_analytics(
        db,
        regional_id=regional_id,
        centro_id=centro_id,
        ficha_id=ficha_id,
        programa_codigo=programa_codigo,
        nivel_riesgo=nivel_riesgo
    )


@router.get("/casos", response_model=CasosAnalyticsResponse)
async def get_casos_analytics(
    regional_id: Optional[List[str]] = Query(None),
    centro_id: Optional[List[str]] = Query(None),
    ficha_id: Optional[List[str]] = Query(None),
    programa_codigo: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener el análisis estadístico de casos de atención, seguimiento y alertas tempranas."""
    if current_user.rol in ["direccion", "Dirección"] and current_user.regional_id:
        regional_id = [current_user.regional_id]
    elif current_user.rol in ["coordinador", "Coordinador", "instructor", "lider_bienestar", "lider_contratacion"] and current_user.centro_id:
        centro_id = [current_user.centro_id]

    return await AnalyticsService.get_casos_analytics(
        db,
        regional_id=regional_id,
        centro_id=centro_id,
        ficha_id=ficha_id,
        programa_codigo=programa_codigo
    )


@router.get("/contratacion", response_model=ContratacionAnalyticsResponse)
async def get_contratacion_analytics(
    regional_id: Optional[List[str]] = Query(None),
    centro_id: Optional[List[str]] = Query(None),
    ficha_id: Optional[List[str]] = Query(None),
    programa_codigo: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener el análisis estadístico de patrocinio empresarial, vinculación laboral y contratos."""
    if current_user.rol in ["direccion", "Dirección"] and current_user.regional_id:
        regional_id = [current_user.regional_id]
    elif current_user.rol in ["coordinador", "Coordinador", "instructor", "lider_bienestar", "lider_contratacion"] and current_user.centro_id:
        centro_id = [current_user.centro_id]

    return await AnalyticsService.get_contratacion_analytics(
        db,
        regional_id=regional_id,
        centro_id=centro_id,
        ficha_id=ficha_id,
        programa_codigo=programa_codigo
    )


@router.get("/beneficios/aprendices", response_model=ApprenticeListResponse)
async def get_beneficios_aprendices(
    q: Optional[str] = None,
    regional_id: Optional[List[str]] = Query(None),
    centro_id: Optional[List[str]] = Query(None),
    ficha_id: Optional[List[str]] = Query(None),
    programa_codigo: Optional[List[str]] = Query(None),
    nivel_riesgo: Optional[List[str]] = Query(None),
    categoria_id: Optional[List[str]] = Query(None),
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener la tabla detallada de aprendices para el módulo de Beneficios Institucionales."""
    if current_user.rol in ["direccion", "Dirección"] and current_user.regional_id:
        regional_id = [current_user.regional_id]
    elif current_user.rol in ["coordinador", "Coordinador", "instructor", "lider_bienestar", "lider_contratacion"] and current_user.centro_id:
        centro_id = [current_user.centro_id]

    return await AnalyticsService.get_module_apprentices(
        db,
        modulo="beneficios",
        q=q,
        regional_id=regional_id,
        centro_id=centro_id,
        ficha_id=ficha_id,
        programa_codigo=programa_codigo,
        nivel_riesgo=nivel_riesgo,
        categoria_id=categoria_id,
        page=page,
        limit=limit
    )


@router.get("/casos/aprendices", response_model=ApprenticeListResponse)
async def get_casos_aprendices(
    q: Optional[str] = None,
    regional_id: Optional[List[str]] = Query(None),
    centro_id: Optional[List[str]] = Query(None),
    ficha_id: Optional[List[str]] = Query(None),
    programa_codigo: Optional[List[str]] = Query(None),
    nivel_riesgo: Optional[List[str]] = Query(None),
    categoria_id: Optional[List[str]] = Query(None),
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener la tabla detallada de aprendices para el módulo de Casos de Atención & Alertas."""
    if current_user.rol in ["direccion", "Dirección"] and current_user.regional_id:
        regional_id = [current_user.regional_id]
    elif current_user.rol in ["coordinador", "Coordinador", "instructor", "lider_bienestar", "lider_contratacion"] and current_user.centro_id:
        centro_id = [current_user.centro_id]

    return await AnalyticsService.get_module_apprentices(
        db,
        modulo="casos",
        q=q,
        regional_id=regional_id,
        centro_id=centro_id,
        ficha_id=ficha_id,
        programa_codigo=programa_codigo,
        nivel_riesgo=nivel_riesgo,
        categoria_id=categoria_id,
        page=page,
        limit=limit
    )


@router.get("/contratacion/aprendices", response_model=ApprenticeListResponse)
async def get_contratacion_aprendices(
    q: Optional[str] = None,
    regional_id: Optional[List[str]] = Query(None),
    centro_id: Optional[List[str]] = Query(None),
    ficha_id: Optional[List[str]] = Query(None),
    programa_codigo: Optional[List[str]] = Query(None),
    nivel_riesgo: Optional[List[str]] = Query(None),
    categoria_id: Optional[List[str]] = Query(None),
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener la tabla detallada de aprendices para el módulo de Contratación de Aprendices."""
    if current_user.rol in ["direccion", "Dirección"] and current_user.regional_id:
        regional_id = [current_user.regional_id]
    elif current_user.rol in ["coordinador", "Coordinador", "instructor", "lider_bienestar", "lider_contratacion"] and current_user.centro_id:
        centro_id = [current_user.centro_id]

    return await AnalyticsService.get_module_apprentices(
        db,
        modulo="contratacion",
        q=q,
        regional_id=regional_id,
        centro_id=centro_id,
        ficha_id=ficha_id,
        programa_codigo=programa_codigo,
        nivel_riesgo=nivel_riesgo,
        categoria_id=categoria_id,
        page=page,
        limit=limit
    )


@router.get("/aprendices/{aprendiz_id}/360", response_model=Apprentice360Response)
async def get_aprendiz_360(
    aprendiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener el perfil 360 completo de un aprendiz por su ID."""
    return await AnalyticsService.get_aprendiz_360_detail(db, aprendiz_id)



