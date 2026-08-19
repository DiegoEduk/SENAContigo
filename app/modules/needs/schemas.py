from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NecesidadBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    categoria_relacionada: Optional[str] = None
    activa: bool = True


class NecesidadCreate(NecesidadBase):
    pass


class NecesidadRead(NecesidadBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
