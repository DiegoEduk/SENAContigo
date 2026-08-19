from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.modules.identity.schemas import UsuarioRead


class SeguimientoCasoBase(BaseModel):
    caso_id: int
    observacion: str
    estado_caso_resultante: Optional[str] = None


class SeguimientoCasoCreate(SeguimientoCasoBase):
    pass


class SeguimientoCasoRead(SeguimientoCasoBase):
    id: int
    usuario_id: int
    created_at: datetime
    usuario: Optional[UsuarioRead] = None
    model_config = ConfigDict(from_attributes=True)
