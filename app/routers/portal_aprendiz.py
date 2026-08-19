from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Encuesta, Respuesta, Regla, Caso, OpcionVariable
from app.schemas.schemas import EncuestaResponse, RespuestasFormSubmission, RespuestaResponse
from app.core.security import get_current_user_data, TokenData

router = APIRouter(prefix="/portal", tags=["Portal del Aprendiz & Respuestas Históricas"])


@router.get("/encuestas-pendientes", response_model=List[EncuestaResponse])
def get_encuestas_pendientes(
    user_data: TokenData = Depends(get_current_user_data),
    db: Session = Depends(get_db)
):
    if user_data.rol != "aprendiz":
        # Allow admins to view for testing
        pass

    # Active surveys
    encuestas = db.query(Encuesta).filter(Encuesta.estado == "activa").all()
    return encuestas


@router.post("/responder")
def submit_respuestas(
    payload: RespuestasFormSubmission,
    user_data: TokenData = Depends(get_current_user_data),
    db: Session = Depends(get_db)
):
    fecha_corte = datetime.utcnow()
    respuestas_creadas = []

    for item in payload.respuestas:
        resp = Respuesta(
            aprendiz_id=user_data.user_id,
            encuesta_id=payload.encuesta_id,
            variable_id=item.variable_id,
            opcion_id=item.opcion_id,
            respuesta_texto=item.respuesta_texto,
            fecha_respuesta=fecha_corte,
            observacion=item.observacion
        )
        db.add(resp)
        db.flush()
        respuestas_creadas.append(resp)

        # Evaluador de Motor de Reglas Automáticas
        if item.opcion_id:
            opcion = db.query(OpcionVariable).filter(OpcionVariable.id == item.opcion_id).first()
            if opcion:
                # Match active rules
                reglas = db.query(Regla).filter(
                    Regla.activa == True,
                    Regla.variable_id == item.variable_id
                ).all()

                for r in reglas:
                    match = False
                    if r.opcion_id and r.opcion_id == item.opcion_id:
                        match = True
                    elif r.nivel_afectacion_minimo is not None and opcion.nivel_afectacion >= r.nivel_afectacion_minimo:
                        match = True

                    if match:
                        # Avoid duplicate open case for same necesidad and aprendiz
                        caso_existente = db.query(Caso).filter(
                            Caso.aprendiz_id == user_data.user_id,
                            Caso.necesidad_id == r.necesidad_id,
                            Caso.estado.in_(["ABIERTO", "EN_PROCESO"])
                        ).first()

                        if not caso_existente:
                            nuevo_caso = Caso(
                                aprendiz_id=user_data.user_id,
                                respuesta_origen_id=resp.id,
                                necesidad_id=r.necesidad_id,
                                titulo=f"Alerta Automática: {r.nombre}",
                                descripcion=f"Generado automáticamente por respuesta con Nivel {opcion.nivel_afectacion} ({opcion.texto}). Observación: {item.observacion or 'Sin observacion'}",
                                prioridad=r.prioridad,
                                estado="ABIERTO",
                                fecha_creacion=fecha_corte
                            )
                            db.add(nuevo_caso)

    db.commit()
    return {"status": "ok", "message": f"Se registraron {len(respuestas_creadas)} respuestas longitudinales."}


@router.get("/mi-historial", response_model=List[RespuestaResponse])
def get_mi_historial(
    user_data: TokenData = Depends(get_current_user_data),
    db: Session = Depends(get_db)
):
    respuestas = db.query(Respuesta).filter(
        Respuesta.aprendiz_id == user_data.user_id
    ).order_by(Respuesta.fecha_respuesta.desc()).all()
    return respuestas
