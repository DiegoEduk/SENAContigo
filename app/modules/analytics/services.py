from typing import Any, List, Optional, Union
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.models  # noqa: F401
from app.modules.academic.models import Ficha
from app.modules.apprentices.models import Aprendiz
from app.modules.contracts.models import ContratoAprendizaje
from app.modules.cases.models import Caso
from app.modules.responses.models import Respuesta
from app.modules.variables.models import OpcionVariable
from app.core.security import TokenData
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
    def get_allowed_filters(user: TokenData):
        from app.modules.analytics.schemas import AllowedFiltersResponse
        rol = (user.rol or "").lower()
        locked = {}
        if user.regional_id:
            locked["regional_id"] = user.regional_id
        if user.centro_id:
            locked["centro_id"] = user.centro_id

        if rol == "superadmin":
            allowed = ["regional_id", "centro_id", "programa_codigo", "ficha_id", "nivel_riesgo", "categoria_id"]
            locked = {}
        elif rol in ["direccion", "dirección"]:
            allowed = ["centro_id", "programa_codigo", "ficha_id", "nivel_riesgo", "categoria_id"]
        elif rol in ["coordinador", "coordinación"]:
            allowed = ["programa_codigo", "ficha_id", "nivel_riesgo", "categoria_id"]
        elif rol == "instructor":
            allowed = ["ficha_id", "nivel_riesgo"]
        elif rol == "lider_bienestar":
            allowed = ["programa_codigo", "ficha_id", "nivel_riesgo", "categoria_id"]
        elif rol == "lider_contratacion":
            allowed = ["programa_codigo", "ficha_id"]
        else:
            allowed = ["programa_codigo", "ficha_id"]

        return AllowedFiltersResponse(
            allowed_filters=allowed,
            locked_values=locked,
            user_role=rol
        )

    @staticmethod
    async def get_filter_options(
        session: AsyncSession,
        user: TokenData,
        regional_id: Optional[Any] = None,
        centro_id: Optional[Any] = None,
        programa_codigo: Optional[Any] = None,
        q: Optional[str] = None,
        target: Optional[str] = None
    ):
        from sqlalchemy import or_
        from app.modules.organization.models import Regional, CentroFormacion
        from app.modules.academic.models import ProgramaFormacion, Ficha
        from app.modules.variables.models import CategoriaVariable
        from app.modules.analytics.schemas import FilterOptionsResponse, FilterItem

        def to_list(val):
            if val is None:
                return []
            if isinstance(val, (list, tuple)):
                return [str(v) for v in val if str(v).strip()]
            if isinstance(val, str):
                return [v.strip() for v in val.split(",") if v.strip()]
            return [str(val)]

        reg_list = to_list(regional_id)
        c_list = to_list(centro_id)
        p_list = to_list(programa_codigo)

        # Enforce user scoping
        if user.rol in ["direccion", "Dirección"] and user.regional_id:
            reg_list = [user.regional_id]
        elif user.rol in ["coordinador", "Coordinador", "instructor", "lider_bienestar", "lider_contratacion"] and user.centro_id:
            c_list = [user.centro_id]

        query_str = (q or "").strip()
        has_min_q = len(query_str) > 4
        pattern = f"%{query_str.lower()}%" if has_min_q else None

        regionales = []
        centros = []
        programas = []
        fichas = []

        # 1. Regionales (Solo buscar si target == 'regional' y query_str > 4, o si se especifican IDs)
        if target == 'regional' or (has_min_q and not target):
            if has_min_q:
                reg_stmt = select(Regional).where(
                    (Regional.activo == True) &
                    (or_(
                        func.lower(Regional.codigo_regional).like(pattern),
                        func.lower(Regional.nombre).like(pattern)
                    ))
                ).order_by(Regional.nombre)
                if reg_list:
                    reg_stmt = reg_stmt.where(Regional.codigo_regional.in_(reg_list))
                reg_res = await session.execute(reg_stmt)
                regionales = [FilterItem(id=r.codigo_regional, label=r.nombre) for r in reg_res.scalars().all()]

        # 2. Centros
        if target == 'centro' or (has_min_q and not target):
            if has_min_q:
                c_stmt = select(CentroFormacion).where(
                    (CentroFormacion.activo == True) &
                    (or_(
                        func.lower(CentroFormacion.codigo_centro).like(pattern),
                        func.lower(CentroFormacion.nombre).like(pattern)
                    ))
                ).order_by(CentroFormacion.nombre)
                if reg_list:
                    c_stmt = c_stmt.where(CentroFormacion.regional_id.in_(reg_list))
                if c_list:
                    c_stmt = c_stmt.where(CentroFormacion.codigo_centro.in_(c_list))
                c_res = await session.execute(c_stmt)
                centros = [FilterItem(id=c.codigo_centro, label=c.nombre) for c in c_res.scalars().all()]

        # 3. Programas
        if target == 'programa' or (has_min_q and not target):
            if has_min_q:
                p_stmt = select(ProgramaFormacion).where(
                    (ProgramaFormacion.activo == True) &
                    (or_(
                        func.lower(ProgramaFormacion.codigo_programa).like(pattern),
                        func.lower(ProgramaFormacion.nombre).like(pattern)
                    ))
                ).order_by(ProgramaFormacion.nombre)
                if c_list or reg_list:
                    p_stmt = p_stmt.join(Ficha, (ProgramaFormacion.codigo_programa == Ficha.programa_codigo) & (ProgramaFormacion.version == Ficha.programa_version))
                    if c_list:
                        p_stmt = p_stmt.where(Ficha.centro_id.in_(c_list))
                    elif reg_list:
                        p_stmt = p_stmt.join(CentroFormacion, Ficha.centro_id == CentroFormacion.codigo_centro).where(CentroFormacion.regional_id.in_(reg_list))
                    p_stmt = p_stmt.distinct()
                p_res = await session.execute(p_stmt)
                programas = [FilterItem(id=p.codigo_programa, label=f"{p.codigo_programa} - {p.nombre}") for p in p_res.scalars().all()]

        # 4. Fichas
        if target == 'ficha' or (has_min_q and not target):
            if has_min_q:
                f_stmt = select(Ficha).where(
                    func.lower(Ficha.ficha_caracterizacion).like(pattern)
                ).order_by(Ficha.ficha_caracterizacion)
                if c_list:
                    f_stmt = f_stmt.where(Ficha.centro_id.in_(c_list))
                elif reg_list:
                    f_stmt = f_stmt.join(CentroFormacion, Ficha.centro_id == CentroFormacion.codigo_centro).where(CentroFormacion.regional_id.in_(reg_list))

                if p_list:
                    f_stmt = f_stmt.where(Ficha.programa_codigo.in_(p_list))

                f_res = await session.execute(f_stmt)
                fichas = [FilterItem(id=f.ficha_caracterizacion, label=f"Ficha {f.ficha_caracterizacion}") for f in f_res.scalars().all()]

        # 5. Niveles de Riesgo (Fijo)
        niveles_riesgo = [
            FilterItem(id="Bajo", label="Verde - Bajo (<25%)"),
            FilterItem(id="Medio", label="Amarillo - Medio (25-49%)"),
            FilterItem(id="Alto", label="Naranja - Alto (50-74%)"),
            FilterItem(id="Crítico", label="Rojo - Crítico (≥75%)")
        ]

        # 6. Categorías (Fijo)
        cat_stmt = select(CategoriaVariable).where(CategoriaVariable.activa == True).order_by(CategoriaVariable.id)
        cat_res = await session.execute(cat_stmt)
        categorias = [FilterItem(id=str(c.id), label=c.nombre) for c in cat_res.scalars().all()]

        return FilterOptionsResponse(
            regionales=regionales,
            centros=centros,
            programas=programas,
            fichas=fichas,
            niveles_riesgo=niveles_riesgo,
            categorias=categorias
        )

    @staticmethod
    async def get_tabulation(
        session: AsyncSession,
        regional_id: Optional[Any] = None,
        centro_id: Optional[Any] = None,
        ficha_id: Optional[Any] = None,
        programa_codigo: Optional[Any] = None,
        nivel_riesgo: Optional[Any] = None,
        categoria_id: Optional[Any] = None
    ):
        from app.modules.variables.models import CategoriaVariable, Variable, VariableVersion, OpcionVariable
        from app.modules.apprentices.models import Matricula
        from app.modules.organization.models import CentroFormacion
        from app.modules.analytics.schemas import (
            TabulacionResponse, TabulacionCategoria, PreguntaTabulada, OpcionTabulada, KpiTabulacion
        )

        def to_list(val):
            if val is None:
                return []
            if isinstance(val, (list, tuple)):
                return [str(v) for v in val if str(v).strip()]
            if isinstance(val, str):
                return [v.strip() for v in val.split(",") if v.strip()]
            return [str(val)]

        reg_list = to_list(regional_id)
        c_list = to_list(centro_id)
        f_list = to_list(ficha_id)
        p_list = to_list(programa_codigo)
        r_list = to_list(nivel_riesgo)
        cat_list = [int(x) for x in to_list(categoria_id) if x.isdigit()]

        # 1. Obtener todas las categorías, variables, versiones y opciones activas
        stmt_cats = (
            select(CategoriaVariable)
            .where(CategoriaVariable.activa == True)
        )
        if cat_list:
            stmt_cats = stmt_cats.where(CategoriaVariable.id.in_(cat_list))
        stmt_cats = stmt_cats.order_by(CategoriaVariable.id)

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

        if reg_list or c_list or f_list or p_list:
            stmt_resp = stmt_resp.join(Matricula, Aprendiz.id == Matricula.aprendiz_id).join(Ficha, Matricula.ficha_id == Ficha.ficha_caracterizacion)
            if f_list:
                stmt_resp = stmt_resp.where(Ficha.ficha_caracterizacion.in_(f_list))
            if p_list:
                stmt_resp = stmt_resp.where(Ficha.programa_codigo.in_(p_list))
            if c_list:
                stmt_resp = stmt_resp.where(Ficha.centro_id.in_(c_list))
            if reg_list:
                stmt_resp = stmt_resp.join(CentroFormacion, Ficha.centro_id == CentroFormacion.codigo_centro).where(CentroFormacion.regional_id.in_(reg_list))

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

    @staticmethod
    async def get_beneficios_analytics(
        session: AsyncSession,
        regional_id: Optional[Any] = None,
        centro_id: Optional[Any] = None,
        ficha_id: Optional[Any] = None,
        programa_codigo: Optional[Any] = None,
        nivel_riesgo: Optional[Any] = None
    ):
        from app.modules.benefits.models import AprendizBeneficio, Beneficio
        from app.modules.academic.models import Ficha
        from app.modules.organization.models import CentroFormacion
        from app.modules.analytics.schemas import BeneficiosAnalyticsResponse

        def to_list(val):
            if val is None: return []
            if isinstance(val, (list, tuple)): return [str(v) for v in val if str(v).strip()]
            if isinstance(val, str): return [v.strip() for v in val.split(",") if v.strip()]
            return [str(val)]

        reg_list = to_list(regional_id)
        c_list = to_list(centro_id)
        f_list = to_list(ficha_id)
        p_list = to_list(programa_codigo)

        stmt = select(AprendizBeneficio, Beneficio).join(
            Beneficio, AprendizBeneficio.beneficio_id == Beneficio.id
        )

        if reg_list or c_list or f_list or p_list:
            stmt = stmt.join(Aprendiz, AprendizBeneficio.aprendiz_id == Aprendiz.id)\
                       .join(Matricula, Aprendiz.id == Matricula.aprendiz_id)\
                       .join(Ficha, Matricula.ficha_id == Ficha.ficha_caracterizacion)
            if f_list: stmt = stmt.where(Ficha.ficha_caracterizacion.in_(f_list))
            if p_list: stmt = stmt.where(Ficha.programa_codigo.in_(p_list))
            if c_list: stmt = stmt.where(Ficha.centro_id.in_(c_list))
            if reg_list: stmt = stmt.join(CentroFormacion, Ficha.centro_id == CentroFormacion.codigo_centro).where(CentroFormacion.regional_id.in_(reg_list))

        res = await session.execute(stmt)
        rows = res.all()

        total_otorgamientos = len(rows)
        aprendices_ids = set()
        dist_tipo = {}

        for otorg, ben in rows:
            aprendices_ids.add(otorg.aprendiz_id)
            tipo = ben.nombre or ben.tipo_beneficio or "Apoyo Institucional"
            dist_tipo[tipo] = dist_tipo.get(tipo, 0) + 1

        stmt_apr = select(func.count(Aprendiz.id.distinct()))
        if reg_list or c_list or f_list or p_list:
            stmt_apr = stmt_apr.join(Matricula, Aprendiz.id == Matricula.aprendiz_id)\
                               .join(Ficha, Matricula.ficha_id == Ficha.ficha_caracterizacion)
            if f_list: stmt_apr = stmt_apr.where(Ficha.ficha_caracterizacion.in_(f_list))
            if p_list: stmt_apr = stmt_apr.where(Ficha.programa_codigo.in_(p_list))
            if c_list: stmt_apr = stmt_apr.where(Ficha.centro_id.in_(c_list))
            if reg_list: stmt_apr = stmt_apr.join(CentroFormacion, Ficha.centro_id == CentroFormacion.codigo_centro).where(CentroFormacion.regional_id.in_(reg_list))

        res_apr = await session.execute(stmt_apr)
        total_apr_juris = res_apr.scalar_one_or_none() or 0

        unicos = len(aprendices_ids)
        cobertura = round((unicos / total_apr_juris * 100), 2) if total_apr_juris > 0 else 0.0

        return BeneficiosAnalyticsResponse(
            total_otorgamientos=total_otorgamientos,
            aprendices_beneficiados_unicos=unicos,
            tasa_cobertura_porcentaje=cobertura,
            distribucion_por_tipo=dist_tipo,
            distribucion_por_riesgo={"Bajo": 0, "Medio": 0, "Alto": 0, "Crítico": 0},
            desglose_centros=[]
        )

    @staticmethod
    async def get_casos_analytics(
        session: AsyncSession,
        regional_id: Optional[Any] = None,
        centro_id: Optional[Any] = None,
        ficha_id: Optional[Any] = None,
        programa_codigo: Optional[Any] = None
    ):
        from app.modules.cases.models import Caso
        from app.modules.academic.models import Ficha
        from app.modules.organization.models import CentroFormacion
        from app.modules.analytics.schemas import CasosAnalyticsResponse

        def to_list(val):
            if val is None: return []
            if isinstance(val, (list, tuple)): return [str(v) for v in val if str(v).strip()]
            if isinstance(val, str): return [v.strip() for v in val.split(",") if v.strip()]
            return [str(val)]

        reg_list = to_list(regional_id)
        c_list = to_list(centro_id)
        f_list = to_list(ficha_id)
        p_list = to_list(programa_codigo)

        stmt = select(Caso)
        if reg_list or c_list or f_list or p_list:
            stmt = stmt.join(Aprendiz, Caso.aprendiz_id == Aprendiz.id)\
                       .join(Matricula, Aprendiz.id == Matricula.aprendiz_id)\
                       .join(Ficha, Matricula.ficha_id == Ficha.ficha_caracterizacion)
            if f_list: stmt = stmt.where(Ficha.ficha_caracterizacion.in_(f_list))
            if p_list: stmt = stmt.where(Ficha.programa_codigo.in_(p_list))
            if c_list: stmt = stmt.where(Ficha.centro_id.in_(c_list))
            if reg_list: stmt = stmt.join(CentroFormacion, Ficha.centro_id == CentroFormacion.codigo_centro).where(CentroFormacion.regional_id.in_(reg_list))

        res = await session.execute(stmt)
        casos = res.scalars().all()

        total = len(casos)
        abiertos = 0
        en_proceso = 0
        cerrados = 0
        criticos_abiertos = 0

        dist_estado = {}
        dist_prioridad = {}
        dist_tipo = {}

        for c in casos:
            est = (c.estado or "Abierto").capitalize()
            prio = (c.prioridad or "Media").capitalize()
            tipo = c.tipo_caso_id or "General"

            dist_estado[est] = dist_estado.get(est, 0) + 1
            dist_prioridad[prio] = dist_prioridad.get(prio, 0) + 1
            dist_tipo[tipo] = dist_tipo.get(tipo, 0) + 1

            if est.lower() in ["abierto", "abierta"]: abiertos += 1
            elif est.lower() in ["en proceso", "en_proceso"]: en_proceso += 1
            elif est.lower() in ["cerrado", "cerrada", "resuelto"]: cerrados += 1

            if est.lower() in ["abierto", "en proceso"] and prio.lower() in ["alta", "crítica", "critica"]:
                criticos_abiertos += 1

        resolucion = round((cerrados / total * 100), 2) if total > 0 else 0.0

        return CasosAnalyticsResponse(
            total_casos=total,
            casos_abiertos=abiertos,
            casos_en_proceso=en_proceso,
            casos_cerrados=cerrados,
            tasa_resolucion_porcentaje=resolucion,
            casos_criticos_altos_abiertos=criticos_abiertos,
            distribucion_por_estado=dist_estado,
            distribucion_por_prioridad=dist_prioridad,
            distribucion_por_tipo_atencion=dist_tipo
        )

    @staticmethod
    async def get_contratacion_analytics(
        session: AsyncSession,
        regional_id: Optional[Any] = None,
        centro_id: Optional[Any] = None,
        ficha_id: Optional[Any] = None,
        programa_codigo: Optional[Any] = None
    ):
        from datetime import datetime, timedelta
        from app.modules.contracts.models import ContratoAprendizaje
        from app.modules.academic.models import Ficha
        from app.modules.organization.models import CentroFormacion
        from app.modules.analytics.schemas import ContratacionAnalyticsResponse

        def to_list(val):
            if val is None: return []
            if isinstance(val, (list, tuple)): return [str(v) for v in val if str(v).strip()]
            if isinstance(val, str): return [v.strip() for v in val.split(",") if v.strip()]
            return [str(val)]

        reg_list = to_list(regional_id)
        c_list = to_list(centro_id)
        f_list = to_list(ficha_id)
        p_list = to_list(programa_codigo)

        stmt_apr = select(Aprendiz.id.distinct())
        if reg_list or c_list or f_list or p_list:
            stmt_apr = stmt_apr.join(Matricula, Aprendiz.id == Matricula.aprendiz_id)\
                               .join(Ficha, Matricula.ficha_id == Ficha.ficha_caracterizacion)
            if f_list: stmt_apr = stmt_apr.where(Ficha.ficha_caracterizacion.in_(f_list))
            if p_list: stmt_apr = stmt_apr.where(Ficha.programa_codigo.in_(p_list))
            if c_list: stmt_apr = stmt_apr.where(Ficha.centro_id.in_(c_list))
            if reg_list: stmt_apr = stmt_apr.join(CentroFormacion, Ficha.centro_id == CentroFormacion.codigo_centro).where(CentroFormacion.regional_id.in_(reg_list))

        res_apr = await session.execute(stmt_apr)
        aprendices_ids = set(res_apr.scalars().all())
        total_apr = len(aprendices_ids)

        stmt_con = select(ContratoAprendizaje).join(Matricula, ContratoAprendizaje.matricula_id == Matricula.id)
        if aprendices_ids:
            stmt_con = stmt_con.where(Matricula.aprendiz_id.in_(aprendices_ids))

        res_con = await session.execute(stmt_con)
        contratos = res_con.scalars().all()

        contratados_ids = set()
        dist_tipo = {}
        dist_estado = {}
        empresas_count = {}
        por_vencer_30d = 0
        hoy = datetime.now().date()
        limite_30d = hoy + timedelta(days=30)

        for c in contratos:
            contratados_ids.add(c.aprendiz_id)
            tipo = c.tipo_contrato or "Contrato de Aprendizaje"
            est = c.estado_contrato or "Activo"
            emp = c.empresa_patrocinadora or "Empresa No Registrada"

            dist_tipo[tipo] = dist_tipo.get(tipo, 0) + 1
            dist_estado[est] = dist_estado.get(est, 0) + 1
            empresas_count[emp] = empresas_count.get(emp, 0) + 1

            if c.fecha_fin and hoy <= c.fecha_fin <= limite_30d:
                por_vencer_30d += 1

        n_contratados = len(contratados_ids)
        sin_contrato = max(0, total_apr - n_contratados)
        tasa_patrocinio = round((n_contratados / total_apr * 100), 2) if total_apr > 0 else 0.0

        top_empresas = [
            {"empresa": k, "contratos": v}
            for k, v in sorted(empresas_count.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        return ContratacionAnalyticsResponse(
            total_aprendices=total_apr,
            aprendices_contratados=n_contratados,
            aprendices_sin_contrato=sin_contrato,
            tasa_patrocinio_porcentaje=tasa_patrocinio,
            contratos_por_vencer_30d=por_vencer_30d,
            distribucion_por_tipo_contrato=dist_tipo,
            distribucion_por_estado_contrato=dist_estado,
            top_empresas_patrocinadoras=top_empresas
        )

