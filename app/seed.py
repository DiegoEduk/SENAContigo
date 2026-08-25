import asyncio
import os
import traceback
import xml.etree.ElementTree as ET
from sqlalchemy import select
import app.api.router
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.modules.identity.models import Rol, Usuario
from app.modules.organization.models import CentroFormacion, Regional
from app.modules.academic.models import Ficha, ProgramaFormacion
from app.modules.variables.models import CategoriaVariable
from app.modules.needs.models import TipoCaso

from app.modules.apprentices.models import Aprendiz, Matricula
from app.modules.contracts.models import ContratoAprendizaje
from app.modules.cases.models import Caso
from app.modules.benefits.models import Beneficio, AprendizBeneficio
from datetime import datetime, date


async def seed_data():
    from app.core.database import Base, engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        try:
            print("🌱 Iniciando poblamiento de datos iniciales en SENAContigo...")

            # 1. Crear Roles
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

            # 3. Crear Usuarios Iniciales (SuperAdmin, Líder Bienestar, Líder Contratación)
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
                                    programa_version=p_info[1],
                                    departamento="BOGOTÁ D.C.",
                                    ciudad="BOGOTÁ D.C."
                                ))
                            else:
                                f_obj.fecha_inicial = d_start
                                f_obj.fecha_final = d_end
                                f_obj.estado_ficha = f_item['estado']
                                f_obj.centro_id = f_item['cod_centro']
                                f_obj.programa_codigo = p_info[0]
                                f_obj.programa_version = p_info[1]
                                if not f_obj.departamento:
                                    f_obj.departamento = "BOGOTÁ D.C."
                                if not f_obj.ciudad:
                                    f_obj.ciudad = "BOGOTÁ D.C."
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
            excel_file = "AprendicesFicha3410079.xlsx"
            if os.path.exists(excel_file):
                try:
                    import pandas as pd
                    from app.modules.apprentices.models import Aprendiz, Matricula
                    df_apr = pd.read_excel(excel_file, skiprows=4, header=None)
                    df_apr.columns = ['tipo_documento', 'numero_documento', 'nombres', 'apellidos', 'celular', 'correo', 'estado']
                    
                    ficha_id_ex = '3410079'
                    for _, row_apr in df_apr.iterrows():
                        t_doc = str(row_apr['tipo_documento']).strip()
                        if t_doc.lower().startswith('tipo'):
                            continue
                        n_doc = str(row_apr['numero_documento']).strip()
                        nom = str(row_apr['nombres']).strip()
                        ape = str(row_apr['apellidos']).strip()
                        mail = str(row_apr['correo']).strip()
                        cel_raw = str(row_apr['celular']).strip().replace('.0', '') if pd.notna(row_apr['celular']) else None
                        cel = cel_raw if cel_raw and cel_raw.lower() != 'nan' else None
                        est = 'En formación' if 'FORMACION' in str(row_apr['estado']).upper() else str(row_apr['estado']).strip()

                        res_a = await session.execute(select(Aprendiz).where(Aprendiz.numero_documento == n_doc))
                        a_obj = res_a.scalar_one_or_none()
                        if not a_obj:
                            a_obj = Aprendiz(
                                tipo_documento=t_doc,
                                numero_documento=n_doc,
                                nombres=nom,
                                apellidos=ape,
                                correo=mail,
                                celular=cel,
                                activo=True
                            )
                            session.add(a_obj)
                            await session.flush()
                        
                        # Matricular en la ficha
                        res_m = await session.execute(
                            select(Matricula).where(
                                (Matricula.aprendiz_id == a_obj.id) &
                                (Matricula.ficha_id == ficha_id_ex)
                            )
                        )
                        if not res_m.scalar_one_or_none():
                            session.add(Matricula(
                                aprendiz_id=a_obj.id,
                                ficha_id=ficha_id_ex,
                                estado_matricula=est
                            ))
                    print(f"✅ Se poblaron aprendices y matrículas de la ficha {ficha_id_ex} desde {excel_file}")
                except Exception as ex_excel:
                    print(f"⚠️ Error cargando {excel_file}: {ex_excel}")

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

            # 6. Crear Catálogo de Tipos de Caso Iniciales
            tipos_caso_data = [
                ("APOYO_PSICOSOCIAL", "Acompañamiento y orientación psicosocial", "Orientación ante situaciones personales, familiares o emocionales que afecten al aprendiz.", "FAMILIA"),
                ("APOYO_ALIMENTACION", "Apoyo de alimentación", "Apoyo para aprendices con dificultades para cubrir sus necesidades alimentarias.", "ALIMENTACION"),
                ("APOYO_TRANSPORTE", "Apoyo de transporte", "Apoyo para facilitar el desplazamiento del aprendiz a sus actividades formativas.", "TRANSPORTE"),
                ("APOYO_CONECTIVIDAD", "Plan de datos y conectividad", "Apoyo para facilitar el acceso a Internet y la conectividad requerida para la formación.", "CONECTIVIDAD"),
                ("APOYO_EQUIPO_COMPUTO", "Acceso a equipo de cómputo", "Gestión de acceso a equipos necesarios para las actividades de formación.", "CONECTIVIDAD"),
                ("APOYO_INCLUSION", "Atención diferencial e inclusión", "Apoyo para superar barreras que afecten la participación en la formación.", "INCLUSION"),
                ("APOYO_ACADEMICO", "Acompañamiento académico", "Orientación ante dificultades que afecten el desempeño o avance académico.", "ACADEMICA"),
                ("APOYO_ETAPA_PRODUCTIVA", "Gestión de etapa productiva", "Orientación para facilitar la vinculación a una alternativa de etapa productiva.", "EMPLEO"),
                ("APOYO_PERMANENCIA", "Seguimiento para permanencia", "Seguimiento a factores que puedan afectar la continuidad del aprendiz.", "ACADEMICA"),
                ("APOYO_HABITACIONAL", "Apoyo para situación habitacional", "Orientación y gestión ante dificultades de vivienda o alojamiento.", "VIVIENDA")
            ]

            for tc_code, tc_name, tc_desc, tc_cat in tipos_caso_data:
                res_tc = await session.execute(select(TipoCaso).where(TipoCaso.codigo == tc_code))
                if not res_tc.scalar_one_or_none():
                    session.add(TipoCaso(codigo=tc_code, nombre=tc_name, descripcion=tc_desc, categoria_relacionada=tc_cat, activa=True))



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

            # 8. Crear Contratos de Aprendizaje Semilla de Ejemplo (si existen matrículas)
            from app.modules.apprentices.models import Matricula
            from app.modules.contracts.models import ContratoAprendizaje

            res_mats = await session.execute(select(Matricula).limit(5))
            mats = list(res_mats.scalars().all())
            if mats:
                # Matrícula 1: Contrato en Etapa Práctica
                mat1 = mats[0]
                res_c1 = await session.execute(
                    select(ContratoAprendizaje).where(ContratoAprendizaje.matricula_id == mat1.id)
                )
                if not res_c1.scalar_one_or_none():
                    session.add(ContratoAprendizaje(
                        matricula_id=mat1.id,
                        nombre_empresa="TECNOLOGÍA Y SISTEMAS S.A.S.",
                        departamento="BOGOTÁ D.C.",
                        ciudad="BOGOTÁ D.C.",
                        fecha_inicio_contrato=date(2025, 2, 1),
                        estado_contrato="EN ETAPA PRACTICA",
                        observaciones="Contrato de aprendizaje activo en desarrollo de software"
                    ))

                # Matrícula 2: Contrato en Patrocinio
                if len(mats) > 1:
                    mat2 = mats[1]
                    res_c2 = await session.execute(
                        select(ContratoAprendizaje).where(ContratoAprendizaje.matricula_id == mat2.id)
                    )
                    if not res_c2.scalar_one_or_none():
                        session.add(ContratoAprendizaje(
                            matricula_id=mat2.id,
                            nombre_empresa="SERVICIOS INFORMÁTICOS GLOBAL LTDA",
                            departamento="CUNDINAMARCA",
                            ciudad="SOACHA",
                            fecha_inicio_contrato=date(2025, 6, 15),
                            estado_contrato="EN PATROCINIO",
                            observaciones="Aprendiz apoyado por patrocinio empresarial durante etapa lectiva"
                        ))

            # 9. Crear Encuesta Inicial de Caracterización (sin la palabra 'Nacional')
            from app.modules.surveys.models import Encuesta, CorteEncuesta
            res_enc = await session.execute(select(Encuesta).where(Encuesta.titulo.like("%Caracterización Socioeconómica%")))
            enc_obj = res_enc.scalar_one_or_none()
            if not enc_obj:
                enc_obj = Encuesta(
                    titulo="Encuesta de Caracterización Socioeconómica y Bienestar SENA",
                    descripcion="Instrumento institucional para la caracterización socioeconómica, identificación de necesidades y medición de vulnerabilidad de los aprendices SENA.",
                    tipo="CARACTERIZACION",
                    estado="PUBLICADA",
                    fecha_inicio=date(2026, 1, 1),
                    fecha_fin=date(2026, 12, 31)
                )
                session.add(enc_obj)
                await session.flush()

                # Crear Corte de Encuesta Semilla
                corte_obj = CorteEncuesta(
                    encuesta_id=enc_obj.id,
                    nombre_corte="Corte I - 2026",
                    fecha_corte=datetime.now(),
                    descripcion="Primer corte de caracterización del año 2026"
                )
                session.add(corte_obj)
            else:
                if "Nacional" in enc_obj.titulo:
                    enc_obj.titulo = enc_obj.titulo.replace("Nacional ", "").replace(" Nacional", "")

            await session.commit()
            print("✅ Poblamiento de datos completado exitosamente.")
        except Exception as e:
            await session.rollback()
            print(f"❌ Error durante el poblamiento de datos seed: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(seed_data())
