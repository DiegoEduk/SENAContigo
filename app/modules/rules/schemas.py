from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ReglaCondicionBase(BaseModel):
    variable_id: int
    opcion_id: Optional[int] = None
    operador: str = "EQUALS"
    valor_comparar: Optional[str] = None


class ReglaCondicionCreate(ReglaCondicionBase):
    pass


class ReglaCondicionRead(ReglaCondicionBase):
    id: int
    regla_id: int
    model_config = ConfigDict(from_attributes=True)


class ReglaAccionBase(BaseModel):
    tipo_accion: str
    necesidad_id: Optional[int] = None
    prioridad_caso: str = "MEDIA"
    titulo_caso: Optional[str] = None
    mensaje_notificacion: Optional[str] = None


class ReglaAccionCreate(ReglaAccionBase):
    pass


class ReglaAccionRead(ReglaAccionBase):
    id: int
    regla_id: int
    model_config = ConfigDict(from_attributes=True)


class ReglaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activa: bool = True
    prioridad: int = 1


class ReglaCreate(ReglaBase):
    condiciones: List[ReglaCondicionCreate] = []
    acciones: List[ReglaAccionCreate] = []


class ReglaRead(ReglaBase):
    id: int
    created_at: datetime
    condiciones: List[ReglaCondicionRead] = []
    acciones: List[ReglaAccionRead] = []
    model_config = ConfigDict(from_attributes=True)
