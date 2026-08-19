from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Regla, Caso, SeguimientoCaso, Necesidad
from app.schemas.schemas import (
    ReglaCreate, ReglaResponse, CasoCreate, CasoResponse,
    SeguimientoCasoCreate, SeguimientoCasoResponse
)
from app.core.security import get_current_user_data, TokenData, RoleChecker

router = APIRouter(prefix="/casos", tags=["Motor de Reglas & Gestión de Casos"])


@router.get("/reglas", response_model=List[ReglaResponse])
def get_reglas(db: Session = Depends(get_db)):
    return db.query(Regla).all()


@router.post("/reglas", response_model=ReglaResponse)
def create_regla(
    payload: ReglaCreate,
    db: Session = Depends(get_db),
    user_data: TokenData = Depends(RoleChecker(["superadmin", "direccion", "coordinador"]))
):
    r = Regla(
        nombre=payload.nombre,
        descripcion=payload.descripcion,
        variable_id=payload.variable_id,
        opcion_id=payload.opcion_id,
        nivel_afectacion_minimo=payload.nivel_afectacion_minimo,
        necesidad_id=payload.necesidad_id,
        prioridad=payload.prioridad,
        activa=payload.activa
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.get("/", response_model=List[CasoResponse])
def list_casos(
    estado: Optional[str] = Query(None),
    prioridad: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_data: TokenData = Depends(get_current_user_data)
):
    query = db.query(Caso)
    if estado:
        query = query.filter(Caso.estado == estado)
    if prioridad:
        query = query.filter(Caso.prioridad == prioridad)

    return query.order_by(Caso.fecha_creacion.desc()).all()


@router.post("/{id}/seguimiento", response_model=SeguimientoCasoResponse)
def add_seguimiento(
    id: int,
    payload: SeguimientoCasoCreate,
    db: Session = Depends(get_db),
    user_data: TokenData = Depends(get_current_user_data)
):
    caso = db.query(Caso).filter(Caso.id == id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    seg = SeguimientoCaso(
        caso_id=caso.id,
        usuario_id=user_data.user_id,
        fecha=datetime.utcnow(),
        comentario=payload.comentario,
        nuevo_estado=payload.nuevo_estado
    )
    db.add(seg)

    if payload.nuevo_estado:
        caso.estado = payload.nuevo_estado
        if payload.nuevo_estado in ["RESUELTO", "CANCELADO"]:
            caso.fecha_cierre = datetime.utcnow()

    db.commit()
    db.refresh(seg)
    return seg
