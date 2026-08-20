from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ContratoBase(BaseModel):
    nombre_empresa: str
    departamento: str
    ciudad: str
    fecha_inicio_contrato: date
    fecha_fin_contrato: Optional[date] = None
    estado_contrato: str = "EN PATROCINIO"
    observaciones: Optional[str] = None


class ContratoCreate(ContratoBase):
    matricula_id: int


class ContratoUpdate(BaseModel):
    nombre_empresa: Optional[str] = None
    departamento: Optional[str] = None
    ciudad: Optional[str] = None
    fecha_inicio_contrato: Optional[date] = None
    fecha_fin_contrato: Optional[date] = None
    estado_contrato: Optional[str] = None
    observaciones: Optional[str] = None


class ContratoMatriculaInfo(BaseModel):
    id: int
    aprendiz_id: int
    ficha_id: str
    estado_matricula: str
    model_config = ConfigDict(from_attributes=True)


class ContratoAprendizInfo(BaseModel):
    id: int
    numero_documento: str
    nombres: str
    apellidos: str
    correo: str
    model_config = ConfigDict(from_attributes=True)


class ContratoRead(ContratoBase):
    id: int
    matricula_id: int
    created_at: datetime
    updated_at: datetime
    
    # Extra helper fields for detailed responses
    ficha_id: Optional[str] = None
    aprendiz_id: Optional[int] = None
    aprendiz_nombre_completo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
