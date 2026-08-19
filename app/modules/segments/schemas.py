from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SegmentoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    regional_id: Optional[int] = None
    centro_id: Optional[int] = None
    programa_id: Optional[int] = None
    ficha_id: Optional[int] = None
    solo_afectados: bool = False
    nivel_afectacion_minimo: int = 0
    activo: bool = True


class SegmentoCreate(SegmentoBase):
    pass


class SegmentoRead(SegmentoBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
