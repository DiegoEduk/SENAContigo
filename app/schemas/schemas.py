from datetime import datetime
from typing import Optional, List, Any, Union
from pydantic import BaseModel, EmailStr, ConfigDict


# Auth Schemas
class LoginRequest(BaseModel):
    correo: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: "UsuarioResponse"


# Organization Schemas
class RegionalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo_regional: str
    nombre: str


class CentroFormacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo_centro: str
    nombre: str
    regional_id: int


class ProgramaFormacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo_programa: str
    version: str
    nombre: str
    nivel_formacion: str
    estado: str


class FichaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ficha_caracterizacion: str
    fecha_inicial: Optional[datetime] = None
    fecha_final: Optional[datetime] = None
    estado_ficha: str
    centro_id: int
    programa_id: int


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo_documento: str
    numero_documento: str
    nombres: str
    apellidos: str
    celular: Optional[str] = None
    correo_electronico: str
    rol: str
    centro_id: Optional[int] = None
    regional_id: Optional[int] = None
    activo: bool


# Dynamic Variables Schemas
class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    icono: Optional[str] = None
    orden: int = 0


class CategoriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    descripcion: Optional[str] = None
    icono: Optional[str] = None
    orden: int
    variables: List["VariableResponse"] = []


class OpcionVariableBase(BaseModel):
    codigo: str
    texto: str
    valor_numerico: float = 0.0
    orden: int = 0
    nivel_afectacion: int = 0  # 0: Sin afectación, 1: Leve, 2: Moderada, 3: Grave, 4: Crítica
    activa: bool = True


class OpcionVariableCreate(OpcionVariableBase):
    pass


class OpcionVariableResponse(OpcionVariableBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    variable_id: int
    version_id: Optional[int] = None


class VariableBase(BaseModel):
    categoria_id: int
    nombre: str
    codigo: str
    descripcion: Optional[str] = None
    tipo_respuesta: str = "opcion"  # opcion, texto, numero
    obligatoria: bool = True
    activa: bool = True


class VariableCreate(VariableBase):
    opciones: List[OpcionVariableCreate] = []


class VariableUpdate(BaseModel):
    categoria_id: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_respuesta: Optional[str] = None
    obligatoria: Optional[bool] = None
    activa: Optional[bool] = None
    descripcion_cambio: Optional[str] = "Actualización de opciones"
    opciones: Optional[List[OpcionVariableCreate]] = None


class VariableResponse(VariableBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fecha_creacion: Optional[datetime] = None
    opciones: List[OpcionVariableResponse] = []


# Surveys Schemas
class PreguntaEncuestaBase(BaseModel):
    variable_id: int
    orden: int = 0
    obligatoria: bool = True


class PreguntaEncuestaResponse(PreguntaEncuestaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    encuesta_id: int
    variable: Optional[VariableResponse] = None


class EncuestaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    estado: str = "activa"  # borrador, activa, cerrada
    tipo: str = "emergencia"  # inicial, seguimiento, emergencia
    segmento_filtro_json: Optional[Any] = None


class EncuestaCreate(EncuestaBase):
    variables_ids: List[int] = []


class EncuestaResponse(EncuestaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    preguntas: List[PreguntaEncuestaResponse] = []


# Responses Schemas (Longitudinal Responses)
class RespuestaItemCreate(BaseModel):
    variable_id: int
    opcion_id: Optional[int] = None
    respuesta_texto: Optional[str] = None
    observacion: Optional[str] = None


class RespuestasFormSubmission(BaseModel):
    encuesta_id: int
    respuestas: List[RespuestaItemCreate]


class RespuestaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    aprendiz_id: int
    encuesta_id: int
    variable_id: int
    opcion_id: Optional[int] = None
    respuesta_texto: Optional[str] = None
    fecha_respuesta: datetime
    observacion: Optional[str] = None
    opcion: Optional[OpcionVariableResponse] = None
    variable: Optional[VariableResponse] = None


# Dynamic Rules & Cases Schemas
class ReglaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    variable_id: int
    opcion_id: Optional[int] = None
    nivel_afectacion_minimo: Optional[int] = 3
    necesidad_id: int
    prioridad: str = "ALTA"  # BAJA, MEDIA, ALTA, CRITICA
    activa: bool = True


class ReglaResponse(ReglaCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class NecesidadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    prioridad_defecto: str
    categoria_id: Optional[int] = None


class CasoCreate(BaseModel):
    aprendiz_id: int
    necesidad_id: int
    titulo: str
    descripcion: Optional[str] = None
    prioridad: str = "ALTA"


class CasoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    aprendiz_id: int
    respuesta_origen_id: Optional[int] = None
    necesidad_id: int
    titulo: str
    descripcion: Optional[str] = None
    prioridad: str
    estado: str
    asignado_a_id: Optional[int] = None
    fecha_creacion: datetime
    fecha_cierre: Optional[datetime] = None
    aprendiz: Optional[UsuarioResponse] = None
    necesidad: Optional[NecesidadResponse] = None


class SeguimientoCasoCreate(BaseModel):
    comentario: str
    nuevo_estado: Optional[str] = None


class SeguimientoCasoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    caso_id: int
    usuario_id: int
    fecha: datetime
    comentario: str
    nuevo_estado: Optional[str] = None
    usuario: Optional[UsuarioResponse] = None


# Analytics Schemas
class ResumenAfectacionVariable(BaseModel):
    variable_nombre: str
    codigo: str
    sin_afectacion: int
    leve: int
    moderada: int
    grave: int
    critica: int
    total_respuestas: int


class EvolucionCorteHistorico(BaseModel):
    fecha_corte: str
    encuesta_nombre: str
    niveles: dict  # {"0": count, "1": count, "2": count, "3": count, "4": count}


class IndiceAfectacionAprendiz(BaseModel):
    aprendiz_id: int
    nombres: str
    apellidos: str
    ficha: str
    indice_total: float
    nivel_clasificacion: str  # BAJO, MODERADO, ALTO, CRITICO
