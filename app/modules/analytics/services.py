from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.models  # noqa: F401
from app.modules.academic.models import Ficha
from app.modules.apprentices.models import Aprendiz
from app.modules.contracts.models import ContratoAprendizaje
from app.modules.cases.models import Caso
from app.modules.responses.models import Respuesta
from app.modules.variables.models import OpcionVariable
from app.modules.analytics.schemas import DashboardSummary


class AnalyticsService:
    @staticmethod
    async def get_dashboard_summary(
        session: AsyncSession,
        regional_id: Optional[str] = None,
        centro_id: Optional[str] = None,
        ficha_id: Optional[str] = None
    ) -> DashboardSummary:
        # Filter aprendices based on org level
        stmt_apr = select(func.count(func.distinct(Aprendiz.id)))
        if regional_id or centro_id or ficha_id:
            from app.modules.apprentices.models import Matricula
            stmt_apr = stmt_apr.join(Matricula, Aprendiz.id == Matricula.aprendiz_id).join(Ficha, Matricula.ficha_id == Ficha.ficha_caracterizacion)
            if ficha_id:
                stmt_apr = stmt_apr.where(Ficha.ficha_caracterizacion == ficha_id)
            if centro_id:
                stmt_apr = stmt_apr.where(Ficha.centro_id == centro_id)
            if regional_id:
                from app.modules.organization.models import CentroFormacion
                stmt_apr = stmt_apr.join(CentroFormacion, Ficha.centro_id == CentroFormacion.codigo_centro).where(CentroFormacion.regional_id == regional_id)

        res_apr = await session.execute(stmt_apr)
        total_aprendices = res_apr.scalar() or 0

        # Count cases by state
        stmt_cases = select(Caso.estado, func.count(Caso.id)).group_by(Caso.estado)
        res_cases = await session.execute(stmt_cases)
        casos_by_state = {row[0]: row[1] for row in res_cases.all()}

        total_casos_abiertos = sum(v for k, v in casos_by_state.items() if k in ["NUEVO", "ASIGNADO", "EN_ATENCION", "ESCALADO"])

        # Count critical cases
        stmt_crit = select(func.count(Caso.id)).where(Caso.prioridad == "CRITICA")
        res_crit = await session.execute(stmt_crit)
        total_casos_criticos = res_crit.scalar() or 0

        # Count affected vs non affected based on latest response level > 0
        stmt_resp = select(func.count(func.distinct(Respuesta.aprendiz_id))).join(OpcionVariable, Respuesta.opcion_id == OpcionVariable.id).where(OpcionVariable.nivel_afectacion > 0)
        res_resp = await session.execute(stmt_resp)
        total_afectados = res_resp.scalar() or 0

        total_no_afectados = max(0, total_aprendices - total_afectados)
        porcentaje = round((total_afectados / total_aprendices * 100), 2) if total_aprendices > 0 else 0.0

        return DashboardSummary(
            total_aprendices=total_aprendices,
            total_afectados=total_afectados,
            total_no_afectados=total_no_afectados,
            porcentaje_afectacion=porcentaje,
            total_casos_abiertos=total_casos_abiertos,
            total_casos_criticos=total_casos_criticos,
            casos_por_estado=casos_by_state,
            afectacion_por_categoria={}
        )

    @staticmethod
    async def get_tabulation(
        session: AsyncSession,
        regional_id: Optional[str] = None,
        centro_id: Optional[str] = None,
        ficha_id: Optional[str] = None
    ):
        from app.modules.variables.models import CategoriaVariable, Variable, VariableVersion, OpcionVariable
        from app.modules.apprentices.models import Matricula
        from app.modules.organization.models import CentroFormacion
        from app.modules.analytics.schemas import (
            TabulacionResponse, TabulacionCategoria, PreguntaTabulada, OpcionTabulada, KpiTabulacion
        )

        # 1. Obtener todas las categorías, variables, versiones y opciones activas
        stmt_cats = (
            select(CategoriaVariable)
            .where(CategoriaVariable.activa == True)
            .order_by(CategoriaVariable.id)
        )
        res_cats = await session.execute(stmt_cats)
        categorias_db = res_cats.scalars().all()

        stmt_vars = (
            select(Variable)
            .where(Variable.activa == True)
            .order_by(Variable.categoria_id, Variable.id)
        )
        res_vars = await session.execute(stmt_vars)
        variables_db = res_vars.scalars().all()

        stmt_vers = (
            select(VariableVersion)
            .where(VariableVersion.activa == True)
        )
        res_vers = await session.execute(stmt_vers)
        versiones_db = {v.variable_id: v for v in res_vers.scalars().all()}

        stmt_opts = (
            select(OpcionVariable)
            .where(OpcionVariable.activa == True)
            .order_by(OpcionVariable.variable_version_id, OpcionVariable.orden)
        )
        res_opts = await session.execute(stmt_opts)
        opciones_db = res_opts.scalars().all()

        # Indexar opciones por version_id
        opciones_por_version = {}
        for op in opciones_db:
            opciones_por_version.setdefault(op.variable_version_id, []).append(op)

        # 2. Consultar respuestas con filtro de organización
        stmt_resp = (
            select(
                Respuesta.variable_id,
                Respuesta.opcion_id,
                Respuesta.aprendiz_id,
                OpcionVariable.nivel_afectacion,
                Variable.codigo.label("codigo_variable")
            )
            .join(OpcionVariable, Respuesta.opcion_id == OpcionVariable.id)
            .join(Variable, Respuesta.variable_id == Variable.id)
            .join(Aprendiz, Respuesta.aprendiz_id == Aprendiz.id)
        )

        if regional_id or centro_id or ficha_id:
            stmt_resp = stmt_resp.join(Matricula, Aprendiz.id == Matricula.aprendiz_id).join(Ficha, Matricula.ficha_id == Ficha.ficha_caracterizacion)
            if ficha_id:
                stmt_resp = stmt_resp.where(Ficha.ficha_caracterizacion == ficha_id)
            if centro_id:
                stmt_resp = stmt_resp.where(Ficha.centro_id == centro_id)
            if regional_id:
                stmt_resp = stmt_resp.join(CentroFormacion, Ficha.centro_id == CentroFormacion.codigo_centro).where(CentroFormacion.regional_id == regional_id)

        res_resp = await session.execute(stmt_resp)
        respuestas_rows = res_resp.all()

        # Mapear frecuencias y métricas
        # { (variable_id, opcion_id): conteo }
        frecuencias = {}
        aprendices_caracterizados = set()
        afectacion_por_aprendiz = {} # { aprendiz_id: suma_afectacion }
        respuestas_por_aprendiz_count = {} # { aprendiz_id: total_respuestas }

        alerta_alimentaria_aprendices = set()
        riesgo_desercion_aprendices = set()
        sin_computador_internet_aprendices = set()

        for r in respuestas_rows:
            var_id = r.variable_id
            op_id = r.opcion_id
            apr_id = r.aprendiz_id
            nivel_af = r.nivel_afectacion or 0
            cod_var = r.codigo_variable

            frecuencias[(var_id, op_id)] = frecuencias.get((var_id, op_id), 0) + 1
            aprendices_caracterizados.add(apr_id)

            afectacion_por_aprendiz[apr_id] = afectacion_por_aprendiz.get(apr_id, 0) + nivel_af
            respuestas_por_aprendiz_count[apr_id] = respuestas_por_aprendiz_count.get(apr_id, 0) + 1

            # Detectar alertas específicas
            if cod_var in ["INSEGURIDAD_ALIMENTARIA", "FALTA_ALIMENTACION"] and nivel_af >= 3:
                alerta_alimentaria_aprendices.add(apr_id)
            if cod_var in ["CONTINUIDAD_FORMACION", "ACCESO_CENTRO"] and nivel_af >= 3:
                riesgo_desercion_aprendices.add(apr_id)
            if cod_var in ["DISPONIBILIDAD_COMPUTADOR", "ACCESO_INTERNET"] and nivel_af >= 3:
                sin_computador_internet_aprendices.add(apr_id)

        total_aprendices_caracterizados = len(aprendices_caracterizados)
        total_respuestas_registradas = len(respuestas_rows)

        # 3. Construir estructura de categorías y preguntas tabuladas
        categorias_tabuladas = []
        todas_preguntas_promedios = []

        for cat in categorias_db:
            vars_cat = [v for v in variables_db if v.categoria_id == cat.id]
            preguntas_tab = []
            total_resp_cat = 0
            promedios_cat = []

            for var in vars_cat:
                version = versiones_db.get(var.id)
                opts = opciones_por_version.get(version.id, []) if version else []

                # Contar total respuestas para la pregunta
                total_resp_preg = sum(frecuencias.get((var.id, op.id), 0) for op in opts)
                total_resp_cat += total_resp_preg

                opciones_tab = []
                suma_ponderada_afectacion = 0

                for op in opts:
                    freq_abs = frecuencias.get((var.id, op.id), 0)
                    freq_rel = round((freq_abs / total_resp_preg * 100), 2) if total_resp_preg > 0 else 0.0
                    suma_ponderada_afectacion += (freq_abs * op.nivel_afectacion)

                    opciones_tab.append(OpcionTabulada(
                        opcion_id=op.id,
                        codigo=op.codigo,
                        texto=op.texto,
                        valor_numerico=op.valor_numerico,
                        nivel_afectacion=op.nivel_afectacion,
                        frecuencia_absoluta=freq_abs,
                        frecuencia_relativa=freq_rel
                    ))

                promedio_afectacion_preg = round(suma_ponderada_afectacion / total_resp_preg, 2) if total_resp_preg > 0 else 0.0
                promedios_cat.append(promedio_afectacion_preg)
                todas_preguntas_promedios.append(promedio_afectacion_preg)

                preguntas_tab.append(PreguntaTabulada(
                    variable_id=var.id,
                    codigo_variable=var.codigo,
                    nombre_variable=var.nombre,
                    titulo_pregunta=version.titulo_pregunta if version else var.nombre,
                    tipo_respuesta=var.tipo_respuesta,
                    total_respuestas=total_resp_preg,
                    promedio_afectacion=promedio_afectacion_preg,
                    opciones=opciones_tab
                ))

            prom_cat = round(sum(promedios_cat) / len(promedios_cat), 2) if promedios_cat else 0.0
            categorias_tabuladas.append(TabulacionCategoria(
                categoria_id=cat.id,
                codigo_categoria=cat.codigo,
                nombre_categoria=cat.nombre,
                total_respuestas_categoria=total_resp_cat,
                promedio_afectacion_categoria=prom_cat,
                preguntas=preguntas_tab
            ))

        # 4. Clasificación de Niveles de Riesgo por Aprendiz (IGVS)
        distribucion_riesgo = {"Bajo": 0, "Medio": 0, "Alto": 0, "Crítico": 0}
        aprendices_alto_critico = 0

        for apr_id, total_af in afectacion_por_aprendiz.items():
            num_resp = respuestas_por_aprendiz_count.get(apr_id, 20)
            max_posible = num_resp * 4
            igvs = (total_af / max_posible * 100) if max_posible > 0 else 0.0

            if igvs < 25:
                distribucion_riesgo["Bajo"] += 1
            elif igvs < 50:
                distribucion_riesgo["Medio"] += 1
            elif igvs < 75:
                distribucion_riesgo["Alto"] += 1
                aprendices_alto_critico += 1
            else:
                distribucion_riesgo["Crítico"] += 1
                aprendices_alto_critico += 1

        indice_vulnerabilidad_prom = round(
            (sum(todas_preguntas_promedios) / (len(todas_preguntas_promedios) * 4) * 100), 2
        ) if todas_preguntas_promedios else 0.0

        pct_alto_critico = round(
            (aprendices_alto_critico / total_aprendices_caracterizados * 100), 2
        ) if total_aprendices_caracterizados > 0 else 0.0

        kpis = KpiTabulacion(
            total_aprendices_caracterizados=total_aprendices_caracterizados,
            total_respuestas_registradas=total_respuestas_registradas,
            indice_vulnerabilidad_promedio=indice_vulnerabilidad_prom,
            porcentaje_vulnerabilidad_alta_critica=pct_alto_critico,
            aprendices_alerta_alimentaria=len(alerta_alimentaria_aprendices),
            aprendices_riesgo_desercion=len(riesgo_desercion_aprendices),
            aprendices_sin_computador_internet=len(sin_computador_internet_aprendices)
        )

        return TabulacionResponse(
            kpis=kpis,
            categorias=categorias_tabuladas,
            distribucion_niveles_riesgo=distribucion_riesgo,
            regional_id=regional_id,
            centro_id=centro_id,
            ficha_id=ficha_id
        )

