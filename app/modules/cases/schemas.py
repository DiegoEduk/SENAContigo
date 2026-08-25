from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.modules.apprentices.schemas import AprendizRead
from app.modules.identity.schemas import UsuarioRead
from app.modules.needs.schemas import TipoCasoRead
from app.modules.followups.schemas import SeguimientoCasoRead


class CasoBase(BaseModel):
    aprendiz_id: int
    tipo_caso_id: Optional[int] = None
    descripcion: Optional[str] = None
    prioridad: str = "MEDIA"
    estado: str = "NUEVO"
    responsable_id: Optional[int] = None
    origen: str = "MANUAL"


class CasoCreate(CasoBase):
    pass


class CasoUpdate(BaseModel):
    tipo_caso_id: Optional[int] = None
    descripcion: Optional[str] = None
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    responsable_id: Optional[int] = None


class CasoRead(CasoBase):
    id: int
    fecha_creacion: datetime
    fecha_cierre: Optional[datetime] = None
    aprendiz: Optional[AprendizRead] = None
    responsable: Optional[UsuarioRead] = None
    tipo_caso: Optional[TipoCasoRead] = None
    seguimientos: List[SeguimientoCasoRead] = []
    model_config = ConfigDict(from_attributes=True)

