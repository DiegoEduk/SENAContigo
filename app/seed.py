import asyncio
import os
import traceback
import xml.etree.ElementTree as ET
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.modules.identity.models import Rol, Usuario
from app.modules.organization.models import CentroFormacion, Regional
from app.modules.academic.models import Ficha, ProgramaFormacion
from app.modules.variables.models import CategoriaVariable
from app.modules.needs.models import Necesidad
from app.modules.benefits.models import Beneficio
from datetime import datetime, date


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
                    regional_id=reg.codigo_regional,
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
                    regional_id=None,
                    centro_id=None,
                    activo=True,
                    roles=[superadmin_role] if superadmin_role else []
                )
                session.add(admin)

            # 4. Poblar Programas de Formación y Fichas desde DF-49_1.xml
            xml_file = "DF-49_1.xml"
            if os.path.exists(xml_file):
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    ns = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}
                    table = root.find('.//ss:Table', ns)
                    rows = table.findall('ss:Row', ns) if table is not None else []
                    header_idx = None
                    programs = {}
                    fichas_raw = []

                    for row_idx, row in enumerate(rows):
                        cells_data = {}
                        current_col = 1
                        for cell in row.findall('ss:Cell', ns):
                            idx_attr = cell.attrib.get('{urn:schemas-microsoft-com:office:spreadsheet}Index')
                            if idx_attr:
                                current_col = int(idx_attr)
                            data_el = cell.find('ss:Data', ns)
                            val = data_el.text.strip() if data_el is not None and data_el.text else ''
                            cells_data[current_col] = val
                            current_col += 1

                        if 5 in cells_data and cells_data[5] == 'FICHA_CARACTERIZACION':
                            header_idx = row_idx
                            continue

                        if header_idx is not None and row_idx > header_idx:
                            cod_centro = cells_data.get(3, '')
                            ficha_num = cells_data.get(5, '')
                            f_init_raw = cells_data.get(6, '')
                            f_fin_raw = cells_data.get(7, '')
                            est_ficha = cells_data.get(8, '')
                            cod = cells_data.get(9, '')
                            ver = cells_data.get(10, '1')
                            prog = cells_data.get(11, '')
                            nivel = cells_data.get(12, '')

                            if cod and prog and nivel:
                                if cod not in programs or int(ver) >= int(programs[cod]['ver']):
                                    programs[cod] = {'cod': cod, 'ver': ver, 'prog': prog[:200], 'nivel': nivel[:50]}

                            if ficha_num and cod_centro and cod:
                                f_init = f_init_raw.split(' ')[0] if ' ' in f_init_raw else f_init_raw
                                f_fin = f_fin_raw.split(' ')[0] if ' ' in f_fin_raw else f_fin_raw
                                fichas_raw.append({
                                    'ficha': ficha_num,
                                    'f_init': f_init,
                                    'f_fin': f_fin,
                                    'estado': est_ficha,
                                    'cod_centro': cod_centro,
                                    'cod_prog': cod,
                                    'ver_prog': ver
                                })

                    # Seed Programs
                    progs_db_map = {}
                    for cod, item in programs.items():
                        res_p = await session.execute(
                            select(ProgramaFormacion).where(
                                (ProgramaFormacion.codigo_programa == cod) &
                                (ProgramaFormacion.version == item['ver'])
                            )
                        )
                        p_obj = res_p.scalar_one_or_none()
                        if not p_obj:
                            p_obj = ProgramaFormacion(
                                codigo_programa=item['cod'],
                                version=item['ver'],
                                nombre=item['prog'],
                                nivel_formacion=item['nivel'],
                                activo=True
                            )
                            session.add(p_obj)
                            await session.flush()
                        else:
                            p_obj.nombre = item['prog']
                            p_obj.nivel_formacion = item['nivel']
                        progs_db_map[cod] = (item['cod'], item['ver'])

                    # Seed Fichas
                    for f_item in fichas_raw:
                        p_info = progs_db_map.get(f_item['cod_prog'])
                        if f_item['cod_centro'] and p_info:
                            res_f = await session.execute(select(Ficha).where(Ficha.ficha_caracterizacion == f_item['ficha']))
                            f_obj = res_f.scalar_one_or_none()
                            d_start = datetime.strptime(f_item['f_init'], "%Y-%m-%d").date() if f_item['f_init'] else date.today()
                            d_end = datetime.strptime(f_item['f_fin'], "%Y-%m-%d").date() if f_item['f_fin'] else date.today()

                            if not f_obj:
                                session.add(Ficha(
                                    ficha_caracterizacion=f_item['ficha'],
                                    fecha_inicial=d_start,
                                    fecha_final=d_end,
                                    estado_ficha=f_item['estado'],
                                    centro_id=f_item['cod_centro'],
                                    programa_codigo=p_info[0],
                                    programa_version=p_info[1]
                                ))
                            else:
                                f_obj.fecha_inicial = d_start
                                f_obj.fecha_final = d_end
                                f_obj.estado_ficha = f_item['estado']
                                f_obj.centro_id = f_item['cod_centro']
                                f_obj.programa_codigo = p_info[0]
                                f_obj.programa_version = p_info[1]

                except Exception as ex_xml:
                    print(f"⚠️ Error leyendo {xml_file}: {ex_xml}")
            else:
                default_progs = [
                    ("228118", "1", "ANALISIS Y DESARROLLO DE SOFTWARE.", "TECNÓLOGO"),
                    ("233108", "1", "GESTIÓN DE REDES DE DATOS", "TECNÓLOGO"),
                    ("220101", "1", "MANTENIMIENTO DE EQUIPOS DE CÓMPUTO", "TÉCNICO")
                ]
                for cod, ver, nom, niv in default_progs:
                    res_p = await session.execute(select(ProgramaFormacion).where(ProgramaFormacion.codigo_programa == cod))
                    if not res_p.scalar_one_or_none():
                        session.add(ProgramaFormacion(codigo_programa=cod, version=ver, nombre=nom, nivel_formacion=niv, activo=True))

            # 5. Crear Categorías de Variables Iniciales
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

            # 6. Crear Catálogo de Necesidades Iniciales
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

            # 7. Crear Catálogo de Beneficios Institucionales SENA por Defecto
            beneficios_data = [
                ("BEN-SOSTENIMIENTO", "Apoyo de Sostenimiento", "Apoyo económico mensual de sostenimiento regular o FIC para el proceso formativo del aprendiz SENA", "APOYO_FINANCIERO", True),
                ("BEN-TRANSPORTE", "Apoyo de Transporte", "Subsidio o auxilio de transporte institucional para facilitar el desplazamiento al centro de formación", "APOYO_FINANCIERO", True),
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
