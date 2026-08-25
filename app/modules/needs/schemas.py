from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TipoCasoBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    categoria_relacionada: Optional[str] = None
    activa: bool = True


class TipoCasoCreate(TipoCasoBase):
    pass


class TipoCasoRead(TipoCasoBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Aliases
NecesidadBase = TipoCasoBase
NecesidadCreate = TipoCasoCreate
NecesidadRead = TipoCasoRead

