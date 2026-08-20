import asyncio
import traceback
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.modules.identity.models import Rol, Usuario
from app.modules.organization.models import CentroFormacion, Regional
from app.modules.variables.models import CategoriaVariable
from app.modules.needs.models import Necesidad
from app.modules.benefits.models import Beneficio


async def seed_data():
    async with AsyncSessionLocal() as session:
        try:
            print("🌱 Iniciando poblamiento de datos iniciales en SENAContigo...")

            # 1. Crear Roles
            roles_data = [
                ("superadmin", "Administrador Global Nacional con acceso a todo el sistema"),
                ("direccion", "Dirección de Regional con acceso a todos sus centros"),
                ("coordinador", "Coordinador de Centro de Formación"),
                ("instructor", "Instructor encargado de fichas específicas"),
                ("aprendiz", "Aprendiz SENA")
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

            # 2. Crear Regional y Centro Inicial
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
                    regional_id=reg.id,
                    activo=True
                )
                session.add(centro)
                await session.flush()

            # 3. Crear Usuario SuperAdmin Inicial
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
                    regional_id=reg.id,
                    centro_id=centro.id,
                    activo=True,
                    roles=[superadmin_role] if superadmin_role else []
                )
                session.add(admin)

            # 4. Crear Categorías de Variables Iniciales
            categorias_data = [
                ("VIVIENDA", "Vivienda y Habitabilidad", "Preguntas sobre el estado de la vivienda y alojamiento"),
                ("TRANSPORTE", "Transporte y Movilidad", "Preguntas sobre facilidad de desplazamiento al centro de formación"),
                ("CONECTIVIDAD", "Tecnología y Conectividad", "Disponibilidad de equipo de cómputo e internet"),
                ("FAMILIA", "Situación Familiar", "Entorno familiar y personas a cargo"),
                ("EMPLEO", "Situación Laboral", "Vinculación laboral u ocupación actual"),
                ("ECONOMIA", "Situación Económica", "Ingresos y sostenibilidad financiera"),
                ("ALIMENTACION", "Alimentación y Nutrición", "Acceso a alimentación diaria")
            ]

            for cat_code, cat_name, cat_desc in categorias_data:
                res_cat = await session.execute(select(CategoriaVariable).where(CategoriaVariable.codigo == cat_code))
                if not res_cat.scalar_one_or_none():
                    session.add(CategoriaVariable(codigo=cat_code, nombre=cat_name, descripcion=cat_desc, activa=True))

            # 5. Crear Catálogo de Necesidades Iniciales
            necesidades_data = [
                ("ALOJAMIENTO", "Alojamiento Temporal", "Necesidad de reubicación o alojamiento de emergencia", "VIVIENDA"),
                ("CONECTIVIDAD", "Internet y Equipo Computacional", "Necesidad de plan de datos o préstamo de computador", "CONECTIVIDAD"),
                ("ALIMENTARIO", "Apoyo Alimentario", "Bono o paquete alimentario de emergencia", "ALIMENTACION"),
                ("ECONOMICO", "Apoyo Económico de Emergencia", "Auxilio económico temporal", "ECONOMIA"),
                ("PSICOLOGICO", "Acompañamiento Psicosocial", "Atención por bienestar al aprendiz", "FAMILIA"),
                ("FORMATIVO", "Riesgo de Deserción / Continuidad Formativa", "Plan de mejoramiento o reprogramación de guía", "EMPLEO")
            ]

            for nec_code, nec_name, nec_desc, nec_cat in necesidades_data:
                res_nec = await session.execute(select(Necesidad).where(Necesidad.codigo == nec_code))
                if not res_nec.scalar_one_or_none():
                    session.add(Necesidad(codigo=nec_code, nombre=nec_name, descripcion=nec_desc, categoria_relacionada=nec_cat, activa=True))

            # 6. Crear Catálogo de Beneficios Institucionales SENA por Defecto
            beneficios_data = [
                ("BEN-SEGURO", "Póliza de Seguro Estudiantil contra Accidentes", "Cobertura médica y seguro de accidentes personales durante el proceso formativo en el SENA", "SALUD_Y_PROTECCION", True),
                ("BEN-BIBLIOTECA", "Acceso a Sistema de Bibliotecas y Repositorio Digital", "Préstamo de material bibliográfico físico y acceso ilimitado a bases de datos digitales institucionales", "INSTITUCIONAL_AUTOMATICO", True),
                ("BEN-SALUD-PREV", "Atención Médica Preventiva y Enfermería de Centro", "Primeros auxilios, atención básica de enfermería y campañas de prevención de salud en el centro de formación", "SALUD_Y_PROTECCION", True),
                ("BEN-ORIENTACION-PSICO", "Orientación Psicosocial y Apoyo Emocional", "Acompañamiento y asesoría psicológica preventiva impartida por el equipo de Bienestar al Aprendiz", "INSTITUCIONAL_AUTOMATICO", True),
                ("BEN-ALIMENTACION", "Apoyo Alimentario Institucional / Refrigerios", "Apoyo nutricional de refrigerios o almuerzos asignado por la coordinación de bienestar", "APOYO_FINANCIERO", False),
                ("BEN-DEPORTES", "Programas de Cultura, Deporte y Recreación", "Participación libre en selecciones deportivas, actividades culturales y áreas de esparcimiento del SENA", "CULTURA_Y_DEPORTE", True)
            ]

            for ben_code, ben_name, ben_desc, ben_tipo, ben_auto in beneficios_data:
                res_ben = await session.execute(select(Beneficio).where(Beneficio.codigo == ben_code))
                if not res_ben.scalar_one_or_none():
                    session.add(Beneficio(
                        codigo=ben_code,
                        nombre=ben_name,
                        descripcion=ben_desc,
                        tipo_beneficio=ben_tipo,
                        es_automatico_matricula=ben_auto,
                        activo=True
                    ))

            await session.commit()
            print("✅ Poblamiento de datos completado exitosamente.")
        except Exception as e:
            await session.rollback()
            print(f"❌ Error durante el poblamiento de datos seed: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(seed_data())
