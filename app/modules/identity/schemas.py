from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PermisoBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    modulo: str


class PermisoRead(PermisoBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RolBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


class RolCreate(RolBase):
    permisos_ids: Optional[List[int]] = []


class RolRead(RolBase):
    id: int
    created_at: datetime
    permisos: List[PermisoRead] = []
    model_config = ConfigDict(from_attributes=True)


class UsuarioBase(BaseModel):
    tipo_documento: str = "CC"
    numero_documento: str
    nombres: str
    apellidos: str
    correo: EmailStr
    celular: Optional[str] = None
    regional_id: Optional[str] = None
    centro_id: Optional[int] = None
    aprendiz_id: Optional[int] = None
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)
    roles_ids: Optional[List[int]] = []


class UsuarioUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    correo: Optional[EmailStr] = None
    celular: Optional[str] = None
    regional_id: Optional[str] = None
    centro_id: Optional[int] = None
    aprendiz_id: Optional[int] = None
    activo: Optional[bool] = None
    password: Optional[str] = None
    roles_ids: Optional[List[int]] = None


class UsuarioRead(UsuarioBase):
    id: int
    created_at: datetime
    updated_at: datetime
    roles: List[RolRead] = []
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    usuario: UsuarioRead
