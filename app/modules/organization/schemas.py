from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CentroFormacionBase(BaseModel):
    codigo_centro: str
    nombre: str
    regional_id: int
    activo: bool = True


class CentroFormacionCreate(CentroFormacionBase):
    pass


class CentroFormacionUpdate(BaseModel):
    nombre: Optional[str] = None
    activo: Optional[bool] = None


class CentroFormacionRead(CentroFormacionBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RegionalBase(BaseModel):
    codigo_regional: str
    nombre: str
    activo: bool = True


class RegionalCreate(RegionalBase):
    pass


class RegionalUpdate(BaseModel):
    nombre: Optional[str] = None
    activo: Optional[bool] = None


class RegionalRead(RegionalBase):
    id: int
    created_at: datetime
    centros: List[CentroFormacionRead] = []
    model_config = ConfigDict(from_attributes=True)
