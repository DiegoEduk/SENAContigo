from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.modules.variables.schemas import VariableRead


class CorteEncuestaBase(BaseModel):
    nombre_corte: str
    descripcion: Optional[str] = None


class CorteEncuestaCreate(CorteEncuestaBase):
    pass


class CorteEncuestaRead(CorteEncuestaBase):
    id: int
    encuesta_id: int
    fecha_corte: datetime
    model_config = ConfigDict(from_attributes=True)


class EncuestaVariableRead(BaseModel):
    variable_id: int
    orden: int
    variable: Optional[VariableRead] = None
    model_config = ConfigDict(from_attributes=True)


class EncuestaBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    tipo: str = "seguimiento_emergencia"
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    estado: str = "publicada"
    segmento_id: Optional[int] = None


class EncuestaCreate(EncuestaBase):
    variables_ids: List[int] = []


class EncuestaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None
    segmento_id: Optional[int] = None
    variables_ids: Optional[List[int]] = None


class EncuestaRead(EncuestaBase):
    id: int
    created_at: datetime
    variables_asociadas: List[EncuestaVariableRead] = []
    cortes: List[CorteEncuestaRead] = []
    model_config = ConfigDict(from_attributes=True)
