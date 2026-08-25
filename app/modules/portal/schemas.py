from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class PerfilAprendizUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    correo: Optional[EmailStr] = None
    celular: Optional[str] = None
    direccion_vivienda: Optional[str] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None


class PortalBeneficioCreate(BaseModel):
    beneficio_id: int
    observaciones: Optional[str] = None


class PortalContratoCreate(BaseModel):
    nombre_empresa: str
    departamento: str
    ciudad: str
    fecha_inicio_contrato: date
    fecha_fin_contrato: Optional[date] = None
    estado_contrato: str = "EN PATROCINIO"
    observaciones: Optional[str] = None


class PortalContratoUpdate(BaseModel):
    nombre_empresa: Optional[str] = None
    departamento: Optional[str] = None
    ciudad: Optional[str] = None
    fecha_inicio_contrato: Optional[date] = None
    fecha_fin_contrato: Optional[date] = None
    estado_contrato: Optional[str] = None
    observaciones: Optional[str] = None


class PortalCasoCreate(BaseModel):
    tipo: str
    prioridad: Optional[str] = "MEDIA"
    necesidades_ids: List[int] = []


class PortalCasoUpdate(BaseModel):
    tipo: Optional[str] = None
    prioridad: Optional[str] = None


class PortalCasoAgregarNecesidades(BaseModel):
    necesidades_ids: List[int]

