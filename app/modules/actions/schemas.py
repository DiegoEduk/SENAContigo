from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AccionCasoBase(BaseModel):
    caso_id: int
    responsable_id: Optional[int] = None
    descripcion: str
    fecha_compromiso: Optional[date] = None
    fecha_ejecucion: Optional[date] = None
    estado: str = "PENDIENTE"
    observaciones: Optional[str] = None
    evidencia_url: Optional[str] = None


class AccionCasoCreate(AccionCasoBase):
    pass


class AccionCasoUpdate(BaseModel):
    estado: Optional[str] = None
    fecha_ejecucion: Optional[date] = None
    observaciones: Optional[str] = None
    evidencia_url: Optional[str] = None


class AccionCasoRead(AccionCasoBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
