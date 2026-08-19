from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.modules.apprentices.schemas import AprendizRead
from app.modules.identity.schemas import UsuarioRead
from app.modules.needs.schemas import NecesidadRead


class CasoNecesidadRead(BaseModel):
    necesidad_id: int
    necesidad: Optional[NecesidadRead] = None
    model_config = ConfigDict(from_attributes=True)


class CasoBase(BaseModel):
    aprendiz_id: int
    tipo: str
    prioridad: str = "MEDIA"
    estado: str = "NUEVO"
    responsable_id: Optional[int] = None
    origen: str = "MANUAL"


class CasoCreate(CasoBase):
    necesidades_ids: List[int] = []


class CasoUpdate(BaseModel):
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    responsable_id: Optional[int] = None


class CasoRead(CasoBase):
    id: int
    fecha_creacion: datetime
    fecha_cierre: Optional[datetime] = None
    aprendiz: Optional[AprendizRead] = None
    responsable: Optional[UsuarioRead] = None
    necesidades_asociadas: List[CasoNecesidadRead] = []
    model_config = ConfigDict(from_attributes=True)
