import asyncio
import sys
import os
from datetime import datetime, date
from sqlalchemy import select, delete

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app.models  # noqa: F401
from app.core.database import AsyncSessionLocal, engine
from app.modules.variables.models import CategoriaVariable, Variable, VariableVersion, OpcionVariable
from app.modules.surveys.models import Encuesta, EncuestaVariable, CorteEncuesta
from app.modules.responses.models import Respuesta
from app.modules.cases.models import Caso, CasoNecesidad
from app.modules.rules.models import Regla, ReglaCondicion, ReglaAccion

NEW_SURVEY_QUESTIONS = [
    # 1. Vivienda y alojamiento
    {
        "orden": 1,
        "categoria_codigo": "VIVIENDA",
        "codigo": "ALOJAMIENTO_ACTUAL",
        "nombre": "Situación actual de alojamiento",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Dónde se encuentra alojado actualmente?",
        "opciones": [
            "Vivienda propia",
            "Vivienda arrendada",
            "Vivienda de un familiar",
            "Vivienda prestada o cedida",
            "Alojamiento temporal",
            "Albergue",
            "Sin alojamiento estable"
        ]
    },
    {
        "orden": 2,
        "categoria_codigo": "VIVIENDA",
        "codigo": "ESTADO_VIVIENDA",
        "nombre": "Estado de la vivienda",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿En qué estado se encuentra actualmente la vivienda donde reside?",
        "opciones": [
            "Sin afectación / En condiciones normales",
            "Afectada levemente",
            "Afectada moderadamente",
            "Inhabitable",
            "Destruida"
        ]
    },
    {
        "orden": 3,
        "categoria_codigo": "VIVIENDA",
        "codigo": "SERVICIO_AGUA",
        "nombre": "Servicio de agua",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Cómo se encuentra actualmente el servicio de agua de la vivienda donde reside?",
        "opciones": [
            "Cuenta con agua normalmente",
            "El servicio presenta interrupciones o fallas",
            "No tiene servicio de agua"
        ]
    },
    {
        "orden": 4,
        "categoria_codigo": "VIVIENDA",
        "codigo": "SERVICIO_ENERGIA",
        "nombre": "Servicio de energía eléctrica",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Cómo se encuentra actualmente el servicio de energía eléctrica de la vivienda donde reside?",
        "opciones": [
            "Funciona normalmente",
            "Funciona parcialmente o presenta fallas",
            "No tiene servicio de energía eléctrica"
        ]
    },
    {
        "orden": 5,
        "categoria_codigo": "VIVIENDA",
        "codigo": "SERVICIO_GAS",
        "nombre": "Servicio de gas",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Cómo se encuentra actualmente el servicio de gas de la vivienda donde reside?",
        "opciones": [
            "Cuenta con gas normalmente",
            "El servicio presenta interrupciones o fallas",
            "No tiene servicio de gas",
            "No utiliza este servicio"
        ]
    },

    # 2. Transporte y movilidad
    {
        "orden": 6,
        "categoria_codigo": "TRANSPORTE",
        "codigo": "ACCESO_TRANSPORTE",
        "nombre": "Acceso al transporte",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Cómo se encuentra actualmente su acceso al transporte que utiliza habitualmente?",
        "opciones": [
            "Puede utilizarlo normalmente",
            "Puede utilizarlo, pero presenta algunas dificultades",
            "Tiene dificultades importantes para utilizarlo",
            "No tiene acceso al transporte habitual"
        ]
    },
    {
        "orden": 7,
        "categoria_codigo": "TRANSPORTE",
        "codigo": "ACCESO_CENTRO",
        "nombre": "Acceso al centro de formación",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Actualmente puede desplazarse hasta su centro de formación para asistir a actividades presenciales?",
        "opciones": [
            "Sí, normalmente",
            "Sí, pero con dificultad",
            "No puede desplazarse actualmente"
        ]
    },

    # 3. Tecnología y conectividad
    {
        "orden": 8,
        "categoria_codigo": "CONECTIVIDAD",
        "codigo": "DISPONIBILIDAD_COMPUTADOR",
        "nombre": "Acceso a computador",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Tiene acceso a un computador adecuado para realizar sus actividades de formación?",
        "opciones": [
            "Sí, de uso personal",
            "Sí, pero debe compartirlo",
            "Sí, pero presenta dificultades o limitaciones",
            "No tiene acceso a un computador"
        ]
    },
    {
        "orden": 9,
        "categoria_codigo": "CONECTIVIDAD",
        "codigo": "ACCESO_INTERNET",
        "nombre": "Acceso a Internet",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Tiene actualmente acceso a una conexión a Internet adecuada para realizar su formación?",
        "opciones": [
            "Sí, estable",
            "Sí, pero es intermitente",
            "No tiene acceso a Internet"
        ]
    },
    {
        "orden": 10,
        "categoria_codigo": "CONECTIVIDAD",
        "codigo": "CONDICIONES_FORMACION_VIRTUAL",
        "nombre": "Condiciones para formación virtual",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Considera que actualmente cuenta con las condiciones necesarias para continuar su formación de manera virtual?",
        "opciones": [
            "Sí, sin dificultades",
            "Sí, pero con algunas dificultades",
            "No cuenta con las condiciones necesarias"
        ]
    },

    # 4. Grupo familiar
    {
        "orden": 11,
        "categoria_codigo": "FAMILIA",
        "codigo": "AFECTACION_FAMILIAR",
        "nombre": "Situación del grupo familiar",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿En qué nivel se encuentra afectado actualmente su grupo familiar por la situación que está atravesando?",
        "opciones": [
            "Sin afectación",
            "Afectación leve",
            "Afectación moderada",
            "Afectación grave",
            "Afectación crítica"
        ]
    },
    {
        "orden": 12,
        "categoria_codigo": "FAMILIA",
        "codigo": "PERSONAS_A_CARGO",
        "nombre": "Personas a cargo",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Cuántas personas dependen económicamente o requieren de su apoyo para su sostenimiento?",
        "opciones": [
            "Ninguna",
            "1 persona",
            "2 personas",
            "3 personas",
            "4 o más personas"
        ]
    },

    # 5. Situación laboral
    {
        "orden": 13,
        "categoria_codigo": "EMPLEO",
        "codigo": "SITUACION_LABORAL",
        "nombre": "Situación laboral actual",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Cuál es su situación laboral actual?",
        "opciones": [
            "Empleado",
            "Trabajador independiente",
            "Trabajador informal",
            "Desempleado y buscando empleo",
            "No trabaja actualmente"
        ]
    },
    {
        "orden": 14,
        "categoria_codigo": "EMPLEO",
        "codigo": "PERDIDA_EMPLEO",
        "nombre": "Pérdida reciente de empleo",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Ha perdido su empleo durante los últimos 6 meses?",
        "opciones": [
            "Sí",
            "No",
            "No tenía empleo durante ese período"
        ]
    },

    # 6. Situación económica
    {
        "orden": 15,
        "categoria_codigo": "ECONOMIA",
        "codigo": "SITUACION_INGRESOS",
        "nombre": "Situación actual de los ingresos",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Cómo se encuentra actualmente la situación de los ingresos de su hogar?",
        "opciones": [
            "Los ingresos se mantienen normalmente",
            "Han disminuido ligeramente",
            "Han disminuido considerablemente",
            "Han disminuido gravemente",
            "El hogar actualmente no tiene ingresos"
        ]
    },
    {
        "orden": 16,
        "categoria_codigo": "ECONOMIA",
        "codigo": "DIFICULTAD_NECESIDADES_BASICAS",
        "nombre": "Dificultad para cubrir necesidades básicas",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Actualmente tiene dificultades para cubrir las necesidades básicas de su hogar?",
        "opciones": [
            "No tiene dificultades",
            "Sí, ocasionalmente",
            "Sí, frecuentemente",
            "Sí, de manera grave"
        ]
    },
    {
        "orden": 17,
        "categoria_codigo": "ECONOMIA",
        "codigo": "REQUIERE_APOYO_ECONOMICO",
        "nombre": "Necesidad de apoyo económico",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Considera que actualmente requiere apoyo económico para cubrir sus necesidades básicas?",
        "opciones": [
            "Sí",
            "No"
        ]
    },

    # 7. Alimentación
    {
        "orden": 18,
        "categoria_codigo": "ALIMENTACION",
        "codigo": "INSEGURIDAD_ALIMENTARIA",
        "nombre": "Seguridad alimentaria",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Con qué frecuencia ha tenido dificultades para garantizar la alimentación de su hogar durante el último mes?",
        "opciones": [
            "Nunca",
            "Algunas veces",
            "Frecuentemente",
            "Siempre"
        ]
    },
    {
        "orden": 19,
        "categoria_codigo": "ALIMENTACION",
        "codigo": "FALTA_ALIMENTACION",
        "nombre": "Falta de alimentación",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "Durante los últimos 7 días, ¿hubo algún día en que usted o algún miembro de su hogar no pudo consumir alguna de las comidas habituales por falta de recursos?",
        "opciones": [
            "No",
            "Sí, 1 o 2 días",
            "Sí, 3 o 4 días",
            "Sí, 5 o más días"
        ]
    },

    # 8. Continuidad de la formación
    {
        "orden": 20,
        "categoria_codigo": "EMPLEO",
        "codigo": "CONTINUIDAD_FORMACION",
        "nombre": "Continuidad de la formación",
        "tipo_respuesta": "opcion_unica",
        "pregunta": "¿Puede continuar actualmente con su proceso de formación?",
        "opciones": [
            "Sí, puede continuar normalmente",
            "Sí, pero con dificultades",
            "No puede continuar actualmente"
        ]
    }
]

async def rebuild_survey_db():
    async with AsyncSessionLocal() as session:
        try:
            print("🔄 Reconstruyendo estructura oficial de la encuesta SENAContigo...")

            # 1. Limpiar datos de prueba antiguos (respuestas, casos, condiciones, reglas asociadas)
            await session.execute(delete(Respuesta))
            await session.execute(delete(CasoNecesidad))
            await session.execute(delete(Caso))
            await session.execute(delete(ReglaCondicion))
            await session.execute(delete(ReglaAccion))
            await session.execute(delete(Regla))
            await session.execute(delete(EncuestaVariable))
            await session.execute(delete(OpcionVariable))
            await session.execute(delete(VariableVersion))
            await session.execute(delete(Variable))
            await session.execute(delete(CorteEncuesta))
            await session.execute(delete(Encuesta))
            await session.flush()

            # 2. Crear Categorías necesarias si no existen
            categories_map = {
                "VIVIENDA": ("Vivienda y Habitabilidad", "Preguntas sobre el estado de la vivienda y alojamiento"),
                "TRANSPORTE": ("Transporte y Movilidad", "Preguntas sobre facilidad de desplazamiento al centro de formación"),
                "CONECTIVIDAD": ("Tecnología y Conectividad", "Disponibilidad de equipo de cómputo e internet"),
                "FAMILIA": ("Situación Familiar", "Entorno familiar y personas a cargo"),
                "EMPLEO": ("Situación Laboral", "Vinculación laboral u ocupación actual"),
                "ECONOMIA": ("Situación Económica", "Ingresos y sostenibilidad financiera"),
                "ALIMENTACION": ("Alimentación y Nutrición", "Acceso a alimentación diaria")
            }

            cat_objs = {}
            for code, (name, desc) in categories_map.items():
                res = await session.execute(select(CategoriaVariable).where(CategoriaVariable.codigo == code))
                cat = res.scalar_one_or_none()
                if not cat:
                    cat = CategoriaVariable(codigo=code, nombre=name, descripcion=desc, activa=True)
                    session.add(cat)
                    await session.flush()
                cat_objs[code] = cat

            # 3. Crear Encuesta Oficial y Corte
            enc = Encuesta(
                titulo="Encuesta de Caracterización Socioeconómica y Bienestar SENA",
                descripcion="Encuesta institucional para evaluar las condiciones de vivienda, servicios, transporte, conectividad, grupo familiar, empleo, economía, alimentación y continuidad formativa del aprendiz.",
                tipo="CARACTERIZACION",
                estado="PUBLICADA",
                fecha_inicio=date(2026, 1, 1),
                fecha_fin=date(2026, 12, 31)
            )
            session.add(enc)
            await session.flush()

            corte = CorteEncuesta(
                encuesta_id=enc.id,
                nombre_corte="Corte I - 2026",
                fecha_corte=datetime.now(),
                descripcion="Primer corte de caracterización 2026"
            )
            session.add(corte)
            await session.flush()

            # 4. Crear las 20 Variables, Versiones, Opciones y Asociarlas a la Encuesta
            variables_db = {}
            opciones_db = {}  # (var_codigo, opcion_texto) -> OpcionVariable

            for q_data in NEW_SURVEY_QUESTIONS:
                cat = cat_objs.get(q_data["categoria_codigo"])
                var = Variable(
                    codigo=q_data["codigo"],
                    nombre=q_data["nombre"],
                    descripcion=q_data["pregunta"],
                    tipo_respuesta=q_data["tipo_respuesta"],
                    categoria_id=cat.id if cat else None,
                    activa=True
                )
                session.add(var)
                await session.flush()

                version = VariableVersion(
                    variable_id=var.id,
                    numero_version=1,
                    titulo_pregunta=q_data["pregunta"],
                    activa=True
                )
                session.add(version)
                await session.flush()

                var.version_actual_id = version.id
                variables_db[q_data["codigo"]] = var

                # Opciones de Respuesta
                for opt_idx, opt_text in enumerate(q_data["opciones"], 1):
                    op_code = f"{q_data['codigo']}_OPT_{opt_idx}"
                    op = OpcionVariable(
                        variable_version_id=version.id,
                        codigo=op_code,
                        texto=opt_text,
                        orden=opt_idx
                    )
                    session.add(op)
                    await session.flush()
                    opciones_db[(q_data["codigo"], opt_text)] = op

                # Asociar a Encuesta
                ev = EncuestaVariable(
                    encuesta_id=enc.id,
                    variable_id=var.id,
                    orden=q_data["orden"]
                )
                session.add(ev)

            # 5. Crear Reglas del Motor ajustadas a las nuevas opciones
            reglas_config = [
                {
                    "nombre": "Alerta Inseguridad Alimentaria",
                    "descripcion": "Se activa si presenta falta de recursos para alimentarse o inseguridad alta",
                    "prioridad": 1,
                    "condicion_var": "FALTA_ALIMENTACION",
                    "opciones_trigger": ["Sí, 1 o 2 días", "Sí, 3 o 4 días", "Sí, 5 o más días"],
                    "prioridad_caso": "CRITICA",
                    "titulo_caso": "Riesgo de Inseguridad Alimentaria en el Hogar"
                },
                {
                    "nombre": "Alerta por Riesgo Crítico de Deserción",
                    "descripcion": "Se activa si presenta dificultad grave para cubrir necesidades básicas",
                    "prioridad": 1,
                    "condicion_var": "DIFICULTAD_NECESIDADES_BASICAS",
                    "opciones_trigger": ["Sí, frecuentemente", "Sí, de manera grave"],
                    "prioridad_caso": "ALTA",
                    "titulo_caso": "Dificultad Grave para Cubrir Necesidades Básicas"
                },
                {
                    "nombre": "Alerta por Imposibilidad de Continuar Formación",
                    "descripcion": "Se activa si el aprendiz manifiesta que no puede continuar actualmente",
                    "prioridad": 1,
                    "condicion_var": "CONTINUIDAD_FORMACION",
                    "opciones_trigger": ["No puede continuar actualmente"],
                    "prioridad_caso": "CRITICA",
                    "titulo_caso": "Riesgo de Deserción y Suspensión de Formación"
                },
                {
                    "nombre": "Alerta por Estado de Vivienda Inhabitable/Destruida",
                    "descripcion": "Se activa si la vivienda es inhabitable o destruida",
                    "prioridad": 1,
                    "condicion_var": "ESTADO_VIVIENDA",
                    "opciones_trigger": ["Inhabitable", "Destruida"],
                    "prioridad_caso": "CRITICA",
                    "titulo_caso": "Vivienda en Estado Inhabitable o Destruida"
                },
                {
                    "nombre": "Alerta por Vulnerabilidad de Alojamiento",
                    "descripcion": "Se activa si se encuentra en albergue o sin alojamiento estable",
                    "prioridad": 1,
                    "condicion_var": "ALOJAMIENTO_ACTUAL",
                    "opciones_trigger": ["Albergue", "Sin alojamiento estable"],
                    "prioridad_caso": "ALTA",
                    "titulo_caso": "Vulnerabilidad Extrema de Alojamiento"
                },
                {
                    "nombre": "Alerta por Falta de Computador",
                    "descripcion": "Se activa si no tiene acceso a computador",
                    "prioridad": 2,
                    "condicion_var": "DISPONIBILIDAD_COMPUTADOR",
                    "opciones_trigger": ["No tiene acceso a un computador"],
                    "prioridad_caso": "MEDIA",
                    "titulo_caso": "Requiere Equipo Computacional para Formación"
                },
                {
                    "nombre": "Alerta por Pérdida de Empleo Reciente",
                    "descripcion": "Se activa si perdió el empleo en los últimos 6 meses",
                    "prioridad": 2,
                    "condicion_var": "PERDIDA_EMPLEO",
                    "opciones_trigger": ["Sí"],
                    "prioridad_caso": "MEDIA",
                    "titulo_caso": "Pérdida Reciente de Empleo"
                }
            ]

            for r_info in reglas_config:
                regla = Regla(
                    nombre=r_info["nombre"],
                    descripcion=r_info["descripcion"],
                    activa=True,
                    prioridad=r_info["prioridad"]
                )
                session.add(regla)
                await session.flush()

                var_obj = variables_db.get(r_info["condicion_var"])
                if var_obj:
                    for opt_trig in r_info["opciones_trigger"]:
                        op_obj = opciones_db.get((r_info["condicion_var"], opt_trig))
                        cond = ReglaCondicion(
                            regla_id=regla.id,
                            variable_id=var_obj.id,
                            opcion_id=op_obj.id if op_obj else None,
                            operador="EQUALS",
                            valor_comparar=opt_trig
                        )
                        session.add(cond)

                accion = ReglaAccion(
                    regla_id=regla.id,
                    tipo_accion="CREAR_CASO",
                    prioridad_caso=r_info["prioridad_caso"],
                    titulo_caso=r_info["titulo_caso"],
                    mensaje_notificacion=f"Generación automática de caso por regla: {r_info['nombre']}"
                )
                session.add(accion)

            await session.commit()
            print("✅ Estructura oficial de 20 preguntas y opciones reconstruida exitosamente.")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error reconstruyendo la encuesta: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(rebuild_survey_db())
