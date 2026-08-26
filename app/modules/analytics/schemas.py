from typing import Any, Dict, List, Optional, Union
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
    regional_id: Optional[Union[str, List[str]]] = None
    centro_id: Optional[Union[str, List[str]]] = None
    ficha_id: Optional[Union[str, List[str]]] = None
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


class BeneficiosAnalyticsResponse(BaseModel):
    total_otorgamientos: int
    aprendices_beneficiados_unicos: int
    tasa_cobertura_porcentaje: float
    distribucion_por_tipo: Dict[str, int] = {}
    distribucion_por_riesgo: Dict[str, int] = {}
    desglose_centros: List[Dict[str, Any]] = []
    model_config = ConfigDict(from_attributes=True)


class CasosAnalyticsResponse(BaseModel):
    total_casos: int
    casos_abiertos: int
    casos_en_proceso: int
    casos_cerrados: int
    tasa_resolucion_porcentaje: float
    casos_criticos_altos_abiertos: int
    distribucion_por_estado: Dict[str, int] = {}
    distribucion_por_prioridad: Dict[str, int] = {}
    distribucion_por_tipo_atencion: Dict[str, int] = {}
    model_config = ConfigDict(from_attributes=True)


class ContratacionAnalyticsResponse(BaseModel):
    total_aprendices: int
    aprendices_contratados: int
    aprendices_sin_contrato: int
    tasa_patrocinio_porcentaje: float
    contratos_por_vencer_30d: int
    distribucion_por_tipo_contrato: Dict[str, int] = {}
    distribucion_por_estado_contrato: Dict[str, int] = {}
    top_empresas_patrocinadoras: List[Dict[str, Any]] = []
    model_config = ConfigDict(from_attributes=True)


class ApprenticeRow(BaseModel):
    id: int
    tipo_documento: str
    numero_documento: str
    nombres: str
    apellidos: str
    nombre_completo: str
    numero_ficha: str
    nombre_programa: str
    nivel_formacion: str
    detalle_modulo: Optional[str] = None
    nivel_riesgo: Optional[str] = None
    matricula_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class ApprenticeListResponse(BaseModel):
    items: List[ApprenticeRow] = []
    total: int = 0
    page: int = 1
    limit: int = 10
    total_pages: int = 1
    model_config = ConfigDict(from_attributes=True)


class BenefitDetailItem(BaseModel):
    id: int
    codigo: Optional[str] = None
    nombre: str
    tipo_beneficio: str
    fecha_asignacion: Optional[str] = None
    estado: str
    observaciones: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class CaseDetailItem(BaseModel):
    id: int
    prioridad: str
    estado: str
    origen: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_creacion: Optional[str] = None
    fecha_cierre: Optional[str] = None
    responsable_nombre: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ContractDetailItem(BaseModel):
    id: int
    nombre_empresa: str
    departamento: str
    ciudad: str
    fecha_inicio_contrato: Optional[str] = None
    fecha_fin_contrato: Optional[str] = None
    estado_contrato: str
    observaciones: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class Apprentice360Response(BaseModel):
    id: int
    tipo_documento: str
    numero_documento: str
    nombres: str
    apellidos: str
    nombre_completo: str
    correo: Optional[str] = None
    celular: Optional[str] = None
    direccion_vivienda: Optional[str] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None
    matricula_id: Optional[int] = None
    numero_ficha: Optional[str] = None
    nombre_programa: Optional[str] = None
    nivel_formacion: Optional[str] = None
    nombre_centro: Optional[str] = None
    nombre_regional: Optional[str] = None
    nivel_riesgo: Optional[str] = None
    beneficios: List[BenefitDetailItem] = []
    casos: List[CaseDetailItem] = []
    contratos: List[ContractDetailItem] = []
    model_config = ConfigDict(from_attributes=True)




