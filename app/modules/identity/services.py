from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import DuplicateResourceException, NotFoundException, UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.modules.identity.models import Permiso, Rol, Usuario
from app.modules.identity.schemas import LoginRequest, RolCreate, TokenResponse, UsuarioCreate, UsuarioUpdate


class IdentityService:
    @staticmethod
    async def authenticate_user(session: AsyncSession, login_data: LoginRequest) -> TokenResponse:
        stmt = (
            select(Usuario)
            .where(Usuario.correo == login_data.correo)
            .options(selectinload(Usuario.roles).selectinload(Rol.permisos))
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise UnauthorizedException("Credenciales inválidas (correo o contraseña incorrectos)")

        if not user.activo:
            raise UnauthorizedException("La cuenta de usuario se encuentra desactivada")

        main_role = user.roles[0].nombre if user.roles else "aprendiz"
        token_payload = {
            "correo": user.correo,
            "rol": main_role,
            "regional_id": user.regional_id,
            "centro_id": user.centro_id,
            "aprendiz_id": user.aprendiz_id
        }

        access_token = create_access_token(subject=user.id, payload=token_payload)
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            usuario=user
        )

    @staticmethod
    async def authenticate_aprendiz(
        session: AsyncSession,
        numero_documento: str,
        ficha_caracterizacion: str
    ) -> dict:
        from app.modules.apprentices.models import Aprendiz
        
        # 1. Buscar aprendiz activo por documento
        stmt = (
            select(Aprendiz)
            .where(Aprendiz.numero_documento == numero_documento, Aprendiz.activo == True)
            .options(selectinload(Aprendiz.matriculas))
        )
        res = await session.execute(stmt)
        aprendiz = res.scalar_one_or_none()

        if not aprendiz:
            raise UnauthorizedException("No se encontró un aprendiz activo con el número de documento proporcionado.")

        # 2. Verificar que el aprendiz tenga matrícula en la ficha indicada
        matricula_valida = next((m for m in aprendiz.matriculas if m.ficha_id == ficha_caracterizacion), None)
        if not matricula_valida:
            raise UnauthorizedException(f"El aprendiz no se encuentra matriculado en la ficha de formación {ficha_caracterizacion}.")

        # 3. Obtener información de centro y regional desde la Ficha
        from app.modules.academic.models import Ficha
        ficha_stmt = select(Ficha).where(Ficha.ficha_caracterizacion == ficha_caracterizacion).options(selectinload(Ficha.centro))
        ficha_res = await session.execute(ficha_stmt)
        ficha_obj = ficha_res.scalar_one_or_none()
        centro_id = ficha_obj.centro_id if ficha_obj else None
        regional_id = ficha_obj.centro.regional_id if (ficha_obj and ficha_obj.centro) else None

        # 4. Generar Tokens
        token_payload = {
            "correo": aprendiz.correo,
            "rol": "aprendiz",
            "regional_id": regional_id,
            "centro_id": centro_id,
            "aprendiz_id": aprendiz.id,
            "ficha_id": ficha_caracterizacion
        }

        access_token = create_access_token(subject=aprendiz.id, payload=token_payload)
        refresh_token = create_refresh_token(subject=aprendiz.id)

        aprendiz_dict = {
            "id": aprendiz.id,
            "tipo_documento": aprendiz.tipo_documento,
            "numero_documento": aprendiz.numero_documento,
            "nombres": aprendiz.nombres,
            "apellidos": aprendiz.apellidos,
            "correo": aprendiz.correo,
            "celular": aprendiz.celular,
            "direccion_vivienda": aprendiz.direccion_vivienda,
            "ciudad": aprendiz.ciudad,
            "departamento": aprendiz.departamento,
            "activo": aprendiz.activo
        }

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "aprendiz": aprendiz_dict,
            "ficha_id": ficha_caracterizacion
        }

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int):
        stmt = (
            select(Usuario)
            .where(Usuario.id == user_id)
            .options(selectinload(Usuario.roles).selectinload(Rol.permisos))
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return user
        
        # Consultar si es un Aprendiz ingresado por enlace público
        from app.modules.apprentices.models import Aprendiz
        ap_stmt = select(Aprendiz).where(Aprendiz.id == user_id)
        ap_res = await session.execute(ap_stmt)
        aprendiz = ap_res.scalar_one_or_none()
        if aprendiz:
            return {
                "id": aprendiz.id,
                "tipo_documento": aprendiz.tipo_documento,
                "numero_documento": aprendiz.numero_documento,
                "nombres": aprendiz.nombres,
                "apellidos": aprendiz.apellidos,
                "correo": aprendiz.correo,
                "celular": aprendiz.celular,
                "regional_id": None,
                "centro_id": None,
                "aprendiz_id": aprendiz.id,
                "activo": aprendiz.activo,
                "created_at": aprendiz.created_at,
                "updated_at": aprendiz.updated_at,
                "roles": [{"id": 0, "nombre": "aprendiz", "descripcion": "Aprendiz SENA", "activo": True, "created_at": aprendiz.created_at, "permisos": []}]
            }

        raise NotFoundException("Usuario", user_id)


    @staticmethod
    async def list_users(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        centro_id: Optional[str] = None,
        regional_id: Optional[str] = None
    ) -> List[Usuario]:
        stmt = (
            select(Usuario)
            .options(selectinload(Usuario.roles).selectinload(Rol.permisos))
        )
        if centro_id:
            stmt = stmt.where(Usuario.centro_id == centro_id)
        elif regional_id:
            stmt = stmt.where(Usuario.regional_id == regional_id)

        stmt = stmt.offset(skip).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_user(session: AsyncSession, user_in: UsuarioCreate) -> Usuario:
        # Check existing email/document
        existing_stmt = select(Usuario).where(
            (Usuario.correo == user_in.correo) | (Usuario.numero_documento == user_in.numero_documento)
        )
        existing_res = await session.execute(existing_stmt)
        if existing_res.scalar_one_or_none():
            raise DuplicateResourceException("Ya existe un usuario registrado con este correo o número de documento.")

        hashed_pwd = get_password_hash(user_in.password)
        user = Usuario(
            tipo_documento=user_in.tipo_documento,
            numero_documento=user_in.numero_documento,
            nombres=user_in.nombres,
            apellidos=user_in.apellidos,
            correo=user_in.correo,
            hashed_password=hashed_pwd,
            celular=user_in.celular,
            regional_id=user_in.regional_id,
            centro_id=user_in.centro_id,
            aprendiz_id=user_in.aprendiz_id,
            activo=user_in.activo
        )

        if user_in.roles_ids:
            roles_stmt = select(Rol).where(Rol.id.in_(user_in.roles_ids))
            roles_res = await session.execute(roles_stmt)
            user.roles = list(roles_res.scalars().all())

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return await IdentityService.get_user_by_id(session, user.id)

    @staticmethod
    async def update_user(session: AsyncSession, user_id: int, user_in: UsuarioUpdate) -> Usuario:
        user = await IdentityService.get_user_by_id(session, user_id)
        
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            user.hashed_password = get_password_hash(update_data.pop("password"))
        
        if "roles_ids" in update_data and update_data["roles_ids"] is not None:
            roles_ids = update_data.pop("roles_ids")
            roles_stmt = select(Rol).where(Rol.id.in_(roles_ids))
            roles_res = await session.execute(roles_stmt)
            user.roles = list(roles_res.scalars().all())

        for field, value in update_data.items():
            setattr(user, field, value)

        await session.commit()
        await session.refresh(user)
        return await IdentityService.get_user_by_id(session, user.id)

    @staticmethod
    async def list_roles(session: AsyncSession) -> List[Rol]:
        stmt = select(Rol).options(selectinload(Rol.permisos))
        res = await session.execute(stmt)
        return list(res.scalars().all())
