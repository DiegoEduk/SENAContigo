from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class MatriculaBase(BaseModel):
    aprendiz_id: int
    ficha_id: str
    estado_matricula: str = "En formación"


class MatriculaCreate(MatriculaBase):
    pass


class MatriculaUpdate(BaseModel):
    estado_matricula: Optional[str] = None


class MatriculaRead(MatriculaBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AprendizBase(BaseModel):
    tipo_documento: str = "CC"
    numero_documento: str
    nombres: str
    apellidos: str
    correo: EmailStr
    celular: Optional[str] = None
    direccion_vivienda: Optional[str] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None
    activo: bool = True


class AprendizCreate(AprendizBase):
    pass


class AprendizUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    correo: Optional[EmailStr] = None
    celular: Optional[str] = None
    direccion_vivienda: Optional[str] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None
    activo: Optional[bool] = None


class AprendizRead(AprendizBase):
    id: int
    created_at: datetime
    updated_at: datetime
    matriculas: List[MatriculaRead] = []
    model_config = ConfigDict(from_attributes=True)
