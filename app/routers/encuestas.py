from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Encuesta, PreguntaEncuesta, Variable
from app.schemas.schemas import EncuestaCreate, EncuestaResponse
from app.core.security import get_current_user_data, TokenData, RoleChecker

router = APIRouter(prefix="/encuestas", tags=["Engine de Encuestas & Segmentación"])


@router.get("/", response_model=List[EncuestaResponse])
def list_encuestas(db: Session = Depends(get_db)):
    return db.query(Encuesta).order_by(Encuesta.id.desc()).all()


@router.post("/", response_model=EncuestaResponse)
def create_encuesta(
    payload: EncuestaCreate,
    db: Session = Depends(get_db),
    user_data: TokenData = Depends(RoleChecker(["superadmin", "direccion", "coordinador", "instructor"]))
):
    enc = Encuesta(
        nombre=payload.nombre,
        descripcion=payload.descripcion,
        fecha_inicio=payload.fecha_inicio,
        fecha_fin=payload.fecha_fin,
        estado=payload.estado,
        tipo=payload.tipo,
        segmento_filtro_json=payload.segmento_filtro_json
    )
    db.add(enc)
    db.commit()
    db.refresh(enc)

    # Link variables as questions
    for idx, var_id in enumerate(payload.variables_ids):
        var = db.query(Variable).filter(Variable.id == var_id).first()
        if var:
            pq = PreguntaEncuesta(
                encuesta_id=enc.id,
                variable_id=var.id,
                orden=idx + 1,
                obligatoria=var.obligatoria
            )
            db.add(pq)

    db.commit()
    db.refresh(enc)
    return enc


@router.get("/{id}", response_model=EncuestaResponse)
def get_encuesta_detail(id: int, db: Session = Depends(get_db)):
    enc = db.query(Encuesta).filter(Encuesta.id == id).first()
    if not enc:
        raise HTTPException(status_code=404, detail="Encuesta no encontrada")
    return enc
