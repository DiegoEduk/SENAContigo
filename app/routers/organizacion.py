from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Regional, CentroFormacion, ProgramaFormacion, Ficha, Usuario, AprendizFicha
from app.schemas.schemas import (
    RegionalResponse, CentroFormacionResponse, ProgramaFormacionResponse,
    FichaResponse, UsuarioResponse
)
from app.core.security import get_current_user_data, TokenData, RoleChecker

router = APIRouter(prefix="/organizacion", tags=["Estructura Organizacional SENA"])


@router.get("/regionales", response_model=List[RegionalResponse])
def list_regionales(
    db: Session = Depends(get_db),
    user_data: TokenData = Depends(get_current_user_data)
):
    query = db.query(Regional)
    if user_data.rol == "direccion" and user_data.regional_id:
        query = query.filter(Regional.id == user_data.regional_id)
    return query.all()


@router.get("/centros", response_model=List[CentroFormacionResponse])
def list_centros(
    regional_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user_data: TokenData = Depends(get_current_user_data)
):
    query = db.query(CentroFormacion)
    if regional_id:
        query = query.filter(CentroFormacion.regional_id == regional_id)
    elif user_data.rol == "direccion" and user_data.regional_id:
        query = query.filter(CentroFormacion.regional_id == user_data.regional_id)
    elif user_data.rol == "coordinador" and user_data.centro_id:
        query = query.filter(CentroFormacion.id == user_data.centro_id)
    return query.all()


@router.get("/programas", response_model=List[ProgramaFormacionResponse])
def list_programas(db: Session = Depends(get_db)):
    return db.query(ProgramaFormacion).all()


@router.get("/fichas", response_model=List[FichaResponse])
def list_fichas(
    centro_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user_data: TokenData = Depends(get_current_user_data)
):
    query = db.query(Ficha)
    if centro_id:
        query = query.filter(Ficha.centro_id == centro_id)
    elif user_data.rol == "coordinador" and user_data.centro_id:
        query = query.filter(Ficha.centro_id == user_data.centro_id)
    return query.all()


@router.get("/aprendices", response_model=List[UsuarioResponse])
def list_aprendices(
    ficha_id: Optional[int] = Query(None),
    centro_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_data: TokenData = Depends(get_current_user_data)
):
    query = db.query(Usuario).filter(Usuario.rol == "aprendiz")

    if ficha_id:
        query = query.join(AprendizFicha).filter(AprendizFicha.ficha_id == ficha_id)
    if centro_id:
        query = query.filter(Usuario.centro_id == centro_id)
    if search:
        query = query.filter(
            (Usuario.nombres.ilike(f"%{search}%")) |
            (Usuario.apellidos.ilike(f"%{search}%")) |
            (Usuario.numero_documento.ilike(f"%{search}%"))
        )

    # Scope filtering by role
    if user_data.rol == "coordinador" and user_data.centro_id:
        query = query.filter(Usuario.centro_id == user_data.centro_id)
    elif user_data.rol == "direccion" and user_data.regional_id:
        query = query.filter(Usuario.regional_id == user_data.regional_id)

    return query.all()
