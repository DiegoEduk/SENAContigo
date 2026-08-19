from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class MatriculaBase(BaseModel):
    aprendiz_id: int
    ficha_id: int
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
    centro_id: Optional[int] = None
    regional_id: Optional[int] = None
    activo: bool = True


class AprendizCreate(AprendizBase):
    pass


class AprendizUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    correo: Optional[EmailStr] = None
    celular: Optional[str] = None
    centro_id: Optional[int] = None
    regional_id: Optional[int] = None
    activo: Optional[bool] = None


class AprendizRead(AprendizBase):
    id: int
    created_at: datetime
    updated_at: datetime
    matriculas: List[MatriculaRead] = []
    model_config = ConfigDict(from_attributes=True)
