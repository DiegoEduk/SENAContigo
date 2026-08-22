from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class RespuestaInputItem(BaseModel):
    variable_id: int
    variable_version_id: Optional[int] = None
    opcion_id: Optional[int] = None
    valor_texto: Optional[str] = None
    valor_numero: Optional[float] = None


class BatchRespuestaCreate(BaseModel):
    aprendiz_id: Optional[int] = None
    encuesta_id: Optional[int] = None
    corte_id: Optional[int] = None
    origen: str = "web"
    respuestas: List[RespuestaInputItem]


class RespuestaRead(BaseModel):
    id: int
    aprendiz_id: int
    variable_id: int
    variable_version_id: int
    opcion_id: Optional[int] = None
    encuesta_id: Optional[int] = None
    corte_id: Optional[int] = None
    valor_texto: Optional[str] = None
    valor_numero: Optional[float] = None
    fecha_respuesta: datetime
    origen: str
    model_config = ConfigDict(from_attributes=True)


class HistorialItemDetalle(BaseModel):
    id: int
    fecha_respuesta: datetime
    respuesta_texto: str
    origen: str = "web"
    model_config = ConfigDict(from_attributes=True)


class RespuestaHistorialRead(BaseModel):
    variable_id: int
    variable_codigo: Optional[str] = None
    variable_nombre: Optional[str] = None
    pregunta_texto: Optional[str] = None
    orden: int = 0
    respuestas: List[HistorialItemDetalle] = []

    # Campos planos opcionales para compatibilidad previa
    id: Optional[int] = None
    fecha_respuesta: Optional[datetime] = None
    aprendiz_id: Optional[int] = None
    variable_version_id: Optional[int] = None
    respuesta_texto: Optional[str] = None
    origen: Optional[str] = "web"
    model_config = ConfigDict(from_attributes=True)


class EstadoActualAprendizItem(BaseModel):
    variable_id: int
    variable_nombre: str
    categoria_nombre: str
    ultima_medicion_fecha: datetime
    opcion_texto: Optional[str] = None
    nivel_afectacion: int = 0
    valor_texto: Optional[str] = None
    valor_numero: Optional[float] = None


class EstadoActualAprendiz(BaseModel):
    aprendiz_id: int
    total_variables_medidas: int
    nivel_afectacion_global: int
    indicador_afectacion_score: float
    estado_variables: List[EstadoActualAprendizItem] = []
