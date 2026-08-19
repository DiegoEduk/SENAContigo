from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.modules.identity.schemas import UsuarioRead


class AuditoriaLogBase(BaseModel):
    usuario_id: Optional[int] = None
    accion: str
    entidad: str
    entidad_id: Optional[str] = None
    valor_anterior: Optional[str] = None
    valor_nuevo: Optional[str] = None
    ip_origen: Optional[str] = None


class AuditoriaLogCreate(AuditoriaLogBase):
    pass


class AuditoriaLogRead(AuditoriaLogBase):
    id: int
    created_at: datetime
    usuario: Optional[UsuarioRead] = None
    model_config = ConfigDict(from_attributes=True)
