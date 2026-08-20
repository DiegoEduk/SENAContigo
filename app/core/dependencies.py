from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import TokenData, decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class OrganizationalScope:
    def __init__(
        self,
        user_id: int,
        rol: str,
        regional_id: Optional[str] = None,
        centro_id: Optional[int] = None,
        aprendiz_id: Optional[int] = None,
        fichas_ids: List[int] = None
    ):
        self.user_id = user_id
        self.rol = rol
        self.regional_id = regional_id
        self.centro_id = centro_id
        self.aprendiz_id = aprendiz_id
        self.fichas_ids = fichas_ids or []

    def is_superadmin(self) -> bool:
        return self.rol in ["superadmin", "SuperAdmin"]

    def is_direccion(self) -> bool:
        return self.rol in ["direccion", "Dirección", "Direccion"]

    def is_coordinador(self) -> bool:
        return self.rol in ["coordinador", "Coordinador"]

    def is_instructor(self) -> bool:
        return self.rol in ["instructor", "Instructor"]

    def is_aprendiz(self) -> bool:
        return self.rol in ["aprendiz", "Aprendiz"]


async def get_current_user_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedException("Token de acceso inválido o expirado")
    
    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedException("Subjet del token faltante")

    return TokenData(
        user_id=int(sub),
        correo=payload.get("correo", ""),
        rol=payload.get("rol", "aprendiz"),
        regional_id=payload.get("regional_id"),
        centro_id=payload.get("centro_id"),
        aprendiz_id=payload.get("aprendiz_id")
    )


def require_roles(allowed_roles: List[str]):
    """Role-Based Access Control (RBAC) dependency."""
    async def role_checker(token_data: TokenData = Depends(get_current_user_token)) -> TokenData:
        user_rol = token_data.rol.lower()
        allowed_lower = [r.lower() for r in allowed_roles]
        
        if "superadmin" in user_rol:
            return token_data
        
        if user_rol not in allowed_lower:
            raise ForbiddenException(f"Acceso denegado. Se requiere uno de los siguientes roles: {allowed_roles}")
        
        return token_data

    return role_checker
