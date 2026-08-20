from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# --- Beneficio Schemas ---

class BeneficioBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    tipo_beneficio: str = "INSTITUCIONAL_AUTOMATICO"
    es_automatico_matricula: bool = True
    activo: bool = True


class BeneficioCreate(BeneficioBase):
    pass


class BeneficioUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_beneficio: Optional[str] = None
    es_automatico_matricula: Optional[bool] = None
    activo: Optional[bool] = None


class BeneficioResponse(BeneficioBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- AprendizBeneficio Schemas ---

class AprendizBeneficioCreate(BaseModel):
    aprendiz_id: int
    beneficio_id: int
    origen: str = "ASIGNACION_DIRECTA"
    caso_id: Optional[int] = None
    observaciones: Optional[str] = None


class AprendizBeneficioUpdateState(BaseModel):
    estado: str  # ACTIVO, SUSPENDIDO, VENCIDO, FINALIZADO
    observaciones: Optional[str] = None


class AprendizBeneficioResponse(BaseModel):
    id: int
    aprendiz_id: int
    beneficio_id: int
    fecha_asignacion: datetime
    estado: str
    origen: str
    caso_id: Optional[int] = None
    observaciones: Optional[str] = None
    created_at: datetime
    beneficio: Optional[BeneficioResponse] = None

    model_config = ConfigDict(from_attributes=True)
