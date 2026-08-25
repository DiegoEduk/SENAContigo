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


class OpcionTabulada(BaseModel):
    opcion_id: int
    codigo: str
    texto: str
    valor_numerico: int
    nivel_afectacion: int
    frecuencia_absoluta: int
    frecuencia_relativa: float
    model_config = ConfigDict(from_attributes=True)


class PreguntaTabulada(BaseModel):
    variable_id: int
    codigo_variable: str
    nombre_variable: str
    titulo_pregunta: str
    tipo_respuesta: str
    total_respuestas: int
    promedio_afectacion: float
    opciones: List[OpcionTabulada] = []
    model_config = ConfigDict(from_attributes=True)


class TabulacionCategoria(BaseModel):
    categoria_id: int
    codigo_categoria: str
    nombre_categoria: str
    total_respuestas_categoria: int
    promedio_afectacion_categoria: float
    preguntas: List[PreguntaTabulada] = []
    model_config = ConfigDict(from_attributes=True)


class KpiTabulacion(BaseModel):
    total_aprendices_caracterizados: int
    total_respuestas_registradas: int
    indice_vulnerabilidad_promedio: float
    porcentaje_vulnerabilidad_alta_critica: float
    aprendices_alerta_alimentaria: int
    aprendices_riesgo_desercion: int
    aprendices_sin_computador_internet: int
    model_config = ConfigDict(from_attributes=True)


class TabulacionResponse(BaseModel):
    kpis: KpiTabulacion
    categorias: List[TabulacionCategoria] = []
    distribucion_niveles_riesgo: Dict[str, int] = {}
    regional_id: Optional[str] = None
    centro_id: Optional[str] = None
    ficha_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class FilterItem(BaseModel):
    id: str
    label: str
    extra: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class AllowedFiltersResponse(BaseModel):
    allowed_filters: List[str] = []
    locked_values: Dict[str, str] = {}
    user_role: str
    model_config = ConfigDict(from_attributes=True)


class FilterOptionsResponse(BaseModel):
    regionales: List[FilterItem] = []
    centros: List[FilterItem] = []
    programas: List[FilterItem] = []
    fichas: List[FilterItem] = []
    niveles_riesgo: List[FilterItem] = []
    categorias: List[FilterItem] = []
    model_config = ConfigDict(from_attributes=True)


