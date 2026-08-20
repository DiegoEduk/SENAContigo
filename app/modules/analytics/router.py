from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token
from app.core.security import TokenData
from app.modules.analytics.schemas import DashboardSummary
from app.modules.analytics.services import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Dashboard y Analítica"])


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    regional_id: Optional[str] = None,
    centro_id: Optional[int] = None,
    ficha_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """Obtener resumen general de métricas para el Dashboard institucional (SENA, Regional, Centro o Ficha)."""
    # Enforce scoping if restricted
    if current_user.rol in ["direccion", "Dirección"] and current_user.regional_id:
        regional_id = current_user.regional_id
    elif current_user.rol in ["coordinador", "Coordinador"] and current_user.centro_id:
        centro_id = current_user.centro_id

    return await AnalyticsService.get_dashboard_summary(
        db, regional_id=regional_id, centro_id=centro_id, ficha_id=ficha_id
    )
