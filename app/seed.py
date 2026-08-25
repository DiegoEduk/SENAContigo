import asyncio
import traceback
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.modules.identity.models import Rol, Usuario
from app.modules.organization.models import Regional, CentroFormacion


async def seed_data():
    from app.core.database import Base, engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        try:
            print("🌱 Inicializando roles y usuario SuperAdmin en SENAContigo...")

            # 1. Crear Roles del Sistema
            roles_data = [
                ("superadmin", "Administrador Global Nacional con acceso a todo el sistema"),
                ("direccion", "Dirección de Regional con acceso a todos sus centros"),
                ("coordinador", "Coordinador de Centro de Formación"),
                ("instructor", "Instructor encargado de fichas específicas"),
                ("aprendiz", "Aprendiz SENA"),
                ("lider_bienestar", "Líder de Bienestar con acceso completo al módulo de beneficios"),
                ("lider_contratacion", "Líder de Contratación con acceso completo al módulo de contratos de aprendizaje")
            ]

            roles_dict = {}
            for r_name, r_desc in roles_data:
                res = await session.execute(select(Rol).where(Rol.nombre == r_name))
                rol_obj = res.scalar_one_or_none()
                if not rol_obj:
                    rol_obj = Rol(nombre=r_name, descripcion=r_desc, activo=True)
                    session.add(rol_obj)
                    await session.flush()
                roles_dict[r_name] = rol_obj

            # 2. Crear Regional y Centro Inicial por defecto
            res_reg = await session.execute(select(Regional).where(Regional.codigo_regional == "11"))
            reg = res_reg.scalar_one_or_none()
            if not reg:
                reg = Regional(codigo_regional="11", nombre="REGIONAL DISTRITO CAPITAL", activo=True)
                session.add(reg)
                await session.flush()

            res_centro = await session.execute(select(CentroFormacion).where(CentroFormacion.codigo_centro == "9201"))
            centro = res_centro.scalar_one_or_none()
            if not centro:
                centro = CentroFormacion(
                    codigo_centro="9201",
                    nombre="CENTRO DE DISEÑO Y METROLOGÍA",
                    regional_id=reg.codigo_regional,
                    activo=True
                )
                session.add(centro)
                await session.flush()

            # 3. Crear Usuario SuperAdmin
            res_admin = await session.execute(select(Usuario).where(Usuario.correo == "admin@senacontigo.edu.co"))
            admin = res_admin.scalar_one_or_none()
            if not admin:
                superadmin_role = roles_dict.get("superadmin")
                admin = Usuario(
                    tipo_documento="CC",
                    numero_documento="1000000000",
                    nombres="SuperAdmin",
                    apellidos="SENAContigo",
                    correo="admin@senacontigo.edu.co",
                    hashed_password=get_password_hash("Admin123456*"),
                    celular="3000000000",
                    regional_id=None,
                    centro_id=None,
                    activo=True,
                    roles=[superadmin_role] if superadmin_role else []
                )
                session.add(admin)

            # Usuarios auxiliares para roles de prueba del sistema
            res_bienestar = await session.execute(select(Usuario).where(Usuario.correo == "bienestar@senacontigo.edu.co"))
            if not res_bienestar.scalar_one_or_none():
                bienestar_role = roles_dict.get("lider_bienestar")
                u_b = Usuario(
                    tipo_documento="CC",
                    numero_documento="1000000001",
                    nombres="Líder",
                    apellidos="Bienestar",
                    correo="bienestar@senacontigo.edu.co",
                    hashed_password=get_password_hash("Bienestar123456*"),
                    celular="3001112233",
                    regional_id="11",
                    centro_id="9201",
                    activo=True,
                    roles=[bienestar_role] if bienestar_role else []
                )
                session.add(u_b)

            res_contratacion = await session.execute(select(Usuario).where(Usuario.correo == "contratacion@senacontigo.edu.co"))
            if not res_contratacion.scalar_one_or_none():
                contratacion_role = roles_dict.get("lider_contratacion")
                u_c = Usuario(
                    tipo_documento="CC",
                    numero_documento="1000000002",
                    nombres="Líder",
                    apellidos="Contratación",
                    correo="contratacion@senacontigo.edu.co",
                    hashed_password=get_password_hash("Contratacion123456*"),
                    celular="3002223344",
                    regional_id="11",
                    centro_id="9201",
                    activo=True,
                    roles=[contratacion_role] if contratacion_role else []
                )
                session.add(u_c)

            await session.commit()
            print("✅ Inicialización de roles y SuperAdmin completada exitosamente.")
        except Exception as e:
            await session.rollback()
            print(f"❌ Error durante la inicialización de datos seed: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(seed_data())
