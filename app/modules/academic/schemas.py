from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProgramaFormacionBase(BaseModel):
    codigo_programa: str
    version: str = "1"
    nombre: str
    nivel_formacion: str
    activo: bool = True


class ProgramaFormacionCreate(ProgramaFormacionBase):
    pass


class ProgramaFormacionUpdate(BaseModel):
    nombre: Optional[str] = None
    version: Optional[str] = None
    nivel_formacion: Optional[str] = None
    activo: Optional[bool] = None


class ProgramaFormacionRead(ProgramaFormacionBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FichaBase(BaseModel):
    ficha_caracterizacion: str
    fecha_inicial: date
    fecha_final: date
    estado_ficha: str = "En ejecución"
    centro_id: int
    programa_id: int


class FichaCreate(FichaBase):
    pass


class FichaUpdate(BaseModel):
    fecha_inicial: Optional[date] = None
    fecha_final: Optional[date] = None
    estado_ficha: Optional[str] = None
    centro_id: Optional[int] = None
    programa_id: Optional[int] = None


class FichaRead(FichaBase):
    id: int
    created_at: datetime
    programa: Optional[ProgramaFormacionRead] = None
    model_config = ConfigDict(from_attributes=True)
