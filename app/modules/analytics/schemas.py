from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class DashboardSummary(BaseModel):
    total_aprendices: int
    total_afectados: int
    total_no_afectados: int
    porcentaje_afectacion: float
    total_casos_abiertos: int
    total_casos_criticos: int
    casos_por_estado: Dict[str, int] = {}
    afectacion_por_categoria: Dict[str, int] = {}
    model_config = ConfigDict(from_attributes=True)
