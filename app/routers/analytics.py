from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.models import Respuesta, OpcionVariable, Variable, Usuario, Encuesta, Ficha, AprendizFicha
from app.schemas.schemas import ResumenAfectacionVariable, IndiceAfectacionAprendiz
from app.core.security import get_current_user_data, TokenData

router = APIRouter(prefix="/analytics", tags=["Centro de Analítica & Evolución Longitudinal"])


@router.get("/estado-actual", response_model=List[ResumenAfectacionVariable])
def get_estado_actual(
    centro_id: int = Query(None),
    ficha_id: int = Query(None),
    db: Session = Depends(get_db),
    user_data: TokenData = Depends(get_current_user_data)
):
    variables = db.query(Variable).filter(Variable.activa == True).all()
    resultado = []

    for v in variables:
        # Subquery for latest response per aprendiz & variable
        subq = db.query(
            Respuesta.aprendiz_id,
            func.max(Respuesta.id).label("max_id")
        ).filter(Respuesta.variable_id == v.id).group_by(Respuesta.aprendiz_id).subquery()

        query = db.query(Respuesta).join(subq, Respuesta.id == subq.c.max_id).join(OpcionVariable, Respuesta.opcion_id == OpcionVariable.id)

        if centro_id:
            query = query.join(Usuario, Respuesta.aprendiz_id == Usuario.id).filter(Usuario.centro_id == centro_id)
        if ficha_id:
            query = query.join(AprendizFicha, Respuesta.aprendiz_id == AprendizFicha.aprendiz_id).filter(AprendizFicha.ficha_id == ficha_id)

        respuestas_recientes = query.all()

        counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        for r in respuestas_recientes:
            if r.opcion:
                lvl = r.opcion.nivel_afectacion
                if lvl in counts:
                    counts[lvl] += 1

        total = sum(counts.values())

        resultado.append(ResumenAfectacionVariable(
            variable_nombre=v.nombre,
            codigo=v.codigo,
            sin_afectacion=counts[0],
            leve=counts[1],
            moderada=counts[2],
            grave=counts[3],
            critica=counts[4],
            total_respuestas=total
        ))

    return resultado


@router.get("/evolucion-longitudinal")
def get_evolucion_longitudinal(db: Session = Depends(get_db)):
    encuestas = db.query(Encuesta).order_by(Encuesta.id.asc()).all()
    evolucion = []

    for enc in encuestas:
        respuestas = db.query(Respuesta).filter(Respuesta.encuesta_id == enc.id).all()
        counts = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0}
        for r in respuestas:
            if r.opcion:
                lvl_str = str(r.opcion.nivel_afectacion)
                if lvl_str in counts:
                    counts[lvl_str] += 1

        evolucion.append({
            "encuesta_id": enc.id,
            "encuesta_nombre": enc.nombre,
            "fecha_inicio": enc.fecha_inicio,
            "total_respuestas": len(respuestas),
            "niveles": counts
        })

    return evolucion


@router.get("/indice-afectacion", response_model=List[IndiceAfectacionAprendiz])
def get_indice_afectacion(db: Session = Depends(get_db)):
    aprendices = db.query(Usuario).filter(Usuario.rol == "aprendiz").all()
    resultado = []

    for apr in aprendices:
        # Subquery latest response per variable for this learner
        subq = db.query(
            Respuesta.variable_id,
            func.max(Respuesta.id).label("max_id")
        ).filter(Respuesta.aprendiz_id == apr.id).group_by(Respuesta.variable_id).subquery()

        latest_resp = db.query(Respuesta).join(subq, Respuesta.id == subq.c.max_id).all()

        score = 0.0
        for r in latest_resp:
            if r.opcion:
                score += r.opcion.nivel_afectacion * 2.0

        if score <= 4:
            clasif = "BAJO"
        elif score <= 9:
            clasif = "MODERADO"
        elif score <= 14:
            clasif = "ALTO"
        else:
            clasif = "CRITICO"

        # Get ficha name
        af = db.query(AprendizFicha).filter(AprendizFicha.aprendiz_id == apr.id).first()
        ficha_code = af.ficha.ficha_caracterizacion if (af and af.ficha) else "N/A"

        resultado.append(IndiceAfectacionAprendiz(
            aprendiz_id=apr.id,
            nombres=apr.nombres,
            apellidos=apr.apellidos,
            ficha=ficha_code,
            indice_total=score,
            nivel_clasificacion=clasif
        ))

    return resultado
