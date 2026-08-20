from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.academic.models import Ficha
from app.modules.apprentices.models import Aprendiz
from app.modules.cases.models import Caso
from app.modules.responses.models import Respuesta
from app.modules.variables.models import OpcionVariable
from app.modules.analytics.schemas import DashboardSummary


class AnalyticsService:
    @staticmethod
    async def get_dashboard_summary(
        session: AsyncSession,
        regional_id: Optional[str] = None,
        centro_id: Optional[int] = None,
        ficha_id: Optional[int] = None
    ) -> DashboardSummary:
        # Filter aprendices based on org level
        stmt_apr = select(func.count(Aprendiz.id))
        if regional_id:
            stmt_apr = stmt_apr.where(Aprendiz.regional_id == regional_id)
        if centro_id:
            stmt_apr = stmt_apr.where(Aprendiz.centro_id == centro_id)

        res_apr = await session.execute(stmt_apr)
        total_aprendices = res_apr.scalar() or 0

        # Count cases by state
        stmt_cases = select(Caso.estado, func.count(Caso.id)).group_by(Caso.estado)
        res_cases = await session.execute(stmt_cases)
        casos_by_state = {row[0]: row[1] for row in res_cases.all()}

        total_casos_abiertos = sum(v for k, v in casos_by_state.items() if k in ["NUEVO", "ASIGNADO", "EN_ATENCION", "ESCALADO"])

        # Count critical cases
        stmt_crit = select(func.count(Caso.id)).where(Caso.prioridad == "CRITICA")
        res_crit = await session.execute(stmt_crit)
        total_casos_criticos = res_crit.scalar() or 0

        # Count affected vs non affected based on latest response level > 0
        stmt_resp = select(func.count(func.distinct(Respuesta.aprendiz_id))).join(OpcionVariable, Respuesta.opcion_id == OpcionVariable.id).where(OpcionVariable.nivel_afectacion > 0)
        res_resp = await session.execute(stmt_resp)
        total_afectados = res_resp.scalar() or 0

        total_no_afectados = max(0, total_aprendices - total_afectados)
        porcentaje = round((total_afectados / total_aprendices * 100), 2) if total_aprendices > 0 else 0.0

        return DashboardSummary(
            total_aprendices=total_aprendices,
            total_afectados=total_afectados,
            total_no_afectados=total_no_afectados,
            porcentaje_afectacion=porcentaje,
            total_casos_abiertos=total_casos_abiertos,
            total_casos_criticos=total_casos_criticos,
            casos_por_estado=casos_by_state,
            afectacion_por_categoria={}
        )
