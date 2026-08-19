from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CategoriaVariableBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activa: bool = True


class CategoriaVariableCreate(CategoriaVariableBase):
    pass


class CategoriaVariableRead(CategoriaVariableBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OpcionVariableBase(BaseModel):
    codigo: str
    texto: str
    valor_numerico: int = 0
    orden: int = 0
    nivel_afectacion: int = 0
    activa: bool = True


class OpcionVariableCreate(OpcionVariableBase):
    pass


class OpcionVariableRead(OpcionVariableBase):
    id: int
    variable_version_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class VariableVersionBase(BaseModel):
    titulo_pregunta: str
    descripcion: Optional[str] = None
    activa: bool = True


class VariableVersionCreate(VariableVersionBase):
    opciones: List[OpcionVariableCreate] = []


class VariableVersionRead(VariableVersionBase):
    id: int
    variable_id: int
    numero_version: int
    created_at: datetime
    opciones: List[OpcionVariableRead] = []
    model_config = ConfigDict(from_attributes=True)


class VariableBase(BaseModel):
    categoria_id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    tipo_respuesta: str = "opcion_unica"
    es_sensible: bool = False
    es_obligatoria: bool = True
    activa: bool = True


class VariableCreate(VariableBase):
    titulo_pregunta: str
    opciones: List[OpcionVariableCreate] = []


class VariableUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    es_sensible: Optional[bool] = None
    es_obligatoria: Optional[bool] = None
    activa: Optional[bool] = None


class VariableRead(VariableBase):
    id: int
    version_actual: int
    created_at: datetime
    updated_at: datetime
    categoria: CategoriaVariableRead
    versiones: List[VariableVersionRead] = []
    model_config = ConfigDict(from_attributes=True)
