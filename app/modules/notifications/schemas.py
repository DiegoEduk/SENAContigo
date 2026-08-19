from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NotificacionBase(BaseModel):
    usuario_id: Optional[int] = None
    aprendiz_id: Optional[int] = None
    titulo: str
    mensaje: str
    tipo: str = "INFO"
    leida: bool = False


class NotificacionCreate(NotificacionBase):
    pass


class NotificacionRead(NotificacionBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
