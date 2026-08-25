import io
from datetime import datetime
from typing import Dict, Any, Optional


def generate_tabulation_pdf(
    tabulation_data: Dict[str, Any],
    regional_nombre: Optional[str] = "Todas las Regionales",
    centro_nombre: Optional[str] = "Todos los Centros",
    ficha_codigo: Optional[str] = "Todas las Fichas",
    generado_por: str = "Sistema SENAContigo"
) -> bytes:
    """Genera un archivo PDF con el informe institucional de tabulación de la encuesta socioeconómica."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    except ImportError:
        raise RuntimeError("La librería 'reportlab' no está instalada en este entorno Python.")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados SENA
    sena_green = colors.HexColor("#39A900")
    sena_dark = colors.HexColor("#00324D")
    sena_light_bg = colors.HexColor("#F4F7F6")
    text_dark = colors.HexColor("#2C3E50")
    border_color = colors.HexColor("#D1D5DB")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=sena_dark,
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=sena_green,
        alignment=TA_CENTER
    )

    h2_style = ParagraphStyle(
        'Heading2_Sena',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=sena_dark,
        spaceBefore=10,
        spaceAfter=6
    )

    h3_style = ParagraphStyle(
        'Heading3_Sena',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=sena_green,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body_Sena',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=text_dark
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=text_dark
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=text_dark,
        alignment=TA_CENTER
    )

    story = []

    # 1. Encabezado Institucional
    story.append(Paragraph("SENAContigo - SERVICIO NACIONAL DE APRENDIZAJE", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("INFORME DE TABULACIÓN SOCIOECONÓMICA Y DIAGNÓSTICO INSTITUCIONAL", title_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=sena_green, spaceBefore=2, spaceAfter=10))

    # Meta datos del informe
    fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    meta_text = (
        f"<b>Regional:</b> {regional_nombre} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Centro:</b> {centro_nombre} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Ficha:</b> {ficha_codigo}<br/>"
        f"<b>Fecha de Generación:</b> {fecha_str} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Generado por:</b> {generado_por}"
    )
    story.append(Paragraph(meta_text, body_style))
    story.append(Spacer(1, 12))

    # 2. Resumen Ejecutivo y KPIs
    kpis = tabulation_data.get("kpis", {})
    story.append(Paragraph("1. Resumen Ejecutivo de Indicadores Clave (KPIs)", h2_style))

    kpi_data = [
        [
            Paragraph("<b>Población Caracterizada</b>", table_cell_center),
            Paragraph("<b>IGVS Promedio</b>", table_cell_center),
            Paragraph("<b>Vulnerabilidad Alta/Crítica</b>", table_cell_center),
            Paragraph("<b>Alerta Alimentaria</b>", table_cell_center),
            Paragraph("<b>Riesgo Deserción</b>", table_cell_center),
            Paragraph("<b>Brecha Digital</b>", table_cell_center)
        ],
        [
            Paragraph(f"<b>{kpis.get('total_aprendices_caracterizados', 0)}</b>", table_cell_center),
            Paragraph(f"<b>{kpis.get('indice_vulnerabilidad_promedio', 0.0)}%</b>", table_cell_center),
            Paragraph(f"<b>{kpis.get('porcentaje_vulnerabilidad_alta_critica', 0.0)}%</b>", table_cell_center),
            Paragraph(f"<b>{kpis.get('aprendices_alerta_alimentaria', 0)}</b>", table_cell_center),
            Paragraph(f"<b>{kpis.get('aprendices_riesgo_desercion', 0)}</b>", table_cell_center),
            Paragraph(f"<b>{kpis.get('aprendices_sin_computador_internet', 0)}</b>", table_cell_center)
        ]
    ]

    t_kpi = Table(kpi_data, colWidths=[90, 90, 95, 85, 85, 95])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), sena_dark),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('BACKGROUND', (0, 1), (-1, 1), sena_light_bg),
        ('PADDING', (0, 0), (-1, -1), 6)
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 12))

    # Distribución por Nivel de Riesgo
    dist = tabulation_data.get("distribucion_niveles_riesgo", {})
    dist_data = [
        [
            Paragraph("<b>Nivel Bajo (< 25%)</b>", table_cell_center),
            Paragraph("<b>Nivel Medio (25-49%)</b>", table_cell_center),
            Paragraph("<b>Nivel Alto (50-74%)</b>", table_cell_center),
            Paragraph("<b>Nivel Crítico (≥ 75%)</b>", table_cell_center)
        ],
        [
            Paragraph(f"{dist.get('Bajo', 0)} aprendices", table_cell_center),
            Paragraph(f"{dist.get('Medio', 0)} aprendices", table_cell_center),
            Paragraph(f"{dist.get('Alto', 0)} aprendices", table_cell_center),
            Paragraph(f"{dist.get('Crítico', 0)} aprendices", table_cell_center)
        ]
    ]
    t_dist = Table(dist_data, colWidths=[135, 135, 135, 135])
    t_dist.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), sena_green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('BACKGROUND', (0, 1), (-1, 1), colors.whitesmoke),
        ('PADDING', (0, 0), (-1, -1), 5)
    ]))
    story.append(t_dist)
    story.append(Spacer(1, 14))

    # 3. Tabulaciones Desglosadas por Categoría y Pregunta
    story.append(Paragraph("2. Tabulación Desglosada por Categorías de Variables (20 Preguntas)", h2_style))

    categorias = tabulation_data.get("categorias", [])
    for cat in categorias:
        cat_story = []
        cat_title = f"Categoría {cat.get('categoria_id')}: {cat.get('nombre_categoria')} (Promedio Afectación: {cat.get('promedio_afectacion_categoria', 0.0)})"
        cat_story.append(Paragraph(cat_title, h3_style))

        preguntas = cat.get("preguntas", [])
        for preg in preguntas:
            preg_title = f"<b>Pregunta {preg.get('variable_id')}:</b> {preg.get('titulo_pregunta')} (Total: {preg.get('total_respuestas')} respuestas)"
            cat_story.append(Paragraph(preg_title, body_style))
            cat_story.append(Spacer(1, 3))

            # Tabla de Opciones
            table_rows = [
                [
                    Paragraph("<b>Opción de Respuesta</b>", table_header_style),
                    Paragraph("<b>Nivel Afectación</b>", table_header_style),
                    Paragraph("<b>Frecuencia (n)</b>", table_header_style),
                    Paragraph("<b>Porcentaje (%)</b>", table_header_style)
                ]
            ]

            opciones = preg.get("opciones", [])
            for op in opciones:
                table_rows.append([
                    Paragraph(op.get("texto", ""), table_cell_style),
                    Paragraph(str(op.get("nivel_afectacion", 0)), table_cell_center),
                    Paragraph(str(op.get("frecuencia_absoluta", 0)), table_cell_center),
                    Paragraph(f"{op.get('frecuencia_relativa', 0.0)}%", table_cell_center)
                ])

            t_preg = Table(table_rows, colWidths=[270, 90, 90, 90])
            t_preg.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), sena_dark),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, sena_light_bg]),
                ('PADDING', (0, 0), (-1, -1), 4)
            ]))
            cat_story.append(t_preg)
            cat_story.append(Spacer(1, 8))

        story.append(KeepTogether(cat_story))
        story.append(Spacer(1, 10))

    # 4. Conclusiones y Recomendaciones de Atención
    recom_story = [
        Paragraph("3. Recomendaciones Institucionales de Intervención", h2_style),
        Paragraph(
            "Basado en los resultados tabulados de la encuesta socioeconómica, la Coordinación de Bienestar al Aprendiz y los Equipos Interdisciplinarios deben priorizar las siguientes acciones:",
            body_style
        ),
        Spacer(1, 6),
        Paragraph("• <b>Seguridad Alimentaria:</b> Focalizar la asignación de apoyos de alimentación temporal a aprendices clasificados en riesgo severo/crítico.", body_style),
        Spacer(1, 3),
        Paragraph("• <b>Permanencia y Conectividad:</b> Articular préstamos de equipos de cómputo y bonos de conectividad para reducir la brecha digital en formación virtual.", body_style),
        Spacer(1, 3),
        Paragraph("• <b>Apoyo Socioeconómico:</b> Priorizar convocatorias de apoyo de sostenimiento regular a aprendices jefes de hogar con personas a cargo.", body_style),
        Spacer(1, 3),
        Paragraph("• <b>Acompañamiento Psicosocial:</b> Realizar seguimiento individualizado a casos con afectación familiar o habitacional grave.", body_style)
    ]
    story.append(KeepTogether(recom_story))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
